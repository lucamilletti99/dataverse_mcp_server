"""MCP Tools for Dataverse operations."""

import json
import os
from typing import Any, Dict, List, Optional

from server.dataverse.client import DataverseClient


def get_dataverse_client() -> DataverseClient:
  """Get a configured Dataverse client instance.
  
  Returns:
      DataverseClient configured with environment credentials
  """
  return DataverseClient()


# ========================================
# Tool Implementation Functions
# These can be called directly by the agent router
# ========================================

def list_tables_impl(
  filter_query: str = None,
  top: int = 100,
  custom_only: bool = False,
) -> dict:
  """Implementation of list_tables tool."""
  print(f"\n🔧 list_tables_impl called with filter_query={filter_query}, top={top}, custom_only={custom_only}")
  try:
    client = get_dataverse_client()
    
    # Apply custom_only filter
    if custom_only and not filter_query:
      filter_query = "IsCustomEntity eq true"
      print(f"   Applying custom_only filter: {filter_query}")
    
    print(f"📞 Calling client.list_tables...")
    result = client.list_tables(filter_query=filter_query, top=top)
    tables = result.get('value', [])
    print(f"✅ Got {len(tables)} tables from client")
    
    # Format table info
    formatted_tables = []
    print(f"🔄 Formatting table info...")
    for i, table in enumerate(tables):
      if i < 3:  # Log first 3 for debugging
        print(f"   Table {i}: {table.get('LogicalName')} ({table.get('EntitySetName')})")
      
      # Safely extract display name (can be None or nested)
      display_name = None
      display_name_obj = table.get('DisplayName')
      if display_name_obj and isinstance(display_name_obj, dict):
        user_label = display_name_obj.get('UserLocalizedLabel')
        if user_label and isinstance(user_label, dict):
          display_name = user_label.get('Label')
      
      formatted_tables.append({
        'logical_name': table.get('LogicalName'),
        'display_name': display_name,
        'entity_set_name': table.get('EntitySetName'),
        'is_custom': table.get('IsCustomEntity'),
      })
    
    print(f"✅ list_tables_impl returning {len(formatted_tables)} tables")
    return {
      'success': True,
      'tables': formatted_tables,
      'count': len(formatted_tables),
    }
  except Exception as e:
    error_msg = str(e)
    print(f"❌ list_tables_impl ERROR: {error_msg}")
    return {
      'success': False,
      'error': error_msg,
      'tables': [],
      'count': 0,
    }


def describe_table_impl(table_name: str) -> dict:
  """Implementation of describe_table tool - keep it simple!"""
  try:
    client = get_dataverse_client()
    result = client.describe_table(table_name)
    
    print(f"🔍 describe_table_impl got result type: {type(result)}")
    
    if not result:
      return {
        'success': False,
        'error': f"No metadata returned for table '{table_name}'",
        'table_name': table_name,
      }
    
    # Keep it simple - just extract the basics and let the LLM handle the rest
    attributes = result.get('Attributes', []) or []
    
    # Simplify attribute extraction - just get the essentials
    simplified_attrs = []
    for attr in attributes[:50]:  # Limit to first 50 to keep response size reasonable
      simplified_attrs.append({
        'LogicalName': attr.get('LogicalName'),
        'AttributeType': attr.get('AttributeType'),
        'IsPrimaryId': attr.get('IsPrimaryId', False),
      })
    
    return {
      'success': True,
      'table_name': result.get('LogicalName', table_name),
      'attributes': simplified_attrs,
      'attribute_count': len(attributes),
      'message': f"Found {len(attributes)} attributes for table '{table_name}' (showing first 50)"
    }
  except Exception as e:
    print(f"❌ describe_table_impl error: {str(e)}")
    return {
      'success': False,
      'error': str(e),
      'table_name': table_name,
    }


def read_query_impl(
  table_name: str,
  select: List[str] = None,
  filter_query: str = None,
  order_by: str = None,
  top: int = 100,
) -> dict:
  """Implementation of read_query tool using OData (simpler than FetchXML)."""
  try:
    client = get_dataverse_client()

    # Get entity set name
    entity_set_name = client.get_entity_set_name(table_name)

    # Query with OData
    result = client.read_query(
      entity_set_name=entity_set_name,
      select=select,
      filter_query=filter_query,
      order_by=order_by,
      top=top,
    )
    records = result.get('value', [])

    return {
      'success': True,
      'table_name': table_name,
      'entity_set_name': entity_set_name,
      'records': records,
      'count': len(records),
      'message': f'Retrieved {len(records)} record(s) from {table_name}',
    }
  except Exception as e:
    return {
      'success': False,
      'error': str(e),
      'table_name': table_name,
      'records': [],
      'count': 0,
    }


