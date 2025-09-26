import datetime as dt
import uuid

import sqlalchemy as sa
import sqlalchemy.orm as orm

from app import database


class User(database.Base):
    class Config:
        from_attributes = True

    __tablename__ = "users"
    id = sa.Column(sa.String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))

    email = sa.Column(sa.String, unique=True, index=True)
    hashed_password = sa.Column(sa.String)

    servers = orm.relationship("Server", back_populates="owner")
    channels = orm.relationship("Channel", back_populates="user")

    date_created = sa.Column(sa.DateTime, default=dt.datetime.now(dt.timezone.utc))
    date_last_updated = sa.Column(sa.DateTime, default=dt.datetime.now(dt.timezone.utc))
