from fastapi import APIRouter
from pydantic import BaseModel
from app.pipeline.ingestion import IngestionPipeline

router = APIRouter()
pipeline = IngestionPipeline()

class QueryRequest(BaseModel):
    query: str
    user_role: str = "engineer"

@router.post("/query")
async def query(request: QueryRequest):
    results = pipeline.search(request.query, top_k=5)

    if not results:
        return {
            "answer": "No documents indexed yet. Please upload a document first.",
            "sources": [],
            "confidence": "LOW",
            "agent_used": "Basic Search",
            "intent": "expert_query",
            "processing_time_ms": 0
        }

    top_result = results[0]
    sources = [
        {
            "index": i + 1,
            "title": r["metadata"].get("title", "Unknown"),
            "page": r["metadata"].get("page_number", 1),
            "doc_id": r["metadata"].get("doc_id", ""),
            "doc_type": r["metadata"].get("doc_type", "unknown"),
            "snippet": r["text"][:200],
            "score": r["score"]
        }
        for i, r in enumerate(results)
    ]

    answer = f"Found {len(results)} relevant sections.\n\n"
    answer += f"Most relevant (score: {top_result['score']}):\n"
    answer += top_result["text"][:500]
    answer += "\n\n[Full RAG with Groq LLM coming Day 3]"

    return {
        "answer": answer,
        "sources": sources,
        "confidence": "MEDIUM",
        "agent_used": "Basic Search (Day 2)",
        "intent": "expert_query",
        "processing_time_ms": 100
    }

@router.get("/history")
async def get_history():
    return {"history": []}