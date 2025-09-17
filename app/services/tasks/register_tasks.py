from fastapi_utils.tasks import repeat_every

from app.services.tasks.update_epg import update_epg_task_wrapper


def register_tasks(app):
    @app.on_event("startup")
    @repeat_every(seconds=60 * 60 * 24)
    async def _update_epg_task():
        await update_epg_task_wrapper()
