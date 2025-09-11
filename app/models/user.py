import datetime as dt

import sqlalchemy as sa
import sqlalchemy.orm as orm
import passlib.hash as passlib_hash

from app import database


class User(database.Base):
  class Config:
    from_attributes = True

  __tablename__ = "users"
  id = sa.Column(sa.Integer, primary_key=True, index=True)
  email = sa.Column(sa.String, unique=True, index=True)
  hashed_password = sa.Column(sa.String)

  servers = orm.relationship("Server", back_populates="owner")

  date_created = sa.Column(sa.DateTime, default=dt.datetime.now(dt.timezone.utc))
  date_last_updated = sa.Column(sa.DateTime, default=dt.datetime.now(dt.timezone.utc))

  def verify_password(self, password: str):
    return passlib_hash.bcrypt.verify(password, self.hashed_password)
