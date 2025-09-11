import os
import time

import requests
from xdg_base_dirs import xdg_cache_home

from app.services.config import settings
from app.services.logger import get_logger
from app.utils import xmltv
from app.utils.time_utils import is_file_older_cache_time

logger = get_logger(__name__)


class EPGParser:
  def __init__(self, url, server, user):
    self._epg_url = url
    self._programs = {}
    cache_dir = (os.getenv("CACHE_PATH") or
                 os.path.join(xdg_cache_home(), "xtreamium"))

    self._cache_file = os.path.join(cache_dir, f"{user}", server, "epg.xml")

    # Create the full directory path for the cache file if it doesn't exist
    cache_file_dir = os.path.dirname(self._cache_file)
    if not os.path.exists(cache_file_dir):
      os.makedirs(cache_file_dir)

  def cache_epg(self):
    if not os.path.isfile(self._cache_file) or is_file_older_cache_time(self._cache_file):
      logger.debug(f"Downloading EPG to {self._cache_file}")
      data = requests.get(self._epg_url)
      with open(self._cache_file, 'wb') as file:
        file.write(data.content)

    logger.debug("Parsing EPG")
    try:
      logger.debug(f"Parsing EPG from {self._cache_file}")
      self._programs = xmltv.read_programmes(open(self._cache_file, 'r'))
      logger.debug(f"Parsed {len(self._programs)} programs")
    except Exception as e:
      logger.error(f"Failed to parse EPG: {e}")
      self._programs = []


def get_listings(self, channel_id):
  listings = [d for d in self._programs if d['channel'] ==
              channel_id and d['stop'] > int(time.time())]
  return listings
