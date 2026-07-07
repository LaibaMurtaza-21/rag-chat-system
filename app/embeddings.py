from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL_NAME


class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    def embed_one(self, text: str):
        """Embed a single string, return a list of floats."""
        return self.model.encode(text).tolist()

    def embed_many(self, texts: list):
        """Embed a list of strings, return a list of lists of floats."""
        return self.model.encode(texts).tolist()


# Singleton instance used across the app
embedder = Embedder()