<div align="center">
  <img src="RAGScore.png" alt="RAGScore Logo" width="400"/>
  
  [![PyPI version](https://badge.fury.io/py/ragscore.svg)](https://pypi.org/project/ragscore/)
  [![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
  [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
  [![Ollama Supported](https://img.shields.io/badge/Ollama-Supported-orange)](https://ollama.ai)
  
  **生成高质量的问答数据集，用于评估您的 RAG 系统**
  
  🔒 **隐私优先** • ⚡ **轻量级** • 🤖 **多提供商** • 🏠 **本地 LLM 支持**
  
  [English](README.md) | [中文](README_CN.md) | [日本語](README_JP.md)
</div>

---

## 🌟 为什么选择 RAGScore？

### **隐私优先架构**
- 🔒 **无需嵌入** - 您的文档永不离开本地
- 🏠 **本地 LLM 支持** - 使用 Ollama、vLLM 或任何本地模型
- 🔐 **符合 GDPR/HIPAA** - 适合敏感数据处理
- ✅ **文档处理零外部调用** - 数据完全本地化

### **轻量快速**
- ⚡ **仅 50 MB 安装** - 比同类工具小 90%（其他 500MB+）
- 🚀 **无重型 ML 依赖** - 无需 PyTorch、TensorFlow
- 💨 **快速启动** - 秒级就绪，而非分钟

### **真正的多提供商**
- 🤖 **自动检测** - 只需设置 API 密钥，其余交给我们
- 🔄 **即时切换** - 无需修改代码即可更换提供商
- 🌐 **支持所有主流服务** - OpenAI、Anthropic、Groq、Ollama、vLLM 等

### **开发者友好**
- 📄 **文件或目录** - 处理单个文件、多个文件或文件夹
- 🎯 **零配置** - 无需配置文件，无需设置脚本

---

## 🏠 本地 LLM：100% 隐私，100% 免费

**完美适用于：**
- 🏢 **企业** - 处理敏感数据（金融、医疗、法律）
- 🔬 **研究人员** - 处理机密论文
- 💰 **成本敏感用户** - 零 API 费用
- 🌍 **离线环境** - 无需互联网连接

### 方案 1：Ollama（推荐 - 最简单）

```bash
# 1. 安装 Ollama
brew install ollama  # 或访问 https://ollama.ai

# 2. 拉取模型
ollama pull llama3.1        # 4.7 GB，质量优秀
# 或
ollama pull qwen2.5:7b      # 4.7 GB，中文问答优秀
# 或
ollama pull llama3.1:70b    # 40 GB，最佳质量

# 3. 启动 Ollama
ollama serve

# 4. 使用 RAGScore（自动检测 Ollama！）
ragscore generate paper.pdf
```

**就这么简单！** 无需 API 密钥，无需配置，100% 隐私。

### 方案 2：vLLM（生产环境）

```bash
# 1. 安装 vLLM
pip install vllm

# 2. 启动服务器
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --host 0.0.0.0 \
  --port 8000

# 3. 配置 RAGScore
export LLM_BASE_URL="http://localhost:8000/v1"
ragscore generate paper.pdf
```

### 方案 3：LM Studio（图形界面）

1. 下载 [LM Studio](https://lmstudio.ai/)
2. 加载模型（llama-3.1、qwen-2.5 等）
3. 启动本地服务器
4. 使用 RAGScore（自动检测！）

---

## 🚀 快速开始

### 云端 LLM（快速，需要 API 密钥）

```bash
# 1. 安装
pip install "ragscore[openai]"  # 或 [anthropic]、[dashscope]

# 2. 设置 API 密钥
export OPENAI_API_KEY="sk-..."

# 3. 生成问答对
ragscore generate paper.pdf
```

### 本地 LLM（隐私，无需 API 密钥）

```bash
# 1. 安装
pip install ragscore

# 2. 启动 Ollama
ollama pull llama3.1 && ollama serve

# 3. 生成问答对（100% 隐私！）
ragscore generate paper.pdf
```

---

## 📖 使用示例

### 单个文件
```bash
ragscore generate paper.pdf
```

### 多个文件
```bash
ragscore generate paper.pdf report.txt notes.md
```

### 通配符模式
```bash
ragscore generate *.pdf
ragscore generate docs/**/*.md
```

### 目录
```bash
ragscore generate ./my_documents/
```

### 混合使用
```bash
ragscore generate paper.pdf ./more_docs/ *.txt
```

---

## 🔌 支持的提供商

### 云端提供商

| 提供商 | 设置 | 说明 |
|--------|------|------|
| **OpenAI** | `export OPENAI_API_KEY="sk-..."` | 质量最佳，广泛使用 |
| **Anthropic** | `export ANTHROPIC_API_KEY="sk-ant-..."` | 长上下文（200K tokens）|
| **Groq** | `export GROQ_API_KEY="..."` | 超快推理速度 |
| **Together AI** | `export TOGETHER_API_KEY="..."` | 多种开源模型 |
| **DashScope** | `export DASHSCOPE_API_KEY="..."` | 通义千问模型（中文）|

> 查看各提供商网站了解最新定价和功能。

### 本地提供商（隐私且免费！）

| 提供商 | 设置 | 说明 |
|--------|------|------|
| **Ollama** | `ollama serve` | 最简单设置，入门首选 |
| **vLLM** | `vllm serve model` | 生产级，高性能 |
| **LM Studio** | GUI 应用 | 用户友好界面 |
| **llama.cpp** | `./server -m model.gguf` | 轻量级，CPU 运行 |
| **LocalAI** | Docker 容器 | OpenAI 兼容 API |

### 即时切换提供商

```bash
# 周一：使用 OpenAI
export OPENAI_API_KEY="sk-..."
ragscore generate paper.pdf

# 周二：切换到本地（更隐私！）
unset OPENAI_API_KEY
ollama serve
ragscore generate paper.pdf  # 同样的命令！

# 周三：尝试 Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
ragscore generate paper.pdf  # 还是同样的命令！
```

---

## 🎯 使用场景

### 隐私敏感行业
适合处理机密数据的组织：
- 🏥 **医疗** - 本地处理医疗文档
- ⚖️ **法律** - 分析案件文件，无云端暴露
- 🏦 **金融** - 从内部报告生成问答
- 🔬 **研究** - 处理未发表论文
- 🏢 **企业** - 处理专有文档

### 通用应用
- 📚 **RAG 评估** - 为 RAG 系统生成测试数据集
- 🎓 **文档** - 从技术文档创建问答对
- 🤖 **微调** - 生成模型微调训练数据
- 📊 **知识管理** - 从公司知识库提取问答
- 🔍 **内容分析** - 理解和查询大型文档集

**所有场景都支持云端和本地 LLM！**

```bash
# 示例：本地处理文档以保护隐私
ollama pull llama3.1
ragscore generate confidential_docs/*.pdf
# ✅ 数据永不离开您的基础设施

# 示例：使用云端 LLM 获得最佳质量
export OPENAI_API_KEY="sk-..."
ragscore generate research_papers/*.pdf
# ✅ 高质量问答生成
```

---

## 📊 输出格式

```json
{
  "id": "abc123",
  "question": "什么是 RAG？",
  "answer": "RAG（检索增强生成）结合了...",
  "rationale": "这在引言中明确说明...",
  "support_span": "RAG 系统检索相关文档...",
  "difficulty": "easy",
  "doc_id": "xyz789",
  "source_path": "docs/rag_intro.pdf"
}
```

---

## 🚀 从生成到审计（RAGScore Pro）

**您已经生成了 1,000 个问答对。然后呢？**

生成数据是**第一步**。**第二步**是向审计人员证明您的 RAG 系统是安全的。

RAGScore Pro（企业版）连接到您生成的数据集，提供：

- 🕵️ **幻觉检测** - RAG 是否编造了内容？
- 📉 **回归测试** - 最新的提示更改是否破坏了 20% 的答案？
- 🏢 **团队仪表板** - 与利益相关者共享准确性报告
- 📊 **多维度评分** - 准确性、相关性、完整性
- ⚡ **CI/CD 集成** - 在流水线中自动化评估

**[加入候补名单 →](https://github.com/HZYAI/RagScore/issues/1)**

---

## 🧪 Python API

```python
from ragscore import run_pipeline, generate_qa_for_chunk
from ragscore.providers import get_provider

# 简单使用
run_pipeline(paths=["paper.pdf", "report.txt"])

# 使用本地 Ollama
provider = get_provider("ollama", model="llama3.1")
qas = generate_qa_for_chunk(
    chunk_text="您的文本内容...",
    difficulty="hard",
    n=5,
    provider=provider
)

# 使用本地 vLLM
provider = get_provider(
    "openai",  # vLLM 兼容 OpenAI
    base_url="http://localhost:8000/v1",
    api_key="not-needed"
)
qas = generate_qa_for_chunk(
    chunk_text="您的文本内容...",
    difficulty="medium",
    n=3,
    provider=provider
)
```

---

## ⚙️ 配置

RAGScore **零配置**即可工作，但您可以自定义：

```bash
# 可选：自定义分块大小
export RAGSCORE_CHUNK_SIZE=512

# 可选：每块问题数
export RAGSCORE_QUESTIONS_PER_CHUNK=5

# 可选：工作目录
export RAGSCORE_WORK_DIR=/path/to/workspace
```

---

## 🔐 隐私与安全

### 哪些数据保留在本地？
- ✅ **您的文档** - 永不发送到嵌入 API
- ✅ **文档块** - 本地处理
- ✅ **文件元数据** - 保留在您的机器上

### 哪些数据发送到 LLM？
- ⚠️ **仅文本块** - 发送到 LLM 进行问答生成
- ✅ **使用本地 LLM** - 甚至这些也保留在您的机器上！

### 合规性
- ✅ **符合 GDPR** - 无数据发送给第三方（使用本地 LLM）
- ✅ **HIPAA 友好** - 使用本地 LLM 处理 PHI
- ✅ **SOC 2 就绪** - 本地部署完全控制数据

---

## 🧪 开发

```bash
# 克隆仓库
git clone https://github.com/HZYAI/RagScore.git
cd RagScore

# 安装开发依赖
pip install -e ".[dev,all]"

# 运行测试
pytest

# 运行代码检查
ruff check src/
black --check src/
```

---

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解指南。

---

## 📄 许可证

Apache 2.0 许可证 - 详见 [LICENSE](LICENSE)。

---

## 🔗 链接

- [文档](https://github.com/HZYAI/RagScore#readme)
- [更新日志](CHANGELOG.md)
- [问题跟踪](https://github.com/HZYAI/RagScore/issues)
- [PyPI 包](https://pypi.org/project/ragscore/)

---

<p align="center">
  <b>⭐ 如果 RAGScore 对您有帮助，请在 GitHub 上给我们加星！</b><br>
  用 ❤️ 为 RAG 社区打造
</p>
