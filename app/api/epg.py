from fastapi import APIRouter, Request

from app.utils.XTream import XTream

router = APIRouter()


def __get_provider(request: Request):
  return XTream(
    request.headers.get("x-xtream-server"),
    request.headers.get("x-xtream-username"),
    request.headers.get("x-xtream-password"),
  )


@router.get("/channels")
def epg(request: Request):
  provider = __get_provider(request)
  categories = provider.get_categories()
  return categories.json()


@router.get("/channel/{channel_id}")
async def get_channel_epg(channel_id, request: Request):
  provider = __get_provider(request)
  channels = provider.get_streams_for_category(channel_id)
  return channels.json()


@router.get("/channel/url/{program_id}")
async def get_live_stream(program_id: str, request: Request):
  provider = __get_provider(request)
  url = provider.get_live_stream_url(program_id)
  return {
    "url": url
  }
