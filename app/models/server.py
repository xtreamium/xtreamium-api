import datetime as dt

import sqlalchemy as sa
from sqlalchemy import orm as orm

from app import database


class Server(database.Base):
  class Config:
    from_attributes = True

  __tablename__ = "servers"
  id = sa.Column(sa.Integer, primary_key=True, index=True)
  owner_id = sa.Column(sa.String(36), sa.ForeignKey("users.id"), nullable=False)
  name = sa.Column(sa.String, unique=True, index=True)
  url = sa.Column(sa.String, index=True)
  username = sa.Column(sa.String, index=True)
  password = sa.Column(sa.String, index=True)
  epg_url = sa.Column(sa.String, index=True)

  owner = orm.relationship("User", back_populates="servers")

  date_created = sa.Column(sa.DateTime, default=dt.datetime.now(dt.timezone.utc))
  date_last_updated = sa.Column(sa.DateTime, default=dt.datetime.now(dt.timezone.utc))
