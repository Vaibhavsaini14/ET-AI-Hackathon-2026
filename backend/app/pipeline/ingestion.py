import os
import shutil
from loguru import logger
from app.pipeline.parser import DocumentParser
from app.pipeline.chunker import HierarchicalChunker
from app.pipeline.embedder import EmbeddingService
from app.services.bm25_service import BM25Service
from app.services.entity_extraction_service import EntityExtractionService   
from app.services.knowledge_graph_service import KnowledgeGraphService

UPLOAD_DIR = "./data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class IngestionPipeline:

    def __init__(self):
        self.parser = DocumentParser()
        self.chunker = HierarchicalChunker()
        self.embedder = EmbeddingService()
        self.bm25 = BM25Service()
        self.entity_extractor = EntityExtractionService()   
        self.kg = KnowledgeGraphService() 

    def process(self, file_path: str, doc_id: str) -> dict:
        logger.info(f"Starting ingestion: {doc_id}")

        try:
            # Stage 1: Parse
            logger.info("Stage 1/4: Parsing document...")
            parsed = self.parser.parse(file_path, doc_id)

            # Stage 2: Chunk
            logger.info("Stage 2/4: Chunking text...")
            chunks = self.chunker.chunk(parsed, doc_id)

            if not chunks:
                return {
                    "doc_id": doc_id,
                    "status": "failed",
                    "error": "No text could be extracted"
                }

            # Stage 3: Embed and store in ChromaDB
            logger.info("Stage 3/4: Embedding and storing in ChromaDB...")
            self.embedder.embed_and_store(chunks)

            # Stage 4: Add to BM25 index
            logger.info("Stage 4/4: Updating BM25 keyword index...")
            self.bm25.add_chunks(chunks)

             # Stage 5: Extract entities into knowledge graph          
            logger.info("Stage 5/5: Extracting entities into knowledge graph...")  
            for chunk in chunks[:30]:                                  
                extraction = self.entity_extractor.extract(chunk.text, chunk.chunk_id) 
                if extraction["entities"] or extraction["relationships"]:  
                    self.kg.add_extraction(extraction)

            result = {
                "doc_id": doc_id,
                "title": parsed.title,
                "status": "ready",
                "chunk_count": len(chunks),
                "page_count": len(parsed.pages),
                "doc_type": parsed.doc_type
            }

            logger.info(
                f"Ingestion complete: {parsed.title} — {len(chunks)} chunks"
            )
            return result

        except Exception as e:
            logger.error(f"Ingestion failed: {str(e)}")
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