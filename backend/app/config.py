import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / 'backend' / '.env')
DATABASE_URL = os.getenv('DATABASE_URL', f"sqlite:///{(ROOT / 'backend' / 'veribrand.db').as_posix()}")
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
MODELS = [os.getenv('GROQ_MODEL_PRIMARY') or 'openai/gpt-oss-120b',
          os.getenv('GROQ_MODEL_FALLBACK') or 'openai/gpt-oss-20b',
          os.getenv('GROQ_MODEL_THIRD') or 'qwen/qwen3.8-27b']
