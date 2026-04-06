from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from app.api.v1.router import api_router
from app.core.config import settings
from app.agents.orchestrator import AgentOrchestrator
from app.infrastructure.database import init_db

orchestrator: AgentOrchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global orchestrator
    
    # Startup
    await init_db()
    orchestrator = AgentOrchestrator()
    await orchestrator.start_all_agents()
    
    yield
    
    # Shutdown
    await orchestrator.stop_all_agents()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}

@app.get("/agents/status")
async def get_agent_status():
    """Get status of all agents"""
    if orchestrator:
        return await orchestrator.get_agent_status()
    return {"status": "orchestrator_not_initialized"}