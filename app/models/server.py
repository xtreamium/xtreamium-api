import datetime as dt

import sqlalchemy as sa
from sqlalchemy import orm as orm

from app import database


class Server(database.Base):
  __tablename__ = "servers"
  id = sa.Column(sa.Integer, primary_key=True, index=True)
  owner_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
  name = sa.Column(sa.String, unique=True, index=True)
  url = sa.Column(sa.String, unique=True, index=True)
  username = sa.Column(sa.String, unique=True, index=True)
  password = sa.Column(sa.String, unique=True, index=True)
  epg_url = sa.Column(sa.String, unique=True, index=True)

  date_created = sa.Column(sa.DateTime, default=dt.datetime.now(dt.timezone.utc))
  date_last_updated = sa.Column(sa.DateTime, default=dt.datetime.now(dt.timezone.utc))

  owner = orm.relationship("User", back_populates="servers")
