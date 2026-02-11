"""
Basic RAGScore Usage Example

This example shows how to generate QA pairs from documents.
"""

from pathlib import Path

from ragscore import run_pipeline
from ragscore.data_processing import chunk_text, read_docs
from ragscore.llm import generate_qa_for_chunk


def pipeline_example():
    """Option 1: Run the full pipeline (easiest)."""
    # Just place documents in data/docs/ and run:
    run_pipeline()


def component_example():
    """Option 2: Use individual components for more control."""
    # Read documents
    docs = read_docs(dir_path=Path("./my_documents"))

    # Process each document
    for doc in docs:
        # Chunk the text
        chunks = chunk_text(doc["text"], chunk_size=512)

        # Generate QA pairs for each chunk
        for chunk in chunks:
            qa_pairs = generate_qa_for_chunk(chunk, difficulty="medium", n=3)

            for qa in qa_pairs:
                print(f"Q: {qa['question']}")
                print(f"A: {qa['answer']}")
                print("---")


if __name__ == "__main__":
    # Choose one:
    pipeline_example()
    # component_example()
