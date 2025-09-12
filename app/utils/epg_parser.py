import os
import time
import sqlalchemy.orm as orm

import requests
from xdg_base_dirs import xdg_cache_home

from app.services.logger import get_logger
from app.utils.iptv_parser_ng import parse_xmltv_file
from app.utils.time_utils import is_file_older_cache_time
from app.services.data.epg_data_services import store_epg_channels, get_programmes_for_channel

logger = get_logger(__name__)


class EPGParser:
  def __init__(self, url, server_id, user_id):
    self._epg_url = url
    self._server_id = server_id
    self._user_id = user_id
    cache_dir = (os.getenv("CACHE_PATH") or
                 os.path.join(xdg_cache_home(), "xtreamium"))

    self._cache_file = os.path.join(
      cache_dir, f"{user_id}", str(server_id), "epg.xml")

    # Create the full directory path for the cache file if it doesn't exist
    cache_file_dir = os.path.dirname(self._cache_file)
    if not os.path.exists(cache_file_dir):
      os.makedirs(cache_file_dir)

  async def cache_epg(self, db: orm.Session):
    """Download, parse and store EPG data in the database"""
    if not os.path.isfile(self._cache_file) or is_file_older_cache_time(self._cache_file):
      logger.debug(
        f"Downloading EPG from {self._epg_url} to {self._cache_file}")
      try:
        data = requests.get(self._epg_url, timeout=30)
        with open(self._cache_file, 'wb') as file:
          file.write(data.content)
      except Exception as e:
        logger.error(
          f"Failed to download EPG from {self._epg_url}: {e}")
        return

    logger.debug("Parsing EPG")
    try:
      logger.debug(f"Parsing EPG from {self._cache_file}")
      channels = parse_xmltv_file(self._cache_file)

      logger.debug(f"Parsed {len(channels)} channels")

      # Store in database using the new EPG data service
      result = await store_epg_channels(channels, self._user_id, self._server_id, db)
      
      logger.info(
        f"EPG data stored in database for user {self._user_id}, server {self._server_id}: "
        f"{result['channels']} channels, {result['programmes']} programmes")

    except Exception as e:
      logger.error(f"Failed to parse EPG: {e}")

  async def get_listings(self, channel_id: str, db: orm.Session):
    """Get current and future listings for a channel from the database"""
    from app.services.data.epg_data_services import get_channel_by_xmltv_id, get_programmes_for_channel
    
    # First find the channel by XMLTV ID
    channel = await get_channel_by_xmltv_id(self._user_id, self._server_id, channel_id, db)
    if not channel:
      logger.warning(f"Channel {channel_id} not found for user {self._user_id}, server {self._server_id}")
      return []
    
    # Get programmes for this channel
    programmes = await get_programmes_for_channel(channel.id, db)
    logger.debug(f"Found {len(programmes)} programmes for channel {channel_id}")
    
    return programmes
