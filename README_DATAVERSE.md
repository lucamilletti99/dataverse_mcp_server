# 🔌 Dataverse MCP Server

A Model Context Protocol (MCP) server for Microsoft Dataverse, allowing AI assistants like Claude to interact with your Dataverse data through natural language.

## What is This?

This MCP server exposes Microsoft Dataverse tables and records through the [Model Context Protocol](https://modelcontextprotocol.io/), enabling AI assistants to:

- 📊 **Discover tables** - List and explore Dataverse entities
- 🔍 **Query data** - Read records with OData filters
- ✏️ **Create records** - Insert new data into tables
- 🔄 **Update records** - Modify existing records
- 🤖 **Natural language interface** - Use conversational queries with Claude or other MCP clients

Based on the [Microsoft Dataverse MCP specification](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/data-platform-mcp).

---

## Quick Start (5 Minutes)

### Prerequisites

- Python 3.11+
- Microsoft Dataverse environment
- Azure AD app registration with Dataverse API permissions

### Installation

```bash
# 1. Clone repository (if not already cloned)
git clone <your-repo-url>
cd dataverse_mcp_server

# 2. Install dependencies
pip install fastapi uvicorn requests python-dotenv fastmcp

# 3. Configure credentials
./setup_dataverse.sh
# OR manually: cp env.example .env.local and edit

# 4. Test connection
python test_dataverse.py

# 5. Start server
./watch.sh
```

**Server will be running at:**
- MCP Endpoint: `http://localhost:8000/mcp`
- API Docs: `http://localhost:8000/docs`

📖 **Detailed Guide:** [DATAVERSE_QUICKSTART.md](DATAVERSE_QUICKSTART.md)

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  MCP Clients                        │
│  (Claude Desktop, VS Code, Custom Apps)             │
└─────────────────────────────────────────────────────┘
                        │
                        │ HTTP/MCP Protocol
                        ▼
┌─────────────────────────────────────────────────────┐
│           Dataverse MCP Server (FastAPI)            │
│  ┌───────────────────────────────────────────────┐  │
│  │  MCP Tools (Phase 1)                          │  │
│  │  • list_tables                                │  │
│  │  • describe_table                             │  │
│  │  • read_query                                 │  │
│  │  • create_record                              │  │
│  │  • update_record                              │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │  Dataverse Client                             │  │
│  │  • OAuth Authentication (Service Principal)   │  │
│  │  • Web API v9.2 Client                        │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                        │
                        │ HTTPS/OAuth
                        ▼
┌─────────────────────────────────────────────────────┐
│      Microsoft Dataverse Environment                │
│      (https://org.api.crm.dynamics.com)             │
└─────────────────────────────────────────────────────┘
```

---

## Features

### ✅ Phase 1 (Implemented)

| Feature | Status | Description |
|---------|--------|-------------|
| **Authentication** | ✅ | OAuth 2.0 service principal (M2M) |
| **list_tables** | ✅ | List all Dataverse tables with metadata |
| **describe_table** | ✅ | Get complete table schema and column definitions |
| **read_query** | ✅ | Query records with OData filters, sorting, and column selection |
| **create_record** | ✅ | Insert new records into tables |
| **update_record** | ✅ | Update existing records by GUID |
| **Health Check** | ✅ | Server and connection health monitoring |

### 🚧 Phase 2 (Planned)

| Feature | Status | Description |
|---------|--------|-------------|
| **delete_record** | 🚧 | Delete records from tables |
| **Table Management** | 🚧 | Create, update, delete table definitions |
| **Knowledge Sources** | 🚧 | Integration with Copilot Studio knowledge sources |
| **Custom Prompts** | 🚧 | Execute predefined Dataverse prompts |
| **Batch Operations** | 🚧 | Bulk create/update/delete |
| **On-Behalf-Of Auth** | 🚧 | User-level authentication (OBO flow) |

---

## MCP Tools Reference

### `health()`

Check server and Dataverse connection status.

```python
health()
# Returns: { "status": "healthy", "connection_healthy": true, ... }
```

---

### `list_tables(filter_query, top, custom_only)`

List all tables (entities) in Dataverse.

**Parameters:**
- `filter_query` (str, optional): OData filter (e.g., `"IsActivity eq false"`)
- `top` (int, default=100): Max tables to return
- `custom_only` (bool, default=false): Only show custom tables

**Example:**
```python
list_tables(top=10)
list_tables(custom_only=True)
list_tables(filter_query="IsCustomEntity eq true")
```

---

### `describe_table(table_name)`

Get detailed metadata for a table including all columns and their types.

**Parameters:**
- `table_name` (str, required): Logical name (e.g., `"account"`, `"contact"`)

**Example:**
```python
describe_table("account")
# Returns: Schema with all attributes, types, and metadata
```

---

### `read_query(table_name, select, filter_query, order_by, top)`

Query records from a table using OData syntax.

**Parameters:**
- `table_name` (str, required): Logical name
- `select` (list[str], optional): Columns to return
- `filter_query` (str, optional): OData filter expression
- `order_by` (str, optional): Sort expression
- `top` (int, default=100): Max records to return

**Examples:**
```python
# Get all accounts
read_query("account", top=10)

# Get specific columns
read_query("account", select=["name", "revenue"])

# Filter by condition
read_query("account", filter_query="revenue gt 1000000")

# Sort results
read_query("contact", order_by="fullname asc")
```

**OData Filter Examples:**
- `"name eq 'Contoso'"` - Exact match
- `"revenue gt 1000000"` - Greater than
- `"createdon gt 2024-01-01"` - Date comparison
- `"name startswith 'A'"` - String starts with
- `"contains(name, 'tech')"` - String contains

---

### `create_record(table_name, data)`

Create a new record in a table.

**Parameters:**
- `table_name` (str, required): Logical name
- `data` (dict, required): Record data with column names as keys

**Example:**
```python
create_record("account", {
    "name": "Contoso Ltd",
    "revenue": 5000000,
    "industry": "Technology"
})
# Returns: { "success": true, "entity_id": "guid..." }
```

---

### `update_record(table_name, record_id, data)`

Update an existing record.

**Parameters:**
- `table_name` (str, required): Logical name
- `record_id` (str, required): GUID of record to update
- `data` (dict, required): Fields to update

**Example:**
```python
update_record("account", "12345678-1234-1234-1234-123456789abc", {
    "revenue": 6000000,
    "industry": "Software"
})
# Returns: { "success": true, "record_id": "guid..." }
```

---

## Configuration

### Environment Variables

Create `.env.local` with these required variables:

```bash
# Dataverse Environment URL (required)
DATAVERSE_HOST=https://org1bfe9c69.api.crm.dynamics.com

# Azure AD Credentials (required)
DATAVERSE_TENANT_ID=your-tenant-id-guid
DATAVERSE_CLIENT_ID=your-client-id-guid
DATAVERSE_CLIENT_SECRET=your-client-secret-value

# Optional: Server name
SERVERNAME=dataverse-mcp-server
```

### Azure AD App Setup

Your app registration needs:

1. **API Permissions:**
   - Dynamics CRM → `user_impersonation`
   - Admin consent granted

2. **Application User in Dataverse:**
   - Created in Power Platform Admin Center
   - Assigned security role (e.g., System Administrator)

📖 **Full Setup Guide:** [DATAVERSE_SETUP.md](DATAVERSE_SETUP.md)

---

## Usage Examples

### From Claude Desktop

1. **Configure Claude:**

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "dataverse": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

2. **Use in Claude:**

```
You: "List all tables in my Dataverse environment"
Claude: [Calls list_tables tool]

You: "Show me the top 10 accounts sorted by revenue"
Claude: [Calls read_query with appropriate filters]

You: "Create a new account called 'Fabrikam' with $2M revenue"
Claude: [Calls create_record]
```

---

### From Python (Direct API)

```python
import requests

# Call MCP tool via HTTP
response = requests.post('http://localhost:8000/mcp/call-tool', json={
    "name": "list_tables",
    "arguments": {
        "top": 10,
        "custom_only": True
    }
})

print(response.json())
```

---

### From cURL

```bash
# List tables
curl -X POST http://localhost:8000/mcp/call-tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "list_tables",
    "arguments": {"top": 20}
  }'

# Query accounts
curl -X POST http://localhost:8000/mcp/call-tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "read_query",
    "arguments": {
      "table_name": "account",
      "select": ["name", "revenue"],
      "top": 10
    }
  }'
