"""Debug router - temporary endpoint for testing without OAuth."""

import os
from fastapi import APIRouter, HTTPException, Header
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
async def debug_test(authorized: bool = Header(default=verify_debug_key)):
    """Simple test endpoint to verify debug access."""
    return {
        "status": "ok",
        "message": "Debug endpoint is working",
        "debug_mode": True
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
