from app.schemas.base import _BaseSchema


class _ServerBase(_BaseSchema):
    name: str
    url: str
    username: str
    password: str
    epg_url: str


class ServerCreate(_ServerBase):
    pass


class ServerUpdate(_BaseSchema):
    name: str | None = None
    url: str | None = None
    username: str | None = None
    password: str | None = None
    epg_url: str | None = None


class Server(_ServerBase):
    id: str
    owner_id: str