```

---

## Deployment

### Local Development

```bash
./watch.sh
# Server runs on http://localhost:8000
```

### Databricks Apps (Optional)

The server can be deployed to Databricks Apps using the existing infrastructure:

```bash
# Deploy to Databricks
./deploy.sh --create --app-name dataverse-mcp-prod

# Check status
./app_status.sh
```

The app works as a **stateless proxy** - no local persistence required.

---

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **401 Authentication Error** | Check client secret hasn't expired; verify API permissions |
| **403 Permission Denied** | Assign security role to app user in Power Platform Admin Center |
| **Table Not Found** | Use `list_tables()` to find correct logical name |
| **Connection Timeout** | Verify `DATAVERSE_HOST` is correct; check firewall settings |

📖 **Full Troubleshooting:** [DATAVERSE_SETUP.md](DATAVERSE_SETUP.md#troubleshooting)

---

## Project Structure

```
dataverse_mcp_server/
├── server/
│   ├── app.py                   # FastAPI + MCP server
│   ├── dataverse_tools.py       # MCP tool implementations
│   ├── dataverse/
│   │   ├── auth.py             # OAuth authentication
│   │   ├── client.py           # Dataverse Web API client
│   │   └── __init__.py
│   └── routers/                # FastAPI REST endpoints
├── test_dataverse.py           # Connection test script
├── setup_dataverse.sh          # Interactive setup
├── env.example                 # Environment template
├── config.yaml                 # MCP server config
├── DATAVERSE_QUICKSTART.md     # 5-minute guide
├── DATAVERSE_SETUP.md          # Detailed setup guide
└── README_DATAVERSE.md         # This file
```

---

## Development

### Running Tests

```bash
# Test Dataverse connection
python test_dataverse.py

# Run linter
ruff check server/

# Format code
ruff format server/
```

### Adding New Tools

1. Add tool implementation to `server/dataverse_tools.py`
2. Use `@mcp_server.tool` decorator
3. Add comprehensive docstring
4. Test with `test_dataverse.py`

---

## Reference Links

- [Dataverse Web API Documentation](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/overview)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Microsoft Dataverse MCP](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/data-platform-mcp)
- [Authenticate with Dataverse](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/authenticate-oauth)
- [OData Query Options](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/query-data-web-api)

---

## Contributing

Contributions welcome! Areas for improvement:

- [ ] Implement Phase 2 features (delete, batch operations)
- [ ] Add more comprehensive error handling
- [ ] Implement request caching
- [ ] Add more OData query examples
- [ ] Improve documentation

---

## License

See [LICENSE.md](LICENSE.md)

---

## Support

- **Issues:** Open a GitHub issue
- **Questions:** See [DATAVERSE_SETUP.md](DATAVERSE_SETUP.md)
- **Security:** Report vulnerabilities via [SECURITY.md](SECURITY.md)

---

**Built with ❤️ for the Dataverse and MCP communities**

