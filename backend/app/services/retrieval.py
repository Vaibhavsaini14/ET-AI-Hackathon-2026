from loguru import logger
from app.pipeline.embedder import EmbeddingService
from app.services.bm25_service import BM25Service

class HybridRetrievalService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.semantic = EmbeddingService()
        self.bm25 = BM25Service()
        self._initialized = True
        logger.info("Hybrid retrieval service ready")

    def retrieve(self, query: str, top_k: int = 5) -> list:
        # Step 1: Semantic search
        semantic_results = self.semantic.semantic_search(query, top_k=20)

        # Step 2: BM25 keyword search
        bm25_results = self.bm25.search(query, top_k=20)

        # Step 3: Combine with Reciprocal Rank Fusion
        fused = self._rrf_fusion(semantic_results, bm25_results)

        logger.info(
            f"Retrieved {len(fused)} results for query: '{query[:50]}...'"
        )

        return fused[:top_k]

    def _rrf_fusion(self, list1: list, list2: list, k: int = 60) -> list:
        scores = {}

        for rank, item in enumerate(list1):
            key = item["metadata"].get("chunk_id", item["text"][:50])
            if key not in scores:
                scores[key] = {"score": 0.0, "item": item}
            scores[key]["score"] += 1 / (k + rank + 1)

        for rank, item in enumerate(list2):
            key = item["metadata"].get(
                "chunk_id",
                item.get("chunk_id", item["text"][:50])
            )
            if key not in scores:
                scores[key] = {"score": 0.0, "item": item}
            scores[key]["score"] += 1 / (k + rank + 1)

        sorted_items = sorted(
            scores.values(),
            key=lambda x: x["score"],
            reverse=True
        )

        return [entry["item"] for entry in sorted_items]