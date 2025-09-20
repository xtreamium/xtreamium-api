from typing import List

from pydantic import ConfigDict

from app.schemas.base import _BaseSchema
from app.schemas.server import Server


class _UserBase(_BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    email: str


class User(_UserBase):
    servers: List[Server] = []
    id: str  # Changed from int to str to match UUID


class UserCreate(_UserBase):
    password: str
