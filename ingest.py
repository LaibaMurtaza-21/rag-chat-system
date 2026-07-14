"""
Document ingestion script.

Reads all .txt files from the configured data directory, splits them
into overlapping text chunks, and stores their embeddings in the
ChromaDB vector store. Run this once (or whenever documents change)
before starting the chat backend.
"""

import os
from app.config import DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from app.vector_store import vector_store


def chunk_text(text: str, chunk_size: int, overlap: int):
    """
    Split a long text into overlapping fixed-size chunks.

    Overlap helps preserve context that would otherwise be cut off
    at a hard chunk boundary.

    Args:
        text: The full document text to split.
        chunk_size: Maximum number of characters per chunk.
        overlap: Number of characters shared between consecutive chunks.

    Returns:
        A list of text chunk strings.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        # Advance the window by (chunk_size - overlap) so consecutive
        # chunks share `overlap` characters of context.
        start += chunk_size - overlap
    return chunks


def ingest_file(filepath: str):
    """
    Read a single text file, chunk it, and add it to the vector store.

    Args:
        filepath: Full path to the .txt file to ingest.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
    filename = os.path.basename(filepath)
    # Give each chunk a unique, traceable ID (filename + chunk index).
    ids = [f"{filename}-{i}" for i in range(len(chunks))]
    # Tag every chunk with its source filename for future reference/debugging.
    metadatas = [{"source": filename} for _ in chunks]

    vector_store.add_texts(chunks, ids, metadatas)
    print(f"Ingested {filename} ({len(chunks)} chunks)")


def main():
    """Ingest every .txt file found in the configured DATA_DIR."""
    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)
        if filename.endswith(".txt"):
            ingest_file(filepath)


if __name__ == "__main__":
    main()