"""
Embedding utility module.

Wraps a SentenceTransformer model to convert raw text into numerical
vector embeddings, which are later stored in / queried from ChromaDB.
"""

from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL_NAME


class Embedder:
    """Thin wrapper around a SentenceTransformer model for text embedding."""

    def __init__(self):
        # Load the embedding model once at startup (this is relatively expensive,
        # so it should not be re-instantiated per request).
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    def embed_one(self, text: str):
        """
        Embed a single string.

        Args:
            text: The input text to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        return self.model.encode(text).tolist()

    def embed_many(self, texts: list):
        """
        Embed a batch of strings at once (more efficient than calling
        embed_one repeatedly).

        Args:
            texts: A list of input strings to embed.

        Returns:
            A list of embedding vectors (list of lists of floats),
            in the same order as the input texts.
        """
        return self.model.encode(texts).tolist()


# Singleton instance used across the app so the model is loaded only once.
embedder = Embedder()