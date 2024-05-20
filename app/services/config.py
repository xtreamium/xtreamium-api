from typing import List

from pydantic import AnyHttpUrl
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
  PROJECT_NAME: str = "Xtreamium Backend"
  API_PATH: str = "/api/v1"
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
