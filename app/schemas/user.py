import datetime as dt
import pydantic as pydantic


class _UserBase(pydantic.BaseModel):
  email: str

  class Config:
    from_attributes = True


class UserCreate(_UserBase):
  hashed_password: str

  class Config:
    orm_mode = True


class User(_UserBase):
  id: int

  class Config:
    orm_mode = True
