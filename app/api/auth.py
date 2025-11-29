import fastapi
import fastapi.security as security
import sqlalchemy.orm as orm
from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas import user as schema
from app.services.data import user_data_services as services
from app.services.db_factory import get_db
from app.services.logger import get_logger
from app.services.google_oauth import google_oauth_service

logger = get_logger(__name__)
router = APIRouter()


class GoogleAuthRequest(BaseModel):
    """Request model for Google OAuth authentication."""
    id_token: str


class GoogleAuthCodeRequest(BaseModel):
    """Request model for Google OAuth code exchange."""
    code: str


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


@router.post("/google/token")
async def google_auth_id_token(
    auth_request: GoogleAuthRequest,
    db: orm.Session = fastapi.Depends(get_db),
):
    """Authenticate user with Google ID token."""
    logger.info("POST /auth/google/token - Google authentication with ID token")
    try:
        # Verify the Google ID token
        user_info = await google_oauth_service.verify_id_token(auth_request.id_token)

        email = user_info.get("email")
        google_id = user_info.get("sub")

        if not email or not google_id:
            logger.warning("Google token missing required fields")
            raise fastapi.HTTPException(status_code=400, detail="Invalid Google token")

        # Get or create user
        user = await services.get_or_create_oauth_user(email, "google", google_id, db)

        # Create JWT token for our application
        token = await services.create_token(user)
        logger.info(f"Google authentication successful for user: {email}")

        return {"access_token": token["access_token"], "token_type": "bearer"}

    except ValueError as e:
        logger.error(f"Google token verification failed: {e}")
        raise fastapi.HTTPException(status_code=401, detail="Invalid Google token")
    except Exception as e:
        logger.error(f"Google authentication failed: {e}")
        raise


@router.post("/google/code")
async def google_auth_code(
    auth_request: GoogleAuthCodeRequest,
    db: orm.Session = fastapi.Depends(get_db),
):
    """Authenticate user with Google authorization code."""
    logger.info("POST /auth/google/code - Google authentication with authorization code")
    try:
        # Exchange code for tokens
        token_data = await google_oauth_service.exchange_code_for_token(auth_request.code)

        # Get user info using access token
        user_info = await google_oauth_service.get_user_info(token_data["access_token"])

        email = user_info.get("email")
        google_id = user_info.get("id")

        if not email or not google_id:
            logger.warning("Google user info missing required fields")
            raise fastapi.HTTPException(status_code=400, detail="Invalid Google user info")

        # Get or create user
        user = await services.get_or_create_oauth_user(email, "google", google_id, db)

        # Create JWT token for our application
        token = await services.create_token(user)
        logger.info(f"Google authentication successful for user: {email}")

        return {"access_token": token["access_token"], "token_type": "bearer"}

    except Exception as e:
        logger.error(f"Google code authentication failed: {e}")
        raise fastapi.HTTPException(status_code=401, detail="Google authentication failed")