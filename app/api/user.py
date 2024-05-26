import fastapi
from fastapi import APIRouter
import sqlalchemy.orm as orm
from app.schemas import user as schema
from app.services.data.user_data_services import (
  get_user_by_email,
  create_user,
  create_token
)
from app.services.db_factory import get_db

router = APIRouter()


@router.post("/")
async def user_create(
  user: schema.UserCreate, db: orm.Session = fastapi.Depends(get_db)
):
  db_user = await get_user_by_email(user.email, db)
  if db_user:
    raise fastapi.HTTPException(status_code=400, detail="Email already in use")

  user = await create_user(user, db)

  return await create_token(user)
