import math
import numpy as np
import logging
from typing import List

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.model = None
        self._is_loaded = False

    def _lazy_load(self):
        if not self._is_loaded:
            try:
                from sentence_transformers import SentenceTransformer
                from app.config import settings
                self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
                self._is_loaded = True
                logger.info(f"Loaded sentence transformer model: {settings.EMBEDDING_MODEL_NAME}")
            except Exception as e:
                logger.warning(f"Could not load sentence transformer ({e}). Using dense TF-IDF frequency embeddings.")
                self.model = None
                self._is_loaded = True

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        self._lazy_load()
        if self.model is not None:
            try:
                embeddings = self.model.encode(texts, convert_to_numpy=True)
                return embeddings.tolist()
            except Exception as e:
                logger.error(f"Error in SentenceTransformer encoding: {e}")

        # Lightweight dense vector fallback
        return [self._fallback_embedding(text) for text in texts]

    def _fallback_embedding(self, text: str, dim: int = 64) -> List[float]:
        # Hash-based pseudo dense vector for offline/lightweight execution
        words = text.lower().split()
        vec = [0.0] * dim
        for w in words:
            idx = abs(hash(w)) % dim
            vec[idx] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [round(v / norm, 4) for v in vec]

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a)) or 1.0
        norm_b = math.sqrt(sum(b * b for b in vec_b)) or 1.0
        return round(dot / (norm_a * norm_b), 4)

embedding_service = EmbeddingService()
