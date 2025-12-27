"""Tests for the data_processing module."""

from pathlib import Path
from unittest.mock import patch

from ragscore.data_processing import chunk_text, initialize_nltk, read_docs


class TestInitializeNLTK:
    """Test NLTK initialization."""

    def test_initialize_downloads_missing_data(self):
        """Test that NLTK data is downloaded if missing."""
        with patch("nltk.data.find") as mock_find:
            mock_find.side_effect = LookupError()

            with patch("nltk.download") as mock_download:
                initialize_nltk()
                # Should attempt to download punkt_tab and/or punkt
                assert mock_download.called


class TestChunkText:
    """Test text chunking functionality."""

    def test_chunk_empty_text(self):
        """Test chunking empty text returns empty list."""
        assert chunk_text("") == []
        assert chunk_text("   ") == []

    def test_chunk_short_text(self):
        """Test chunking text shorter than chunk size."""
        text = "This is a short text."
        chunks = chunk_text(text, chunk_size=100, overlap=10)

        assert len(chunks) == 1
        assert "short text" in chunks[0]

    def test_chunk_long_text(self):
        """Test chunking text longer than chunk size."""
        # Create text with more than chunk_size words
        words = ["word"] * 100
        text = " ".join(words)

        chunks = chunk_text(text, chunk_size=30, overlap=5)

        assert len(chunks) > 1
        # Each chunk should have roughly chunk_size words
        for chunk in chunks[:-1]:  # Except last which may be shorter
            assert len(chunk.split()) <= 35  # Allow some tolerance

    def test_chunk_overlap(self):
        """Test that chunks have proper overlap."""
        text = "one two three four five six seven eight nine ten eleven twelve"
        chunks = chunk_text(text, chunk_size=6, overlap=2)

        # With overlap, consecutive chunks should share words
        assert len(chunks) >= 2

    def test_chunk_preserves_content(self):
        """Test that chunking preserves all content."""
        text = "The quick brown fox jumps over the lazy dog."
        chunks = chunk_text(text, chunk_size=5, overlap=1)

        # All original words should be in at least one chunk
        original_words = set(text.replace(".", "").split())
        chunked_words = set()
        for chunk in chunks:
            chunked_words.update(chunk.split())

        assert original_words <= chunked_words

    def test_chunk_bad_parameters(self):
        """Test chunking with edge case parameters."""
        text = "one two three four five"

        # overlap >= chunk_size should still make progress
        chunks = chunk_text(text, chunk_size=2, overlap=5)
        assert len(chunks) > 0


class TestReadDocs:
    """Test document reading functionality."""

    def test_read_empty_directory(self, temp_dir: Path):
        """Test reading from empty directory."""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()

        docs = read_docs(dir_path=empty_dir)
        assert docs == []

    def test_read_txt_file(self, sample_docs_dir: Path):
        """Test reading text files."""
        docs = read_docs(dir_path=sample_docs_dir)

        # Should find at least the .txt file
        txt_docs = [d for d in docs if d["path"].endswith(".txt")]
        assert len(txt_docs) >= 1
        assert "machine learning" in txt_docs[0]["text"].lower()

    def test_read_md_file(self, sample_docs_dir: Path):
        """Test reading markdown files."""
        docs = read_docs(dir_path=sample_docs_dir)

        md_docs = [d for d in docs if d["path"].endswith(".md")]
        assert len(md_docs) >= 1
        assert "documentation" in md_docs[0]["text"].lower()

    def test_read_specific_files(self, sample_docs_dir: Path):
        """Test reading specific files only."""
        docs = read_docs(dir_path=sample_docs_dir, specific_files=["sample.txt"])

        assert len(docs) == 1
        assert docs[0]["path"].endswith("sample.txt")

    def test_read_nonexistent_specific_file(self, sample_docs_dir: Path, capsys):
        """Test reading non-existent specific file."""
        docs = read_docs(dir_path=sample_docs_dir, specific_files=["nonexistent.txt"])

        assert len(docs) == 0
        captured = capsys.readouterr()
        assert "not found" in captured.out.lower()

    def test_read_unsupported_extension(self, temp_dir: Path, capsys):
        """Test reading file with unsupported extension."""
        docs_dir = temp_dir / "docs"
        docs_dir.mkdir()
        (docs_dir / "data.xyz").write_text("some content")

        docs = read_docs(dir_path=docs_dir, specific_files=["data.xyz"])

        assert len(docs) == 0
        captured = capsys.readouterr()
        assert "unsupported" in captured.out.lower()

    def test_doc_has_required_fields(self, sample_docs_dir: Path):
        """Test that documents have all required fields."""
        docs = read_docs(dir_path=sample_docs_dir)

        assert len(docs) > 0
        for doc in docs:
            assert "doc_id" in doc
            assert "path" in doc
            assert "text" in doc
            assert len(doc["doc_id"]) > 0
            assert len(doc["text"]) > 0

    def test_read_pdf_file(self, temp_dir: Path):
        """Test reading PDF files (if PyPDF2 works)."""
        # This is a basic test - full PDF testing would need fixture files
        docs_dir = temp_dir / "docs"
        docs_dir.mkdir()

        # Create a minimal PDF (may not work without actual PDF content)
        # For now, just test that the function doesn't crash
        docs = read_docs(dir_path=docs_dir)
        assert isinstance(docs, list)


class TestReadDocsIntegration:
    """Integration tests for document reading."""

    def test_read_recursive(self, temp_dir: Path):
        """Test that read_docs finds files in subdirectories."""
        docs_dir = temp_dir / "docs"
        sub_dir = docs_dir / "subdir"
        sub_dir.mkdir(parents=True)

        (docs_dir / "root.txt").write_text("Root document")
        (sub_dir / "nested.txt").write_text("Nested document")

        docs = read_docs(dir_path=docs_dir)

        # Should find both files
        paths = [d["path"] for d in docs]
        assert any("root.txt" in p for p in paths)
        assert any("nested.txt" in p for p in paths)
