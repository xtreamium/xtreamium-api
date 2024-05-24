from enum import Enum

import requests

from app.utils.cache import Cache


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

  def _authenticate(self):
    r = requests.get(self.__get_authenticate_url())
    self._cache.auth_data = r.json()
    return r

  def __get_authenticate_url(self):
    url = f'{self._server}/player_api.php?username={self._username}&password={self._password}'
    return url

  def __get_live_categories_url(self):
    url = f'{self.__get_authenticate_url()}&action=get_live_categories'
    return url

  # TODO: use f strings
  def __get_live_streams_url(self):
    #TODO: why are these methods the same??
    return self.__get_live_categories_url()

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

  def get_channels(self, category_id, stream_type=StreamType.LIVE):
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
