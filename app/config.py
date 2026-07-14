"""
Central configuration module for the RAG Chat System.

This file defines all shared constants (file paths, model names, and
chunking/retrieval parameters) so that every other module can import
consistent settings from a single source of truth.
"""

import os

# Absolute path to the project root directory (one level above 'app/').
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directory where ChromaDB will persist its vector index files.
CHROMA_DIR = os.path.join(BASE_DIR, "storage", "chroma")

# File path for the SQLite database used to store chat history and facts.
SQLITE_DB_PATH = os.path.join(BASE_DIR, "storage", "history.db")

# Directory containing the raw .txt documents to be ingested into the vector store.
DATA_DIR = os.path.join(BASE_DIR, "data")

# Name of the sentence-transformers model used to generate embeddings.
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Number of characters per text chunk when splitting documents for ingestion.
CHUNK_SIZE = 500

# Number of overlapping characters between consecutive chunks (helps preserve context across chunk boundaries).
CHUNK_OVERLAP = 50

# Default number of top-matching chunks to retrieve for a given query.
TOP_K_RESULTS = 3