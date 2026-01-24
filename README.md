<div align="center">
  <img src="RAGScore.png" alt="RAGScore Logo" width="400"/>
  
  [![PyPI version](https://badge.fury.io/py/ragscore.svg)](https://pypi.org/project/ragscore/)
  [![PyPI Downloads](https://static.pepy.tech/personalized-badge/ragscore?period=total&units=international_system&left_color=black&right_color=green&left_text=downloads)](https://pepy.tech/projects/ragscore)
  [![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
  [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
  [![Ollama](https://img.shields.io/badge/Ollama-Supported-orange)](https://ollama.ai)
  
  **Generate QA datasets & evaluate RAG systems in 2 commands**
  
  🔒 Privacy-First • ⚡ Async & Fast • 🤖 Any LLM • 🏠 Local or Cloud
  
  [English](README.md) | [中文](README_CN.md) | [日本語](README_JP.md)
</div>

---

## ⚡ 2-Line RAG Evaluation

```bash
# Step 1: Generate QA pairs from your docs
ragscore generate docs/

# Step 2: Evaluate your RAG system
ragscore evaluate http://localhost:8000/query
```

**That's it.** Get accuracy scores and incorrect QA pairs instantly.

```
============================================================
✅ EXCELLENT: 85/100 correct (85.0%)
Average Score: 4.20/5.0
============================================================

❌ 15 Incorrect Pairs:

  1. Q: "What is RAG?"
     Score: 2/5 - Factually incorrect

  2. Q: "How does retrieval work?"
     Score: 3/5 - Incomplete answer
```

---

## 🚀 Quick Start

### Install

```bash
pip install ragscore              # Core (works with Ollama)
pip install "ragscore[openai]"    # + OpenAI support
pip install "ragscore[notebook]"  # + Jupyter/Colab support
pip install "ragscore[all]"       # + All providers
```

### Option 1: Python API (Notebook-Friendly)

Perfect for **Jupyter, Colab, and rapid iteration**. Get instant visualizations.

```python
from ragscore import quick_test

# 1. Audit your RAG in one line
result = quick_test(
    endpoint="http://localhost:8000/query",  # Your RAG API
    docs="docs/",                            # Your documents
    n=10,                                    # Number of test questions
)

# 2. See the report
result.plot()

# 3. Inspect failures
bad_rows = result.df[result.df['score'] < 3]
display(bad_rows[['question', 'rag_answer', 'reason']])
```

**Rich Object API:**
- `result.accuracy` - Accuracy score
- `result.df` - Pandas DataFrame of all results
- `result.plot()` - 3-panel visualization
- `result.corrections` - List of items to fix

### Option 2: CLI (Production)

### Generate QA Pairs

```bash
# Set API key (or use local Ollama - no key needed!)
export OPENAI_API_KEY="sk-..."

# Generate from any document
ragscore generate paper.pdf
ragscore generate docs/*.pdf --concurrency 10
```

### Evaluate Your RAG

```bash
# Point to your RAG endpoint
ragscore evaluate http://localhost:8000/query

# Custom options
ragscore evaluate http://api/ask --model gpt-4o --output results.json
```

---

## 🏠 100% Private with Local LLMs

```bash
# Use Ollama - no API keys, no cloud, 100% private
ollama pull llama3.1
ragscore generate confidential_docs/*.pdf
ragscore evaluate http://localhost:8000/query
```

**Perfect for:** Healthcare 🏥 • Legal ⚖️ • Finance 🏦 • Research 🔬

---

## 🔌 Supported LLMs

| Provider | Setup | Notes |
|----------|-------|-------|
| **Ollama** | `ollama serve` | Local, free, private |
| **OpenAI** | `export OPENAI_API_KEY="sk-..."` | Best quality |
| **Anthropic** | `export ANTHROPIC_API_KEY="..."` | Long context |
| **DashScope** | `export DASHSCOPE_API_KEY="..."` | Qwen models |
| **vLLM** | `export LLM_BASE_URL="..."` | Production-grade |
| **Any OpenAI-compatible** | `export LLM_BASE_URL="..."` | Groq, Together, etc. |

---

## 📊 Output Formats

### Generated QA Pairs (`output/generated_qas.jsonl`)

```json
{
  "id": "abc123",
  "question": "What is RAG?",
  "answer": "RAG (Retrieval-Augmented Generation) combines...",
  "rationale": "This is explicitly stated in the introduction...",
  "support_span": "RAG systems retrieve relevant documents...",
  "difficulty": "medium",
  "source_path": "docs/rag_intro.pdf"
}
```

### Evaluation Results (`--output results.json`)

```json
{
  "summary": {
    "total": 100,
    "correct": 85,
    "incorrect": 15,
    "accuracy": 0.85,
    "avg_score": 4.2
  },
  "incorrect_pairs": [
    {
      "question": "What is RAG?",
      "golden_answer": "RAG combines retrieval with generation...",
      "rag_answer": "RAG is a database system.",
      "score": 2,
      "reason": "Factually incorrect - RAG is not a database"
    }
  ]
}
```

---

## 🧪 Python API

```python
from ragscore import run_pipeline, run_evaluation

# Generate QA pairs
run_pipeline(paths=["docs/"], concurrency=10)

# Evaluate RAG
results = run_evaluation(
    endpoint="http://localhost:8000/query",
    model="gpt-4o",  # LLM for judging
)
print(f"Accuracy: {results.accuracy:.1%}")
```

---

## 🤖 AI Agent Integration

RAGScore is designed for AI agents and automation:

```bash
# Structured CLI with predictable output
ragscore generate docs/ --concurrency 5
ragscore evaluate http://api/query --output results.json

# Exit codes: 0 = success, 1 = error
# JSON output for programmatic parsing
```

**CLI Reference:**

| Command | Description |
|---------|-------------|
| `ragscore generate <paths>` | Generate QA pairs from documents |
| `ragscore evaluate <endpoint>` | Evaluate RAG against golden QAs |
| `ragscore --help` | Show all commands and options |
| `ragscore generate --help` | Show generate options |
| `ragscore evaluate --help` | Show evaluate options |

---

## ⚙️ Configuration

Zero config required. Optional environment variables:

```bash
export RAGSCORE_CHUNK_SIZE=512          # Chunk size for documents
export RAGSCORE_QUESTIONS_PER_CHUNK=5   # QAs per chunk
export RAGSCORE_WORK_DIR=/path/to/dir   # Working directory
```

---

## 🔐 Privacy & Security

| Data | Cloud LLM | Local LLM |
|------|-----------|-----------|
| Documents | ✅ Local | ✅ Local |
| Text chunks | ⚠️ Sent to LLM | ✅ Local |
| Generated QAs | ✅ Local | ✅ Local |
| Evaluation results | ✅ Local | ✅ Local |

**Compliance:** GDPR ✅ • HIPAA ✅ (with local LLMs) • SOC 2 ✅

---

## 🧪 Development

```bash
git clone https://github.com/HZYAI/RagScore.git
cd RagScore
pip install -e ".[dev,all]"
pytest
```

---

## 🔗 Links

- [GitHub](https://github.com/HZYAI/RagScore) • [PyPI](https://pypi.org/project/ragscore/) • [Issues](https://github.com/HZYAI/RagScore/issues) • [Discussions](https://github.com/HZYAI/RagScore/discussions)

---

<p align="center">
  <b>⭐ Star us on GitHub if RAGScore helps you!</b><br>
  Made with ❤️ for the RAG community
</p>
