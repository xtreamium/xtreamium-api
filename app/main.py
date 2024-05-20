import os

from app.services.app_factory import create_app
from app.services.config import settings
from app.utils.epg import EPGParser

app = create_app()


@app.on_event("startup")
def startup_stuff():
  epg = EPGParser(settings.EPG_URL)
  epg.cache_epg()


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
