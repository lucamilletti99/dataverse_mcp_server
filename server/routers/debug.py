"""Debug router - temporary endpoint for testing without OAuth."""

import os
from fastapi import APIRouter, HTTPException, Header, Request
from typing import Optional

router = APIRouter()

# Simple API key for debugging (change this to something unique)
DEBUG_API_KEY = os.environ.get('DEBUG_API_KEY', 'debug-key-change-me')


def verify_debug_key(x_debug_key: Optional[str] = Header(None)):
    """Verify debug API key."""
    if x_debug_key != DEBUG_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid debug key")
    return True


@router.get('/test')
async def debug_test():
    """Simple test endpoint to verify debug access."""
    return {
        "status": "ok",
        "message": "Debug endpoint is working",
        "debug_mode": True
    }


@router.get('/get-token')
async def get_access_token(request: Request):
    """Get the X-Forwarded-Access-Token from request headers.

    This allows remote testing by extracting the OAuth token that
    Databricks Apps automatically adds to requests.

    Returns:
        Dictionary with the access token (if available)
    """
    # Get the token from request headers (Databricks adds this automatically)
    access_token = request.headers.get('X-Forwarded-Access-Token')

    return {
        "status": "ok",
        "has_token": bool(access_token),
        "access_token": access_token if access_token else None,
        "message": "Use this token to make authenticated requests for testing"
    }


@router.get('/env-check')
async def debug_env_check(authorized: bool = Header(default=verify_debug_key)):
    """Check which environment variables are set."""
    return {
        "databricks_host": bool(os.environ.get('DATABRICKS_HOST')),
        "databricks_path": bool(os.environ.get('DATABRICKS_PATH')),
        "dataverse_host_env": bool(os.environ.get('DATAVERSE_HOST')),
        "dataverse_tenant_env": bool(os.environ.get('DATAVERSE_TENANT_ID')),
        "dataverse_client_env": bool(os.environ.get('DATAVERSE_CLIENT_ID')),
        "dataverse_secret_env": bool(os.environ.get('DATAVERSE_CLIENT_SECRET')),
    }


@router.post('/test-dataverse-connection')
async def debug_test_dataverse(authorized: bool = Header(default=verify_debug_key)):
    """Test Dataverse connection using the configured credentials."""
    try:
        from server.dataverse.client import DataverseClient

        client = DataverseClient()
        result = client.list_tables(top=1)

        return {
            "status": "success",
            "message": "Connected to Dataverse successfully",
            "table_count": len(result.get('value', [])),
            "dataverse_host": client.dataverse_host
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__
        }


# Simple in-memory log capture
recent_requests = []
MAX_LOGS = 50


@router.middleware("http")
async def log_requests(request: Request, call_next):
    """Capture recent requests for debugging."""
    import time
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time

    recent_requests.append({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": round(process_time * 1000, 2)
    })

    # Keep only recent logs
    if len(recent_requests) > MAX_LOGS:
        recent_requests.pop(0)

    return response


@router.get('/recent-requests')
async def get_recent_requests():
    """Get recent API requests for debugging (no auth required in browser)."""
    return {
        "total": len(recent_requests),
        "requests": recent_requests[-20:]  # Last 20 requests
    }
