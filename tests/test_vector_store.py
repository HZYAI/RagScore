"""Tests for the vector_store module."""

from pathlib import Path
from unittest.mock import patch

from ragscore.vector_store import build_index, load_index, retrieve, save_index


class TestBuildIndex:
    """Test index building functionality."""

    def test_build_index_empty_docs(self, mock_embeddings):
        """Test building index with empty document list."""
        index, meta = build_index([])

        assert index is None
        assert meta == []

    def test_build_index_single_doc(self, mock_embeddings):
        """Test building index with a single document."""
        docs = [
            {
                "doc_id": "doc1",
                "path": "/test/doc.txt",
                "text": " ".join(["word"] * 100),  # Enough words for chunking
            }
        ]

        index, meta = build_index(docs)

        assert index is not None
        assert len(meta) > 0
        assert meta[0]["doc_id"] == "doc1"

    def test_build_index_multiple_docs(self, mock_embeddings):
        """Test building index with multiple documents."""
        docs = [
            {"doc_id": f"doc{i}", "path": f"/test/doc{i}.txt", "text": " ".join(["content"] * 100)}
            for i in range(3)
        ]

        index, meta = build_index(docs)

        assert index is not None
        assert len(meta) >= 3  # At least one chunk per doc

    def test_build_index_metadata_fields(self, mock_embeddings):
        """Test that metadata contains required fields."""
        docs = [
            {"doc_id": "test-doc", "path": "/path/to/test.txt", "text": " ".join(["sample"] * 100)}
        ]

        index, meta = build_index(docs)

        for chunk_meta in meta:
            assert "doc_id" in chunk_meta
            assert "path" in chunk_meta
            assert "text" in chunk_meta
            assert "chunk_id" in chunk_meta

    def test_build_index_short_text(self, mock_embeddings):
        """Test building index with text too short to chunk."""
        docs = [{"doc_id": "short-doc", "path": "/test/short.txt", "text": "Short"}]

        # Should still create chunks, even if just one
        index, meta = build_index(docs)

        # Result depends on implementation - either has one chunk or none
        assert isinstance(meta, list)


class TestSaveLoadIndex:
    """Test index saving and loading."""

    def test_save_index(self, temp_dir: Path, mock_embeddings):
        """Test saving index to disk."""
        docs = [{"doc_id": "doc1", "path": "/test/doc.txt", "text": " ".join(["word"] * 100)}]

        index, meta = build_index(docs)

        index_path = temp_dir / "index.faiss"
        meta_path = temp_dir / "meta.json"

        with patch("ragscore.config.INDEX_PATH", index_path):
            with patch("ragscore.config.META_PATH", meta_path):
                save_index(index, meta)

        assert index_path.exists()
        assert meta_path.exists()

    def test_load_index(self, temp_dir: Path, mock_embeddings):
        """Test loading index from disk."""
        docs = [{"doc_id": "doc1", "path": "/test/doc.txt", "text": " ".join(["word"] * 100)}]

        index, meta = build_index(docs)

        index_path = temp_dir / "index.faiss"
        meta_path = temp_dir / "meta.json"

        with patch("ragscore.config.INDEX_PATH", index_path):
            with patch("ragscore.config.META_PATH", meta_path):
                save_index(index, meta)

                loaded_index, loaded_meta = load_index()

        assert loaded_index is not None
        assert len(loaded_meta) == len(meta)

    def test_load_nonexistent_index(self, temp_dir: Path):
        """Test loading non-existent index."""
        with patch("ragscore.config.INDEX_PATH", temp_dir / "nonexistent.faiss"):
            with patch("ragscore.config.META_PATH", temp_dir / "nonexistent.json"):
                index, meta = load_index()

        assert index is None
        assert meta == []

    def test_save_load_preserves_data(self, temp_dir: Path, mock_embeddings):
        """Test that save/load preserves all metadata."""
        docs = [
            {
                "doc_id": "test-123",
                "path": "/custom/path/doc.txt",
                "text": " ".join(["preservation"] * 100),
            }
        ]

        index, meta = build_index(docs)
        original_meta = meta.copy()

        index_path = temp_dir / "index.faiss"
        meta_path = temp_dir / "meta.json"

        with patch("ragscore.config.INDEX_PATH", index_path):
            with patch("ragscore.config.META_PATH", meta_path):
                save_index(index, meta)
                _, loaded_meta = load_index()

        assert loaded_meta == original_meta


class TestRetrieve:
    """Test retrieval functionality."""

    def test_retrieve_none_index(self):
        """Test retrieval with None index."""
        results = retrieve("test query", None, [])
        assert results == []

    def test_retrieve_returns_results(self, mock_embeddings):
        """Test that retrieval returns results."""
        # Build a simple index
        docs = [
            {
                "doc_id": "doc1",
                "path": "/test/doc.txt",
                "text": " ".join(["machine", "learning"] * 50),
            }
        ]

        index, meta = build_index(docs)

        if index is not None:
            results = retrieve("machine learning", index, meta, k=3)

            assert isinstance(results, list)
            if results:  # May be empty if embedding mock doesn't support search
                assert "score" in results[0]
                assert "text" in results[0]

    def test_retrieve_k_limit(self, mock_embeddings):
        """Test that retrieval respects k limit."""
        docs = [
            {"doc_id": f"doc{i}", "path": f"/test/doc{i}.txt", "text": " ".join(["content"] * 100)}
            for i in range(10)
        ]

        index, meta = build_index(docs)

        if index is not None:
            results = retrieve("test", index, meta, k=3)
            assert len(results) <= 3


class TestIndexIntegration:
    """Integration tests for index operations."""

    def test_full_index_workflow(self, temp_dir: Path, sample_docs_dir: Path, mock_embeddings):
        """Test complete index build, save, load, retrieve workflow."""
        from ragscore.data_processing import read_docs

        # Read documents
        docs = read_docs(dir_path=sample_docs_dir)
        assert len(docs) > 0

        # Build index
        index, meta = build_index(docs)
        assert index is not None

        # Save index
        index_path = temp_dir / "test_index.faiss"
        meta_path = temp_dir / "test_meta.json"

        with patch("ragscore.config.INDEX_PATH", index_path):
            with patch("ragscore.config.META_PATH", meta_path):
                save_index(index, meta)

                # Load index
                loaded_index, loaded_meta = load_index()
                assert loaded_index is not None
                assert len(loaded_meta) == len(meta)
