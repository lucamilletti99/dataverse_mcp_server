"""User router - simplified for Dataverse MCP Server."""

import os
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

router = APIRouter()


class UserInfo(BaseModel):
  """User information."""

  userName: str
  displayName: str | None = None
  active: bool = True
  authMethod: str = 'unknown'


@router.get('/me', response_model=UserInfo)
async def get_current_user(
  x_forwarded_access_token: str = Header(None, alias='X-Forwarded-Access-Token')
):
  """Get current user information.
  
  Returns user info from OBO token if available, otherwise returns service principal info.
  """
  try:
    # Check if running with OBO token
    if x_forwarded_access_token:
      # Try to get user info from Databricks
      try:
        from databricks.sdk import WorkspaceClient
        from databricks.sdk.core import Config
        
        config = Config(
          host=os.environ.get('DATABRICKS_HOST'),
          token=x_forwarded_access_token,
          auth_type='pat'
        )
        w = WorkspaceClient(config=config)
        current_user = w.current_user.me()
        
        return UserInfo(
          userName=current_user.user_name or 'unknown',
          displayName=current_user.display_name,
          active=current_user.active,
          authMethod='on-behalf-of',
        )
      except Exception as e:
        # Fallback if Databricks SDK not available or fails
        return UserInfo(
          userName='authenticated-user',
          displayName='Authenticated User',
          active=True,
          authMethod='token',
        )
    else:
      # No OBO token - running as service principal
      return UserInfo(
        userName='service-principal',
        displayName='Dataverse MCP Server',
        active=True,
        authMethod='service-principal',
      )
  except Exception as e:
    raise HTTPException(
      status_code=500,
      detail=f'Failed to get user info: {str(e)}'
    )


@router.get('/health')
async def user_health():
  """Health check for user router."""
  return {
    'status': 'healthy',
    'service': 'user-info',
  }
