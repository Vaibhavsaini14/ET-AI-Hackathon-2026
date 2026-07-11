from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.config import settings

Base = declarative_base()

engine = create_async_engine(settings.postgres_url, echo=False)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    doc_type = Column(String(50), default="unknown")
    file_path = Column(String(500))
    upload_date = Column(DateTime, default=datetime.utcnow)
    processing_status = Column(String(20), default="pending")
    chunk_count = Column(Integer, default=0)
    entity_count = Column(Integer, default=0)
    page_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), nullable=False)
    chunk_index = Column(Integer)
    page_number = Column(Integer)
    section_title = Column(String(255), nullable=True)
    chunk_text = Column(Text)
    token_count = Column(Integer)
    vector_id = Column(String(100))
    metadata_json = Column(JSON, nullable=True)

class QueryLog(Base):
    __tablename__ = "query_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_text = Column(Text)
    agent_used = Column(String(50))
    answer_text = Column(Text)
    confidence = Column(String(10))
    processing_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    source_doc_ids = Column(JSON, nullable=True)

class ComplianceAudit(Base):
    __tablename__ = "compliance_audits"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    standard_name = Column(String(100))
    audit_date = Column(DateTime, default=datetime.utcnow)
    total_clauses = Column(Integer)
    compliant_count = Column(Integer)
    gap_count = Column(Integer)
    partial_count = Column(Integer)
    results_json = Column(JSON)
    report_path = Column(String(500), nullable=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()