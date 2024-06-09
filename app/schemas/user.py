import datetime as dt
from typing import List

import pydantic as pydantic
from pydantic import ConfigDict

from app.schemas.base import _BaseSchema
from app.schemas.server import Server


class _UserBase(_BaseSchema):
  model_config = ConfigDict(from_attributes=True)

  email: str


class User(_UserBase):
  servers: List[Server] = []

  class Config:
    orm_mode = True


class UserCreate(_UserBase):
  hashed_password: str

  class Config:
    orm_mode = True


class ServerCreate(pydantic.BaseModel):
  owner_id: int
  name: str
  url: str
  username: str
  password: str
  epg_url: str
