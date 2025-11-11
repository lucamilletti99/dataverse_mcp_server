"""FastAPI application for Databricks App Template."""

import os
from pathlib import Path

import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastmcp import FastMCP

from server.routers import router
from server.dataverse_tools import load_dataverse_tools

# Optional: Load Dataverse config from Python file (for local dev)
# When running in Databricks Apps, credentials are loaded from Databricks Secrets
try:
    from dataverse_config import apply_dataverse_config
    apply_dataverse_config()
    print("ℹ️  Loaded configuration from dataverse_config.py")
except ImportError:
    # dataverse_config.py not found - this is fine
    # Credentials will be loaded from:
    # 1. .env.local (local dev)
    # 2. Databricks Secrets scope 'dataverse' (production)
    pass


# Load environment variables from .env.local if it exists
def load_env_file(filepath: str) -> None:
  """Load environment variables from a file."""
  if Path(filepath).exists():
    with open(filepath) as f:
      for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
          key, _, value = line.partition('=')
          if key and value:
            os.environ[key] = value


# Load .env files
load_env_file('.env')
load_env_file('.env.local')


# Load configuration from config.yaml
def load_config() -> dict:
  """Load configuration from config.yaml."""
  config_path = Path('config.yaml')
  if config_path.exists():
    with open(config_path, 'r') as f:
      return yaml.safe_load(f)
  return {}


config = load_config()
servername = config.get('servername', 'databricks-mcp')

# Create MCP server
mcp_server = FastMCP(name=servername)

# Load Dataverse tools
load_dataverse_tools(mcp_server)

# Create ASGI app from MCP server
# Passing no path automatically hosts this at the /mcp route
mcp_asgi_app = mcp_server.http_app()

# Pass the MCP app's lifespan to FastAPI
app = FastAPI(
  title='Databricks App API',
  description='Modern FastAPI application template for Databricks Apps with React frontend',
  version='0.1.0',
  lifespan=mcp_asgi_app.lifespan,
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=[
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
  ],
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'],
)


# Add request logging middleware
@app.middleware("http")
async def log_requests_middleware(request, call_next):
  """Log all requests for debugging."""
  import time
  from server.request_logger import log_request

  start_time = time.time()
  response = await call_next(request)
  duration_ms = (time.time() - start_time) * 1000

  # Log the request
  log_request(
    method=request.method,
    path=str(request.url.path),
    status_code=response.status_code,
    duration_ms=duration_ms
  )

  return response

app.include_router(router, prefix='/api', tags=['api'])

# ============================================================================
# SERVE STATIC FILES FROM CLIENT BUILD DIRECTORY (MUST BE LAST!)
# ============================================================================
# This static file mount MUST be the last route registered!
# It catches all unmatched requests and serves the React app.
# Any routes added after this will be unreachable!
if os.path.exists('client/build'):
  app.mount('/', StaticFiles(directory='client/build', html=True), name='static')

# Combines both the routes from FastMCP and FastAPI
combined_app = FastAPI(
    title="Combined MCP App",
    routes=[
        *mcp_asgi_app.routes,  # MCP routes
        *app.routes,      # Original API routes
    ],
    lifespan=mcp_asgi_app.lifespan,
)

if __name__ == '__main__':
  import uvicorn

  port = int(os.environ.get('DATABRICKS_APP_PORT', 8000))
  uvicorn.run(combined_app, host='0.0.0.0', port=port)
