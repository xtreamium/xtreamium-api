from fastapi_utils.tasks import repeat_every

from app.services.logger import get_logger
from app.services.tasks.update_epg import update_epg_task_wrapper

logger = get_logger(__name__)


def register_tasks(app):
    @app.on_event("startup")
    @repeat_every(seconds=60 * 60 * 24)
    async def _update_epg_task():
        logger.info("Starting scheduled EPG update task")
        try:
            await update_epg_task_wrapper()
            logger.info("EPG update task completed successfully")
        except Exception as e:
            logger.error(f"EPG update task failed: {e}")

    logger.info("Registered EPG update task to run every 24 hours")
