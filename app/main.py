import os, sys

# https://github.com/sixfwa/react-fastapi/blob/main/backend/models.py
print(f"path {sys.path}", flush=True)
print(f"executable {sys.executable}", flush=True)

from services.app_factory import create_app
from services.db_factory import create_database
from app.utils.epg_parser import epg_parser

create_database()
app = create_app()


@app.on_event("startup")
def startup_stuff():
  if False:
    epg_parser.cache_epg()


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
