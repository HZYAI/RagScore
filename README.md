<div align="center">
  <img src="assets/ragscore-logo.png" width="260" alt="RagScore Logo" />
  <h1>RagScore</h1>
  <p><b>Multimodal RAG Assessment SDK for Python</b></p>

  <p>
    <a href="https://pypi.org/project/ragscore/">
      <img alt="PyPI" src="https://img.shields.io/pypi/v/ragscore?color=1f6feb" />
    </a>
    <a href="https://pypi.org/project/ragscore/">
      <img alt="Python" src="https://img.shields.io/pypi/pyversions/ragscore?color=f59e0b" />
    </a>
    <a href="./LICENSE">
      <img alt="License" src="https://img.shields.io/badge/license-Apache--2.0-blue" />
    </a>
  </p>
</div>

---

## ✨ What is RagScore?

**RagScore** is a lightweight Python SDK for evaluating **multimodal Retrieval-Augmented Generation (RAG)** systems.  
It provides consistent scoring across **retrieval quality**, **context usefulness**, and **generation faithfulness** — for **text + image** workflows.

---

## 🚀 Installation

```bash
pip install ragscore
```

---

## ✅ Key Features

- 📌 **Multimodal RAG evaluation** (Text / Image-ready)
- 🎯 Retrieval quality & context alignment scoring
- 🧠 Generation faithfulness & groundedness metrics
- ⚡ Simple Python SDK API, works with any RAG pipeline
- 📊 Designed for automated regression testing & benchmarking

---

## 🧩 Quick Start

```python
from ragscore import RagScorer

scorer = RagScorer()

result = scorer.score(
    query="What is shown in the image?",
    context=[
        {"type": "text", "content": "This photo shows a red sports car parked near a lake."},
        {"type": "image", "content": "https://example.com/image.jpg"}
    ],
    answer="A red sports car parked near a lake."
)

print(result)
```

---

## 📌 Output Format (Example)

```json
{
  "rag_score": 0.87,
  "retrieval": 0.90,
  "groundedness": 0.84,
  "faithfulness": 0.86,
  "details": {...}
}
```

---

## 📚 Documentation

- API reference: `docs/`
- Examples: `examples/`

---

## 🤝 Contributing

Pull requests and issues are welcome.  
Please read `CONTRIBUTING.md` before submitting.

---

## 📄 License

Licensed under the **Apache 2.0 License**.
