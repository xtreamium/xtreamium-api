from fastapi import APIRouter, Request, HTTPException

from app.services.config import settings

router = APIRouter()


@router.get("/")
async def debug_endpoint(request: Request):
    client_ip = request.client.host

    if client_ip != "46.7.158.25" and client_ip != "10.1.1.1":
        raise HTTPException(status_code=403, detail="Access denied")

    return dict(settings)
