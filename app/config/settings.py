from dotenv import load_dotenv
import os
from typing import Dict, Optional

load_dotenv()  # Load environment variables from .env

class Settings:
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY", None)
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    FASTAPI_HOST: str = os.getenv("FASTAPI_HOST", "0.0.0.0")
    FASTAPI_PORT: int = int(os.getenv("FASTAPI_PORT", 8000))
    EMBED_MODEL_NAME: str = "all-MiniLM-L6-v2"
    PERSIST_DIR: str = "./chroma_db"
    CHUNKING_PARAM: Dict[str, int] = {"size": 300, "overlap": 60}
    MODEL_NAME: Dict[str, str] = {"gpt": "gpt-4o-mini", "llama": "llama-3.1-8b-instant"}