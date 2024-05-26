from fastapi import APIRouter

from app.api import ping, epg, user

api_router = APIRouter()

api_router.include_router(ping.router, prefix="/ping", tags=["ping"])
api_router.include_router(epg.router, prefix="/epg", tags=["epg"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
