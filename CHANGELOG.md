# Changelog

All notable changes to RAGScore will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0] - 2026-03-13

### Added
- **`--golden` flag for reusing QA datasets** — generate once, evaluate many times
  - CLI: `ragscore generate docs/ -o golden.jsonl` + `ragscore evaluate <endpoint> -g golden.jsonl`
  - Python API: `quick_test(endpoint, golden="golden.jsonl")` and `save_golden="golden.jsonl"`
  - MCP server: `quick_test_rag(endpoint, golden="golden.jsonl")`
  - Saves LLM cost and enables deterministic CI/CD regression testing
- `--output` / `-o` flag on `ragscore generate` to save QAs to a custom path
- Improved `--help` with golden QA reuse workflow examples

## [0.7.8] - 2026-03-12

### Added
- `ragscore --version` CLI command

### Changed
- Ollama default model updated from `llama2` to `llama3.1`
- Updated CHANGELOG with all missing entries (v0.6.4–v0.7.7)

## [0.7.7] - 2026-02-27

### Fixed
- **CJK chunk filtering** — `is_chunk_long_enough()` helper uses character count for Japanese/Chinese/Korean text where `split()` returns 1 token for entire sentences
- Fixed Japanese and German Colab notebooks to pin `ragscore>=0.7.7`

### Changed
- CLI `--help` now shows richer examples for generate and evaluate commands

## [0.7.6] - 2026-02-15

### Added
- **Japanese language support** — auto-detected prompts, QA generation, and judging in Japanese
- **German language support** — auto-detected prompts, QA generation, and judging in German
- `README_JP.md` and `README_DE.md` translations
- `examples/japanese_demo.ipynb` and `examples/german_demo.ipynb` Colab notebooks

## [0.7.5] - 2026-02-11

### Added
- **`--audience` and `--purpose` flags** for tailored QA generation
  - `ragscore generate docs/ --audience developers --purpose faq`
  - Works in CLI, Python API (`quick_test`), and MCP server
- `examples/audience_purpose_demo.ipynb` Colab notebook
- PostHog telemetry for MCP server usage tracking

## [0.7.4] - 2026-02-07

### Changed
- Multilingual QA generation improvements
- README updates across all languages

## [0.7.3] - 2026-02-05

### Added
- Star CTA in evaluate/quick_test output
- Colab badge now links to detailed evaluation demo

### Changed
- Better API key setup guidance in error messages

## [0.7.2] - 2026-02-03

### Added
- Ollama auto-detects best available model from pulled models
- MCP `num_questions` parameter

### Fixed
- Better error messages for missing providers

## [0.7.1] - 2026-01-31

### Fixed
- MCP server `asyncio.run()` bug in notebook environments
- Demo notebook: restored RAG builder cell, fixed faithfulness reference
- Dollar sign rendering in notebook output

## [0.7.0] - 2026-01-30

### Added
- **`--detailed` multi-metric evaluation** — 5 dimensions per answer in a single LLM call
  - Metrics: correctness, completeness, relevance, conciseness, faithfulness
  - Radar chart visualization in `.plot()`
  - CLI: `ragscore evaluate --detailed`
- `examples/detailed_evaluation_demo.ipynb` Colab notebook

## [0.6.10] - 2026-01-28

### Fixed
- MCP Registry server name fix

## [0.6.9] - 2026-01-28

### Added
- MCP Registry `server.json` and badge

## [0.6.8] - 2026-01-27

### Fixed
- MCP server provider parameter handling
- Corrections persistence in MCP server
- Examples lint and API correctness

## [0.6.7] - 2026-01-27

### Fixed
- Provider signatures, prompt quality, JSON parsing improvements
- Python 3.13 compatibility fixes

## [0.6.6] - 2026-01-26

### Fixed
- Added `requests` to core dependencies for Ollama support

## [0.6.5] - 2026-01-26

### Added
- Python 3.13 support

## [0.6.4] - 2026-01-25

### Changed
- Ollama performance improvements and model guide in README
- Updated tagline to "The Fastest RAG Audit"

## [0.6.3] - 2026-01-25

### Added
- **CLI `--provider` and `--model` options** - Force specific LLM provider from command line
  - `ragscore generate docs/ --provider ollama --model llama3`
  - Enables explicit Ollama usage without env var workarounds

