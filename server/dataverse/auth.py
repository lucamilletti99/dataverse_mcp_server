"""Dataverse OAuth authentication module."""

import os
import time
from typing import Dict, Optional

import requests


def get_databricks_secret(scope: str, key: str) -> Optional[str]:
  """Get secret from Databricks Secrets (when running in Databricks Apps).

  Args:
      scope: Secret scope name (e.g., 'dataverse')
      key: Secret key name (e.g., 'host')

  Returns:
      Secret value or None if not found/not in Databricks
  """
  try:
    import base64
    from databricks.sdk import WorkspaceClient

    # Get workspace client (uses service principal when in Databricks Apps)
    w = WorkspaceClient()
    secret = w.secrets.get_secret(scope=scope, key=key)
    
    # Databricks SDK returns secrets base64-encoded, so we need to decode them
    value = base64.b64decode(secret.value).decode('utf-8')
    print(f"   ✅ Successfully loaded secret: {scope}/{key}")
    return value
  except ImportError:
    # databricks-sdk not installed (local dev)
    return None
  except Exception as e:
    # Not in Databricks, secret not found, or permission denied
    print(f"   ⚠️  Could not read Databricks secret {scope}/{key}: {type(e).__name__}: {e}")
    return None


class DataverseAuth:
  """Handle OAuth authentication for Dataverse API using Service Principal (M2M).
  
  Uses client credentials flow (OAuth 2.0) to obtain access tokens.
  Tokens are cached and automatically refreshed when expired.
  
  Reference: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/authenticate-oauth
  """

  def __init__(
    self,
    tenant_id: str = None,
    client_id: str = None,
    client_secret: str = None,
    dataverse_host: str = None,
  ):
    """Initialize Dataverse authentication.
    
    Args:
        tenant_id: Azure AD tenant ID (or from env DATAVERSE_TENANT_ID)
        client_id: App registration client ID (or from env DATAVERSE_CLIENT_ID)
        client_secret: App registration client secret (or from env DATAVERSE_CLIENT_SECRET)
        dataverse_host: Dataverse environment URL (or from env DATAVERSE_HOST)
    """
    # Get credentials from (in order of priority):
    # 1. Function parameters
    # 2. Environment variables
    # 3. Databricks Secrets scope 'dataverse' (when running in Databricks Apps)

    print("🔐 Loading Dataverse credentials...")
    
    # Try environment variables first (for local dev)
    self.dataverse_host = (
      dataverse_host or
      os.environ.get('DATAVERSE_HOST') or
      get_databricks_secret('dataverse', 'host')
    )

    self.tenant_id = (
      tenant_id or
      os.environ.get('DATAVERSE_TENANT_ID') or
      get_databricks_secret('dataverse', 'tenant_id')
    )

    self.client_id = (
      client_id or
      os.environ.get('DATAVERSE_CLIENT_ID') or
      get_databricks_secret('dataverse', 'client_id')
    )

    self.client_secret = (
      client_secret or
      os.environ.get('DATAVERSE_CLIENT_SECRET') or
      get_databricks_secret('dataverse', 'client_secret')
    )

    # Log where credentials came from
    if os.environ.get('DATAVERSE_HOST'):
      print("✅ Using credentials from environment variables")
    elif self.dataverse_host:
      print("✅ Using credentials from Databricks Secrets (scope: dataverse)")
    else:
      print("⚠️  No credentials loaded from any source")

    # Validate all required credentials are present
    missing = []
    if not self.dataverse_host:
      missing.append('DATAVERSE_HOST')
    if not self.tenant_id:
      missing.append('DATAVERSE_TENANT_ID')
    if not self.client_id:
      missing.append('DATAVERSE_CLIENT_ID')
    if not self.client_secret:
      missing.append('DATAVERSE_CLIENT_SECRET')
    
    if missing:
      error_msg = (
        f'Missing required Dataverse credentials: {", ".join(missing)}\n'
        f'Please ensure:\n'
        f'  1. For local dev: Set environment variables in .env.local\n'
        f'  2. For Databricks Apps: Run ./setup_databricks_secrets.sh\n'
        f'  3. Verify the SPN has READ access to the "dataverse" secret scope'
      )
      print(f"❌ {error_msg}")
      raise ValueError(error_msg)

    # Token cache
    self._access_token: Optional[str] = None
    self._token_expires_at: float = 0

    # OAuth endpoint
    self.token_endpoint = f'https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token'
    
    # Scope: {dataverse_host}/.default
    # This grants all permissions assigned to the app registration
    self.scope = f'{self.dataverse_host}/.default'

  def get_access_token(self, force_refresh: bool = False) -> str:
    """Get a valid access token, refreshing if necessary.
    
    Args:
        force_refresh: Force token refresh even if cached token is valid
        
    Returns:
        Valid OAuth access token
        
    Raises:
        RuntimeError: If token acquisition fails
    """
    # Check if we have a valid cached token
    current_time = time.time()
    if not force_refresh and self._access_token and current_time < self._token_expires_at:
      return self._access_token

    # Acquiring new token (minimal logging)

    # Request new token using client credentials flow
    token_data = {
      'grant_type': 'client_credentials',
      'client_id': self.client_id,
      'client_secret': self.client_secret,
      'scope': self.scope,
    }

    try:
      response = requests.post(self.token_endpoint, data=token_data, timeout=30)
      response.raise_for_status()
      
      token_response = response.json()
      self._access_token = token_response['access_token']

      # Cache token with 5 minute buffer before expiry
      expires_in = token_response.get('expires_in', 3600)
      self._token_expires_at = current_time + expires_in - 300

      print(f'✅ Successfully obtained access token (expires in {expires_in}s)')
      return self._access_token

    except requests.exceptions.RequestException as e:
      error_msg = f'Failed to obtain Dataverse access token: {str(e)}'
      if hasattr(e, 'response') and e.response is not None:
        try:
          error_detail = e.response.json()
          error_msg += f'\n  Error: {error_detail.get("error", "unknown")}'
          error_msg += f'\n  Description: {error_detail.get("error_description", "unknown")}'
        except:
          error_msg += f'\n  Response: {e.response.text[:200]}'
      
      print(f'❌ {error_msg}')
      raise RuntimeError(error_msg)

  def get_auth_headers(self) -> Dict[str, str]:
    """Get HTTP headers with Bearer token for Dataverse API requests.
    
    Returns:
        Dictionary with Authorization and other required headers
    """
    token = self.get_access_token()
    return {
      'Authorization': f'Bearer {token}',
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'OData-MaxVersion': '4.0',
      'OData-Version': '4.0',
    }

