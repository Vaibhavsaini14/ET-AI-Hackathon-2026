import os
import chromadb
from sentence_transformers import SentenceTransformer
from loguru import logger
from app.config import settings

class EmbeddingService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        logger.info("Loading embedding model (first time takes 1-2 mins)...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Embedding model loaded successfully")

        # ==========================
        # DEBUG INFO
        # ==========================
        print("\n" + "=" * 80)
        print("CURRENT WORKING DIRECTORY:")
        print(os.getcwd())

        print("\nCHROMA PERSIST DIRECTORY (CONFIG):")
        print(settings.chroma_persist_dir)

        print("\nABSOLUTE CHROMA PATH:")
        print(os.path.abspath(settings.chroma_persist_dir))
        print("=" * 80 + "\n")

        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir
        )

        self.collection = self.client.get_or_create_collection(
            name="nexus_documents",
            metadata={"hnsw:space": "cosine"}
        )

        logger.info(f"ChromaDB ready — {self.collection.count()} chunks stored")
        self._initialized = True

    def embed_and_store(self, chunks: list) -> None:
        if not chunks:
            logger.warning("No chunks to embed")
            return

        texts = [chunk.text for chunk in chunks]
        ids = [chunk.chunk_id for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]

        logger.info(f"Embedding {len(texts)} chunks...")
        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )

        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas
        )

        logger.info(f"Stored {len(chunks)} chunks in ChromaDB")

    def semantic_search(self, query: str, top_k: int = 5, doc_ids: list = None) -> list:
        total = self.collection.count()

        if total == 0:
            logger.warning("ChromaDB is empty — no documents indexed yet")
            return []

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True
        )
        where_filter = {"doc_id": {"$in": doc_ids}} if doc_ids else None

        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=min(top_k, total),
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        # ==========================
        # DEBUG INFO
        # ==========================
        print("\n" + "=" * 80)
        print("CHROMA RESULTS")
        print("=" * 80)

        for meta in results["metadatas"][0]:
            print(meta)

        print("=" * 80 + "\n")

        output = []

        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            output.append({
                "text": doc,
                "metadata": meta,
                "score": round(1 - dist, 4)
            })

        return output

    def delete_document(self, doc_id: str) -> None:
        results = self.collection.get(
            where={"doc_id": doc_id}
        )

        if results["ids"]:
            self.collection.delete(ids=results["ids"])
            logger.info(f"Deleted {len(results['ids'])} chunks for doc {doc_id}")

    def get_total_chunks(self) -> int:
        return self.collection.count()