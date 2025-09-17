#!/usr/bin/env python3
"""
CLI utility for managing database migrations
"""
import argparse
import sys
import os

# Add the project root to the Python path and ensure our app takes precedence
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Remove any conflicting app modules from sys.modules
modules_to_remove = [k for k in sys.modules.keys() if k.startswith('app') and 'flask' in str(sys.modules[k])]
for module in modules_to_remove:
    del sys.modules[module]

from alembic import command
from alembic.config import Config

# Simple logging for CLI instead of importing app logger to avoid conflicts
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def get_alembic_config():
    """Get Alembic configuration"""
    alembic_cfg_path = os.path.join(project_root, "alembic.ini")
    return Config(alembic_cfg_path)


def upgrade_database(revision="head"):
    """Upgrade database to a specific revision"""
    try:
        logger.info(f"Upgrading database to revision: {revision}")
        alembic_cfg = get_alembic_config()
        command.upgrade(alembic_cfg, revision)
        logger.info("Database upgrade completed successfully")
    except Exception as e:
        logger.error(f"Failed to upgrade database: {e}")
        sys.exit(1)


def downgrade_database(revision):
    """Downgrade database to a specific revision"""
    try:
        logger.info(f"Downgrading database to revision: {revision}")
        alembic_cfg = get_alembic_config()
        command.downgrade(alembic_cfg, revision)
        logger.info("Database downgrade completed successfully")
    except Exception as e:
        logger.error(f"Failed to downgrade database: {e}")
        sys.exit(1)


def create_migration(message, autogenerate=True):
    """Create a new migration"""
    try:
        logger.info(f"Creating new migration: {message}")
        alembic_cfg = get_alembic_config()
        command.revision(alembic_cfg, message=message, autogenerate=autogenerate)
        logger.info("Migration created successfully")
    except Exception as e:
        logger.error(f"Failed to create migration: {e}")
        sys.exit(1)


def show_current_revision():
    """Show current database revision"""
    try:
        alembic_cfg = get_alembic_config()
        command.current(alembic_cfg, verbose=True)
    except Exception as e:
        logger.error(f"Failed to show current revision: {e}")
        sys.exit(1)


def show_migration_history():
    """Show migration history"""
    try:
        alembic_cfg = get_alembic_config()
        command.history(alembic_cfg, verbose=True)
    except Exception as e:
        logger.error(f"Failed to show migration history: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Database migration management")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Upgrade command
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade database")
    upgrade_parser.add_argument("--revision", default="head", help="Target revision (default: head)")

    # Downgrade command
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade database")
    downgrade_parser.add_argument("revision", help="Target revision")

    # Create migration command
    create_parser = subparsers.add_parser("create", help="Create new migration")
    create_parser.add_argument("message", help="Migration message")
    create_parser.add_argument("--no-autogenerate", action="store_true", help="Don't autogenerate migration")

    # Current revision command
    subparsers.add_parser("current", help="Show current revision")

    # History command
    subparsers.add_parser("history", help="Show migration history")

    args = parser.parse_args()

    if args.command == "upgrade":
        upgrade_database(args.revision)
    elif args.command == "downgrade":
        downgrade_database(args.revision)
    elif args.command == "create":
        create_migration(args.message, not args.no_autogenerate)
    elif args.command == "current":
        show_current_revision()
    elif args.command == "history":
        show_migration_history()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
