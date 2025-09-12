import os
import time
import sqlalchemy.orm as orm

import requests
from xdg_base_dirs import xdg_cache_home

from app.services.logger import get_logger
from app.services.data.epg_data_services import upsert_epg_data, get_listings_for_channel
from app.utils import xmltv
from app.utils.time_utils import is_file_older_cache_time

logger = get_logger(__name__)


class EPGParser:
  def __init__(self, url, server_id, user_id):
    self._epg_url = url
    self._server_id = server_id
    self._user_id = user_id
    cache_dir = (os.getenv("CACHE_PATH") or
                 os.path.join(xdg_cache_home(), "xtreamium"))

    self._cache_file = os.path.join(cache_dir, f"{user_id}", str(server_id), "epg.xml")

    # Create the full directory path for the cache file if it doesn't exist
    cache_file_dir = os.path.dirname(self._cache_file)
    if not os.path.exists(cache_file_dir):
      os.makedirs(cache_file_dir)

  async def cache_epg(self, db: orm.Session):
    """Download, parse and store EPG data in the database"""
    if not os.path.isfile(self._cache_file) or is_file_older_cache_time(self._cache_file):
      logger.debug(f"Downloading EPG from {self._epg_url} to {self._cache_file}")
      try:
        data = requests.get(self._epg_url, timeout=30)
        with open(self._cache_file, 'wb') as file:
          file.write(data.content)
      except Exception as e:
        logger.error(f"Failed to download EPG from {self._epg_url}: {e}")
        return

    logger.debug("Parsing EPG")
    try:
      logger.debug(f"Parsing EPG from {self._cache_file}")
      with open(self._cache_file, 'r') as file:
        programs = xmltv.read_programmes(file)
      logger.debug(f"Parsed {len(programs)} programs")

      # Store in database
      await upsert_epg_data(self._user_id, self._server_id, programs, db)
      logger.info(f"EPG data stored in database for user {self._user_id}, server {self._server_id}")

    except Exception as e:
      logger.error(f"Failed to parse EPG: {e}")

  async def get_listings(self, channel_id: str, db: orm.Session):
    """Get current and future listings for a channel from the database"""
    return await get_listings_for_channel(self._user_id, self._server_id, channel_id, db)
