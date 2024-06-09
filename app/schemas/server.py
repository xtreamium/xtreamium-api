import datetime as dt
import pydantic as pydantic
from pydantic import ConfigDict

from app.schemas.base import _BaseSchema


class _ServerBase(_BaseSchema):
  name: str
  url: str
  username: str
  password: str
  epg_url: str


class ServerCreate(_ServerBase):
  pass


class Server(_ServerBase):
  id: int
  owner_id: int
