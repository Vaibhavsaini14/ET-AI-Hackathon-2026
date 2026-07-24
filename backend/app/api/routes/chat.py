import time
from fastapi import APIRouter
from pydantic import BaseModel
from loguru import logger
from app.agents.orchestrator import Orchestrator

router = APIRouter()
orchestrator = Orchestrator()

class QueryRequest(BaseModel):
    query: str
    user_role: str = "engineer"
    doc_ids: list[str] = []

query_history = []

@router.post("/query")
async def query(request: QueryRequest):
    logger.info(f"Query received: {request.query[:80]}")

    result = orchestrator.route(request.query, request.user_role, request.doc_ids)

    log_entry = {
        "query": request.query,
        "agent_used": result["agent_used"],
        "intent": result["intent"],
        "confidence": result["confidence"],
        "processing_time_ms": result["processing_time_ms"],
        "source_count": len(result["sources"])
    }
    query_history.append(log_entry)

    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "confidence": result["confidence"],
        "agent_used": result["agent_used"],
        "intent": result["intent"],
        "processing_time_ms": result["processing_time_ms"],
        "cached": result["cached"]
    }

@router.get("/history")
async def get_history():
    return {
        "history": query_history[-20:],
        "total": len(query_history)
    }

@router.get("/stats")
async def get_stats():
    if not query_history:
        return {
            "total_queries": 0,
            "avg_processing_time_ms": 0,
            "confidence_breakdown": {
                "HIGH": 0, "MEDIUM": 0, "LOW": 0
            }
        }

    total = len(query_history)
    avg_time = sum(q["processing_time_ms"] for q in query_history) // total
    confidence_breakdown = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

    for q in query_history:
        c = q.get("confidence", "MEDIUM")
        if c in confidence_breakdown:
            confidence_breakdown[c] += 1

    return {
        "total_queries": total,
        "avg_processing_time_ms": avg_time,
        "confidence_breakdown": confidence_breakdown
    }