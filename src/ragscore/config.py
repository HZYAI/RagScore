import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Paths ---
# Use current working directory for data/output (not package location)
WORK_DIR = Path(os.getenv("RAGSCORE_WORK_DIR", Path.cwd()))
DATA_DIR = WORK_DIR / "data"
DOCS_DIR = DATA_DIR / "docs"
OUTPUT_DIR = WORK_DIR / "output"
GENERATED_QAS_PATH = OUTPUT_DIR / "generated_qas.jsonl"


def ensure_dirs():
    """Create necessary directories. Call this before operations that need them."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)


# --- Text Processing ---
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64


# --- LLM & QA Generation ---
DASHSCOPE_MODEL = "qwen-turbo"
DASHSCOPE_TEMPERATURE = 0.7
NUM_Q_PER_CHUNK = 5  # Number of questions to generate per chunk
DIFFICULTY_MIX = ["easy", "medium", "hard"]


# --- API Keys (lazy loading, no error at import time) ---
def get_api_key(provider: str = "dashscope") -> str:
    """Get API key for the specified provider."""
    key_map = {
        "dashscope": "DASHSCOPE_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "groq": "GROQ_API_KEY",
    }
    env_var = key_map.get(provider, f"{provider.upper()}_API_KEY")
    key = os.getenv(env_var)
    if not key:
        raise ValueError(f"{env_var} not found. Please set it in your environment or .env file.")
    return key


# Legacy support
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
