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


@router.get('/app-status')
async def get_app_status():
    """Get application status and basic diagnostics."""
    import sys

    return {
        "status": "running",
        "python_version": sys.version,
        "endpoints_available": [
            "/api/health",
            "/api/user/me",
            "/api/chat/models",
            "/api/agent/chat",
            "/api/debug/get-token",
            "/api/debug/app-status",
            "/api/debug/recent-requests"
        ],
        "message": "Application is running normally"
    }


@router.get('/recent-requests')
async def get_recent_requests_endpoint():
    """Get recent API requests for debugging.

    Returns the last 20 requests with:
    - Timestamp
    - HTTP method
    - Request path
    - Status code
    - Duration in milliseconds

    No authentication required for easy debugging.
    """
    from server.request_logger import get_recent_requests, get_all_requests

    all_requests = get_all_requests()
    recent = get_recent_requests(limit=20)

    return {
        "total_logged": len(all_requests),
        "showing": len(recent),
        "requests": recent
    }
