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


@router.post("/login")
async def login(
    form_data: security.OAuth2PasswordRequestForm = fastapi.Depends(),
    db: orm.Session = fastapi.Depends(get_db),
):
    """Authenticate user and return access token."""
    logger.info(f"POST /auth/login - Authentication attempt for user: {form_data.username}")
    try:
        user = await services.authenticate_user(form_data.username, form_data.password, db)

        if not user:
            logger.warning(f"Authentication failed for user: {form_data.username}")
            raise fastapi.HTTPException(status_code=400, detail="Invalid Credentials")

        logger.info(f"Authentication successful for user: {form_data.username}")
        token = await services.create_token(user)
        logger.debug(f"Token generated for authenticated user: {form_data.username}")
        return token
    except Exception as e:
        logger.error(f"Login failed for user {form_data.username}: {e}")
        raise


@router.post("/register", status_code=201)
async def register(
    user: schema.UserCreate, db: orm.Session = fastapi.Depends(get_db)
):
    """Register a new user account."""
    logger.info(f"POST /auth/register - Registering new user with email: {user.email}")
    try:
        db_user = await services.get_user_by_email(user.email, db)
        if db_user:
            logger.warning(f"User registration failed - email already in use: {user.email}")
            raise fastapi.HTTPException(status_code=400, detail="Email already in use")

        created_user = await services.create_user(user, db)
        logger.info(f"User registered successfully: {created_user.email}")

        token = await services.create_token(created_user)
        logger.debug(f"Token generated for new registered user: {created_user.email}")
        return {"access_token": token["access_token"], "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Failed to register user {user.email}: {e}")
        raise