import os
from argon2 import PasswordHasher
from argon2.exceptions import HashingError
import sqlalchemy.orm as orm

from app.models.user import User
from app.services.logger import get_logger

logger = get_logger(__name__)

# Initialize Argon2 password hasher with secure defaults
ph = PasswordHasher()


def check_and_create_initial_user(db: orm.Session):
    """
    Check if this is the first run (no users exist) and create an initial user
    if INITIAL_USER_EMAIL and INITIAL_USER_PASSWORD environment variables are set.
    """
    try:
        # Check if any users exist in the database
        user_count = db.query(User).count()

        if user_count > 0:
            logger.debug("Users already exist in database, skipping initial user creation")
            return

        logger.info("No users found in database, checking for initial user environment variables")

        # Get environment variables
        initial_email = os.environ.get('INITIAL_USER_EMAIL')
        initial_password = os.environ.get('INITIAL_USER_PASSWORD')

        # Check if both environment variables are set
        if not initial_email or not initial_password:
            logger.warning(
                "First time setup detected but INITIAL_USER_EMAIL and/or INITIAL_USER_PASSWORD "
                "environment variables are not set. No initial user will be created. "
                "You can create users manually through the API or set these variables and restart."
            )
            return

        logger.info(f"Creating initial user with email: {initial_email}")

        # Create the initial user directly (avoiding circular imports)
        hashed_password = ph.hash(initial_password)
        db_user = User(email=initial_email, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.info(f"Initial user created successfully with ID: {db_user.id}")

    except HashingError as e:
        logger.error(f"Failed to hash password for initial user: {e}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Failed to create initial user: {e}")
        db.rollback()
        raise
