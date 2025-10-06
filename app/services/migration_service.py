import os
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.services.logger import get_logger

logger = get_logger(__name__)


def run_migrations():
    """Run database migrations using Alembic"""
    try:
        logger.info("Running database migrations...")

        # Get project root and alembic config
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        alembic_cfg_path = os.path.join(project_root, "alembic.ini")

        logger.info(f"Looking for alembic.ini at: {alembic_cfg_path}")

        alembic_cfg = Config(alembic_cfg_path)

        # Check if database has any tables at all
        from app import database

        engine = database.engine
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        if not existing_tables:
            logger.info("Empty database detected, running initial migration...")
        else:
            logger.info(f"Database has {len(existing_tables)} tables, checking for updates...")

        # Run the upgrade without trying to check current revision first
        logger.info("Executing Alembic upgrade to head...")
        command.upgrade(alembic_cfg, "head")

        # Verify tables were created - create a fresh inspector to see the changes
        fresh_inspector = inspect(engine)
        updated_tables = fresh_inspector.get_table_names()
        logger.info(f"After migration: {len(updated_tables)} tables in database")

        if not updated_tables:
            raise Exception("Migration completed but no tables were created!")

        logger.info("Database migrations completed successfully")

    except Exception as e:
        logger.error(f"Failed to run database migrations: {e}")
        raise


def create_initial_migration():
    """Create an initial migration with all current models"""
    try:
        logger.info("Creating initial migration...")

        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        alembic_cfg_path = os.path.join(project_root, "alembic.ini")

        # Create Alembic configuration
        alembic_cfg = Config(alembic_cfg_path)

        # Generate migration
        command.revision(alembic_cfg, autogenerate=True, message="Initial migration")

        logger.info("Initial migration created successfully")

    except Exception as e:
        logger.error(f"Failed to create initial migration: {e}")
        raise
