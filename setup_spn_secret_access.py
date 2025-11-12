#!/usr/bin/env python3
"""
Setup Service Principal access to Databricks Secrets.

This script grants the app's SPN access to the 'dataverse' secret scope
so it can read credentials when running as a Databricks App.

Usage:
    export DATABRICKS_HOST="https://your-workspace.azuredatabricks.net"
    export DATABRICKS_TOKEN="your-token"
    python setup_spn_secret_access.py
"""

import os
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.workspace import AclPermission

# SPN for the Databricks App
APP_SPN_ID = "8e80703e-902e-4164-b195-80692ba6fce1"
SECRET_SCOPE = "dataverse"

def main():
    print("=" * 60)
    print("Setup SPN Secret Access")
    print("=" * 60)
    print()
    
    # Initialize workspace client from environment variables
    print("🔐 Connecting to Databricks workspace...")
    print(f"   Host: {os.getenv('DATABRICKS_HOST', '(using default profile)')}")
    w = WorkspaceClient()  # Uses DATABRICKS_HOST and DATABRICKS_TOKEN from env or ~/.databrickscfg
    print("✅ Connected to Databricks")
    print()
    
    # Check if secret scope exists
    print(f"🔍 Checking secret scope '{SECRET_SCOPE}'...")
    try:
        scopes = list(w.secrets.list_scopes())
        scope_names = [s.name for s in scopes]
        
        if SECRET_SCOPE not in scope_names:
            print(f"❌ Secret scope '{SECRET_SCOPE}' does not exist!")
            print()
            print("Please create it first:")
            print(f"  databricks secrets create-scope {SECRET_SCOPE}")
            print()
            print("Or run: ./setup_databricks_secrets.sh")
            return 1
        
        print(f"✅ Secret scope '{SECRET_SCOPE}' exists")
    except Exception as e:
        print(f"❌ Error checking scopes: {e}")
        return 1
    
    print()
    
    # List current ACLs
    print(f"📋 Current ACLs for scope '{SECRET_SCOPE}':")
    try:
        acls = list(w.secrets.list_acls(scope=SECRET_SCOPE))
        if acls:
            for acl in acls:
                print(f"   - Principal: {acl.principal}, Permission: {acl.permission}")
        else:
            print("   (No ACLs - scope creator has full access)")
    except Exception as e:
        print(f"   ⚠️  Could not list ACLs: {e}")
    
    print()
    
    # Grant SPN access
    print(f"🔑 Granting MANAGE permission to SPN {APP_SPN_ID}...")
    try:
        w.secrets.put_acl(
            scope=SECRET_SCOPE,
            principal=APP_SPN_ID,
            permission=AclPermission.MANAGE
        )
        print("✅ Successfully granted MANAGE permission")
    except Exception as e:
        print(f"❌ Error granting permission: {e}")
        print()
        print("This might happen if:")
        print("  1. The SPN already has access (this is fine)")
        print("  2. You don't have permission to modify ACLs")
        print("  3. The secret scope is workspace-level and ACLs are managed differently")
        print()
        print("Trying with CLI command instead...")
        import subprocess
        try:
            result = subprocess.run(
                ["databricks", "secrets", "put-acl", SECRET_SCOPE, APP_SPN_ID, "MANAGE"],
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ Successfully granted MANAGE permission via CLI")
        except subprocess.CalledProcessError as cli_error:
            print(f"❌ CLI command also failed: {cli_error}")
            return 1
    
    print()
    
    # Verify access
    print("🔍 Verifying SPN has access...")
    try:
        acls = list(w.secrets.list_acls(scope=SECRET_SCOPE))
        spn_acl = next((a for a in acls if a.principal == APP_SPN_ID), None)
        
        if spn_acl:
            print(f"✅ SPN has {spn_acl.permission} permission")
        else:
            print("⚠️  SPN not found in ACL list, but this might be OK if scope is workspace-level")
    except Exception as e:
        print(f"⚠️  Could not verify: {e}")
    
    print()
    
    # List secrets in scope
    print(f"📋 Secrets in scope '{SECRET_SCOPE}':")
    try:
        secrets = list(w.secrets.list_secrets(scope=SECRET_SCOPE))
        if secrets:
            for secret in secrets:
                print(f"   - {secret.key}")
            print()
            print(f"✅ Found {len(secrets)} secret(s)")
        else:
            print("   (No secrets found)")
            print()
            print("⚠️  You need to create secrets first:")
            print("   ./setup_databricks_secrets.sh")
    except Exception as e:
        print(f"❌ Error listing secrets: {e}")
        return 1
    
    print()
    print("=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Make sure secrets are populated: ./setup_databricks_secrets.sh")
    print("  2. Remove hardcoded fallback credentials from server/dataverse/auth.py")
    print("  3. Redeploy the app: ./deploy.sh")
    print()
    
    return 0

if __name__ == "__main__":
    exit(main())

