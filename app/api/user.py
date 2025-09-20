import fastapi
import fastapi.security as security
import sqlalchemy.orm as orm
from fastapi import APIRouter

from app.schemas import server as server_schema
from app.schemas import user as schema
from app.services.data import user_data_services as services
from app.services.db_factory import get_db
from app.services.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/")
async def get_current_user_info(
    current_user: schema.User = fastapi.Depends(services.get_current_user)
):
    """Get current authenticated user information."""
    logger.debug(f"GET /user - Fetching current user info for: {current_user.email}")
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "status": "ok"
    }


@router.get("/me")
async def get_user_profile(
    current_user: schema.User = fastapi.Depends(services.get_current_user)
):
    """Get user profile information."""
    logger.debug(f"GET /user/me - Fetching user profile for: {current_user.email}")
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "servers": current_user.servers if hasattr(current_user, 'servers') else []
    }


@router.post("/")
async def create_user(
    user: schema.UserCreate, db: orm.Session = fastapi.Depends(get_db)
):
    logger.info(f"POST /user - Creating new user with email: {user.email}")
    try:
        db_user = await services.get_user_by_email(user.email, db)
        if db_user:
            logger.warning(f"User creation failed - email already in use: {user.email}")
            raise fastapi.HTTPException(status_code=400, detail="Email already in use")

        created_user = await services.create_user(user, db)
        logger.info(f"User created successfully: {created_user.email}")

        token = await services.create_token(created_user)
        logger.debug(f"Token generated for new user: {created_user.email}")
        return token
    except Exception as e:
        logger.error(f"Failed to create user {user.email}: {e}")
        raise


@router.post("/register")
async def register_user(
    user: schema.UserCreate, db: orm.Session = fastapi.Depends(get_db)
):
    """Register a new user account."""
    logger.info(f"POST /user/register - Registering new user with email: {user.email}")
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


@router.post("/token")
async def generate_token(
    form_data: security.OAuth2PasswordRequestForm = fastapi.Depends(),
    db: orm.Session = fastapi.Depends(get_db),
):
    logger.info(f"POST /token - Authentication attempt for user: {form_data.username}")
    try:
        user = await services.authenticate_user(form_data.username, form_data.password, db)

        if not user:
            logger.warning(f"Authentication failed for user: {form_data.username}")
            raise fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

        logger.info(f"Authentication successful for user: {form_data.username}")
        token = await services.create_token(user)
        logger.debug(f"Token generated for authenticated user: {form_data.username}")
        return token
    except Exception as e:
        logger.error(f"Token generation failed for user {form_data.username}: {e}")
        raise


@router.get("/servers", response_model=list[server_schema.Server])
async def get_servers(user: schema.User = fastapi.Depends(services.get_current_user),
                      db: orm.Session = fastapi.Depends(get_db)):
    logger.info(f"GET /user/servers - Fetching servers for user: {user.email}")
    try:
        servers = await services.get_user_servers(user.id, db)
        logger.info(f"Retrieved {len(servers)} servers for user: {user.email}")
        return servers
    except Exception as e:
        logger.error(f"Failed to get servers for user {user.email}: {e}")
        raise


@router.post("/server")
async def add_server(
    server: server_schema.ServerCreate,
    user: schema.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(get_db)
):
    logger.info(f"POST /user/server - Adding server for user: {user.email}")
    try:
        new_server = await services.create_server(server, user.id, db)
        logger.info(f"Server added successfully for user {user.email}: {server.name}")
        return new_server
    except Exception as e:
        logger.error(f"Failed to add server for user {user.email}: {e}")
        raise


@router.delete("/server/{server_id}")
async def delete_server(server_id: str,
                        db: orm.Session = fastapi.Depends(get_db)):
    await services.delete_server(server_id, db)
    return {"ok": True}
