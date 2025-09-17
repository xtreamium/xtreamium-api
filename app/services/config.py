from typing import List

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Xtreamium Backend"
    API_PATH: str = "/api/v1"
    JWT_SECRET: str = "446974df0ad13e965b7b3a169aa82f08d07bf12a9feb3696e25844c0c677720e"

    BACKEND_CORS_ORIGINS: List = [
        "https://xtreamium.dev.fergl.ie:3000",
        "https://streams.dev.fergl.ie:3000",
        "https://streams.ferg.al",
        "http://127.0.0.1:35729",
        "http://localhost:35729",
    ]


settings = Settings()
