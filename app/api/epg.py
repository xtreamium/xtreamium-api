from fastapi import APIRouter, Request, HTTPException

from app.services.logger import get_logger
from app.utils.XTream import XTream
from app.utils.epg_parser import epg_parser

logger = get_logger(__name__)
router = APIRouter()


def __get_provider(request: Request):
  server = request.headers.get("x-xtream-server")
  username = request.headers.get("x-xtream-username")
  password = request.headers.get("x-xtream-password")

  logger.debug(f"Creating XTream provider for server: {server}, username: {username}")

  if not all([server, username, password]):
    logger.warning("Missing required headers for XTream provider")
    raise HTTPException(status_code=400, detail="Missing required XTream headers")

  return XTream(server, username, password)


@router.get("/categories")
def get_categories(request: Request):
  logger.info("GET /categories - Fetching channel categories")
  try:
    provider = __get_provider(request)
    categories = provider.get_categories()
    logger.info("Successfully retrieved categories")
    return categories.json()
  except Exception as e:
    logger.error(f"Failed to get categories: {e}")
    raise HTTPException(status_code=500, detail="Failed to retrieve categories")


@router.get("/channels/{category_id}")
async def get_channels(category_id, request: Request):
  logger.info(f"GET /channels/{category_id} - Fetching channels for category")
  try:
    provider = __get_provider(request)
    channels = provider.get_channels(category_id)
    logger.info(f"Successfully retrieved channels for category {category_id}")
    return channels.json()
  except Exception as e:
    logger.error(f"Failed to get channels for category {category_id}: {e}")
    raise HTTPException(status_code=500, detail="Failed to retrieve channels")


@router.get("/listing/{channel_id}")
async def get_channel_listing_from_epg(channel_id, request: Request):
  logger.info(f"GET /listing/{channel_id} - Fetching EPG listings")
  try:
    listings = epg_parser.get_listings(channel_id)
    sorted_listings = sorted(listings, key=lambda l: l['start'])
    logger.info(f"Successfully retrieved {len(sorted_listings)} EPG listings for channel {channel_id}")
    return sorted_listings
  except Exception as e:
    logger.error(f"Failed to get EPG listings for channel {channel_id}: {e}")
    raise HTTPException(status_code=500, detail="Failed to retrieve EPG listings")


@router.get("/channel/url/{program_id}")
async def get_live_stream(program_id: str, request: Request):
  logger.info(f"GET /channel/url/{program_id} - Fetching live stream URL")
  try:
    provider = __get_provider(request)
    url = provider.get_live_stream_url(program_id)
    logger.info(f"Successfully retrieved live stream URL for program {program_id}")
    return {"url": url}
  except Exception as e:
    logger.error(f"Failed to get live stream URL for program {program_id}: {e}")
    raise HTTPException(status_code=500, detail="Failed to retrieve live stream URL")
