from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_graph():
    return {
        "nodes": [],
        "edges": [],
        "stats": {
            "node_count": 0,
            "edge_count": 0
        }
    }

@router.get("/search")
async def search_graph(q: str = ""):
    return {"nodes": [], "query": q}