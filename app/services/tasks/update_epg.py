from fastapi_utils.tasks import repeat_every

from app.services.config import settings
from app.services.logger import logger
from app.utils.epg import EPGParser


@repeat_every(seconds=60 * 60)  # every hour
async def update_epg_task() -> None:
  epg = EPGParser(settings.EPG_URL)
  logger.debug("Caching EPG task started")
  epg.cache_epg()
  logger.debug("Caching EPG task ended")
