import fastapi
import fastapi.security as security
import sqlalchemy.orm as orm
from fastapi import APIRouter

from app.schemas import user as schema
from app.services.data import user_data_services as services
from app.services.db_factory import get_db
from app.services.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/me")
async def get_current_user_me(
    current_user: schema.User = fastapi.Depends(services.get_current_user)
):
    """Get current user information (alternative endpoint)."""
    logger.debug(f"GET /users/me - Fetching current user info for: {current_user.email}")
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "servers": current_user.servers if hasattr(current_user, 'servers') else []
    }