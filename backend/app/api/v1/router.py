from fastapi import APIRouter
from app.api.v1.endpoints import agents, resources, costs, incidents, dashboard

api_router = APIRouter()

api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(resources.router, prefix="/resources", tags=["resources"])
api_router.include_router(costs.router, prefix="/costs", tags=["costs"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])