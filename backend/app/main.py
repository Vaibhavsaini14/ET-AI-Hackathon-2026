from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.models.database import init_db
from app.api.routes import health, documents, chat, knowledge_graph, compliance

logger = logging.getLogger(__name__)

app = FastAPI(
    title="NEXUS — Industrial Knowledge Intelligence",
    description="AI-powered platform for industrial document intelligence.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(knowledge_graph.router, prefix="/api/graph", tags=["Knowledge Graph"])
app.include_router(compliance.router, prefix="/api/compliance", tags=["Compliance"])

@app.on_event("startup")
async def startup():
    logger.info("NEXUS starting up...")
    await init_db()
    logger.info("Database tables initialized")
    logger.info("NEXUS ready at http://localhost:8000")

@app.get("/")
async def root():
    return {
        "message": "NEXUS Industrial Knowledge Intelligence API",
        "status": "operational",
        "version": "1.0.0",
        "docs": "http://localhost:8000/docs"
    }