import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Paths ---
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
DOCS_DIR = DATA_DIR / "docs"
OUTPUT_DIR = ROOT_DIR / "output"
INDEX_PATH = OUTPUT_DIR / "index.faiss"
META_PATH = OUTPUT_DIR / "meta.json"
GENERATED_QAS_PATH = OUTPUT_DIR / "generated_qas.jsonl"
ASSESSMENT_REPORT_PATH = OUTPUT_DIR / "assessment_report.xlsx"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)
DOCS_DIR.mkdir(exist_ok=True)


# --- Embeddings & Vector Store ---
MODEL_EMB = "text-embedding-v3"  # DashScope embedding model
TOP_K = 6
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64


# --- LLM & QA Generation ---
DASHSCOPE_MODEL = "qwen-turbo"
DASHSCOPE_TEMPERATURE = 0.7
NUM_Q_PER_CHUNK = 5  # Number of questions to generate per chunk
DIFFICULTY_MIX = ["easy", "medium", "hard"]

# --- RAG Assessment ---
# Default endpoint configuration (can be overridden via CLI)
RAG_ENDPOINT_URL = os.getenv("RAG_ENDPOINT_URL", "http://localhost:5000/query")
RAG_LOGIN_URL = os.getenv("RAG_LOGIN_URL")
RAG_USERNAME = os.getenv("RAG_USERNAME")
RAG_PASSWORD = os.getenv("RAG_PASSWORD")
ASSESSMENT_RATE_LIMIT = 0.05  # Delay between requests in seconds
ASSESSMENT_TIMEOUT = 40  # Request timeout in seconds

# --- API Keys ---
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

if not DASHSCOPE_API_KEY:
    raise ValueError("DASHSCOPE_API_KEY not found. Please set it in your .env file.")
