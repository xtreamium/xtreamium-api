import fastapi
import sqlalchemy.orm as orm
import jwt
import fastapi.security as security

from app.models.server import Server
from app.models.user import User
from app.schemas.user import User as UserSchema
from app.schemas.server import ServerCreate as ServerCreate
from app.schemas.user import UserCreate
import passlib.hash as passlib_hash

from app.services.config import settings
from app.services.db_factory import get_db

oauth2schema = security.OAuth2PasswordBearer(tokenUrl="/api/v2/user/token")


async def get_user_by_email(email: str, db: orm.Session):
  return db.query(User).filter(User.email == email).first()


async def get_current_user(
  db: orm.Session = fastapi.Depends(get_db),
  token: str = fastapi.Depends(oauth2schema),
):
  try:
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    user = db.query(User).get(payload["id"])

  except Exception as e:
    raise fastapi.HTTPException(
      status_code=401, detail="Invalid Email or Password"
    )

  return UserSchema.from_orm(user)


async def delete_server(server_id: int, db: orm.Session):
  (db.query(Server).filter(Server.id == server_id)
   .delete())
  db.commit()


async def create_server(user_id: int, server: ServerCreate, db: orm.Session):
  server_obj = Server(
    owner_id=user_id,
    name=server.name,
    url=server.url,
    username=server.username,
    password=server.password,
    epg_url=server.epg_url,
  )

  db.add(server_obj)
  db.commit()
  db.refresh(server_obj)
  return server_obj


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

  return dict(access_token=token, token_type="bearer", user=user_obj)


async def authenticate_user(email: str, password: str, db: orm.Session):
  user = await get_user_by_email(db=db, email=email)

  if not user:
    return False

  if not user.verify_password(password):
    return False

  return user


async def get_user_servers(user_id: int, db: orm.Session):
  user = db.query(User).filter(User.id == user_id).first()
  return user.servers
