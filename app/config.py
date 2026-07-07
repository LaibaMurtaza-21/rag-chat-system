import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHROMA_DIR = os.path.join(BASE_DIR, "storage", "chroma")
SQLITE_DB_PATH = os.path.join(BASE_DIR, "storage", "history.db")
DATA_DIR = os.path.join(BASE_DIR, "data")

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 3