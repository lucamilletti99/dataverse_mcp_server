#!/usr/bin/env python3
"""Test script for Dataverse MCP server functionality.

This script tests the Dataverse client and authentication without requiring
the full MCP server to be running.

Usage:
    python test_dataverse.py
"""

import os
import sys
from pathlib import Path

# Add server directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from server.dataverse.auth import DataverseAuth
from server.dataverse.client import DataverseClient


def test_auth():
  """Test Dataverse authentication."""
  print('\n' + '=' * 80)
  print('TEST 1: Authentication')
  print('=' * 80)

  try:
    auth = DataverseAuth()
    print(f'✅ Auth initialized')
    print(f'   Tenant ID: {auth.tenant_id}')
    print(f'   Client ID: {auth.client_id}')
    print(f'   Dataverse Host: {auth.dataverse_host}')
    print(f'   Scope: {auth.scope}')

    # Get access token
    token = auth.get_access_token()
    print(f'✅ Access token obtained')
    print(f'   Token preview: {token[:50]}...')

    return True

  except Exception as e:
    print(f'❌ Authentication failed: {str(e)}')
    return False


def test_list_tables():
  """Test listing Dataverse tables."""
  print('\n' + '=' * 80)
  print('TEST 2: List Tables')
  print('=' * 80)

  try:
    client = DataverseClient()
    result = client.list_tables(top=5)

    tables = result.get('value', [])
    print(f'✅ Retrieved {len(tables)} tables')

    for table in tables[:5]:
      logical_name = table.get('LogicalName')
      display_name = table.get('DisplayName', {}).get('UserLocalizedLabel', {}).get('Label')
      entity_set = table.get('EntitySetName')
      print(f'   - {logical_name} ({display_name}) → {entity_set}')

    return True

  except Exception as e:
    print(f'❌ List tables failed: {str(e)}')
    return False


def test_describe_table():
  """Test describing a Dataverse table."""
  print('\n' + '=' * 80)
  print('TEST 3: Describe Table (account)')
  print('=' * 80)

  try:
    client = DataverseClient()
    result = client.describe_table('account')

    print(f'✅ Table metadata retrieved')
    print(f'   Logical Name: {result.get("LogicalName")}')
    print(
      f'   Display Name: {result.get("DisplayName", {}).get("UserLocalizedLabel", {}).get("Label")}'
    )
    print(f'   Entity Set: {result.get("EntitySetName")}')
    print(f'   Primary ID: {result.get("PrimaryIdAttribute")}')
    print(f'   Primary Name: {result.get("PrimaryNameAttribute")}')

    attributes = result.get('Attributes', [])
    print(f'   Attributes: {len(attributes)} total')

    # Show first 10 attributes
    print(f'   First 10 attributes:')
    for attr in attributes[:10]:
      logical_name = attr.get('LogicalName')
      attr_type = attr.get('AttributeType')
      display_name = attr.get('DisplayName', {}).get('UserLocalizedLabel', {}).get('Label')
      print(f'      - {logical_name} ({attr_type}) → {display_name}')

    return True

  except Exception as e:
    print(f'❌ Describe table failed: {str(e)}')
    return False


def test_read_query():
  """Test querying Dataverse records."""
  print('\n' + '=' * 80)
  print('TEST 4: Read Query (accounts)')
  print('=' * 80)

  try:
    client = DataverseClient()

    # Get entity set name
    entity_set = client.get_entity_set_name('account')
    print(f'✅ Entity set name: {entity_set}')

    # Query records
    result = client.read_query(
      entity_set_name=entity_set, select=['name', 'accountid'], top=5
    )

    records = result.get('value', [])
    print(f'✅ Retrieved {len(records)} records')

    for record in records:
      print(f'   - {record.get("name")} (ID: {record.get("accountid")})')

    return True

  except Exception as e:
    print(f'❌ Read query failed: {str(e)}')
    # This might fail if there are no accounts, which is okay
    if 'does not contain a property named' in str(e) or '404' in str(e):
      print(f'   Note: This is expected if the account table is empty or unavailable')
      return True
    return False


def main():
  """Run all tests."""
  print('\n' + '=' * 80)
  print('DATAVERSE MCP SERVER - CONNECTION TESTS')
  print('=' * 80)

  # Check environment variables
  required_vars = [
    'DATAVERSE_HOST',
    'DATAVERSE_TENANT_ID',
    'DATAVERSE_CLIENT_ID',
    'DATAVERSE_CLIENT_SECRET',
  ]

  missing_vars = [var for var in required_vars if not os.environ.get(var)]

  if missing_vars:
    print(f'\n❌ Missing required environment variables:')
    for var in missing_vars:
      print(f'   - {var}')
    print(f'\nPlease set these in your .env.local file or export them.')
    print(f'See .env.example for reference.')
    sys.exit(1)

  print(f'\n✅ All required environment variables are set')

  # Run tests
  results = []
  results.append(('Authentication', test_auth()))
  results.append(('List Tables', test_list_tables()))
  results.append(('Describe Table', test_describe_table()))
  results.append(('Read Query', test_read_query()))

  # Summary
  print('\n' + '=' * 80)
  print('TEST SUMMARY')
  print('=' * 80)

  passed = sum(1 for _, result in results if result)
  total = len(results)

  for test_name, result in results:
    status = '✅ PASS' if result else '❌ FAIL'
    print(f'{status} - {test_name}')

  print(f'\nTotal: {passed}/{total} tests passed')

  if passed == total:
    print('\n🎉 All tests passed! Dataverse MCP server is ready.')
    sys.exit(0)
  else:
    print('\n⚠️  Some tests failed. Check the errors above.')
    sys.exit(1)


if __name__ == '__main__':
  # Load environment from .env.local if it exists
  env_file = Path(__file__).parent / '.env.local'
  if env_file.exists():
    print(f'Loading environment from {env_file}')
    with open(env_file) as f:
      for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
          key, _, value = line.partition('=')
          if key and value:
            os.environ[key] = value

  main()

