from fastapi import APIRouter

from app.api import ping, epg, user, auth, users

api_router = APIRouter()

api_router.include_router(ping.router, prefix="/ping", tags=["ping"])
api_router.include_router(epg.router, prefix="/epg", tags=["epg"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
