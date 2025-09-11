import sqlalchemy.orm as orm

from app.services.data.user_data_services import get_all_users, get_user_servers
from app.services.db_factory import get_db
from app.services.logger import get_logger
from app.utils.epg_parser import EPGParser

logger = get_logger(__name__)


async def update_epg_task(db: orm.Session) -> None:
  logger.debug("Caching EPG task started")

  try:
    users = await get_all_users(db)

    for user in users:
      logger.debug(f"Updating EPG task for user {user.email}")
      servers = await get_user_servers(user.id, db)
      for server in servers:
        epg_parser = EPGParser(server.epg_url, server.name, user.id)
        epg_parser.cache_epg()
  except Exception as e:
    logger.error(f"Error in EPG update task: {e}")
    raise


async def update_epg_task_wrapper() -> None:
  """
  Wrapper function to handle database session for background tasks
  This is needed for background tasks since they don't have access to request context and cannot use dependency injection
  """
  db = next(get_db())
  try:
    await update_epg_task(db)
  finally:
    db.close()
