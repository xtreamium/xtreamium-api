import fastapi
import sqlalchemy.orm as orm

from app.schemas.user import User
from app.services.data.user_data_services import get_current_user
from app.services.db_factory import get_db
from app.services.tasks.update_epg import update_epg_task

router = fastapi.APIRouter()


@router.post("/trigger-epg-update")
async def trigger_epg_update(
    db: orm.Session = fastapi.Depends(get_db),
    current_user: User = fastapi.Depends(get_current_user)
):
    await update_epg_task(db)
    return {"message": "EPG update task completed successfully"}
