from app import database
from app.models import user, server


def create_database():
  database.Base.metadata.create_all(bind=database.engine)


def get_db():
  db = database.SessionLocal()
  try:
    yield db
  finally:
    db.close()
