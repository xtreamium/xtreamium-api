from app import database
from app.models import user, server
from app.services.logger import get_logger

logger = get_logger(__name__)


def create_database():
    logger.info("Creating database tables...")
    try:
        database.Base.metadata.create_all(bind=database.engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


def get_db():
    logger.debug("Creating database session")
    db = database.SessionLocal()
    try:
        yield db
    finally:
        logger.debug("Closing database session")
        db.close()
