"""Traces router - stub for MLflow trace visualization."""

from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class TraceListResponse(BaseModel):
    """Response model for trace list."""
    traces: List[dict]
    total: int


@router.get('/list', response_model=TraceListResponse)
async def list_traces(limit: int = 50, offset: int = 0) -> TraceListResponse:
    """List recent traces.
    
    Args:
        limit: Maximum number of traces to return (default: 50)
        offset: Number of traces to skip (default: 0)
    
    Returns:
        List of traces with metadata
    """
    # Stub implementation - no traces yet
    # TODO: Integrate with MLflow tracing for Dataverse MCP tools
    return TraceListResponse(traces=[], total=0)


@router.get('/{trace_id}')
async def get_trace(trace_id: str) -> dict:
    """Get detailed trace information by ID.
    
    Args:
        trace_id: The trace ID to retrieve
    
    Returns:
        Complete trace with all spans and metadata
    """
    # Stub implementation
    return {
        'trace_id': trace_id,
        'request_id': trace_id,
        'timestamp_ms': 0,
        'status': 'NOT_FOUND',
        'spans': [],
        'message': 'Trace not found - MLflow tracing not yet configured'
    }

