from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env

class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    FASTAPI_HOST = os.getenv("FASTAPI_HOST", "0.0.0.0")
    FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", 8000))
    EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
    PERSIST_DIR = "./chroma_db"
    CHUNKING_PARAM = {"size": 300, "overlap": 60}
    MODEL_NAME = "llama-3.1-8b-instant"
