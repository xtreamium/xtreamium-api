import datetime as dt
import pydantic as pydantic


class _ServerBase(pydantic.BaseModel):
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
  date_created: dt.datetime
  date_last_updated: dt.datetime

  class Config:
    orm_mode = True
