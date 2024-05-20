from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi_users import fastapi_users, FastAPIUsers
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse

from app.api import api_router
from app.services.config import settings


def create_app():
  description = f"{settings.PROJECT_NAME} API"
  app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_PATH}/openapi.json",
    docs_url="/docs/",
    description=description,
    redoc_url=None,
  )
  setup_routers(app, fastapi_users)
  setup_cors_middleware(app)
  # serve_static_app(app)
  return app


def setup_routers(app: FastAPI, fastapi_users: FastAPIUsers) -> None:
  app.include_router(api_router, prefix=settings.API_PATH)
  use_route_names_as_operation_ids(app)


def setup_cors_middleware(app):
  if settings.BACKEND_CORS_ORIGINS:
    origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
    app.add_middleware(
      CORSMiddleware,
      allow_origins=origins,
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
    )


def use_route_names_as_operation_ids(app: FastAPI) -> None:
  """
  Simplify operation IDs so that generated API clients have simpler function
  names.

  Should be called only after all routes have been added.
  """
  route_names = set()
  for route in app.routes:
    if isinstance(route, APIRoute):
      if route.name in route_names:
        raise Exception("Route function names should be unique")
      route.operation_id = route.name
      route_names.add(route.name)
