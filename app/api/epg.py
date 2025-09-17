import sqlalchemy.orm as orm
from fastapi import APIRouter, Request, HTTPException, Depends

from app.schemas.user import User
from app.services.data import user_data_services as user_services
from app.services.data.epg_data_services import get_channel_by_xmltv_id
from app.services.data.epg_data_services import get_programmes_for_channel
from app.services.db_factory import get_db
from app.services.logger import get_logger
from app.utils.XTream import XTream

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


@router.get("/listing/{server_id}/{channel_id}")
async def get_channel_listing_from_epg(
    server_id: str,
    channel_id: str,
    request: Request,
    current_user: User = Depends(user_services.get_current_user),
    db: orm.Session = Depends(get_db)
):
    logger.info(f"GET /listing/{server_id}/{channel_id} - Fetching EPG listings for user {current_user.email}")
    try:
        channel = await get_channel_by_xmltv_id(current_user.id, server_id, channel_id, db)

        if not channel:
            logger.warning(f"Channel not found: {channel_id} for user {current_user.email}, server {server_id}")
            raise HTTPException(status_code=404, detail="Channel not found")

        # Get programmes for this channel
        programmes = await get_programmes_for_channel(channel.id, db)

        # Convert to response format
        sorted_listings = []
        for programme in programmes:
            listing = {
                "start": programme.start_time,
                "stop": programme.stop_time,
                "title": programme.get_default_title(),
                "description": programme.get_default_description(),
                "categories": programme.get_categories() or []
            }
            sorted_listings.append(listing)

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
