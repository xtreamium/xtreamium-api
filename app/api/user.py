import fastapi
from fastapi import APIRouter
import fastapi.security as security
import sqlalchemy.orm as orm

from app.schemas import user as schema
from app.schemas import server as server_schema
from app.services.data import user_data_services as services
from app.services.db_factory import get_db
from app.services.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


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


@router.get("/me", response_model=schema.User)
async def get_user(user: schema.User = fastapi.Depends(services.get_current_user)):
  logger.debug(f"GET /user/me - Fetching user profile for: {user.email}")
  return user


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
async def delete_server(server_id,
                        db: orm.Session = fastapi.Depends(get_db)):
  await services.delete_server(server_id, db)
  return {"ok": True}
