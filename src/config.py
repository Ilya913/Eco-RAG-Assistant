import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    MODEL_NAME = "gemma3:4b"
    EMBEDDING_MODEL = "bge-m3"
    BASE_URL = "http://localhost:11434"
    TEST_MODEL = "qwen2.5:7b"

    DATA_DIR = os.path.join(os.getcwd(), "data")
    DB_DIR = os.path.join(os.getcwd(), "db")
    DB_NAME = "post_relation_db"

    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 100
    RETRIEVER_K = 3
    
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден в .env файле")

cfg = Config()