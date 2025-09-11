from fastapi_utils.tasks import repeat_every

from app.services.logger import get_logger
from app.utils.epg_parser import epg_parser

logger = get_logger(__name__)


async def update_epg_task() -> None:
    logger.debug("Caching EPG task started")
    epg_parser.cache_epg()
    logger.debug("Caching EPG task ended")
