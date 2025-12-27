<div align="center">
  <img src="RAGScore.png" alt="RAGScore Logo" width="400"/>
  
  [![PyPI version](https://badge.fury.io/py/ragscore.svg)](https://pypi.org/project/ragscore/)
  [![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
  [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
  [![Ollama Supported](https://img.shields.io/badge/Ollama-Supported-orange)](https://ollama.ai)
  
  **RAGシステム評価用の高品質QAデータセットを生成**
  
  🔒 **プライバシー優先** • ⚡ **軽量** • 🤖 **マルチプロバイダー** • 🏠 **ローカルLLM対応**
  
  [English](README.md) | [中文](README_CN.md) | [日本語](README_JP.md)
</div>

---

## 🌟 RAGScoreを選ぶ理由

### **プライバシー優先アーキテクチャ**
- 🔒 **埋め込み不要** - ドキュメントがマシンから出ることはありません
- 🏠 **ローカルLLM対応** - Ollama、vLLM、その他のローカルモデルを使用
- 🔐 **GDPR/HIPAA準拠** - 機密データに最適
- ✅ **ドキュメント処理時の外部API呼び出しゼロ** - 完全ローカル処理

### **軽量で高速**
- ⚡ **50MBのインストール** - 代替ツールより90%小さい（他は500MB以上）
- 🚀 **重いML依存関係なし** - PyTorch、TensorFlow不要
- 💨 **高速起動** - 数秒で準備完了

### **真のマルチプロバイダー**
- 🤖 **自動検出** - APIキーを設定するだけ、あとはお任せ
- 🔄 **即座に切り替え** - コード変更なしでプロバイダーを変更
- 🌐 **すべてに対応** - OpenAI、Anthropic、Groq、Ollama、vLLMなど

### **開発者フレンドリー**
- 📄 **ファイルまたはディレクトリ** - 単一ファイル、複数ファイル、フォルダーを処理
- 🎯 **ゼロコンフィグ** - 設定ファイル不要、セットアップスクリプト不要

---

## 🏠 ローカルLLM：100%プライベート、100%無料

**最適な用途：**
- 🏢 **企業** - 機密データ（金融、医療、法律）の処理
- 🔬 **研究者** - 非公開論文の処理
- 💰 **コスト重視のユーザー** - API料金ゼロ
- 🌍 **オフライン環境** - インターネット接続不要

### オプション1：Ollama（推奨 - 最も簡単）

```bash
# 1. Ollamaをインストール
brew install ollama  # または https://ollama.ai にアクセス

# 2. モデルをプル
ollama pull llama3.1        # 4.7 GB、優れた品質
# または
ollama pull qwen2.5:7b      # 4.7 GB、QAに優れている
# または
ollama pull llama3.1:70b    # 40 GB、最高品質

# 3. Ollamaを起動
ollama serve

# 4. RAGScoreを使用（Ollamaを自動検出！）
ragscore generate paper.pdf
```

**これだけです！** APIキー不要、設定不要、100%プライベート。

### オプション2：vLLM（本番環境向け）

```bash
# 1. vLLMをインストール
pip install vllm

# 2. モデルでサーバーを起動
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --host 0.0.0.0 \
  --port 8000

# 3. RAGScoreを設定
export LLM_BASE_URL="http://localhost:8000/v1"
ragscore generate paper.pdf
```

### オプション3：LM Studio（GUI）

1. [LM Studio](https://lmstudio.ai/)をダウンロード
2. モデルをロード（llama-3.1、qwen-2.5など）
3. ローカルサーバーを起動
4. RAGScoreを使用（自動検出！）

---

## 🚀 クイックスタート

### クラウドLLM（高速、APIキー必要）

```bash
# 1. インストール
pip install "ragscore[openai]"  # または [anthropic]、[dashscope]

# 2. APIキーを設定
export OPENAI_API_KEY="sk-..."

# 3. QAペアを生成
ragscore generate paper.pdf
```

### ローカルLLM（プライベート、APIキー不要）

```bash
# 1. インストール
pip install ragscore

# 2. Ollamaを起動
ollama pull llama3.1 && ollama serve

# 3. QAペアを生成（100%プライベート！）
ragscore generate paper.pdf
```

---

## 📖 使用例

### 単一ファイル
```bash
ragscore generate paper.pdf
```

### 複数ファイル
```bash
ragscore generate paper.pdf report.txt notes.md
```

### グロブパターン
```bash
ragscore generate *.pdf
ragscore generate docs/**/*.md
```

### ディレクトリ
```bash
ragscore generate ./my_documents/
```

### 混在使用
```bash
ragscore generate paper.pdf ./more_docs/ *.txt
```

---

## 🔌 対応プロバイダー

### クラウドプロバイダー

| プロバイダー | セットアップ | 備考 |
|-------------|-------------|------|
| **OpenAI** | `export OPENAI_API_KEY="sk-..."` | 最高品質、広く使用されている |
| **Anthropic** | `export ANTHROPIC_API_KEY="sk-ant-..."` | 長いコンテキスト（200Kトークン）|
| **Groq** | `export GROQ_API_KEY="..."` | 超高速推論 |
| **Together AI** | `export TOGETHER_API_KEY="..."` | 多数のオープンソースモデル |
| **DashScope** | `export DASHSCOPE_API_KEY="..."` | Qwenモデル（中国語）|

> 最新の価格と機能については、各プロバイダーのウェブサイトをご覧ください。

### ローカルプロバイダー（プライベートで無料！）

| プロバイダー | セットアップ | 備考 |
|-------------|-------------|------|
| **Ollama** | `ollama serve` | 最も簡単なセットアップ、入門に最適 |
| **vLLM** | `vllm serve model` | 本番グレード、高性能 |
| **LM Studio** | GUIアプリ | ユーザーフレンドリーなインターフェース |
| **llama.cpp** | `./server -m model.gguf` | 軽量、CPUで動作 |
| **LocalAI** | Dockerコンテナ | OpenAI互換API |

### プロバイダーを即座に切り替え

```bash
# 月曜日：OpenAIを使用
export OPENAI_API_KEY="sk-..."
ragscore generate paper.pdf

# 火曜日：ローカルに切り替え（よりプライベート！）
unset OPENAI_API_KEY
ollama serve
ragscore generate paper.pdf  # 同じコマンド！

# 水曜日：Anthropicを試す
export ANTHROPIC_API_KEY="sk-ant-..."
ragscore generate paper.pdf  # まだ同じコマンド！
```

---

## 🎯 ユースケース

### プライバシー重視の業界
機密データを扱う組織に最適：
- 🏥 **医療** - 医療文書をローカルで処理
- ⚖️ **法律** - クラウド露出なしでケースファイルを分析
- 🏦 **金融** - 内部レポートからQAを生成
- 🔬 **研究** - 未発表論文を処理
- 🏢 **企業** - 独自文書を処理

### 一般的なアプリケーション
- 📚 **RAG評価** - RAGシステム用のテストデータセットを生成
- 🎓 **ドキュメント** - 技術文書からQAペアを作成
- 🤖 **ファインチューニング** - モデルファインチューニング用のトレーニングデータを生成
- 📊 **ナレッジマネジメント** - 企業ナレッジベースからQ&Aを抽出
- 🔍 **コンテンツ分析** - 大規模文書セットを理解しクエリ

**すべてのユースケースでクラウドとローカルLLMの両方に対応！**

```bash
# 例：プライバシー保護のためローカルで文書を処理
ollama pull llama3.1
ragscore generate confidential_docs/*.pdf
# ✅ データがインフラストラクチャから出ることはありません

# 例：最高品質のためクラウドLLMを使用
export OPENAI_API_KEY="sk-..."
ragscore generate research_papers/*.pdf
# ✅ 高品質なQA生成
```

---

## 📊 出力フォーマット

```json
{
  "id": "abc123",
  "question": "RAGとは何ですか？",
  "answer": "RAG（検索拡張生成）は...",
  "rationale": "これは序論で明示的に述べられています...",
  "support_span": "RAGシステムは関連文書を検索します...",
  "difficulty": "easy",
  "doc_id": "xyz789",
  "source_path": "docs/rag_intro.pdf"
}
```

---

## 🚀 生成から監査へ（RAGScore Pro）

**1,000個のQAペアを生成しました。次は？**

データ生成は**ステップ1**です。**ステップ2**は、RAGシステムが安全であることを監査人に証明することです。

RAGScore Pro（エンタープライズ）は、生成されたデータセットに接続して以下を提供します：

- 🕵️ **幻覚検出** - RAGが内容を作り上げていないか？
- 📉 **リグレッションテスト** - 最新のプロンプト変更で回答の20%が壊れていないか？
- 🏢 **チームダッシュボード** - ステークホルダーと精度レポートを共有
- 📊 **多次元スコアリング** - 精度、関連性、完全性
- ⚡ **CI/CD統合** - パイプラインでの自動評価

**[ウェイティングリストに登録 →](https://github.com/HZYAI/RagScore/issues/1)**

---

## 🧪 Python API

```python
from ragscore import run_pipeline, generate_qa_for_chunk
from ragscore.providers import get_provider

# シンプルな使用法
run_pipeline(paths=["paper.pdf", "report.txt"])

# ローカルOllamaを使用
provider = get_provider("ollama", model="llama3.1")
qas = generate_qa_for_chunk(
    chunk_text="あなたのテキスト...",
    difficulty="hard",
    n=5,
    provider=provider
)

# ローカルvLLMを使用
provider = get_provider(
    "openai",  # vLLMはOpenAI互換
    base_url="http://localhost:8000/v1",
    api_key="not-needed"
)
qas = generate_qa_for_chunk(
    chunk_text="あなたのテキスト...",
    difficulty="medium",
    n=3,
    provider=provider
)
```

---

## ⚙️ 設定

RAGScoreは**ゼロコンフィグ**で動作しますが、カスタマイズ可能です：

```bash
# オプション：チャンクサイズをカスタマイズ
export RAGSCORE_CHUNK_SIZE=512

# オプション：チャンクあたりの質問数
export RAGSCORE_QUESTIONS_PER_CHUNK=5

# オプション：作業ディレクトリ
export RAGSCORE_WORK_DIR=/path/to/workspace
```

---

## 🔐 プライバシーとセキュリティ

### ローカルに保持されるデータは？
- ✅ **あなたの文書** - 埋め込みAPIに送信されることはありません
- ✅ **文書チャンク** - ローカルで処理
- ✅ **ファイルメタデータ** - マシンに保持

### LLMに送信されるデータは？
- ⚠️ **テキストチャンクのみ** - QA生成のためLLMに送信
- ✅ **ローカルLLMを使用** - これもマシンに保持されます！

### コンプライアンス
- ✅ **GDPR準拠** - 第三者へのデータ送信なし（ローカルLLM使用時）
- ✅ **HIPAA対応** - PHIにローカルLLMを使用
- ✅ **SOC 2対応** - ローカルデプロイで完全なデータ制御

---

## 🧪 開発

```bash
# リポジトリをクローン
git clone https://github.com/HZYAI/RagScore.git
cd RagScore

# 開発依存関係とともにインストール
pip install -e ".[dev,all]"

# テストを実行
pytest

# リンティングを実行
ruff check src/
black --check src/
```

---

## 🤝 コントリビューション

コントリビューションを歓迎します！ガイドラインについては[CONTRIBUTING.md](CONTRIBUTING.md)をご覧ください。

---

## 📄 ライセンス

Apache 2.0ライセンス - 詳細は[LICENSE](LICENSE)をご覧ください。

---

## 🔗 リンク

- [ドキュメント](https://github.com/HZYAI/RagScore#readme)
- [変更履歴](CHANGELOG.md)
- [イシュートラッカー](https://github.com/HZYAI/RagScore/issues)
- [PyPIパッケージ](https://pypi.org/project/ragscore/)

---

<p align="center">
  <b>⭐ RAGScoreがお役に立ちましたら、GitHubでスターをお願いします！</b><br>
  RAGコミュニティのために ❤️ を込めて作成
</p>
