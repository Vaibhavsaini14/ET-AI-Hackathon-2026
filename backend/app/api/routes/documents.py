import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from loguru import logger
from app.pipeline.ingestion import IngestionPipeline

router = APIRouter()
pipeline = IngestionPipeline()

UPLOAD_DIR = "./data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

doc_registry = {}

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    allowed = {".pdf", ".txt", ".docx"}
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"File type {ext} not supported. Use PDF, TXT, or DOCX."
        )

    doc_id = str(uuid.uuid4())
    save_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{file.filename}")

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    doc_registry[doc_id] = {
        "doc_id": doc_id,
        "filename": file.filename,
        "status": "processing",
        "chunk_count": 0,
        "page_count": 0,
        "error": None
    }

    background_tasks.add_task(
        _process_document, save_path, doc_id
    )

    logger.info(f"Document uploaded: {file.filename} → {doc_id}")

    return {
        "doc_id": doc_id,
        "filename": file.filename,
        "status": "processing",
        "message": "Document is being processed. Check status endpoint."
    }

def _process_document(file_path: str, doc_id: str):
    result = pipeline.process(file_path, doc_id)
    doc_registry[doc_id].update(result)

@router.get("/")
async def list_documents():
    return {
        "documents": list(doc_registry.values()),
        "total": len(doc_registry)
    }

@router.get("/stats")
async def get_stats():
    return pipeline.get_stats()

@router.get("/{doc_id}/status")
async def get_document_status(doc_id: str):
    if doc_id not in doc_registry:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc_registry[doc_id]

@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    if doc_id not in doc_registry:
        raise HTTPException(status_code=404, detail="Document not found")
    pipeline.embedder.delete_document(doc_id)
    del doc_registry[doc_id]
    return {"message": f"Document {doc_id} deleted successfully"}