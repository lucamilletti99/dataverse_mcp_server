"""Dataverse configuration - runtime fallback when app.yaml env vars don't load."""
import os

# WORKAROUND: Databricks Apps may not properly load app.yaml environment variables
#
# INSTRUCTIONS:
# 1. Copy this file to dataverse_config.py (it's in .gitignore)
# 2. Fill in your actual credentials below
# 3. When deploying to Databricks Apps, uncomment and set these values
#
# SECURITY NOTE: Never commit actual secrets to git!
# This file should only be used locally or in secure deployment environments.

DATAVERSE_CONFIG = {
    'DATAVERSE_HOST': os.environ.get('DATAVERSE_HOST', ''),
    'DATAVERSE_TENANT_ID': os.environ.get('DATAVERSE_TENANT_ID', ''),
    'DATAVERSE_CLIENT_ID': os.environ.get('DATAVERSE_CLIENT_ID', ''),
    'DATAVERSE_CLIENT_SECRET': os.environ.get('DATAVERSE_CLIENT_SECRET', ''),
}

# For local development with hardcoded values (NOT RECOMMENDED):
# Uncomment and fill in the values below, but NEVER commit this file with secrets!
# DATAVERSE_CONFIG = {
#     'DATAVERSE_HOST': 'https://your-org.api.crm.dynamics.com',
#     'DATAVERSE_TENANT_ID': 'your-tenant-id-here',
#     'DATAVERSE_CLIENT_ID': 'your-client-id-here',
#     'DATAVERSE_CLIENT_SECRET': 'your-client-secret-here',
# }

def apply_dataverse_config():
    """Apply Dataverse config to environment if not already set."""
    for key, value in DATAVERSE_CONFIG.items():
        if value and (key not in os.environ or not os.environ[key]):
            os.environ[key] = value
            print(f"✅ Set {key} from dataverse_config.py")

