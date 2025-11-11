"""In-memory trace storage for agent execution traces."""

import time
import uuid
from typing import Dict, List, Any, Optional
from collections import OrderedDict

class TraceStorage:
    """Simple in-memory storage for execution traces."""

    def __init__(self, max_traces: int = 100):
        self.max_traces = max_traces
        self.traces: OrderedDict[str, Dict[str, Any]] = OrderedDict()

    def create_trace(self, request_id: str, user_message: str) -> str:
        """Create a new trace for a request.

        Args:
            request_id: Unique request ID
            user_message: User's input message

        Returns:
            trace_id: ID for the created trace
        """
        trace_id = request_id or str(uuid.uuid4())

        trace = {
            'trace_id': trace_id,
            'request_id': trace_id,
            'timestamp_ms': int(time.time() * 1000),
            'status': 'IN_PROGRESS',
            'spans': [],
            'request_metadata': {
                'user_message': user_message
            }
        }

        self.traces[trace_id] = trace

        # Remove oldest traces if we exceed max_traces
        while len(self.traces) > self.max_traces:
            self.traces.popitem(last=False)

        return trace_id

    def add_span(
        self,
        trace_id: str,
        span_type: str,
        name: str,
        inputs: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None
    ) -> str:
        """Add a span to a trace.

        Args:
            trace_id: ID of the trace
            span_type: Type of span (e.g., 'LLM', 'TOOL', 'AGENT')
            name: Name of the span
            inputs: Input data for this span
            parent_id: Parent span ID if nested

        Returns:
            span_id: ID for the created span
        """
        if trace_id not in self.traces:
            return ""

        span_id = str(uuid.uuid4())[:12]

        span = {
            'span_id': span_id,
            'name': name,
            'span_type': span_type,
            'start_time_ms': int(time.time() * 1000),
            'status': 'RUNNING',
            'inputs': inputs or {},
            'parent_id': parent_id
        }

        self.traces[trace_id]['spans'].append(span)
        return span_id

    def complete_span(
        self,
        trace_id: str,
        span_id: str,
        outputs: Optional[Dict[str, Any]] = None,
        status: str = 'OK'
    ):
        """Complete a span with outputs.

        Args:
            trace_id: ID of the trace
            span_id: ID of the span to complete
            outputs: Output data from this span
            status: Final status (OK, ERROR)
        """
        if trace_id not in self.traces:
            return

        for span in self.traces[trace_id]['spans']:
            if span['span_id'] == span_id:
                span['end_time_ms'] = int(time.time() * 1000)
                span['duration_ms'] = span['end_time_ms'] - span['start_time_ms']
                span['outputs'] = outputs or {}
                span['status'] = status
                break

    def complete_trace(self, trace_id: str, status: str = 'OK'):
        """Mark a trace as complete.

        Args:
            trace_id: ID of the trace
            status: Final status (OK, ERROR)
        """
        if trace_id in self.traces:
            trace = self.traces[trace_id]
            trace['status'] = status
            trace['execution_time_ms'] = int(time.time() * 1000) - trace['timestamp_ms']

    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get a trace by ID.

        Args:
            trace_id: ID of the trace to retrieve

        Returns:
            Trace data or None if not found
        """
        return self.traces.get(trace_id)

    def list_traces(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List recent traces.

        Args:
            limit: Maximum number of traces to return
            offset: Number of traces to skip

        Returns:
            List of traces (most recent first)
        """
        all_traces = list(reversed(list(self.traces.values())))
        return all_traces[offset:offset + limit]

    def get_total_traces(self) -> int:
        """Get total number of stored traces."""
        return len(self.traces)


# Global trace storage instance
_trace_storage = TraceStorage(max_traces=100)

def get_trace_storage() -> TraceStorage:
    """Get the global trace storage instance."""
    return _trace_storage
