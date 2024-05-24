from fastapi_utils.tasks import repeat_every

from app.services.logger import logger
from app.utils.epg_parser import epg_parser


@repeat_every(seconds=60 * 60)  # every hour
async def update_epg_task() -> None:
  logger.debug("Caching EPG task started")
  epg_parser.cache_epg()
  logger.debug("Caching EPG task ended")
