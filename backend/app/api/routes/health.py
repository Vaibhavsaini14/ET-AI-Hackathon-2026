from fastapi import APIRouter
from app.models.schemas import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        documents_indexed=0,
        graph_nodes=0,
        graph_edges=0
    )