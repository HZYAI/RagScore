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


# --- Telemetry ---
TELEMETRY_ENABLED = os.getenv("RAGSCORE_NO_TELEMETRY", "").lower() not in ("1", "true", "yes")
POSTHOG_API_KEY = os.getenv("POSTHOG_API_KEY", "phc_19wLYHD0eHcMQel7WUBz2cXUHu22extqJXyqrXX9GuW")
POSTHOG_HOST = os.getenv("POSTHOG_HOST", "https://app.posthog.com")

# Lazy-loaded PostHog client
_posthog_client = None


def get_telemetry_client():
    """Get PostHog client if telemetry is enabled."""
    global _posthog_client
    
    if not TELEMETRY_ENABLED:
        return None
    
    if _posthog_client is None:
        try:
            import posthog
            posthog.project_api_key = POSTHOG_API_KEY
            posthog.host = POSTHOG_HOST
            _posthog_client = posthog
        except ImportError:
            # PostHog not installed, silently disable telemetry
            return None
    
    return _posthog_client


def track_event(event_name: str, properties: dict = None, distinct_id: str = None):
    """
    Track a telemetry event.
    
    Args:
        event_name: Name of the event (e.g., "mcp_generate_qa")
        properties: Event properties (e.g., {"provider": "openai"})
        distinct_id: User identifier (defaults to anonymous machine ID)
    """
    client = get_telemetry_client()
    if client is None:
        return
    
    try:
        if distinct_id is None:
            # Use anonymous machine ID
            import uuid
            import platform
            machine_id = f"{platform.node()}-{uuid.getnode()}"
            distinct_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, machine_id))
        
        client.capture(
            distinct_id=distinct_id,
            event=event_name,
            properties=properties or {}
        )
        # Flush immediately to ensure event is sent
        client.flush()
    except Exception:
        # Silently fail on telemetry errors
        pass
