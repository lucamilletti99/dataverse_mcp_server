# Dataverse MCP Server Routers

from fastapi import APIRouter

from .health import router as health_router
from .mcp_info import router as mcp_info_router
from .user import router as user_router
from .chat import router as chat_router
from .traces import router as traces_router
from .db_resources import router as db_resources_router
from .agent_chat import router as agent_router

router = APIRouter()
router.include_router(health_router, tags=['health'])
router.include_router(mcp_info_router, prefix='/mcp_info', tags=['mcp'])
router.include_router(user_router, prefix='/user', tags=['user'])
router.include_router(chat_router, prefix='/chat', tags=['chat'])
router.include_router(agent_router, prefix='/agent', tags=['agent'])
router.include_router(traces_router, prefix='/traces', tags=['traces'])
router.include_router(db_resources_router, prefix='/db', tags=['database'])
