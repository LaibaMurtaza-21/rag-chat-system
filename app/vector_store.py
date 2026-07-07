import chromadb
from app.config import CHROMA_DIR, TOP_K_RESULTS
from app.embeddings import embedder


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.collection = self.client.get_or_create_collection(name="documents")

    def add_texts(self, texts: list, ids: list, metadatas: list = None):
        """Add chunks of text to the vector store."""
        embeddings = embedder.embed_many(texts)
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas or [{} for _ in texts]
        )

    def query(self, query_text: str, top_k: int = None):
        """Retrieve the most relevant chunks for a query."""
        query_embedding = embedder.embed_one(query_text)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k or TOP_K_RESULTS
        )
        documents = results.get("documents", [[]])[0]
        return documents


# Singleton instance
vector_store = VectorStore()