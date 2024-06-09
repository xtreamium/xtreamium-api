import fastapi
from fastapi import APIRouter
import fastapi.security as security
import sqlalchemy.orm as orm

from app.schemas import user as schema
from app.schemas import server as server_schema
from app.services.data import user_data_services as services
from app.services.db_factory import get_db

router = APIRouter()


@router.post("/")
async def create_user(
  user: schema.UserCreate, db: orm.Session = fastapi.Depends(get_db)
):
  db_user = await services.get_user_by_email(user.email, db)
  if db_user:
    raise fastapi.HTTPException(status_code=400, detail="Email already in use")

  user = await services.create_user(user, db)

  return await services.create_token(user)


@router.post("/server")
async def create_create(
  server: schema.ServerCreate,
  user: schema.User = fastapi.Depends(services.get_current_user),
  db: orm.Session = fastapi.Depends(get_db)
):
  server = await services.create_server(server, db)
  return server

@router.post("/token")
async def generate_token(
  form_data: security.OAuth2PasswordRequestForm = fastapi.Depends(),
  db: orm.Session = fastapi.Depends(get_db),
):
  user = await services.authenticate_user(form_data.username, form_data.password, db)

  if not user:
    raise fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

  return await services.create_token(user)


@router.get("/me", response_model=schema.User)
async def get_user(user: schema.User = fastapi.Depends(services.get_current_user)):
  return user


@router.get("/servers", response_model=list[server_schema.Server])
async def get_servers(user: schema.User = fastapi.Depends(services.get_current_user),
                      db: orm.Session = fastapi.Depends(get_db)):
  return await services.get_user_servers(user.id, db)
