# Databricks Secrets Setup Guide

This guide explains how to securely store your Dataverse credentials in Databricks Secrets for production deployment.

## Why Use Databricks Secrets?

✅ **Secure** - Credentials are encrypted at rest  
✅ **Centralized** - Manage credentials in one place  
✅ **Auditable** - Track who accesses secrets  
✅ **Production-ready** - Industry best practice  

❌ **Don't** hardcode credentials in `app.yaml` (visible to anyone with app access)

---

## Quick Setup (Automated)

### Option A: Automated Script (Recommended)

Run this script to automatically push credentials from `.env.local` to Databricks:

```bash
./setup_databricks_secrets.sh
```

The script will:
1. ✅ Read credentials from your `.env.local`
2. ✅ Create Databricks secret scope named `dataverse`
3. ✅ Store all credentials as secrets
4. ✅ Verify secrets were created

**What it stores:**
- `host` ← Your DATAVERSE_HOST or DYNAMICS_URL
- `tenant_id` ← Your DATAVERSE_TENANT_ID or TENANT_ID
- `client_id` ← Your DATAVERSE_CLIENT_ID or CLIENT_ID
- `client_secret` ← Your DATAVERSE_CLIENT_SECRET or CLIENT_SECRET

---

## Manual Setup (If Needed)

### Step 1: Create Secret Scope

```bash
databricks secrets create-scope dataverse
```

### Step 2: Store Each Credential

```bash
# Store Dataverse host
databricks secrets put-secret dataverse host
# Paste: https://org1bfe9c69.api.crm.dynamics.com

# Store tenant ID
databricks secrets put-secret dataverse tenant_id
# Paste: your-tenant-id-guid

# Store client ID
databricks secrets put-secret dataverse client_id
# Paste: your-client-id-guid

# Store client secret
databricks secrets put-secret dataverse client_secret
# Paste: your-client-secret-value
```

### Step 3: Verify Secrets

```bash
databricks secrets list-secrets --scope dataverse
```

Expected output:
```
Key             Last Updated
host            <timestamp>
tenant_id       <timestamp>
client_id       <timestamp>
client_secret   <timestamp>
```

---

## Configure app.yaml

The `app.yaml` file is already configured to use Databricks Secrets. You just need to make sure the secret references are uncommented:

```yaml
environment:
  # Dataverse credentials from Databricks Secrets
  - name: DATAVERSE_HOST
    value_from:
      secret_scope: dataverse
      secret_key: host
  - name: DATAVERSE_TENANT_ID
    value_from:
      secret_scope: dataverse
      secret_key: tenant_id
  - name: DATAVERSE_CLIENT_ID
    value_from:
      secret_scope: dataverse
      secret_key: client_id
  - name: DATAVERSE_CLIENT_SECRET
    value_from:
      secret_scope: dataverse
      secret_key: client_secret
```

✅ These lines are already uncommented if you used the automated script!

---

## Deploy to Databricks

Now you can deploy:

```bash
./deploy.sh --create
```

Check status:

```bash
./app_status.sh
```

---

## Managing Secrets

### List All Secrets in a Scope

```bash
databricks secrets list-secrets --scope dataverse
```

### Update a Secret

```bash
databricks secrets put-secret dataverse client_secret
# Paste new value
```

### Delete a Secret

```bash
databricks secrets delete-secret dataverse <key-name>
```

### Delete Entire Scope

```bash
databricks secrets delete-scope dataverse
```

---

## Multiple Environments

For dev/staging/prod, create separate scopes:

```bash
# Development
databricks secrets create-scope dataverse-dev
databricks secrets put-secret dataverse-dev host
# ... store dev credentials

# Staging
databricks secrets create-scope dataverse-staging
databricks secrets put-secret dataverse-staging host
# ... store staging credentials

# Production
databricks secrets create-scope dataverse-prod
databricks secrets put-secret dataverse-prod host
# ... store prod credentials
```

Then update `app.yaml` for each environment:

```yaml
# For dev
- name: DATAVERSE_HOST
  value_from:
    secret_scope: dataverse-dev
    secret_key: host

# For prod
- name: DATAVERSE_HOST
  value_from:
    secret_scope: dataverse-prod
    secret_key: host
```

---

## Troubleshooting

### "Scope already exists"

This is fine! The scope was created previously. Just proceed to store secrets.

### "Permission denied"

You may need admin permissions to create secret scopes. Contact your Databricks admin.

### "Secret not found" during deployment

Verify secrets exist:

```bash
databricks secrets list-secrets --scope dataverse
```

Make sure `app.yaml` references the correct scope name.

### App can't access secrets

The app's service principal needs READ access to the secret scope. This is usually granted automatically, but if not:

```bash
# Get service principal ID from app_status.sh
./app_status.sh

# Grant READ access
databricks secrets put-acl dataverse <service-principal-id> READ
```

---

## Security Best Practices

### ✅ Do:
- Use Databricks Secrets for all production deployments
- Create separate scopes for dev/staging/prod
- Rotate credentials regularly
- Grant minimal permissions (READ only for apps)
- Monitor secret access logs

### ❌ Don't:
- Hardcode credentials in `app.yaml`
- Share secret scope access broadly
- Commit `.env.local` to git (already in `.gitignore`)
- Use the same credentials across all environments

---

## Variable Name Mapping

The script handles both naming conventions:

| Your .env.local | Databricks Secret | app.yaml Variable |
|----------------|-------------------|-------------------|
| DYNAMICS_URL or DATAVERSE_HOST | host | DATAVERSE_HOST |
| TENANT_ID or DATAVERSE_TENANT_ID | tenant_id | DATAVERSE_TENANT_ID |
| CLIENT_ID or DATAVERSE_CLIENT_ID | client_id | DATAVERSE_CLIENT_ID |
| CLIENT_SECRET or DATAVERSE_CLIENT_SECRET | client_secret | DATAVERSE_CLIENT_SECRET |
| OAUTH_SCOPE | oauth_scope | (optional) |
| TOKEN_ENDPOINT | token_endpoint | (optional) |

---

## Reference

- [Databricks Secrets Documentation](https://docs.databricks.com/en/security/secrets/index.html)
- [Databricks Apps Configuration](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html)

---

## Quick Reference Commands

```bash
# Setup (automated)
./setup_databricks_secrets.sh

# Deploy
./deploy.sh --create

# Check status
./app_status.sh

# View logs
databricks apps logs <your-app-name> --follow

# List secrets
databricks secrets list-secrets --scope dataverse

# Update a secret
databricks secrets put-secret dataverse <key-name>
```

---

**Need help?** See [DATABRICKS_DEPLOYMENT.md](DATABRICKS_DEPLOYMENT.md) for full deployment guide.

