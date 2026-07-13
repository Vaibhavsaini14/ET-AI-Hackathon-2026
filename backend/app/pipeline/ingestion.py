import os
import shutil
import uuid
from loguru import logger
from app.pipeline.parser import DocumentParser
from app.pipeline.chunker import HierarchicalChunker
from app.pipeline.embedder import EmbeddingService

UPLOAD_DIR = "./data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class IngestionPipeline:

    def __init__(self):
        self.parser = DocumentParser()
        self.chunker = HierarchicalChunker()
        self.embedder = EmbeddingService()

    def process(self, file_path: str, doc_id: str) -> dict:
        logger.info(f"Starting ingestion for doc_id: {doc_id}")

        try:
            # Stage 1: Parse
            logger.info("Stage 1/3: Parsing document...")
            parsed = self.parser.parse(file_path, doc_id)

            # Stage 2: Chunk
            logger.info("Stage 2/3: Chunking text...")
            chunks = self.chunker.chunk(parsed, doc_id)

            if not chunks:
                return {
                    "doc_id": doc_id,
                    "status": "failed",
                    "error": "No text could be extracted from document"
                }

            # Stage 3: Embed and store
            logger.info("Stage 3/3: Embedding and storing chunks...")
            self.embedder.embed_and_store(chunks)

            result = {
                "doc_id": doc_id,
                "title": parsed.title,
                "status": "ready",
                "chunk_count": len(chunks),
                "page_count": len(parsed.pages),
                "doc_type": parsed.doc_type
            }

            logger.info(f"Ingestion complete: {parsed.title} — {len(chunks)} chunks")
            return result

        except Exception as e:
            logger.error(f"Ingestion failed for {doc_id}: {str(e)}")
            return {
                "doc_id": doc_id,
                "status": "failed",
                "error": str(e)
            }

    def search(self, query: str, top_k: int = 5) -> list:
        return self.embedder.semantic_search(query, top_k)

    def get_stats(self) -> dict:
        return {
            "total_chunks": self.embedder.get_total_chunks()
        }