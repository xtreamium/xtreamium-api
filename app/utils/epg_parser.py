import os
import time

import requests
from xdg_base_dirs import xdg_cache_home

from app.services.config import settings
from app.services.logger import logger
from app.utils import xmltv
from app.utils.time_utils import is_file_older_cache_time


class EPGParser:
    def __init__(self, url):
        self._epg_url = url
        self._programs = {}
        cache_dir = (os.getenv("CACHE_PATH") or
                     os.path.join(xdg_cache_home(), "xtreamium"))
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        self._cache_file = os.path.join(cache_dir, "epg.xml")

    def cache_epg(self):
        if (not os.path.isfile(self._cache_file) or
            is_file_older_cache_time(
                self._cache_file)):
            logger.debug(f"Downloading EPG to {self._cache_file}")
            data = requests.get(self._epg_url)
            with open(self._cache_file, 'wb') as file:
                file.write(data.content)

        logger.debug("Parsing EPG")

        self._programs = xmltv.read_programmes(open(self._cache_file, 'r'))
        logger.debug("EPG parsed")

    def get_listings(self, channel_id):
        listings = [d for d in self._programs if d['channel'] ==
                    channel_id and d['stop'] > int(time.time())]
        return listings


epg_parser = EPGParser(settings.EPG_URL)
