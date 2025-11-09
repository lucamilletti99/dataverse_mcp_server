# Migration from API Registry to Dataverse MCP Server

This document tracks the changes made during the migration from the Databricks API Registry MCP server to the Dataverse MCP server.

## What Changed

### ✅ New Files Added

**Core Implementation:**
- `server/dataverse/` - New Dataverse client module
  - `auth.py` - OAuth authentication for Dataverse
  - `client.py` - Dataverse Web API client
  - `__init__.py` - Module exports
- `server/dataverse_tools.py` - MCP tools for Dataverse operations

**Configuration & Setup:**
- `setup_dataverse.sh` - Interactive setup script
- `test_dataverse.py` - Connection test suite
- `env.example` - Environment variable template

**Documentation:**
- `README.md` - Updated main README for Dataverse
- `README_DATAVERSE.md` - Complete Dataverse reference
- `DATAVERSE_QUICKSTART.md` - 5-minute quick start guide
- `DATAVERSE_SETUP.md` - Detailed setup with Azure AD
- `MIGRATION_NOTES.md` - This file

### ❌ Files Removed

**Old Databricks/API Registry Code:**
- `server/tools.py` - Old Databricks API registry tools
- `server/prompts.py` - Prompts loader
- `server/trace_manager.py` - Trace manager
- `server/routers/registry.py` - API registry router
- `server/routers/db_resources.py` - Databricks resources router
- `server/routers/agent_chat.py` - Agent chat router
- `server/routers/chat.py` - Chat router
- `server/routers/debug_auth.py` - Debug auth router
- `server/routers/traces.py` - Traces router
- `server/routers/prompts.py` - Prompts router
- `server/services/` - Old services directory

**Scripts & Setup:**
- `setup.sh` - Old Databricks setup
- `deploy.sh` - Databricks deployment script
- `app_status.sh` - Databricks app status
- `setup_shared_secrets.sh` - Databricks secrets setup
- `cleanup_bearer_tokens.sh` - Bearer token cleanup
- `test_api_registry.sh` - API registry tests
- `setup_table.py` - Databricks table setup
- `databricks-mcp-launcher.sh` - MCP launcher
- `run-mcp-proxy.sh` - MCP proxy runner
- `debug_api_auth.py` - Auth debugging
- `check_connection_secrets.py` - Connection secrets checker
- `dba_client.py` - Databricks client
- `dba_logz.py` - Databricks logs viewer

**SQL & Configuration:**
- `setup_api_http_registry_table.sql` - API registry table SQL
- `check_api_secrets.sql` - Secrets check SQL
- `app.yaml` - Databricks app configuration

**Documentation:**
- `SECRETS_WORKAROUND.md` - Databricks secrets guide
- `WORKSPACE_REQUIREMENTS.md` - Databricks workspace requirements
- `CLAUDE.md` - Old Claude documentation

**Directories:**
- `notebooks/` - API registry notebooks
- `prompts/` - Old prompt templates
- `personal_resources/` - Personal reference files
- `claude_scripts/` - Old Claude scripts
- `docs/` - Old documentation
- `dba_mcp_proxy/` - Databricks MCP proxy
- `scripts/` - Old utility scripts
- `server/services/` - Old service modules

### 🔄 Files Modified

**Core Application:**
- `server/app.py` - Updated to use Dataverse tools
  - Removed: Databricks-specific routers
  - Added: Dataverse tools loader
  - Kept: MCP server setup, FastAPI structure

- `server/routers/__init__.py` - Simplified routers
  - Kept: health, mcp_info, user
  - Removed: chat, traces, debug_auth, prompts, registry

**Configuration:**
- `config.yaml` - Updated server name
  - Changed: `servername: dataverse-mcp-server`

- `pyproject.toml` - Updated dependencies
  - Removed: databricks-sdk, databricks-connect, mlflow, pandas, click, rich
  - Kept: fastapi, uvicorn, fastmcp, mcp, requests
  - Updated: project name, description, authors

- `requirements.txt` - Simplified dependencies
  - Removed: All Databricks-specific packages
  - Kept: Core web framework and MCP packages

**Documentation:**
- `README.md` - Rewritten for Dataverse MCP server

### 📝 Files Kept Unchanged

**Routers (Minimal Set):**
- `server/routers/health.py` - Health check endpoint
- `server/routers/mcp_info.py` - MCP metadata endpoint
- `server/routers/user.py` - User info endpoint

**Configuration:**
- `watch.sh` - Development server script
- `fix.sh` - Code formatting script
- `config.yaml` - MCP server configuration

**Frontend (For Future):**
- `client/` - React TypeScript frontend (unchanged, to be updated later)

**Project Files:**
- `LICENSE.md` - License
- `SECURITY.md` - Security policy
- `NOTICE.md` - Third-party notices
- `CODEOWNERS.txt` - Code ownership
- `.gitignore` - Git ignore rules

