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
    id: str
    owner_id: str
