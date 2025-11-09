"""Database resources router - stub for Databricks-specific features."""

from typing import Any, Dict, List

from fastapi import APIRouter

router = APIRouter()


@router.get('/warehouses')
async def list_warehouses(search: str = '') -> Dict[str, List[Dict[str, Any]]]:
    """List SQL warehouses.
    
    Stub implementation - Databricks-specific feature not applicable to Dataverse.
    """
    return {'warehouses': []}


@router.get('/catalogs')
async def list_catalogs(search: str = '') -> Dict[str, List[Dict[str, Any]]]:
    """List Unity Catalog catalogs.
    
    Stub implementation - Databricks-specific feature not applicable to Dataverse.
    """
    return {'catalogs': []}


@router.get('/catalogs/{catalog_name}/schemas')
async def list_schemas(catalog_name: str, search: str = '') -> Dict[str, List[Dict[str, Any]]]:
    """List schemas in a catalog.
    
    Stub implementation - Databricks-specific feature not applicable to Dataverse.
    """
    return {'schemas': []}


@router.get('/catalogs/{catalog_name}/schemas/{schema_name}/validate')
async def validate_catalog_schema(catalog_name: str, schema_name: str) -> Dict[str, Any]:
    """Validate catalog and schema existence.
    
    Stub implementation - Databricks-specific feature not applicable to Dataverse.
    """
    return {
        'exists': False,
        'message': 'Databricks Unity Catalog not applicable to Dataverse MCP server'
    }