### Fixed
- **Ollama "masquerade" mode** - OpenAI provider now reads `OPENAI_MODEL_NAME` and `OPENAI_BASE_URL` env vars
  - Fixes "model 'gpt-4o-mini' not found" error when routing OpenAI calls to local Ollama
- **Pipeline now shows active LLM** - Prints provider and model name before generation starts

## [0.6.2] - 2026-01-25

### Changed
- **PyPI keywords update** - Enhanced discoverability with notebook-focused keywords
  - Added: `jupyter`, `colab`, `notebook`, `visualization`, `mcp`, `llmops`, `ai-evaluation`
  - Removed: `golden-dataset`, `fine-tuning` (too niche)
  - Aligns with GitHub repository tags for consistent SEO

## [0.6.1] - 2026-01-24

### Changed
- **README updates** - Added Python API section with `quick_test()` examples
  - Shows Rich Object pattern (`.df`, `.plot()`, `.corrections`)
  - Organized as "Option 1: Python API" and "Option 2: CLI"
  - Updated all language versions (EN, CN, JP)
- **Demo.ipynb improvements** - Crash-proofed for Colab
  - Added explicit `nest_asyncio.apply()` safety net
  - Auto-creates sample document to prevent empty folder errors
  - Ensures zero-friction out-of-the-box experience

### Fixed
- Added `[notebook]` install option to README install section

## [0.6.0] - 2026-01-24

### Added
- **`quick_test()` function** - One-liner RAG evaluation for notebooks and CI/CD
  - Pass HTTP endpoint or Python function directly
  - Returns `QuickTestResult` with accuracy, details, and corrections
  - `return_df=True` option for pandas DataFrame output
  - Automatic correction export for RAG improvement
- **MCP Server** - AI assistant integration via Model Context Protocol
  - `ragscore serve` command starts MCP server
  - Works with Claude Desktop, Cursor, and other MCP-compatible assistants
  - Tools: `generate_qa_dataset`, `evaluate_rag`, `quick_test_rag`, `get_corrections`
- **Notebook support** - Works in Jupyter and Google Colab
  - Auto-patches asyncio with `nest_asyncio` for notebook compatibility
  - `examples/demo.ipynb` with Ollama-in-Colab setup
- New optional dependencies:
  - `ragscore[notebook]` - Jupyter/Colab support (nest_asyncio, pandas)
  - `ragscore[mcp]` - MCP server support

### Changed
- Updated `llm.txt` with v0.6.0 features and MCP instructions
- CLI help text now includes `serve` command and MCP section

## [0.5.2] - 2026-01-23

### Added
- `llm.txt`
- Updated Chinese (README_CN.md) and Japanese (README_JP.md) documentation

### Changed
- Updated CONTRIBUTING.md with v0.5.x project structure
- Added `aiohttp` to requirements.txt
- Removed RAGScore Pro marketing from .env.example

## [0.5.1] - 2026-01-21

### Fixed
- Python 3.9 compatibility: Replaced `str | Path` union syntax with `Union[str, Path]`

## [0.5.0] - 2026-01-21

### Added
- **RAG Evaluation System** - New `ragscore evaluate` command
  - LLM-as-judge scoring (1-5 scale)
  - Automatic incorrect pair detection
  - JSON output with detailed results
  - Support for custom RAG endpoint field mapping
- **Async Generation** - 5-10x faster QA generation
  - Concurrent LLM calls with configurable concurrency
  - Semaphore-based rate limiting
  - Exponential backoff for 429 errors
- **New CLI Options**
  - `--concurrency` / `-c` for parallel processing
  - `--model` for specifying judge LLM
  - `--output` / `-o` for saving evaluation results
- **Improved CLI Help** - Structured, AI-agent friendly help text

### Changed
- `ragscore evaluate` now takes endpoint as positional argument
- Default golden QA path is `output/generated_qas.jsonl`
- Progress bars show real-time evaluation status
- README completely rewritten with 2-line workflow focus

### Dependencies
- Added `aiohttp>=3.9.0` for async HTTP requests

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

## [0.1.0] - 2025-12-26

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
| 0.1.0 | 2025-12-26 | Initial release with QA generation and assessment |

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

- [GitHub Repository](https://github.com/HZYAI/RagScore)
- [Documentation](https://github.com/HZYAI/RagScore#readme)
- [PyPI Package](https://pypi.org/project/ragscore/)
- [Issue Tracker](https://github.com/HZYAI/RagScore/issues)
