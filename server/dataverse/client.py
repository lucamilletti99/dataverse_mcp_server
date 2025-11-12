"""Dataverse Web API client."""

import os
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urljoin

import requests

from server.dataverse.auth import DataverseAuth


class DataverseClient:
  """Client for interacting with Dataverse Web API v9.2.
  
  Provides high-level methods for table operations, record CRUD, and queries.
  
  Reference: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/overview
  """

  def __init__(self, auth: DataverseAuth = None, dataverse_host: str = None):
    """Initialize Dataverse API client.
    
    Args:
        auth: DataverseAuth instance (creates new one if not provided)
        dataverse_host: Dataverse environment URL (or from env DATAVERSE_HOST)
    """
    # Initialize auth first (it will load credentials from secrets or fallback)
    self.auth = auth or DataverseAuth()
    
    # Get dataverse_host from auth object (which has the fallback logic)
    self.dataverse_host = dataverse_host or os.environ.get('DATAVERSE_HOST') or self.auth.dataverse_host
    
    if not self.dataverse_host:
      error_msg = (
          'DATAVERSE_HOST environment variable is not set. '
          'Please ensure Databricks Secrets are configured correctly. '
          'Run ./setup_databricks_secrets.sh and redeploy.'
      )
      print(f"❌ ERROR: {error_msg}")
      raise ValueError(error_msg)

    # Ensure host doesn't have trailing slash
    self.dataverse_host = self.dataverse_host.rstrip('/')

    # Web API v9.2 base URL
    self.api_base = f'{self.dataverse_host}/api/data/v9.2/'

  def _make_request(
    self,
    method: str,
    endpoint: str,
    params: Dict[str, Any] = None,
    json_data: Dict[str, Any] = None,
    timeout: int = 30,
  ) -> requests.Response:
    """Make an authenticated request to Dataverse Web API.
    
    Args:
        method: HTTP method (GET, POST, PATCH, DELETE)
        endpoint: API endpoint (relative to api_base)
        params: Query parameters
        json_data: JSON body for POST/PATCH
        timeout: Request timeout in seconds
        
    Returns:
        Response object
        
    Raises:
        requests.HTTPError: If request fails
    """
    url = urljoin(self.api_base, endpoint)
    headers = self.auth.get_auth_headers()

    print(f'📡 Dataverse API Request: {method} {endpoint}')
    if params:
      print(f'   Params: {params}')

    try:
      response = requests.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json=json_data,
        timeout=timeout,
      )
      response.raise_for_status()
      return response

    except requests.exceptions.HTTPError as e:
      error_msg = f'Dataverse API error: {e}'
      if e.response is not None:
        try:
          error_detail = e.response.json()
          error_msg += f'\n  Error: {error_detail.get("error", {})}'
        except:
          error_msg += f'\n  Response: {e.response.text[:500]}'
      print(f'❌ {error_msg}')
      raise

  # ========================================
  # Table Operations (Entity Metadata)
  # ========================================

  def list_tables(
    self,
    select: List[str] = None,
    filter_query: str = None,
    top: int = 100,
  ) -> Dict[str, Any]:
    """List all tables (entities) in Dataverse.
    
    Args:
        select: List of properties to return (e.g., ['LogicalName', 'DisplayName'])
        filter_query: OData filter expression (e.g., "IsCustomEntity eq true")
        top: Maximum number of tables to return
        
    Returns:
        Dictionary with 'value' containing list of entity metadata
        
    Reference: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/query-metadata-web-api
    """
    # EntityDefinitions endpoint doesn't support OData query parameters
    # Get all entities and filter in Python instead
    params = {}

    print(f"📡 Making request to EntityDefinitions...")
    # Use longer timeout for metadata operations (can be large responses)
    response = self._make_request('GET', 'EntityDefinitions', params=params, timeout=60)
    
    print(f"✅ Got response, status: {response.status_code}")
    print(f"📦 Response size: {len(response.content)} bytes")
    
    try:
      print(f"🔄 Parsing JSON...")
      data = response.json()
      print(f"✅ JSON parsed successfully")
    except Exception as json_err:
      print(f"❌ Failed to parse JSON: {json_err}")
      raise ValueError(f"Failed to parse Dataverse response: {json_err}")
    
    # Apply filtering in Python since API doesn't support $filter on metadata
    tables = data.get('value', [])
    print(f"📊 Total tables in response: {len(tables)}")
    
    if filter_query:
      # Basic filter support for IsCustomEntity
      if 'IsCustomEntity eq true' in filter_query:
        tables = [t for t in tables if t.get('IsCustomEntity')]
        print(f"🔍 After IsCustomEntity filter: {len(tables)} tables")
    
    # Apply top limit
    if top and len(tables) > top:
      tables = tables[:top]
      print(f"✂️  Truncated to top {top} tables")
    
    print(f"✅ Returning {len(tables)} tables")
    return {'value': tables}

  def describe_table(self, table_name: str) -> Dict[str, Any]:
    """Get detailed metadata for a specific table (entity).
    
    Args:
        table_name: Logical name of the table (e.g., 'account', 'contact')
        
    Returns:
        Dictionary with complete entity metadata including attributes
        
    Reference: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/query-metadata-web-api
    """
    # Query specific entity by LogicalName (direct endpoint, no OData filters needed)
    # EntityDefinitions doesn't support $filter, so we query by LogicalName directly
    endpoint = f'EntityDefinitions(LogicalName=\'{table_name}\')?$expand=Attributes,Keys'
    
    try:
      response = self._make_request('GET', endpoint, timeout=60)
      data = response.json()
      
      # Debug: log what we got
      print(f"📦 describe_table response type: {type(data)}")
      print(f"📦 describe_table response keys: {data.keys() if data else 'None'}")
      
      if not data:
        raise ValueError(f"Empty response for table '{table_name}'")
      
      return data
    except requests.exceptions.HTTPError as e:
      if e.response.status_code == 404:
        raise ValueError(f"Table '{table_name}' not found")
      raise

  # ========================================
  # Record Operations (CRUD)
  # ========================================

  def read_query(
    self,
    entity_set_name: str,
    select: List[str] = None,
    filter_query: str = None,
    order_by: str = None,
    top: int = 100,
    expand: str = None,
  ) -> Dict[str, Any]:
    """Query records from a table using OData query options.
    
    Args:
        entity_set_name: Entity set name (plural form, e.g., 'accounts', 'contacts')
        select: List of columns to return (e.g., ['name', 'emailaddress1'])
        filter_query: OData filter expression (e.g., "revenue gt 100000")
        order_by: OData orderby expression (e.g., "name asc")
        top: Maximum number of records to return
        expand: Navigation properties to expand (e.g., "primarycontactid($select=fullname)")
        
    Returns:
        Dictionary with 'value' containing list of records
        
    Reference: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/query-data-web-api
    """
    params = {}
    
    if select:
      params['$select'] = ','.join(select)
    
    if filter_query:
      params['$filter'] = filter_query
    
    if order_by:
      params['$orderby'] = order_by
    
    if top:
      params['$top'] = top
    
    if expand:
      params['$expand'] = expand

    response = self._make_request('GET', entity_set_name, params=params)
    return response.json()

  def create_record(
    self,
    entity_set_name: str,
    data: Dict[str, Any],
  ) -> Dict[str, Any]:
    """Create a new record in a table.
    
    Args:
        entity_set_name: Entity set name (e.g., 'accounts', 'contacts')
        data: Record data as dictionary (e.g., {'name': 'Contoso', 'revenue': 100000})
        
    Returns:
        Dictionary with created record ID and metadata
        
    Reference: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/create-entity-web-api
    """
    response = self._make_request('POST', entity_set_name, json_data=data)
    
    # Extract record ID from OData-EntityId header
    entity_id = None
    if 'OData-EntityId' in response.headers:
      entity_id_url = response.headers['OData-EntityId']
      # Extract GUID from URL like: https://org.crm.dynamics.com/api/data/v9.2/accounts(guid)
      entity_id = entity_id_url.split('(')[-1].rstrip(')')
    
    return {
      'success': True,
      'entity_id': entity_id,
      'entity_id_url': response.headers.get('OData-EntityId'),
      'status_code': response.status_code,
    }

  def update_record(
    self,
    entity_set_name: str,
    record_id: str,
    data: Dict[str, Any],
  ) -> Dict[str, Any]:
    """Update an existing record.
    
    Args:
        entity_set_name: Entity set name (e.g., 'accounts', 'contacts')
        record_id: GUID of the record to update
        data: Updated fields as dictionary (e.g., {'revenue': 200000})
        
    Returns:
        Dictionary with update status
        
    Reference: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/update-delete-entities-using-web-api
    """
    endpoint = f'{entity_set_name}({record_id})'
    response = self._make_request('PATCH', endpoint, json_data=data)
    
    return {
      'success': True,
      'record_id': record_id,
      'status_code': response.status_code,
    }

  def delete_record(
    self,
    entity_set_name: str,
    record_id: str,
  ) -> Dict[str, Any]:
    """Delete a record from a table.
    
    Args:
        entity_set_name: Entity set name (e.g., 'accounts', 'contacts')
        record_id: GUID of the record to delete
        
    Returns:
        Dictionary with deletion status
        
    Reference: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/update-delete-entities-using-web-api
    """
    endpoint = f'{entity_set_name}({record_id})'
    response = self._make_request('DELETE', endpoint)
    
    return {
      'success': True,
      'record_id': record_id,
      'status_code': response.status_code,
    }

  # ========================================
  # Helper Methods
  # ========================================

  def query_fetchxml(
    self,
    entity_set_name: str,
    fetch_xml: str,
  ) -> Dict[str, Any]:
    """Query records using FetchXML.

    Args:
        entity_set_name: Entity set name (e.g., 'accounts', 'contacts')
        fetch_xml: FetchXML query string

    Returns:
        Dictionary with 'value' containing list of records

    Reference: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/fetchxml/overview
    """
    # URL encode the FetchXML query
    params = {
      'fetchXml': fetch_xml
    }

    response = self._make_request('GET', entity_set_name, params=params)
    return response.json()

  def get_entity_set_name(self, logical_name: str) -> str:
    """Get the entity set name (plural form) for a table's logical name.

    Args:
        logical_name: Logical name (e.g., 'account')

    Returns:
        Entity set name (e.g., 'accounts')
    """
    # Query metadata to get EntitySetName
    params = {
      '$filter': f"LogicalName eq '{logical_name}'",
      '$select': 'EntitySetName',
    }

    response = self._make_request('GET', 'EntityDefinitions', params=params)
    data = response.json()

    if not data.get('value'):
      raise ValueError(f"Table '{logical_name}' not found")

    return data['value'][0]['EntitySetName']

