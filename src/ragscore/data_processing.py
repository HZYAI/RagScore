import uuid
from pathlib import Path
from typing import Any

import nltk
import PyPDF2
from tqdm import tqdm

from . import config


def initialize_nltk():
    """Download necessary NLTK models with SSL fix for Windows."""
    import ssl

    # Fix SSL certificate issues on Windows
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    models_needed = []

    # Check which models are missing
    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        models_needed.append("punkt_tab")

    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        models_needed.append("punkt")

    # Download missing models
    for model in models_needed:
        print(f"Downloading NLTK '{model}' model...")
        try:
            nltk.download(model, quiet=False)
        except Exception as e:
            print(f"Warning: Failed to download {model}: {e}")
            print(
                "You can manually download with: python -c \"import nltk; nltk.download('punkt')\""
            )
            # Try alternative download location
            try:
                nltk.download(model, download_dir=None, quiet=False)
            except Exception:
                pass


def read_docs(
    dir_path: Path = config.DOCS_DIR, specific_files: list[str] = None
) -> list[dict[str, Any]]:
    """
    Reads supported documents from a directory.

    Args:
        dir_path: Directory to read from
        specific_files: Optional list of specific filenames to process (e.g., ['doc1.pdf', 'doc2.txt'])
                       If provided, only these files will be processed.

    Returns:
        List of document dictionaries
    """
    docs = []
    supported_extensions = (".pdf", ".txt", ".md", ".html")

    if specific_files:
        # Only process specified files
        file_paths = []
        for filename in specific_files:
            file_path = dir_path / filename
            if file_path.exists() and file_path.suffix.lower() in supported_extensions:
                file_paths.append(file_path)
            elif file_path.exists():
                print(f"Warning: {filename} has unsupported extension")
            else:
                print(f"Warning: {filename} not found in {dir_path}")
    else:
        # Process all files in directory
        file_paths = [p for p in dir_path.rglob("*") if p.suffix.lower() in supported_extensions]

    if not file_paths:
        print(f"No supported documents found in {dir_path}.")
        return []

    print(f"Found {len(file_paths)} documents to process...")
    for p in tqdm(file_paths, desc="Reading documents"):
        text = ""
        try:
            if p.suffix.lower() == ".pdf":
                with open(p, "rb") as fh:
                    reader = PyPDF2.PdfReader(fh)
                    text = "".join(page.extract_text() or "" for page in reader.pages)
            else:
                with open(p, encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()

            if text.strip():
                docs.append({"doc_id": str(uuid.uuid4()), "path": str(p), "text": text})
            else:
                print(f"Warning: No text extracted from {p}")
        except Exception as e:
            print(f"Error reading {p}: {e}")

    print(f"Successfully loaded {len(docs)} documents.")
    return docs


def chunk_text(
    text: str, chunk_size: int = config.CHUNK_SIZE, overlap: int = config.CHUNK_OVERLAP
) -> list[str]:
    """Splits text into chunks using NLTK tokenizer."""
    if not text:
        return []

    # Try to tokenize with fallback for NLTK version issues
    try:
        tokens = nltk.word_tokenize(text)
    except LookupError:
        # Fallback: simple whitespace tokenization if NLTK data is missing
        print("Warning: NLTK tokenizer unavailable, using simple whitespace tokenization")
        tokens = text.split()

    chunks = []
    i = 0
    while i < len(tokens):
        chunk_tokens = tokens[i : i + chunk_size]
        chunks.append(" ".join(chunk_tokens))
        if chunk_size <= overlap:
            i += 1  # Ensure progress even with bad parameters
        else:
            i += chunk_size - overlap
    return chunks
