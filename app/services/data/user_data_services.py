import fastapi
import fastapi.security as security
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, HashingError
import sqlalchemy.orm as orm

from app.models.server import Server
from app.models.user import User
from app.schemas.server import ServerCreate as ServerCreate, ServerUpdate
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate
from app.services.config import settings
from app.services.db_factory import get_db
from app.services.logger import get_logger

logger = get_logger(__name__)
oauth2schema = security.OAuth2PasswordBearer(tokenUrl="/api/v2/user/token")

# Initialize Argon2 password hasher with secure defaults
ph = PasswordHasher()


async def get_user_by_email(email: str, db: orm.Session):
    logger.debug(f"Looking up user by email: {email}")
    user = db.query(User).filter(User.email == email).first()
    if user:
        logger.debug(f"User found: {email}")
    else:
        logger.debug(f"User not found: {email}")
    return user


async def get_or_create_oauth_user(email: str, oauth_provider: str, oauth_id: str, db: orm.Session):
    """Get existing OAuth user or create a new one."""
    logger.debug(f"Looking up OAuth user: {email} (provider: {oauth_provider})")

    # Try to find user by OAuth provider and ID first
    user = db.query(User).filter(
        User.oauth_provider == oauth_provider,
        User.oauth_id == oauth_id
    ).first()

    if user:
        logger.debug(f"OAuth user found by provider ID: {email}")
        return user

    # Try to find by email (in case user registered with password first)
    user = db.query(User).filter(User.email == email).first()

    if user:
        # Update existing user with OAuth info
        logger.info(f"Linking OAuth provider {oauth_provider} to existing user: {email}")
        user.oauth_provider = oauth_provider
        user.oauth_id = oauth_id
        db.commit()
        db.refresh(user)
        return user

    # Create new OAuth user
    logger.info(f"Creating new OAuth user: {email} (provider: {oauth_provider})")
    new_user = User(
        email=email,
        oauth_provider=oauth_provider,
        oauth_id=oauth_id,
        hashed_password=None  # OAuth users don't have passwords
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"OAuth user created successfully: {email}")
    return new_user


async def get_current_user(
    db: orm.Session = fastapi.Depends(get_db),
    token: str = fastapi.Depends(oauth2schema),
):
    logger.debug("Validating JWT token for current user")
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user = db.query(User).get(payload["id"])

        if not user:
            logger.warning(
                f"Token valid but user not found for ID: {payload['id']}")
            raise fastapi.HTTPException(
                status_code=401, detail="User not found")

        logger.debug(f"Token validated successfully for user: {user.email}")
        return UserSchema.model_validate(user)

    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        raise fastapi.HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        raise fastapi.HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Error validating token: {e}")
        raise fastapi.HTTPException(
            status_code=401, detail="Invalid Email or Password")


async def create_user(user: UserCreate, db: orm.Session):
    logger.info(f"Creating new user in database: {user.email}")
    try:
        hashed_password = ph.hash(user.password)
        db_user = User(email=user.email, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User created successfully in database: {user.email}")
        return db_user
    except HashingError as e:
        logger.error(f"Failed to hash password for user {user.email}: {e}")
        db.rollback()
        raise fastapi.HTTPException(status_code=500, detail="Password hashing failed")
    except Exception as e:
        logger.error(f"Failed to create user in database {user.email}: {e}")
        db.rollback()
        raise


async def authenticate_user(email: str, password: str, db: orm.Session):
    logger.debug(f"Authenticating user: {email}")
    try:
        user = await get_user_by_email(email, db)
        if not user:
            logger.warning(f"Authentication failed - user not found: {email}")
            return False

        try:
            ph.verify(user.hashed_password, password)
            logger.info(f"User authenticated successfully: {email}")
            return user
        except VerifyMismatchError:
            logger.warning(f"Authentication failed - invalid password: {email}")
            return False

    except Exception as e:
        logger.error(f"Error during authentication for {email}: {e}")
        return False


async def create_token(user: User):
    logger.debug(f"Creating JWT token for user: {user.email}")
    try:
        user_obj = UserSchema.model_validate(user)
        token = jwt.encode({"id": user.id}, settings.JWT_SECRET)
        logger.debug(f"JWT token created successfully for user: {user.email}")
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Failed to create token for user {user.email}: {e}")
        raise


async def get_user_servers(user_id: str, db: orm.Session):
    logger.debug(f"Fetching servers for user ID: {user_id}")
    try:
        servers = db.query(Server).filter(Server.owner_id == user_id).all()
        logger.debug(f"Found {len(servers)} servers for user ID: {user_id}")
        return servers
    except Exception as e:
        logger.error(f"Failed to fetch servers for user ID {user_id}: {e}")
        raise


async def create_server(server: ServerCreate, user_id: str, db: orm.Session):
    logger.info(f"Creating server '{server.name}' for user ID: {user_id}")
    try:
        db_server = Server(**server.model_dump(), owner_id=user_id)
        db.add(db_server)
        db.commit()
        db.refresh(db_server)
        logger.info(
            f"Server '{server.name}' created successfully for user ID: {user_id}")
        return db_server
    except Exception as e:
        logger.error(
            f"Failed to create server '{server.name}' for user ID {user_id}: {e}")
        db.rollback()
        raise


async def update_server(server_id: str, user_id: str, data: ServerUpdate, db: orm.Session):
    logger.info(f"Updating server ID: {server_id} for user ID: {user_id}")
    try:
        server = db.query(Server).filter(
            Server.id == server_id,
            Server.owner_id == user_id
        ).first()
        if not server:
            raise fastapi.HTTPException(status_code=404, detail="Server not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(server, field, value)

        import datetime as dt
        server.date_last_updated = dt.datetime.now(dt.timezone.utc)
        db.commit()
        db.refresh(server)
        logger.info(f"Server ID {server_id} updated successfully")
        return server
    except fastapi.HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update server ID {server_id}: {e}")
        db.rollback()
        raise


async def delete_server(server_id: str, db: orm.Session):
    logger.info(f"Deleting server ID: {server_id}")
    try:
        result = db.query(Server).filter(Server.id == server_id).delete()
        db.commit()
        if result:
            logger.info(f"Server ID {server_id} deleted successfully")
        else:
            logger.warning(f"Server ID {server_id} not found for deletion")
    except Exception as e:
        logger.error(f"Failed to delete server ID {server_id}: {e}")
        db.rollback()
        raise


async def get_all_users(db: orm.Session):
    logger.debug("Fetching all users from database")
    try:
        users = db.query(User).all()
        logger.debug(f"Found {len(users)} users in database")
        return users
    except Exception as e:
        logger.error(f"Failed to fetch all users: {e}")
        raise


async def get_user_server_by_id(user_id: str, server_id: str, db: orm.Session):
    """Get a specific server by ID for a user"""
    logger.debug(f"Fetching server {server_id} for user ID: {user_id}")
    try:
        server = db.query(Server).filter(
            Server.id == server_id,
            Server.owner_id == user_id
        ).first()
        if server:
            logger.debug(f"Found server {server.name} for user ID: {user_id}")
        else:
            logger.debug(f"Server {server_id} not found for user ID: {user_id}")
        return server
    except Exception as e:
        logger.error(f"Failed to fetch server {server_id} for user ID {user_id}: {e}")
        raise
