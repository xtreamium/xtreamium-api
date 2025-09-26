from app import database
from app.services.initial_setup import check_and_create_initial_user
from app.services.logger import get_logger
from app.services.migration_service import run_migrations

logger = get_logger(__name__)


def create_database():
    """Initialize database using Alembic migrations"""
    logger.info("Initializing database with migrations...")
    try:
        run_migrations()
        logger.info("Database initialized successfully")
        
        # Check for initial user creation after migrations
        logger.info("Checking for initial user setup...")
        db = database.SessionLocal()
        try:
            check_and_create_initial_user(db)
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_db():
    logger.debug("Creating database session")
    db = database.SessionLocal()
    try:
        yield db
    finally:
        logger.debug("Closing database session")
        db.close()
