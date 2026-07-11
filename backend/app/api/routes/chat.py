from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    user_role: str = "engineer"

@router.post("/query")
async def query(request: QueryRequest):
    return {
        "answer": "RAG pipeline coming Day 3",
        "sources": [],
        "confidence": "N/A",
        "agent_used": "none",
        "intent": "none",
        "processing_time_ms": 0
    }

@router.get("/history")
async def get_history():
    return {"history": []}