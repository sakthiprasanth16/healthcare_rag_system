from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingService:
    def __init__(self, model_name: str = "NeuML/pubmedbert-base-embeddings"):
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> list:
        """Embed a single text string. Returns a list of floats."""
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_batch(self, texts: list) -> list:
        """Embed a batch of texts. Returns list of lists."""
        embeddings = self.model.encode(texts, normalize_embeddings=True, batch_size=32)
        return embeddings.tolist()