---

## Architecture Changes

### Before (API Registry)

```
Databricks API Registry MCP Server
├── Manages external API endpoints
├── Stores API metadata in Databricks Delta tables
├── Unity Catalog HTTP connections for API auth
├── Agent-based chat interface
├── Traces for debugging
└── Deployed as Databricks App
```

### After (Dataverse)

```
Dataverse MCP Server
├── Connects to Microsoft Dataverse
├── OAuth service principal authentication
├── Exposes Dataverse tables as MCP tools
├── No local persistence (stateless proxy)
├── Minimal routers (health, mcp_info, user)
└── Can run locally or on Databricks Apps
```

---

## Dependency Changes

### Before

- databricks-sdk
- databricks-connect
- mlflow[databricks]
- pandas
- rich
- click
- httpx
- python-multipart
- websockets

### After

- requests (for Dataverse API)
- python-dotenv (for config)
- pyyaml (for config)
- fastapi + uvicorn (web framework)
- fastmcp + mcp (MCP protocol)

**Size Reduction:** ~15 dependencies → ~8 dependencies

---

## Environment Variables

### Before (Databricks)

```bash
DATABRICKS_HOST=...
DATABRICKS_TOKEN=...
DATABRICKS_SQL_WAREHOUSE_ID=...
MCP_API_KEY_SCOPE=...
MCP_BEARER_TOKEN_SCOPE=...
```

### After (Dataverse)

```bash
DATAVERSE_HOST=...
DATAVERSE_TENANT_ID=...
DATAVERSE_CLIENT_ID=...
DATAVERSE_CLIENT_SECRET=...
SERVERNAME=dataverse-mcp-server
```

---

## MCP Tools Comparison

### Before (API Registry)

- `register_api` - Register external APIs
- `execute_api_call` - Call registered APIs
- `check_api_http_registry` - List registered APIs
- `smart_register_with_connection` - Smart API discovery
- `execute_dbsql` - Run SQL queries
- `list_warehouses` - List SQL warehouses
- `list_http_connections` - List UC connections
- `health` - Health check

### After (Dataverse)

- `list_tables` - List Dataverse tables
- `describe_table` - Get table schema
- `read_query` - Query records
- `create_record` - Create records
- `update_record` - Update records
- `health` - Health check
- **Stubs:** list_knowledge_sources, retrieve_knowledge, list_prompts, execute_prompt

---

## Testing

### Before

```bash
./test_api_registry.sh
databricks apps logs <app-name>
```

### After

```bash
python test_dataverse.py
# Connection tests, no Databricks required
```

---

## Deployment

### Before

```bash
./setup.sh          # Configure Databricks
./deploy.sh         # Deploy to Databricks Apps
./app_status.sh     # Check status
```

### After

```bash
./setup_dataverse.sh    # Configure Dataverse credentials
./watch.sh              # Run locally
# Or: Can still deploy to Databricks Apps if needed (future)
```

---

## What Was Preserved

### 1. **MCP Architecture**
   - FastMCP framework
   - HTTP endpoint at `/mcp`
   - Tool-based interface
   - OpenAPI docs at `/docs`

### 2. **FastAPI Structure**
   - App initialization
   - CORS middleware
   - Router system
   - Static file serving (for frontend)

### 3. **Development Workflow**
   - `watch.sh` for hot reload
   - `fix.sh` for formatting
   - Ruff configuration
   - TypeScript frontend structure

### 4. **Documentation Standards**
   - Comprehensive README
   - Setup guides
   - Troubleshooting sections
   - Code examples

---

## Migration Checklist

If you need to switch back or run both servers:

- [ ] Keep separate `.env.local` files
- [ ] Use different server names in `config.yaml`
- [ ] Run on different ports if both are active
- [ ] Update MCP client configs (Claude, VS Code) accordingly

---

## Next Steps

### Immediate (Phase 1 Complete)
- ✅ Core Dataverse tools implemented
- ✅ Authentication working
- ✅ Documentation complete
- ✅ Tests passing

### Future (Phase 2)
- [ ] Implement `delete_record`
- [ ] Add table management tools
- [ ] Integrate Copilot Studio knowledge sources
- [ ] Add custom prompts execution
- [ ] Update React frontend for Dataverse
- [ ] Add batch operations
- [ ] Implement On-Behalf-Of authentication

---

## Questions?

- **Setup Issues:** See [DATAVERSE_SETUP.md](DATAVERSE_SETUP.md)
- **Quick Start:** See [DATAVERSE_QUICKSTART.md](DATAVERSE_QUICKSTART.md)
- **Full Reference:** See [README_DATAVERSE.md](README_DATAVERSE.md)

---

**Migration completed:** 2025-01-08

