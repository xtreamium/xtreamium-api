from fastapi import APIRouter, Request

from app.services.config import settings
from app.utils.XTream import XTream
from app.utils.epg_parser import epg_parser

router = APIRouter()


def __get_provider(request: Request):
  return XTream(
    request.headers.get("x-xtream-server"),
    request.headers.get("x-xtream-username"),
    request.headers.get("x-xtream-password"),
  )


@router.get("/categories")
def get_categories(request: Request):
  provider = __get_provider(request)
  categories = provider.get_categories()
  return categories.json()


@router.get("/channels/{category_id}")
async def get_channels(category_id, request: Request):
  provider = __get_provider(request)
  channels = provider.get_channels(category_id)
  return channels.json()


@router.get("/listing/{channel_id}")
async def get_channel_listing_from_epg(channel_id, request: Request):
  listings = epg_parser.get_listings(channel_id)
  return sorted(listings, key=lambda l: l['start'])


@router.get("/channel/url/{program_id}")
async def get_live_stream(program_id: str, request: Request):
  provider = __get_provider(request)
  url = provider.get_live_stream_url(program_id)
  return {
    "url": url
  }
