"""
Pydantic models for API request/response validation.

Matches the contract defined in CORE_SERVICE_INTEGRATION.md.
"""

from pydantic import BaseModel


# ── Incoming from Core Service ─────────────────────────────────

class QueryRequest(BaseModel):
    """Request body for POST /rag/query (sent by Core Service)."""
    conversationId: str
    question: str


class QueryAckResponse(BaseModel):
    """Immediate ACK response to Core Service."""
    status: str = "OK"


# ── Outgoing to Core Service (callback) ───────────────────────

class SourceItem(BaseModel):
    """A single source reference in the callback payload."""
    document: str
    page: int


class CallbackPayload(BaseModel):
    """Request body for POST /rag/callback (sent TO Core Service)."""
    conversationId: str
    answer: str
    sources: list[SourceItem]


# ── Health check ──────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "healthy"
    service: str = "rag"
