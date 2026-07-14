"""
Vector store module.

Provides a ChromaDB-backed interface for storing document chunk
embeddings and retrieving the most semantically relevant chunks
for a given query.
"""

import chromadb
from app.config import CHROMA_DIR, TOP_K_RESULTS
from app.embeddings import embedder


class VectorStore:
    """Wrapper around a persistent ChromaDB collection for document retrieval."""

    def __init__(self):
        # Persistent client writes/reads the vector index to/from disk at CHROMA_DIR.
        self.client = chromadb.PersistentClient(path=CHROMA_DIR)
        # Get or create a single collection named "documents" to hold all ingested chunks.
        self.collection = self.client.get_or_create_collection(name="documents")

    def add_texts(self, texts: list, ids: list, metadatas: list = None):
        """
        Embed and store a batch of text chunks in the vector store.

        Args:
            texts: List of text chunks to store.
            ids: List of unique IDs, one per chunk (must match order of `texts`).
            metadatas: Optional list of metadata dicts (e.g. source filename),
                       one per chunk. Defaults to empty dicts if not provided.
        """
        # Convert all chunks into embeddings in a single batched call for efficiency.
        embeddings = embedder.embed_many(texts)
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas or [{} for _ in texts]
        )

    def query(self, query_text: str, top_k: int = None):
        """
        Retrieve the most relevant stored chunks for a given query string.

        Args:
            query_text: The user's question or search text.
            top_k: Number of top results to return. Falls back to
                   TOP_K_RESULTS from config if not specified.

        Returns:
            A list of the most relevant document chunk strings.
        """
        # Embed the query using the same model used for stored documents,
        # so both live in the same vector space.
        query_embedding = embedder.embed_one(query_text)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k or TOP_K_RESULTS
        )
        # Chroma returns a nested list (one list per query embedding);
        # since we only pass one query, we take the first element.
        documents = results.get("documents", [[]])[0]
        return documents


# Singleton instance so the ChromaDB client/collection is initialized only once.
vector_store = VectorStore()