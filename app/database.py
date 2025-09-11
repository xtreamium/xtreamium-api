import os

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy.ext.declarative as declarative

# Get the absolute path to the app directory
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(APP_DIR, "xtreamium.db")

DATABASE_URL = os.environ.get('DATABASE_URL') or f"sqlite:///{DEFAULT_DB_PATH}"
engine = sa.create_engine(
  DATABASE_URL,
  connect_args={"check_same_thread": False}
)

SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative.declarative_base()
