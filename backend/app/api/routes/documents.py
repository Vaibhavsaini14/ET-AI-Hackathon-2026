from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_documents():
    return {
        "documents": [],
        "message": "Document pipeline coming Day 2"
    }

@router.get("/{doc_id}/status")
async def get_document_status(doc_id: str):
    return {
        "doc_id": doc_id,
        "status": "pipeline not built yet"
    }