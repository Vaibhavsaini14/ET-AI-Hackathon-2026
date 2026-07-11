from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentResponse(BaseModel):
    id: str
    name: str
    original_filename: str
    doc_type: str
    processing_status: str
    chunk_count: int
    entity_count: int
    page_count: int
    upload_date: datetime
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class DocumentStatusResponse(BaseModel):
    doc_id: str
    status: str
    chunk_count: int
    entity_count: int
    error_message: Optional[str] = None

class QueryRequest(BaseModel):
    query: str
    user_role: str = "engineer"

class SourceCitation(BaseModel):
    index: int
    title: str
    page: int
    doc_id: str
    doc_type: str
    snippet: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceCitation]
    confidence: str
    agent_used: str
    intent: str
    processing_time_ms: int
    cached: bool = False

class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    degree: int

class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str

class GraphStats(BaseModel):
    node_count: int
    edge_count: int

class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    stats: GraphStats

class ComplianceRequest(BaseModel):
    standard_name: str

class ComplianceClause(BaseModel):
    clause_id: str
    clause_text: str
    status: str
    evidence: Optional[str] = None
    gap_description: Optional[str] = None
    corrective_action: Optional[str] = None

class ComplianceResponse(BaseModel):
    standard_name: str
    total_clauses: int
    compliant_count: int
    partial_count: int
    gap_count: int
    not_found_count: int
    clauses: list[ComplianceClause]

class HealthResponse(BaseModel):
    status: str
    version: str
    documents_indexed: int
    graph_nodes: int
    graph_edges: int