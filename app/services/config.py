from typing import List

from pydantic import AnyHttpUrl
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
  PROJECT_NAME: str = "Xtreamium Backend"
  API_PATH: str = "/api/v1"
  JWT_SECRET: str = "446974df0ad13e965b7b3a169aa82f08d07bf12a9feb3696e25844c0c677720e"
  EPG_URL: AnyHttpUrl = AnyHttpUrl(
    "http://sr71.biz/xmltv.php?username=Juicy5Bus&password=zYhuTE4qte"
  )
  BACKEND_CORS_ORIGINS: List = [
    "https://streams.dev.fergl.ie:3000",
    "https://streams.fergl.ie",
    "http://127.0.0.1:35729",
    "http://localhost:35729",
  ]


settings = Settings()
