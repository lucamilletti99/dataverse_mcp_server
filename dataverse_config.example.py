"""Dataverse configuration template - copy to dataverse_config.py and fill in your values."""
import os

# WORKAROUND: Databricks Apps may not properly load app.yaml environment variables
#
# INSTRUCTIONS:
# 1. Copy this file to dataverse_config.py (it's in .gitignore)
# 2. Fill in your actual credentials below
# 3. Run the app locally or deploy to Databricks Apps
#
# SECURITY NOTE: Never commit actual secrets to git!
# The dataverse_config.py file is gitignored to prevent accidental commits.

DATAVERSE_CONFIG = {
    'DATAVERSE_HOST': 'https://your-org.api.crm.dynamics.com',
    'DATAVERSE_TENANT_ID': 'your-azure-tenant-id-here',
    'DATAVERSE_CLIENT_ID': 'your-app-registration-client-id-here',
    'DATAVERSE_CLIENT_SECRET': 'your-app-registration-client-secret-here',
}

def apply_dataverse_config():
    """Apply Dataverse config to environment if not already set."""
    for key, value in DATAVERSE_CONFIG.items():
        if value and (key not in os.environ or not os.environ[key]):
            os.environ[key] = value
            print(f"✅ Set {key} from dataverse_config.py")
