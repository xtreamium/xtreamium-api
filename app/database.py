import os

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy.ext.declarative as declarative

DATABASE_URL = os.environ.get('DATABASE_URL') or "sqlite:///./xtreamium.db"
engine = sa.create_engine(
  DATABASE_URL,
  connect_args={"check_same_thread": False}
)

SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative.declarative_base()