def create_record_impl(table_name: str, data: dict) -> dict:
  """Implementation of create_record tool."""
  try:
    client = get_dataverse_client()
    
    # Get entity set name
    entity_set_name = client.get_entity_set_name(table_name)
    
    # Create record
    result = client.create_record(entity_set_name=entity_set_name, data=data)
    
    return {
      'success': True,
      'table_name': table_name,
      'record_id': result.get('entity_id'),
      'message': f'Record created successfully',
    }
  except Exception as e:
    return {
      'success': False,
      'error': str(e),
      'table_name': table_name,
    }


def update_record_impl(table_name: str, record_id: str, data: dict) -> dict:
  """Implementation of update_record tool."""
  try:
    client = get_dataverse_client()
    
    # Get entity set name
    entity_set_name = client.get_entity_set_name(table_name)
    
    # Update record
    client.update_record(entity_set_name=entity_set_name, record_id=record_id, data=data)
    
    return {
      'success': True,
      'table_name': table_name,
      'record_id': record_id,
      'message': f'Record updated successfully',
    }
  except Exception as e:
    return {
      'success': False,
      'error': str(e),
      'table_name': table_name,
      'record_id': record_id,
    }


def delete_record_impl(table_name: str, record_id: str) -> dict:
  """Implementation of delete_record tool - keep it simple!"""
  try:
    client = get_dataverse_client()
    
    # Get entity set name
    entity_set_name = client.get_entity_set_name(table_name)
    
    # Delete record
    result = client.delete_record(entity_set_name=entity_set_name, record_id=record_id)
    
    return {
      'success': True,
      'table_name': table_name,
      'record_id': record_id,
      'message': f'Record deleted successfully',
    }
  except Exception as e:
    return {
      'success': False,
      'error': str(e),
      'table_name': table_name,
      'record_id': record_id,
    }


