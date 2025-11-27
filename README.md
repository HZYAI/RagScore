# RAGScore

A comprehensive two-part pipeline for evaluating RAG (Retrieval-Augmented Generation) systems:

**Part 1: QA Generation** - Processes documents, indexes them in a vector store, and generates high-quality question-answer pairs using LLM.

**Part 2: RAG Assessment** - Queries your target RAG endpoint with generated questions, collects responses, and evaluates them using multi-dimensional LLM-as-judge methodology.

## Features

### Part 1: QA Generation
- **Document Processing**: Supports PDF, TXT, MD, and HTML files
- **Vector Indexing**: Uses FAISS for efficient similarity search
- **QA Generation**: Leverages DashScope's `qwen-turbo` to create high-quality QA pairs
- **Difficulty Levels**: Generates easy, medium, and hard questions

### Part 2: RAG Assessment
- **Endpoint Testing**: Robust client with retry logic and authentication support
- **Multi-Dimensional Evaluation**: Scores on accuracy, relevance, and completeness (0-100 each)
- **LLM-as-Judge**: Uses advanced LLM to evaluate response quality
- **Comprehensive Reports**: Excel reports with summary, detailed results, and poor performers
- **Performance Metrics**: Tracks response times and error rates

### General
- **Modular & Configurable**: Easily extendable and configurable through a central `config.py`
- **CLI Interface**: Simple command-line tools for both parts
- **Web Interface**: User-friendly web UI for QA generation
- **Programmatic API**: Use as a library in your own scripts

## Getting Started

### 1. Installation

This project uses Python's built-in `venv` for virtual environment management.

#### Quick Setup (Recommended)

```bash
cd RAGScore
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Create a virtual environment
- Install PyTorch (CPU version)
- Install all dependencies
- **Install the ragscore package in editable mode** (required!)

#### Manual Setup

```bash
cd RAGScore

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# IMPORTANT: Install the ragscore package
pip install -e .
```

**Note**: The `pip install -e .` step is critical. Without it, you'll get `ModuleNotFoundError: No module named 'ragscore'`.

#### Troubleshooting

If you encounter issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or run:
```bash
./fix_installation.sh
```

### 2. Setup API Key

You need a DashScope API key to run the pipeline. 

1.  Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
2.  Open the `.env` file and add your DashScope API key:
    ```
    DASHSCOPE_API_KEY="YOUR_API_KEY_HERE"
    ```

### 3. Add Documents

Place the documents you want to process into the `data/docs` directory.

### 4. Run the Pipeline

Make sure your virtual environment is activated:
```bash
source venv/bin/activate
```

#### Option A: Command-Line Interface

Execute the QA generation pipeline using the CLI:

```bash
python -m ragscore.cli generate
```

**Options:**

-   `--force-reindex` or `-f`: Force re-reading and re-indexing of all documents.

    ```bash
    python -m ragscore.cli generate --force-reindex
    ```

#### Option B: Web Interface

Start the web application for a user-friendly interface:

```bash
python -m ragscore.web.app
```

Then open your browser to `http://localhost:8000`

### 5. Check the Output

The generated question-answer pairs will be saved in `output/generated_qas.jsonl`.

The FAISS index and its metadata will be stored in the `output/` directory as `index.faiss` and `meta.json`.

---

## Part 2: RAG Assessment

After generating QA pairs, evaluate your RAG system's performance.

### Quick Start

```bash
# Basic assessment
python -m ragscore.assessment_cli \
  --endpoint http://localhost:5000/query

# With authentication
python -m ragscore.assessment_cli \
  --endpoint http://47.99.205.203:5004/api/query \
  --login-url http://47.99.205.203:5004/login \
  --username demo \
  --password demo123

# Test with limited samples
python -m ragscore.assessment_cli \
  --endpoint http://localhost:5000/query \
  --max-samples 50 \
  --output results/test_assessment.xlsx
```

### Assessment Output

The assessment generates an Excel report (`output/assessment_report.xlsx`) with:

1. **Summary Sheet**: Overall metrics and score distribution
2. **Detailed Results**: All QA pairs with multi-dimensional scores
3. **Poor Performers**: Questions scoring < 60 for focused improvement

### Evaluation Metrics

Each response is scored on three dimensions (0-100):

- **Accuracy**: Factual correctness and semantic equivalence
- **Relevance**: How well the response addresses the question
- **Completeness**: Coverage of key points from expected answer

### Programmatic Usage

```python
from ragscore.assessment import RAGEndpointClient, LLMEvaluator, RAGAssessment

# Initialize components
client = RAGEndpointClient(endpoint_url="http://localhost:5000/query")
evaluator = LLMEvaluator(model="qwen-turbo", temperature=0.0)
assessment = RAGAssessment(client, evaluator)

# Run assessment
results = assessment.run_assessment(max_samples=100)
df = assessment.generate_report(results, output_path="report.xlsx")
```

See [docs/ASSESSMENT_GUIDE.md](docs/ASSESSMENT_GUIDE.md) for detailed documentation and [examples/run_assessment_example.py](examples/run_assessment_example.py) for a complete example.
