# RAGScore

[![CI](https://github.com/HZYAI/RagScore/actions/workflows/ci.yml/badge.svg)](https://github.com/HZYAI/RagScore/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/ragscore.svg)](https://badge.fury.io/py/ragscore)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

> Generate high-quality QA datasets to evaluate your RAG systems

RAGScore automatically generates question-answer pairs from your documents, which you can then use to benchmark and evaluate your RAG (Retrieval-Augmented Generation) systems.

## ✨ Features

- 📄 **Multi-format support** - PDF, TXT, Markdown, HTML
- 🌍 **Multi-language** - English and Chinese out of the box
- 🤖 **Multi-provider** - OpenAI, DashScope (Qwen), or any OpenAI-compatible API
- 🎯 **Difficulty levels** - Easy, medium, and hard questions
- 🚀 **Simple CLI** - Easy command-line interface
- ⚡ **Fast indexing** - FAISS-powered vector search

## 🚀 Quick Start

### Installation

```bash
# Basic installation through pypi
pip install ragscore

# Basic installation through source
python -m pip install -e.

# With OpenAI support
pip install ragscore[openai]

# With DashScope support (Chinese users)
pip install ragscore[dashscope]

# All providers
pip install ragscore[all]
```

> **Note:** On first run, RAGScore automatically downloads required NLTK data (~35MB). This only happens once.

### Setup API Key

```bash
# For OpenAI
export OPENAI_API_KEY="your-openai-key"

# For DashScope (Alibaba Cloud)
export DASHSCOPE_API_KEY="your-dashscope-key"
```

### Generate QA Pairs

```bash
# Place documents in data/docs/, then:
ragscore generate
```

### Output

Generated QA pairs are saved to `output/generated_qas.jsonl`:

```json
{
  "id": "abc123",
  "question": "What is RAG?",
  "answer": "RAG (Retrieval-Augmented Generation) combines information retrieval with text generation...",
  "difficulty": "easy",
  "source_path": "docs/rag_intro.pdf"
}
```

## 📖 Usage

### Command Line

```bash
# Generate QA pairs from documents
ragscore generate

# Force re-indexing of documents
ragscore generate --force-reindex

# Use specific provider
ragscore generate --provider openai --model gpt-4o
```

### Python API

```python
from ragscore.pipeline import run_pipeline
from ragscore.data_processing import read_docs
from ragscore.llm import generate_qa_for_chunk

# Run full pipeline
run_pipeline(force_reindex=True)

# Or use individual components
docs = read_docs(dir_path="./my_docs")
for doc in docs:
    qas = generate_qa_for_chunk(doc["text"], difficulty="medium", n=5)
    print(qas)
```

## ⚙️ Configuration

Create a `.env` file or set environment variables:

```bash
# LLM Provider (auto-detected from available API keys)
DASHSCOPE_API_KEY="your-key"  # For DashScope/Qwen
OPENAI_API_KEY="your-key"     # For OpenAI

# Optional: Custom settings
RAGSCORE_CHUNK_SIZE=512
RAGSCORE_QUESTIONS_PER_CHUNK=5
```

## 🔌 Supported LLM Providers

RAGScore works with **any LLM provider** - use your own API keys!

| Provider | Models | Environment Variable |
|----------|--------|---------------------|
| **OpenAI** | gpt-4o, gpt-4o-mini, gpt-3.5-turbo | `OPENAI_API_KEY` |
| **Anthropic** | claude-3-opus, claude-3-sonnet, claude-3-haiku | `ANTHROPIC_API_KEY` |
| **Groq** | llama-3.1-70b, mixtral (ultra fast!) | `GROQ_API_KEY` |
| **Together AI** | llama-3, mistral, many open models | `TOGETHER_API_KEY` |
| **Grok (xAI)** | grok-beta | `XAI_API_KEY` |
| **Mistral** | mistral-large, mistral-medium | `MISTRAL_API_KEY` |
| **DeepSeek** | deepseek-chat, deepseek-coder | `DEEPSEEK_API_KEY` |
| **DashScope** | qwen-turbo, qwen-plus, qwen-max | `DASHSCOPE_API_KEY` |
| **Ollama** | llama2, mistral, codellama (local!) | No key needed |
| **Custom** | Any OpenAI-compatible endpoint | `LLM_BASE_URL` |

### Using Ollama (Free, Local)

```bash
# Install Ollama: https://ollama.ai
ollama pull llama2
ollama serve

# RAGScore auto-detects Ollama
ragscore generate
```

### Using Custom Endpoints

```bash
# Any OpenAI-compatible API (vLLM, LocalAI, etc.)
export LLM_BASE_URL="http://localhost:8000/v1"
export LLM_MODEL="my-model"
ragscore generate
```

## 📁 Project Structure

```
ragscore/
├── data/docs/          # Place your documents here
├── output/             # Generated QA pairs and index
│   ├── generated_qas.jsonl
│   ├── index.faiss
│   └── meta.json
└── src/ragscore/       # Source code
    ├── cli.py          # Command-line interface
    ├── pipeline.py     # Main pipeline
    ├── data_processing.py
    ├── vector_store.py
    ├── llm.py
    └── providers/      # LLM provider implementations
```

## 🚀 RAGScore Pro (Coming Soon)

Need to **evaluate** your RAG system? RAGScore Pro offers:

- 🔍 **Hallucination Detection** - Catch when your RAG makes things up
- 📝 **Citation Quality Scoring** - Verify source attribution accuracy
- 📊 **Multi-dimensional Scoring** - Accuracy, relevance, completeness
- 📈 **Executive Reports** - Excel reports for stakeholders
- ⚡ **API Access** - Integrate evaluation into your CI/CD

**[Join the waitlist →](https://github.com/HZYAI/RagScore/issues/1)**

## 🧪 Development

```bash
# Clone repository
git clone https://github.com/HZYAI/RagScore.git
cd RagScore

# Install with dev dependencies
pip install -e ".[dev,all]"

# Run tests
pytest

# Run linting
ruff check src/
black --check src/
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

Apache 2.0 License - see [LICENSE](LICENSE) for details.

## 🔗 Links

- [Documentation](https://github.com/HZYAI/RagScore#readme)
- [Changelog](CHANGELOG.md)
- [Issue Tracker](https://github.com/HZYAI/RagScore/issues)

---

<p align="center">
  Made with ❤️ for the RAG community
</p>
