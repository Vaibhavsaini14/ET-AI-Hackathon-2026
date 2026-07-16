from fastapi import APIRouter
from app.services.knowledge_graph_service import KnowledgeGraphService
from app.services.cache_service import CacheService
from app.api.routes.chat import query_history

router = APIRouter()
kg = KnowledgeGraphService()
cache = CacheService()

@router.get("/dashboard")
async def dashboard():
    total = len(query_history)
    avg_time = sum(q["processing_time_ms"] for q in query_history) // total if total else 0

    agent_breakdown = {}
    for q in query_history:
        agent = q.get("agent_used", "Unknown")
        agent_breakdown[agent] = agent_breakdown.get(agent, 0) + 1

    return {
        "total_queries": total,
        "avg_processing_time_ms": avg_time,
        "agent_usage": agent_breakdown,
        "knowledge_graph": kg.get_stats(),
        "cache": cache.get_stats()
    }