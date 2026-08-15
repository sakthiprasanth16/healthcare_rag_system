"""
Embedding service — Hugging Face Serverless Inference API version.

Same class/method signatures as the old sentence-transformers version
(embed_text / embed_batch), so nothing else in the codebase (vector_store.py,
routes/upload.py, routes/chat.py) needs to change — just this file.

Why this exists: local PubMedBERT via sentence-transformers + torch OOM-killed
(exit 137) on Render's 512MB free tier. This swaps it for HF's hosted
feature-extraction endpoint, dropping torch/sentence-transformers entirely.

Env vars required:
    HUGGINGFACE_API_KEY   - HF access token (read scope is enough)
                             https://huggingface.co/settings/tokens
"""

import time
import logging
from typing import List

import numpy as np
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError

from backend.config import config

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3
_RETRY_BACKOFF_SECONDS = 5  # HF cold-starts a model on first call; 503 = "loading"


class EmbeddingService:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.EMBEDDING_MODEL

        if not config.HUGGINGFACE_API_KEY:
            raise RuntimeError(
                "HUGGINGFACE_API_KEY env var is not set. "
                "Create one at https://huggingface.co/settings/tokens"
            )

        # provider="hf-inference" pins this to HF's own serverless inference
        # rather than routing to a third-party provider.
        self.client = InferenceClient(
            provider="hf-inference", api_key=config.HUGGINGFACE_API_KEY
        )

    def _call_with_retry(self, inputs):
        last_err = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                return self.client.feature_extraction(inputs, model=self.model_name)
            except HfHubHTTPError as e:
                last_err = e
                status = getattr(e.response, "status_code", None)
                if status == 503 and attempt < _MAX_RETRIES:
                    logger.info(
                        "HF model %s is cold-starting (attempt %d/%d), retrying in %ds",
                        self.model_name, attempt, _MAX_RETRIES, _RETRY_BACKOFF_SECONDS,
                    )
                    time.sleep(_RETRY_BACKOFF_SECONDS)
                    continue
                raise
        raise RuntimeError(
            f"Failed to get embedding from HF Inference API after {_MAX_RETRIES} attempts"
        ) from last_err

    @staticmethod
    def _normalize(vec: np.ndarray) -> np.ndarray:
        """Match old normalize_embeddings=True behavior for cosine-metric Pinecone index."""
        norm = np.linalg.norm(vec, axis=-1, keepdims=True)
        norm = np.where(norm == 0, 1e-12, norm)  # avoid divide-by-zero
        return vec / norm

    def embed_text(self, text: str) -> list:
        """Embed a single text string. Returns a list of floats."""
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text")

        result = self._call_with_retry(text)
        vec = np.array(result)

        # Some models return per-token vectors (n_tokens, 768) instead of a
        # single pooled sentence vector — mean-pool defensively if so.
        if vec.ndim == 2:
            vec = vec.mean(axis=0)

        vec = self._normalize(vec)
        return vec.tolist()

    def embed_batch(self, texts: list) -> list:
        """Embed a batch of texts. Returns list of lists."""
        if not texts:
            return []

        try:
            result = self._call_with_retry(texts)
            vecs = np.array(result)

            if vecs.ndim == 3:
                # (batch, n_tokens, 768) -> mean-pool each item
                vecs = vecs.mean(axis=1)
            elif vecs.ndim != 2 or vecs.shape[0] != len(texts):
                raise ValueError("Unexpected batch response shape from HF API")

            vecs = self._normalize(vecs)
            return vecs.tolist()

        except Exception as e:
            logger.warning(
                "Batched feature_extraction failed (%s), falling back to per-item calls", e
            )
            return [self.embed_text(t) for t in texts]
