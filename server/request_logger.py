"""Request logging storage for debugging."""

import time
from typing import List, Dict
from collections import deque

# Thread-safe deque for storing recent requests
recent_requests: deque = deque(maxlen=50)


def log_request(method: str, path: str, status_code: int, duration_ms: float) -> None:
    """Add a request to the log."""
    recent_requests.append({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2)
    })


def get_recent_requests(limit: int = 20) -> List[Dict]:
    """Get recent requests (most recent last)."""
    return list(recent_requests)[-limit:]


def get_all_requests() -> List[Dict]:
    """Get all stored requests."""
    return list(recent_requests)
