# Changelog

All notable changes to RAGScore will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Multi-provider LLM support (OpenAI, DashScope, Azure OpenAI)
- Custom exception hierarchy for better error handling
- Comprehensive test suite with pytest
- CONTRIBUTING.md guide for contributors
- GitHub Actions CI/CD pipeline
- Optional dependencies for modular installation

### Changed
- Modernized `pyproject.toml` to PEP 621 format
- Simplified `setup.py` for backwards compatibility
- Improved documentation organization

### Fixed
- Removed hardcoded paths in test files
- Fixed duplicate imports in web/app.py

## [0.1.0] - 2024-12-26

### Added
- **Part 1: QA Generation**
  - Document processing for PDF, TXT, MD, HTML files
  - FAISS vector indexing for semantic search
  - LLM-powered QA pair generation with DashScope
  - Multi-language support (English and Chinese)
  - Difficulty levels: easy, medium, hard
  - CLI interface (`ragscore generate`)
  - Web interface for interactive use

- **Part 2: RAG Assessment**
  - RAG endpoint client with retry logic
  - LLM-as-judge evaluation methodology
  - Multi-dimensional scoring (accuracy, relevance, completeness)
  - Advanced metrics (hallucination detection, citation quality, latency)
  - Excel report generation
  - CLI interface (`ragscore.assessment_cli`)

- **General**
  - Modular architecture with clean separation of concerns
  - Configuration via environment variables
  - Comprehensive documentation
  - Example scripts and usage guides

### Technical Details
- Python 3.9+ support
- FAISS for vector similarity search
- DashScope integration for Qwen models
- FastAPI web framework
- WebSocket support for real-time progress updates

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 0.1.0 | 2024-12-26 | Initial release with QA generation and assessment |

## Upgrade Guide

### From Pre-release to 0.1.0

If you were using a development version:

1. Update your installation:
   ```bash
   pip install --upgrade ragscore
   ```

2. Update imports (if needed):
   ```python
   # Old
   from ragscore.llm import generate_qa
   
   # New
   from ragscore.llm import generate_qa_for_chunk
   ```

3. Update configuration:
   - Ensure `.env` file has `DASHSCOPE_API_KEY`
   - Optional: Add `OPENAI_API_KEY` for OpenAI provider

## Links

- [GitHub Repository](https://github.com/ragscore/ragscore)
- [Documentation](https://ragscore.dev/docs)
- [PyPI Package](https://pypi.org/project/ragscore/)
- [Issue Tracker](https://github.com/ragscore/ragscore/issues)
