import os
import tempfile
import time

import requests

import logging

from server.utils.epg import xmltv

log = logging.getLogger(__name__)


class EPGParser:
    def __init__(self, url):
        self._epg_url = url
        self._programs = {}

        self._cache_file = os.path.join(tempfile.mkdtemp(), 'epg.xml')
        self._cache_epg()

    def _cache_epg(self):
        log.debug("Downloading EPG")
        data = requests.get(self._epg_url)
        with open(self._cache_file, 'wb') as file:
            file.write(data.content)

        log.debug("Parsing EPG")

        self._programs = xmltv.read_programmes(open(self._cache_file, 'r'))

    def get_listings(self, channel_id):
        listings = [d for d in self._programs if d['channel'] == channel_id and d['stop'] > int(time.time())]
        return listings
