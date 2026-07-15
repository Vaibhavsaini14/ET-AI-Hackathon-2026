import pickle
import re
import os
from rank_bm25 import BM25Okapi
from loguru import logger

INDEX_PATH = "./bm25_index.pkl"

class BM25Service:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.bm25 = None
        self.corpus = []
        self.chunk_ids = []
        self.metadatas = []
        self.load()
        self._initialized = True

    def build_index(self, chunks: list) -> None:
        self.corpus = [c.text for c in chunks]
        self.chunk_ids = [c.chunk_id for c in chunks]
        self.metadatas = [c.metadata for c in chunks]

        tokenized = [self._tokenize(text) for text in self.corpus]
        self.bm25 = BM25Okapi(tokenized)
        self.save()
        logger.info(f"BM25 index built with {len(self.corpus)} chunks")

    def add_chunks(self, new_chunks: list) -> None:
        for chunk in new_chunks:
            self.corpus.append(chunk.text)
            self.chunk_ids.append(chunk.chunk_id)
            self.metadatas.append(chunk.metadata)

        if self.corpus:
            tokenized = [self._tokenize(text) for text in self.corpus]
            self.bm25 = BM25Okapi(tokenized)
            self.save()
            logger.info(f"BM25 index updated — total chunks: {len(self.corpus)}")

    def search(self, query: str, top_k: int = 20) -> list:
        if not self.bm25 or not self.corpus:
            logger.warning("BM25 index is empty")
            return []

        query_tokens = self._tokenize(query)
        scores = self.bm25.get_scores(query_tokens)

        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]

        results = []
        for i in top_indices:
            if scores[i] > 0:
                results.append({
                    "text": self.corpus[i],
                    "metadata": self.metadatas[i],
                    "score": float(scores[i]),
                    "chunk_id": self.chunk_ids[i]
                })

        return results

    def save(self) -> None:
        with open(INDEX_PATH, "wb") as f:
            pickle.dump({
                "corpus": self.corpus,
                "chunk_ids": self.chunk_ids,
                "metadatas": self.metadatas
            }, f)

    def load(self) -> None:
        if os.path.exists(INDEX_PATH):
            with open(INDEX_PATH, "rb") as f:
                data = pickle.load(f)
            self.corpus = data["corpus"]
            self.chunk_ids = data["chunk_ids"]
            self.metadatas = data["metadatas"]

            if self.corpus:
                tokenized = [self._tokenize(t) for t in self.corpus]
                self.bm25 = BM25Okapi(tokenized)
                logger.info(f"BM25 index loaded — {len(self.corpus)} chunks")

    def _tokenize(self, text: str) -> list:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return text.split()