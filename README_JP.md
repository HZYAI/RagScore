<div align="center">
  <img src="RAGScore.png" alt="RAGScore Logo" width="400"/>
  
  [![PyPI version](https://badge.fury.io/py/ragscore.svg)](https://pypi.org/project/ragscore/)
  [![PyPI Downloads](https://static.pepy.tech/personalized-badge/ragscore?period=total&units=international_system&left_color=black&right_color=green&left_text=downloads)](https://pepy.tech/projects/ragscore)
  [![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
  [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
  [![Ollama](https://img.shields.io/badge/Ollama-Supported-orange)](https://ollama.ai)
  
  **2つのコマンドでQAデータセット生成とRAGシステム評価**
  
  🔒 プライバシー優先 • ⚡ 非同期で高速 • 🤖 任意のLLM • 🏠 ローカルまたはクラウド
  
  [English](README.md) | [中文](README_CN.md) | [日本語](README_JP.md)
</div>

---

## ⚡ 2行でRAG評価

```bash
# ステップ1：ドキュメントからQAペアを生成
ragscore generate docs/

# ステップ2：RAGシステムを評価
ragscore evaluate http://localhost:8000/query
```

**これだけです。** 精度スコアと不正解のQAペアを即座に取得。

```
============================================================
✅ 優秀：85/100 正解 (85.0%)
平均スコア：4.20/5.0
============================================================

❌ 15個の不正解ペア：

  1. Q: "RAGとは何ですか？"
     スコア：2/5 - 事実誤り

  2. Q: "検索はどのように機能しますか？"
     スコア：3/5 - 不完全な回答
```

---

## 🚀 クイックスタート

### インストール

```bash
pip install ragscore              # コア版（Ollama対応）
pip install "ragscore[openai]"    # + OpenAIサポート
pip install "ragscore[notebook]"  # + Jupyter/Colabサポート
pip install "ragscore[all]"       # + 全プロバイダー
```

### オプション1：Python API（ノートブック向け）

**Jupyter、Colab、迅速な反復**に最適。即座に可視化を取得。

```python
from ragscore import quick_test

# 1. 1行でRAGを監査
result = quick_test(
    endpoint="http://localhost:8000/query",  # RAG API
    docs="docs/",                            # ドキュメント
    n=10,                                    # テスト質問数
)

# 2. レポートを表示
result.plot()

# 3. 失敗を検査
bad_rows = result.df[result.df['score'] < 3]
display(bad_rows[['question', 'rag_answer', 'reason']])
```

**リッチオブジェクトAPI：**
- `result.accuracy` - 精度スコア
- `result.df` - 全結果のPandas DataFrame
- `result.plot()` - 3パネル可視化
- `result.corrections` - 修正が必要な項目リスト

### オプション2：CLI（本番環境）

### QAペアの生成

```bash
# APIキーを設定（またはローカルOllamaを使用 - キー不要！）
export OPENAI_API_KEY="sk-..."

# 任意のドキュメントから生成
ragscore generate paper.pdf
ragscore generate docs/*.pdf --concurrency 10
```

### RAGの評価

```bash
# RAGエンドポイントを指定
ragscore evaluate http://localhost:8000/query

# カスタムオプション
ragscore evaluate http://api/ask --model gpt-4o --output results.json
```

---

## 🏠 ローカルLLMで100%プライベート

```bash
# Ollamaを使用 - APIキー不要、クラウド不要、100%プライベート
ollama pull llama3.1
ragscore generate confidential_docs/*.pdf
ragscore evaluate http://localhost:8000/query
```

**最適な用途：** 医療 🏥 • 法律 ⚖️ • 金融 🏦 • 研究 🔬

---

## 🔌 対応LLM

| プロバイダー | セットアップ | 備考 |
|-------------|-------------|------|
| **Ollama** | `ollama serve` | ローカル、無料、プライベート |
| **OpenAI** | `export OPENAI_API_KEY="sk-..."` | 最高品質 |
| **Anthropic** | `export ANTHROPIC_API_KEY="..."` | 長いコンテキスト |
| **DashScope** | `export DASHSCOPE_API_KEY="..."` | Qwenモデル |
| **vLLM** | `export LLM_BASE_URL="..."` | プロダクショングレード |
| **OpenAI互換** | `export LLM_BASE_URL="..."` | Groq、Togetherなど |

---

## 📊 出力フォーマット

### 生成されたQAペア (`output/generated_qas.jsonl`)

```json
{
  "id": "abc123",
  "question": "RAGとは何ですか？",
  "answer": "RAG（検索拡張生成）は...",
  "rationale": "これは序論で明示的に述べられています...",
  "support_span": "RAGシステムは関連ドキュメントを検索...",
  "difficulty": "medium",
  "source_path": "docs/rag_intro.pdf"
}
```

### 評価結果 (`--output results.json`)

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
      "question": "RAGとは何ですか？",
      "golden_answer": "RAGは検索と生成を組み合わせ...",
      "rag_answer": "RAGはデータベースシステムです。",
      "score": 2,
      "reason": "事実誤り - RAGはデータベースではありません"
    }
  ]
}
```

---

## 🧪 Python API

```python
from ragscore import run_pipeline, run_evaluation

# QAペアを生成
run_pipeline(paths=["docs/"], concurrency=10)

# RAGを評価
results = run_evaluation(
    endpoint="http://localhost:8000/query",
    model="gpt-4o",  # 評価用LLM
)
print(f"精度：{results.accuracy:.1%}")
```

---

## 🤖 AIエージェント統合

RAGScoreはAIエージェントと自動化のために設計されています：

```bash
# 構造化されたCLI、予測可能な出力
ragscore generate docs/ --concurrency 5
ragscore evaluate http://api/query --output results.json

# 終了コード：0 = 成功、1 = エラー
# プログラムによる解析用のJSON出力
```

**CLIリファレンス：**

| コマンド | 説明 |
|---------|------|
| `ragscore generate <paths>` | ドキュメントからQAペアを生成 |
| `ragscore evaluate <endpoint>` | ゴールデンQAペアに対してRAGを評価 |
| `ragscore --help` | すべてのコマンドとオプションを表示 |
| `ragscore generate --help` | 生成オプションを表示 |
| `ragscore evaluate --help` | 評価オプションを表示 |

---

## ⚙️ 設定

ゼロコンフィグで動作します。オプションの環境変数：

```bash
export RAGSCORE_CHUNK_SIZE=512          # ドキュメントのチャンクサイズ
export RAGSCORE_QUESTIONS_PER_CHUNK=5   # チャンクあたりのQA数
export RAGSCORE_WORK_DIR=/path/to/dir   # 作業ディレクトリ
```

---

## 🔐 プライバシーとセキュリティ

| データ | クラウドLLM | ローカルLLM |
|--------|------------|------------|
| ドキュメント | ✅ ローカル | ✅ ローカル |
| テキストチャンク | ⚠️ LLMに送信 | ✅ ローカル |
| 生成されたQA | ✅ ローカル | ✅ ローカル |
| 評価結果 | ✅ ローカル | ✅ ローカル |

**コンプライアンス：** GDPR ✅ • HIPAA ✅（ローカルLLM使用時）• SOC 2 ✅

---

## 🧪 開発

```bash
git clone https://github.com/HZYAI/RagScore.git
cd RagScore
pip install -e ".[dev,all]"
pytest
```

---

## 🔗 リンク

- [GitHub](https://github.com/HZYAI/RagScore) • [PyPI](https://pypi.org/project/ragscore/) • [Issues](https://github.com/HZYAI/RagScore/issues) • [Discussions](https://github.com/HZYAI/RagScore/discussions)

---

<p align="center">
  <b>⭐ RAGScoreが役立つ場合は、GitHubでスターをください！</b><br>
  RAGコミュニティのために ❤️ で作られました
</p>
