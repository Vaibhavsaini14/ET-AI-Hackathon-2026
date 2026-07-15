from fastapi import APIRouter
from pydantic import BaseModel
from app.services.knowledge_graph_service import KnowledgeGraphService

router = APIRouter()
kg = KnowledgeGraphService()

class EntityQuery(BaseModel):
    entity_name: str
    hops: int = 1

@router.get("/stats")
async def graph_stats():
    return kg.get_stats()

@router.post("/neighbors")
async def graph_neighbors(request: EntityQuery):
    return kg.get_neighbors(request.entity_name, hops=request.hops)

@router.get("/entities")
async def list_entities():
    return {
        "entities": [
            {"name": n, "type": kg.graph.nodes[n].get("type", "UNKNOWN")}
            for n in kg.graph.nodes
        ][:100]
    }