def load_dataverse_tools(mcp_server):
  """Register all Dataverse MCP tools with the server.
  
  Args:
      mcp_server: The FastMCP server instance to register tools with
  """

  @mcp_server.tool
  def health() -> dict:
    """Check the health of the Dataverse MCP server and connection.
    
    Returns:
        Dictionary with health status and configuration info
    """
    try:
      print("\n" + "="*60)
      print("🏥 HEALTH CHECK - Dataverse MCP Server")
      print("="*60)
      
      # Check if credentials are configured
      tenant_id = os.environ.get('DATAVERSE_TENANT_ID')
      client_id = os.environ.get('DATAVERSE_CLIENT_ID')
      client_secret = os.environ.get('DATAVERSE_CLIENT_SECRET')
      dataverse_host = os.environ.get('DATAVERSE_HOST')

      print("\n📋 Environment Variables Status:")
      env_status = {
          'DATAVERSE_HOST': dataverse_host,
          'DATAVERSE_TENANT_ID': tenant_id,
          'DATAVERSE_CLIENT_ID': client_id,
          'DATAVERSE_CLIENT_SECRET': '***' if client_secret else None,
      }
      
      for key, value in env_status.items():
          if value:
              display_value = value[:30] if key != 'DATAVERSE_CLIENT_SECRET' else '***'
              print(f"   ✅ {key}: {display_value}...")
          else:
              print(f"   ❌ {key}: NOT SET")

      config_complete = all([tenant_id, client_id, client_secret, dataverse_host])
      print(f"\n🔧 Configuration Complete: {'✅ YES' if config_complete else '❌ NO'}")

      # Try to connect if configured
      connection_healthy = False
      error_message = None
      table_count = 0

      if config_complete:
        print("\n🔌 Testing Dataverse Connection...")
        try:
          client = get_dataverse_client()
          # Make a simple API call to verify connection
          result = client.list_tables(top=1)
          table_count = len(result.get('value', []))
          connection_healthy = True
          print(f"✅ Connection successful! (Found {table_count} table(s) in test query)")
        except Exception as e:
          error_message = str(e)
          print(f"❌ Connection failed: {error_message}")
      else:
        error_message = "Configuration incomplete - missing required environment variables"
        print(f"⚠️  {error_message}")

      print("="*60 + "\n")

      return {
        'status': 'healthy' if connection_healthy else 'unhealthy',
        'service': 'dataverse-mcp-server',
        'dataverse_configured': config_complete,
        'connection_healthy': connection_healthy,
        'dataverse_host': dataverse_host if dataverse_host else 'NOT SET',
        'tenant_id': tenant_id[:8] + '...' if tenant_id else 'NOT SET',
        'client_id': client_id[:8] + '...' if client_id else 'NOT SET',
        'client_secret_set': bool(client_secret),
        'error': error_message,
        'architecture': 'Dataverse Web API v9.2',
        'auth_mode': 'service-principal (OAuth M2M)',
        'test_table_count': table_count,
      }

    except Exception as e:
      error_msg = str(e)
      print(f"❌ HEALTH CHECK ERROR: {error_msg}")
      return {
        'status': 'error',
        'service': 'dataverse-mcp-server',
        'error': error_msg,
      }

  # ========================================
  # Table Operations (Phase 1)
  # ========================================

  @mcp_server.tool
  def list_tables(
    filter_query: str = None,
    top: int = 100,
    custom_only: bool = False,
  ) -> dict:
    """List all tables (entities) in Dataverse.
    
    Returns metadata about available tables including logical names, display names,
    and primary attributes. Use this to discover what tables exist before querying data.
    
    Args:
        filter_query: OData filter expression (e.g., "IsCustomEntity eq true")
        top: Maximum number of tables to return (default: 100)
        custom_only: If True, only return custom tables (shortcut for common filter)
        
    Returns:
        Dictionary with:
        - success: Boolean indicating success
        - tables: List of table metadata
        - count: Number of tables returned
        
    Example:
        list_tables(top=10)
        list_tables(custom_only=True)
        list_tables(filter_query="IsActivity eq false")
    """
    try:
      client = get_dataverse_client()

      # Apply custom_only filter if requested
      if custom_only and not filter_query:
        filter_query = 'IsCustomEntity eq true'

      result = client.list_tables(filter_query=filter_query, top=top)

      tables = result.get('value', [])

      # Format table info for easier consumption
      formatted_tables = []
      for table in tables:
        formatted_tables.append({
          'logical_name': table.get('LogicalName'),
          'schema_name': table.get('SchemaName'),
          'display_name': table.get('DisplayName', {}).get('UserLocalizedLabel', {}).get('Label'),
          'entity_set_name': table.get('EntitySetName'),
          'primary_id_attribute': table.get('PrimaryIdAttribute'),
          'primary_name_attribute': table.get('PrimaryNameAttribute'),
          'is_custom': table.get('IsCustomEntity'),
          'is_activity': table.get('IsActivity'),
          'object_type_code': table.get('ObjectTypeCode'),
        })

      return {
        'success': True,
        'tables': formatted_tables,
        'count': len(formatted_tables),
        'message': f'Found {len(formatted_tables)} table(s)',
      }

    except Exception as e:
      print(f'❌ Error listing tables: {str(e)}')
      return {'success': False, 'error': str(e), 'tables': [], 'count': 0}

  @mcp_server.tool
  def describe_table(table_name: str) -> dict:
    """Get detailed metadata for a specific table (entity).
    
    Returns comprehensive information about a table including all its columns (attributes),
    data types, and relationships. Use this to understand the structure before querying.
    
    Args:
        table_name: Logical name of the table (e.g., 'account', 'contact', 'cr123_customtable')
        
    Returns:
        Dictionary with:
        - success: Boolean indicating success
        - table_name: Logical name of the table
        - schema_name: Schema name
        - display_name: User-friendly display name
        - entity_set_name: Plural form used in API queries
        - primary_id_attribute: Primary key column name
        - primary_name_attribute: Main display column name
        - attributes: List of all columns with types and metadata
        
    Example:
        describe_table("account")
        describe_table("contact")
    """
    try:
      client = get_dataverse_client()
      result = client.describe_table(table_name)

      # Extract key information
      attributes = []
      for attr in result.get('Attributes', []):
        attr_info = {
          'logical_name': attr.get('LogicalName'),
          'schema_name': attr.get('SchemaName'),
          'display_name': attr.get('DisplayName', {}).get('UserLocalizedLabel', {}).get('Label'),
          'attribute_type': attr.get('AttributeType'),
          'is_primary_id': attr.get('IsPrimaryId'),
          'is_primary_name': attr.get('IsPrimaryName'),
          'is_valid_for_create': attr.get('IsValidForCreate'),
          'is_valid_for_update': attr.get('IsValidForUpdate'),
          'is_valid_for_read': attr.get('IsValidForRead'),
          'required_level': attr.get('RequiredLevel', {}).get('Value'),
        }

        # Add type-specific info
        if attr.get('AttributeType') == 'String':
          attr_info['max_length'] = attr.get('MaxLength')
        elif attr.get('AttributeType') in ['Integer', 'BigInt']:
          attr_info['min_value'] = attr.get('MinValue')
          attr_info['max_value'] = attr.get('MaxValue')
        elif attr.get('AttributeType') == 'Decimal':
          attr_info['min_value'] = attr.get('MinValue')
          attr_info['max_value'] = attr.get('MaxValue')
          attr_info['precision'] = attr.get('Precision')
        elif attr.get('AttributeType') == 'Picklist':
          attr_info['options'] = [
            {'value': opt.get('Value'), 'label': opt.get('Label', {}).get('UserLocalizedLabel', {}).get('Label')}
            for opt in attr.get('OptionSet', {}).get('Options', [])
          ]

        attributes.append(attr_info)

      return {
        'success': True,
        'table_name': result.get('LogicalName'),
        'schema_name': result.get('SchemaName'),
        'display_name': result.get('DisplayName', {}).get('UserLocalizedLabel', {}).get('Label'),
        'entity_set_name': result.get('EntitySetName'),
        'primary_id_attribute': result.get('PrimaryIdAttribute'),
        'primary_name_attribute': result.get('PrimaryNameAttribute'),
        'is_custom': result.get('IsCustomEntity'),
        'description': result.get('Description', {}).get('UserLocalizedLabel', {}).get('Label'),
        'attributes': attributes,
        'attribute_count': len(attributes),
      }

    except Exception as e:
      print(f'❌ Error describing table: {str(e)}')
      return {'success': False, 'error': str(e)}

  @mcp_server.tool
  def read_query(
    table_name: str,
    select: List[str] = None,
    filter_query: str = None,
    order_by: str = None,
    top: int = 100,
  ) -> dict:
    """Query records from a Dataverse table.
    
    Retrieve data from a table using OData query syntax. You can filter, sort,
    and select specific columns. Use describe_table first to see available columns.
    
    Args:
        table_name: Logical name of the table (e.g., 'account', 'contact')
        select: List of column names to return (e.g., ['name', 'emailaddress1'])
                Leave empty to return all columns
        filter_query: OData filter expression (e.g., "revenue gt 100000", "name eq 'Contoso'")
        order_by: OData orderby expression (e.g., "name asc", "createdon desc")
        top: Maximum number of records to return (default: 100)
        
    Returns:
        Dictionary with:
        - success: Boolean indicating success
        - records: List of record objects
        - count: Number of records returned
        
    Example:
        # Get all accounts
        read_query("account", top=10)
        
        # Get specific columns
        read_query("account", select=["name", "revenue", "industry"])
        
        # Filter by condition
        read_query("account", filter_query="revenue gt 1000000")
        
        # Sort results
        read_query("contact", select=["fullname", "emailaddress1"], order_by="fullname asc")
    """
    try:
      client = get_dataverse_client()

      # Get entity set name (plural form) for the table
      entity_set_name = client.get_entity_set_name(table_name)

      result = client.read_query(
        entity_set_name=entity_set_name,
        select=select,
        filter_query=filter_query,
        order_by=order_by,
        top=top,
      )

      records = result.get('value', [])

      return {
        'success': True,
        'table_name': table_name,
        'entity_set_name': entity_set_name,
        'records': records,
        'count': len(records),
        'message': f'Retrieved {len(records)} record(s) from {table_name}',
      }

    except Exception as e:
      print(f'❌ Error querying records: {str(e)}')
      return {'success': False, 'error': str(e), 'records': [], 'count': 0}

  @mcp_server.tool
  def create_record(table_name: str, data: dict) -> dict:
    """Create a new record in a Dataverse table.
    
    Insert a new row with the specified field values. Use describe_table first
    to see what fields are available and required.
    
    Args:
        table_name: Logical name of the table (e.g., 'account', 'contact')
        data: Record data as dictionary with column names as keys
              Example: {"name": "Contoso Ltd", "revenue": 1000000, "industry": "Technology"}
        
    Returns:
        Dictionary with:
        - success: Boolean indicating success
        - entity_id: GUID of the created record
        - message: Success message
        
    Example:
        # Create an account
        create_record("account", {
            "name": "Contoso Ltd",
            "revenue": 1000000,
            "industry": "Technology"
        })
        
        # Create a contact
        create_record("contact", {
            "firstname": "John",
            "lastname": "Doe",
            "emailaddress1": "john.doe@contoso.com"
        })
    """
    try:
      client = get_dataverse_client()

      # Get entity set name (plural form) for the table
      entity_set_name = client.get_entity_set_name(table_name)

      result = client.create_record(entity_set_name=entity_set_name, data=data)

      return {
        'success': True,
        'table_name': table_name,
        'entity_id': result.get('entity_id'),
        'entity_id_url': result.get('entity_id_url'),
        'message': f'✅ Successfully created record in {table_name}',
      }

    except Exception as e:
      print(f'❌ Error creating record: {str(e)}')
      return {'success': False, 'error': str(e)}

  @mcp_server.tool
  def update_record(table_name: str, record_id: str, data: dict) -> dict:
    """Update an existing record in a Dataverse table.
    
    Modify specific fields of an existing record. Only the fields you provide
    will be updated; other fields remain unchanged.
    
    Args:
        table_name: Logical name of the table (e.g., 'account', 'contact')
        record_id: GUID of the record to update (from primary ID field)
        data: Fields to update as dictionary with column names as keys
              Example: {"revenue": 2000000, "industry": "Finance"}
        
    Returns:
        Dictionary with:
        - success: Boolean indicating success
        - record_id: GUID of the updated record
        - message: Success message
        
    Example:
        # Update an account's revenue
        update_record("account", "12345678-1234-1234-1234-123456789abc", {
            "revenue": 2000000
        })
        
        # Update multiple fields
        update_record("contact", "87654321-4321-4321-4321-cba987654321", {
            "emailaddress1": "newemail@contoso.com",
            "jobtitle": "Senior Manager"
        })
    """
    try:
      client = get_dataverse_client()

      # Get entity set name (plural form) for the table
      entity_set_name = client.get_entity_set_name(table_name)

      result = client.update_record(
        entity_set_name=entity_set_name, record_id=record_id, data=data
      )

      return {
        'success': True,
        'table_name': table_name,
        'record_id': result.get('record_id'),
        'message': f'✅ Successfully updated record in {table_name}',
      }

    except Exception as e:
      print(f'❌ Error updating record: {str(e)}')
      return {'success': False, 'error': str(e)}

  # ========================================
  # Stub Tools (Phase 2)
  # ========================================

  @mcp_server.tool
  def list_knowledge_sources() -> dict:
    """List all knowledge sources available in Dataverse.
    
    **Note:** This is a stub implementation. Knowledge sources integration
    with Copilot Studio is not yet implemented.
    
    Returns:
        Dictionary indicating feature is not yet available
    """
    return {
      'success': False,
      'error': 'Knowledge sources feature not yet implemented',
      'message': 'This feature requires Copilot Studio integration (Phase 2)',
    }

  @mcp_server.tool
  def retrieve_knowledge(query: str) -> dict:
    """Retrieve knowledge from a configured knowledge source.
    
    **Note:** This is a stub implementation. Knowledge retrieval integration
    with Copilot Studio is not yet implemented.
    
    Args:
        query: Search query string
        
    Returns:
        Dictionary indicating feature is not yet available
    """
    return {
      'success': False,
      'error': 'Knowledge retrieval feature not yet implemented',
      'message': 'This feature requires Copilot Studio integration (Phase 2)',
    }

  @mcp_server.tool
  def list_prompts() -> dict:
    """List all predefined prompts available in the environment.
    
    **Note:** This is a stub implementation. Custom prompts integration
    is not yet implemented.
    
    Returns:
        Dictionary indicating feature is not yet available
    """
    return {
      'success': False,
      'error': 'Prompts feature not yet implemented',
      'message': 'This feature will be implemented in Phase 2',
    }

  @mcp_server.tool
  def execute_prompt(prompt_name: str, parameters: dict = None) -> dict:
    """Execute a predefined prompt with optional parameters.
    
    **Note:** This is a stub implementation. Custom prompts integration
    is not yet implemented.
    
    Args:
        prompt_name: Name of the prompt to execute
        parameters: Optional parameters for the prompt
        
    Returns:
        Dictionary indicating feature is not yet available
    """
    return {
      'success': False,
      'error': 'Prompt execution feature not yet implemented',
      'message': 'This feature will be implemented in Phase 2',
    }

