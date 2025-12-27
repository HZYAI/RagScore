<div align="center">
  <img src="RAGScore.png" alt="RAGScore Logo" width="400"/>
  
  [![PyPI version](https://badge.fury.io/py/ragscore.svg)](https://pypi.org/project/ragscore/)
  [![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
  [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
  [![Ollama Supported](https://img.shields.io/badge/Ollama-Supported-orange)](https://ollama.ai)
  
  **Generate high-quality QA datasets to evaluate your RAG systems**
  
  🔒 **Privacy-First** • ⚡ **Lightweight** • 🤖 **Multi-Provider** • 🏠 **Local LLM Support**
  
  [English](README.md) | [中文](README_CN.md) | [日本語](README_JP.md)
</div>

---

## 🌟 Why RAGScore?

### **Privacy-First Architecture**
- 🔒 **No embeddings** - Your documents never leave your machine
- 🏠 **Local LLM support** - Use Ollama, vLLM, or any local model
- 🔐 **GDPR/HIPAA compliant** - Perfect for sensitive data
- ✅ **Zero external API calls** during document processing

### **Lightweight & Fast**
- ⚡ **50 MB install** - 90% smaller than alternatives (500MB+)
- 🚀 **No heavy ML dependencies** - No PyTorch, no TensorFlow
- 💨 **Quick startup** - Ready in seconds, not minutes

### **True Multi-Provider**
- 🤖 **Auto-detection** - Just set API key, we handle the rest
- 🔄 **Switch instantly** - Change providers without code changes
- 🌐 **Works with everything** - OpenAI, Anthropic, Groq, Ollama, vLLM, and more

### **Developer-Friendly**
- 📄 **File or directory** - Process single files, multiple files, or folders
- 🎯 **Zero configuration** - No config files, no setup scripts

---

## 🏠 Local LLMs: 100% Private, 100% Free

**Perfect for:**
- 🏢 **Enterprises** with sensitive data (financial, medical, legal)
- 🔬 **Researchers** processing confidential papers
- 💰 **Cost-conscious users** who want zero API fees
- 🌍 **Offline environments** without internet access

### Option 1: Ollama (Recommended - Easiest)

```bash
# 1. Install Ollama
brew install ollama  # or visit https://ollama.ai

# 2. Pull a model
ollama pull llama3.1        # 4.7 GB, great quality
# or
ollama pull qwen2.5:7b      # 4.7 GB, excellent for QA
# or
ollama pull llama3.1:70b    # 40 GB, best quality

# 3. Start Ollama
ollama serve

# 4. Use RAGScore (auto-detects Ollama!)
ragscore generate paper.pdf
```

**That's it!** No API keys, no configuration, 100% private.

### Option 2: vLLM (For Production)

```bash
# 1. Install vLLM
pip install vllm

# 2. Start server with your model
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --host 0.0.0.0 \
  --port 8000

# 3. Point RAGScore to it
export LLM_BASE_URL="http://localhost:8000/v1"
ragscore generate paper.pdf
```

### Option 3: LM Studio (GUI)

1. Download [LM Studio](https://lmstudio.ai/)
2. Load a model (llama-3.1, qwen-2.5, etc.)
3. Start local server
4. Use with RAGScore (auto-detected!)

---

## 🚀 Quick Start

### Cloud LLMs (Fast, Requires API Key)

```bash
# 1. Install
pip install "ragscore[openai]"  # or [anthropic], [dashscope]

# 2. Set API key
export OPENAI_API_KEY="sk-..."

# 3. Generate QA pairs
ragscore generate paper.pdf
```

### Local LLMs (Private, No API Key)

```bash
# 1. Install
pip install ragscore

# 2. Start Ollama
ollama pull llama3.1 && ollama serve

# 3. Generate QA pairs (100% private!)
ragscore generate paper.pdf
```

---

## 📖 Usage Examples

### Single File
```bash
ragscore generate paper.pdf
```

### Multiple Files
```bash
ragscore generate paper.pdf report.txt notes.md
```

### Glob Patterns
```bash
ragscore generate *.pdf
ragscore generate docs/**/*.md
```

### Directory
```bash
ragscore generate ./my_documents/
```

### Mix Everything
```bash
ragscore generate paper.pdf ./more_docs/ *.txt
```

---

## 🔌 Supported Providers

### Cloud Providers

| Provider | Setup | Notes |
|----------|-------|-------|
| **OpenAI** | `export OPENAI_API_KEY="sk-..."` | Best quality, widely used |
| **Anthropic** | `export ANTHROPIC_API_KEY="sk-ant-..."` | Long context (200K tokens) |
| **DashScope** | `export DASHSCOPE_API_KEY="..."` | Qwen models  |

> See each provider's website for current pricing and features.

### Local Providers (Private & Free!)

| Provider | Setup | Notes |
|----------|-------|-------|
| **Ollama** | `ollama serve` | Easiest setup, great for getting started |
| **vLLM** | `vllm serve model` | Production-grade, high performance |
| **LM Studio** | GUI app | User-friendly interface |
| **llama.cpp** | `./server -m model.gguf` | Lightweight, runs on CPU |
| **LocalAI** | Docker container | OpenAI-compatible API |

### Switch Providers Instantly

```bash
# Monday: Use OpenAI
export OPENAI_API_KEY="sk-..."
ragscore generate paper.pdf

# Tuesday: Switch to local (more private!)
unset OPENAI_API_KEY
ollama serve
ragscore generate paper.pdf  # Same command!

# Wednesday: Try Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
ragscore generate paper.pdf  # Still same command!
```

---

## 🎯 Use Cases

### Privacy-Sensitive Industries
Perfect for organizations handling confidential data:
- 🏥 **Healthcare** - Process medical documents locally
- ⚖️ **Legal** - Analyze case files without cloud exposure  
- 🏦 **Finance** - Generate QA from internal reports
- 🔬 **Research** - Work with unpublished papers
- 🏢 **Enterprise** - Handle proprietary documentation

### General Applications
- 📚 **RAG Evaluation** - Generate test datasets for your RAG system
- 🎓 **Documentation** - Create QA pairs from technical docs
- 🤖 **Fine-tuning** - Generate training data for model fine-tuning
- 📊 **Knowledge Management** - Extract Q&A from company knowledge bases

**All use cases work with both cloud and local LLMs!**

```bash
# Example: Process documents locally for privacy
ollama pull llama3.1
ragscore generate confidential_docs/*.pdf
# ✅ Data never leaves your infrastructure

# Example: Use cloud LLM for best quality
export OPENAI_API_KEY="sk-..."
ragscore generate research_papers/*.pdf
# ✅ High-quality QA generation
```

---

## 📊 Output Format

```json
{
  "id": "abc123",
  "question": "What is RAG?",
  "answer": "RAG (Retrieval-Augmented Generation) combines...",
  "rationale": "This is explicitly stated in the introduction...",
  "support_span": "RAG systems retrieve relevant documents...",
  "difficulty": "easy",
  "doc_id": "xyz789",
  "source_path": "docs/rag_intro.pdf"
}
```

---

## 🚀 From Generation to Audit (RAGScore Pro)

**You've generated 1,000 QA pairs. Now what?**

Generating the data is **Step 1**. **Step 2** is proving to your auditors that your RAG system is safe.

RAGScore Pro (Enterprise) connects to your generated dataset to provide:

- 🕵️ **Hallucination Detection** - Did your RAG make things up?
- 📉 **Regression Testing** - Did your latest prompt change break 20% of your answers?
- 🏢 **Team Dashboards** - Share accuracy reports with stakeholders
- 📊 **Multi-dimensional Scoring** - Accuracy, relevance, completeness
- ⚡ **CI/CD Integration** - Automated evaluation in your pipeline

**[Sign Up for Waitlist →](https://github.com/HZYAI/RagScore/issues/1)**

---

## 🧪 Python API

```python
from ragscore import run_pipeline, generate_qa_for_chunk
from ragscore.providers import get_provider

# Simple usage
run_pipeline(paths=["paper.pdf", "report.txt"])

# Use local Ollama
provider = get_provider("ollama", model="llama3.1")
qas = generate_qa_for_chunk(
    chunk_text="Your text here...",
    difficulty="hard",
    n=5,
    provider=provider
)

# Use local vLLM
provider = get_provider(
    "openai",  # vLLM is OpenAI-compatible
    base_url="http://localhost:8000/v1",
    api_key="not-needed"
)
qas = generate_qa_for_chunk(
    chunk_text="Your text here...",
    difficulty="medium",
    n=3,
    provider=provider
)
```

---

## ⚙️ Configuration

RAGScore works with **zero configuration**, but you can customize:

```bash
# Optional: Customize chunk size
export RAGSCORE_CHUNK_SIZE=512

# Optional: Questions per chunk
export RAGSCORE_QUESTIONS_PER_CHUNK=5

# Optional: Working directory
export RAGSCORE_WORK_DIR=/path/to/workspace
```

---

## 🔐 Privacy & Security

### What Data Stays Local?
- ✅ **Your documents** - Never sent to embedding APIs
- ✅ **Document chunks** - Processed locally
- ✅ **File metadata** - Stays on your machine

### What Data is Sent to LLM?
- ⚠️ **Text chunks only** - Sent to LLM for QA generation
- ✅ **With local LLMs** - Even this stays on your machine!

### Compliance
- ✅ **GDPR compliant** - No data sent to third parties (with local LLMs)
- ✅ **HIPAA friendly** - Use local LLMs for PHI
- ✅ **SOC 2 ready** - Full data control with local deployment

---

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

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

Apache 2.0 License - see [LICENSE](LICENSE) for details.

---

## 🔗 Links

- [Documentation](https://github.com/HZYAI/RagScore#readme)
- [Changelog](CHANGELOG.md)
- [Issue Tracker](https://github.com/HZYAI/RagScore/issues)
- [PyPI Package](https://pypi.org/project/ragscore/)

---

<p align="center">
  <b>⭐ Star us on GitHub if RAGScore helps you!</b><br>
  Made with ❤️ for the RAG community
</p>
