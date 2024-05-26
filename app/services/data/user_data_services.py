import sqlalchemy.orm as orm
import jwt

from app.models.user import User
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate
import passlib.hash as passlib_hash

from app.services.config import settings


async def get_user_by_email(email: str, db: orm.Session):
  return db.query(User).filter(User.email == email).first()


async def create_user(user: UserCreate, db: orm.Session):
  user_obj = User(
    email=user.email, hashed_password=passlib_hash.bcrypt.hash(user.hashed_password)
  )
  db.add(user_obj)
  db.commit()
  db.refresh(user_obj)
  return user_obj


async def create_token(user: User):
  user_obj = UserSchema.from_orm(user)

  token = jwt.encode(user_obj.dict(), settings.JWT_SECRET)

  return dict(access_token=token, token_type="bearer")
