from enum import Enum

from server.utils.cache import Cache
import requests


class UrlNotCreatedException(Exception):
    pass


class StreamType(Enum):
    LIVE = "LIVE",
    VOD = "VOD",
    SERIES = "SERIES"


class XTream:
    _cache = Cache()

    def __init__(self, server, username, password):
        if not (server and username and password):
            raise ValueError("XTream: must specify server, username and password")
        
        self._server = server
        self._username = username
        self._password = password
        self._interface = self._authenticate()

    def _authenticate(self):
        r = requests.get(self.__get_authenticate_url())
        self._cache.authData = r.json()
        return r

    # TODO: use f strings
    def __get_authenticate_url(self):
        url = '%s/player_api.php?username=%s&password=%s' % (self._server, self._username, self._password)
        return url

    def __get_live_categories_url(self):
        url = '%s/player_api.php?username=%s&password=%s&action=%s' % (
            self._server, self._username, self._password, 'get_live_categories')
        return url

    def __get_live_streams_url(self):
        url = '%s/player_api.php?username=%s&password=%s&action=%s' % (
            self._server, self._username, self._password, 'get_live_categories')
        return url

    def __get_live_streams_by_category_url(self, category_id):
        url = '%s/player_api.php?username=%s&password=%s&action=%s&category_id=%s' % (
            self._server, self._username, self._password, 'get_live_streams', category_id)
        return url

    def get_categories(self, stream_type=StreamType.LIVE):
        url = ""
        if stream_type == StreamType.LIVE:
            url = self.__get_live_categories_url()
        # elif stream_type == StreamType.VOD:
        #     url = get_vod_cat_url()
        # elif stream_type == StreamType.SERIES:
        #     url = get_series_cat_url()

        if url == "":
            raise UrlNotCreatedException("Unable to create URL")

        r = requests.get(url)
        return r

    def get_streams_for_category(self, category_id, stream_type=StreamType.LIVE):
        url = ""
        if stream_type == StreamType.LIVE:
            url = self.__get_live_streams_by_category_url(category_id)

        if url == "":
            raise UrlNotCreatedException("Unable to create URL")

        r = requests.get(url)
        return r

    def get_live_stream_url(self, stream_id):
        return f"{self._server}/live/{self._username}/{self._password}/{stream_id}.ts"

    def get_vod_stream_url(self, stream_id):
        return f"{self._server}/movie/{self._username}/{self._password}/{stream_id}.ts"

    def get_series_stream_url(self, stream_id):
        return f"{self._server}/series/{self._username}/{self._password}/{stream_id}.ts"
