import os

from app.services.tasks.register_tasks import register_tasks
from services.app_factory import create_app
from services.db_factory import create_database

create_database()
app = create_app()

register_tasks(app)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        reload=True,
        port=int(os.environ.get('XTREAMIUM_BACKEND_PORT', 8000)),
        ssl_keyfile='/etc/letsencrypt/live/dev.fergl.ie/privkey.pem',
        ssl_certfile='/etc/letsencrypt/live/dev.fergl.ie/fullchain.pem'
    )
