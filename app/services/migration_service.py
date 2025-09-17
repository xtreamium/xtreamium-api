import os
from alembic import command
from alembic.config import Config
from app.services.logger import get_logger

logger = get_logger(__name__)


def run_migrations():
    """Run database migrations using Alembic"""
    try:
        logger.info("Running database migrations...")

        # Get the project root directory (where alembic.ini is located)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        alembic_cfg_path = os.path.join(project_root, "alembic.ini")

        # Create Alembic configuration
        alembic_cfg = Config(alembic_cfg_path)

        # Run migrations to head
        command.upgrade(alembic_cfg, "head")

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
