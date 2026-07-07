import os
from app.config import DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from app.vector_store import vector_store


def chunk_text(text: str, chunk_size: int, overlap: int):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def ingest_file(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
    filename = os.path.basename(filepath)
    ids = [f"{filename}-{i}" for i in range(len(chunks))]
    metadatas = [{"source": filename} for _ in chunks]

    vector_store.add_texts(chunks, ids, metadatas)
    print(f"Ingested {filename} ({len(chunks)} chunks)")


def main():
    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)
        if filename.endswith(".txt"):
            ingest_file(filepath)


if __name__ == "__main__":
    main()