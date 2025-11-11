"""Traces router for retrieving MLflow-style execution traces."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from server.trace_storage import get_trace_storage

router = APIRouter()


class TraceListItem(BaseModel):
    """Summary item for trace list."""
    trace_id: str
    request_id: str
    timestamp_ms: int
    status: str
    execution_time_ms: Optional[int] = None
    user_message: Optional[str] = None


class TraceListResponse(BaseModel):
    """Response for listing traces."""
    traces: List[TraceListItem]
    total: int
    limit: int
    offset: int


@router.get('/list', response_model=TraceListResponse)
async def list_traces(limit: int = 50, offset: int = 0) -> TraceListResponse:
    """List recent traces.

    Args:
        limit: Maximum number of traces to return (default: 50)
        offset: Number of traces to skip (default: 0)

    Returns:
        TraceListResponse with list of traces and pagination info
    """
    trace_storage = get_trace_storage()
    traces = trace_storage.list_traces(limit=limit, offset=offset)
    total = trace_storage.get_total_traces()

    # Convert to response format
    trace_items = []
    for trace in traces:
        trace_items.append(TraceListItem(
            trace_id=trace['trace_id'],
            request_id=trace['request_id'],
            timestamp_ms=trace['timestamp_ms'],
            status=trace['status'],
            execution_time_ms=trace.get('execution_time_ms'),
            user_message=trace.get('request_metadata', {}).get('user_message')
        ))

    return TraceListResponse(
        traces=trace_items,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get('/{trace_id}')
async def get_trace(trace_id: str):
    """Get detailed trace information.

    Args:
        trace_id: ID of the trace to retrieve

    Returns:
        Complete trace data with all spans
    """
    trace_storage = get_trace_storage()
    trace = trace_storage.get_trace(trace_id)

    if not trace:
        raise HTTPException(
            status_code=404,
            detail=f"Trace {trace_id} not found"
        )

    return trace

