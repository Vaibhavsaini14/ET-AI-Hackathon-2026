import time
import hashlib
import numpy as np
from cachetools import TTLCache
from loguru import logger
from app.pipeline.embedder import EmbeddingService

CACHE_TTL_SECONDS = 3600  # 1 hour
SIMILARITY_THRESHOLD = 0.95

class CacheService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.embedder = EmbeddingService()
        self.exact_cache = TTLCache(maxsize=200, ttl=CACHE_TTL_SECONDS)
        self.semantic_entries = []  # list of (embedding, query, result, timestamp)
        self._initialized = True
        logger.info("Cache service ready")

    def _hash_query(self, query: str, user_role: str) -> str:
        return hashlib.md5(f"{query.strip().lower()}_{user_role}".encode()).hexdigest()

    def get(self, query: str, user_role: str):
        # 1. Exact match check
        key = self._hash_query(query, user_role)
        if key in self.exact_cache:
            logger.info("Cache HIT (exact)")
            return self.exact_cache[key]

        # 2. Semantic similarity check
        try:
            query_embedding = self.embedder.model.encode([query], convert_to_numpy=True)[0]
        except Exception as e:
            logger.warning(f"Cache embedding failed: {e}")
            return None

        now = time.time()
        self.semantic_entries = [
            e for e in self.semantic_entries if now - e[3] < CACHE_TTL_SECONDS
        ]

        for emb, cached_query, result, ts in self.semantic_entries:
            sim = self._cosine_sim(query_embedding, emb)
            if sim >= SIMILARITY_THRESHOLD:
                logger.info(f"Cache HIT (semantic, sim={sim:.3f}): '{cached_query[:40]}'")
                return result

        return None

    def set(self, query: str, user_role: str, result: dict) -> None:
        key = self._hash_query(query, user_role)
        self.exact_cache[key] = result

        try:
            query_embedding = self.embedder.model.encode([query], convert_to_numpy=True)[0]
            self.semantic_entries.append((query_embedding, query, result, time.time()))
            if len(self.semantic_entries) > 200:
                self.semantic_entries.pop(0)
        except Exception as e:
            logger.warning(f"Cache store embedding failed: {e}")

    def _cosine_sim(self, a, b) -> float:
        a, b = np.array(a), np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def get_stats(self) -> dict:
        return {
            "exact_cache_size": len(self.exact_cache),
            "semantic_cache_size": len(self.semantic_entries)
        }