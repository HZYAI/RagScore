<div align="center">
  <img src="RAGScore.png" alt="RAGScore Logo" width="400"/>
  
  [![PyPI version](https://badge.fury.io/py/ragscore.svg)](https://pypi.org/project/ragscore/)
  [![PyPI Downloads](https://static.pepy.tech/personalized-badge/ragscore?period=total&units=international_system&left_color=black&right_color=green&left_text=downloads)](https://pepy.tech/projects/ragscore)
  [![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
  [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
  [![Ollama](https://img.shields.io/badge/Ollama-Supported-orange)](https://ollama.ai)
  
  **两行命令生成问答数据集并评估 RAG 系统**
  
  🔒 隐私优先 • ⚡ 异步快速 • 🤖 任意 LLM • 🏠 本地或云端
  
  [English](README.md) | [中文](README_CN.md) | [日本語](README_JP.md)
</div>

---

## ⚡ 两行命令评估 RAG

```bash
# 第一步：从文档生成问答对
ragscore generate docs/

# 第二步：评估您的 RAG 系统
ragscore evaluate http://localhost:8000/query
```

**就这么简单。** 立即获得准确率评分和错误问答对。

```
============================================================
✅ 优秀：85/100 正确 (85.0%)
平均分数：4.20/5.0
============================================================

❌ 15 个错误问答对：

  1. 问："什么是 RAG？"
     分数：2/5 - 事实错误

  2. 问："检索如何工作？"
     分数：3/5 - 回答不完整
```

---

## 🚀 快速开始

### 安装

```bash
pip install ragscore              # 核心版（支持 Ollama）
pip install "ragscore[openai]"    # + OpenAI 支持
pip install "ragscore[all]"       # + 所有提供商
```

### 生成问答对

```bash
# 设置 API 密钥（或使用本地 Ollama - 无需密钥！）
export OPENAI_API_KEY="sk-..."

# 从任意文档生成
ragscore generate paper.pdf
ragscore generate docs/*.pdf --concurrency 10
```

### 评估您的 RAG

```bash
# 指向您的 RAG 端点
ragscore evaluate http://localhost:8000/query

# 自定义选项
ragscore evaluate http://api/ask --model gpt-4o --output results.json
```

---

## 🏠 本地 LLM 实现 100% 隐私

```bash
# 使用 Ollama - 无需 API 密钥，无云端，100% 隐私
ollama pull llama3.1
ragscore generate confidential_docs/*.pdf
ragscore evaluate http://localhost:8000/query
```

**完美适用于：** 医疗 🏥 • 法律 ⚖️ • 金融 🏦 • 研究 🔬

---

## 🔌 支持的 LLM

| 提供商 | 设置 | 说明 |
|--------|------|------|
| **Ollama** | `ollama serve` | 本地、免费、隐私 |
| **OpenAI** | `export OPENAI_API_KEY="sk-..."` | 最佳质量 |
| **Anthropic** | `export ANTHROPIC_API_KEY="..."` | 长上下文 |
| **DashScope** | `export DASHSCOPE_API_KEY="..."` | 通义千问模型 |
| **vLLM** | `export LLM_BASE_URL="..."` | 生产级 |
| **任何 OpenAI 兼容** | `export LLM_BASE_URL="..."` | Groq、Together 等 |

---

## 📊 输出格式

### 生成的问答对 (`output/generated_qas.jsonl`)

```json
{
  "id": "abc123",
  "question": "什么是 RAG？",
  "answer": "RAG（检索增强生成）结合了...",
  "rationale": "这在引言中明确说明...",
  "support_span": "RAG 系统检索相关文档...",
  "difficulty": "medium",
  "source_path": "docs/rag_intro.pdf"
}
```

### 评估结果 (`--output results.json`)

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
      "question": "什么是 RAG？",
      "golden_answer": "RAG 结合检索与生成...",
      "rag_answer": "RAG 是一个数据库系统。",
      "score": 2,
      "reason": "事实错误 - RAG 不是数据库"
    }
  ]
}
```

---

## 🧪 Python API

```python
from ragscore import run_pipeline, run_evaluation

# 生成问答对
run_pipeline(paths=["docs/"], concurrency=10)

# 评估 RAG
results = run_evaluation(
    endpoint="http://localhost:8000/query",
    model="gpt-4o",  # 用于评判的 LLM
)
print(f"准确率：{results.accuracy:.1%}")
```

---

## 🤖 AI 代理集成

RAGScore 专为 AI 代理和自动化设计：

```bash
# 结构化 CLI，输出可预测
ragscore generate docs/ --concurrency 5
ragscore evaluate http://api/query --output results.json

# 退出码：0 = 成功，1 = 错误
# JSON 输出便于程序化解析
```

**CLI 参考：**

| 命令 | 描述 |
|------|------|
| `ragscore generate <paths>` | 从文档生成问答对 |
| `ragscore evaluate <endpoint>` | 对比黄金问答对评估 RAG |
| `ragscore --help` | 显示所有命令和选项 |
| `ragscore generate --help` | 显示生成选项 |
| `ragscore evaluate --help` | 显示评估选项 |

---

## ⚙️ 配置

零配置即可使用。可选环境变量：

```bash
export RAGSCORE_CHUNK_SIZE=512          # 文档分块大小
export RAGSCORE_QUESTIONS_PER_CHUNK=5   # 每块问答数
export RAGSCORE_WORK_DIR=/path/to/dir   # 工作目录
```

---

## 🔐 隐私与安全

| 数据 | 云端 LLM | 本地 LLM |
|------|----------|----------|
| 文档 | ✅ 本地 | ✅ 本地 |
| 文本块 | ⚠️ 发送到 LLM | ✅ 本地 |
| 生成的问答 | ✅ 本地 | ✅ 本地 |
| 评估结果 | ✅ 本地 | ✅ 本地 |

**合规性：** GDPR ✅ • HIPAA ✅（使用本地 LLM）• SOC 2 ✅

---

## 🧪 开发

```bash
git clone https://github.com/HZYAI/RagScore.git
cd RagScore
pip install -e ".[dev,all]"
pytest
```

---

## 🔗 链接

- [GitHub](https://github.com/HZYAI/RagScore) • [PyPI](https://pypi.org/project/ragscore/) • [问题](https://github.com/HZYAI/RagScore/issues) • [讨论](https://github.com/HZYAI/RagScore/discussions)

---

<p align="center">
  <b>⭐ 如果 RAGScore 对您有帮助，请在 GitHub 上给我们加星！</b><br>
  用 ❤️ 为 RAG 社区打造
</p>
