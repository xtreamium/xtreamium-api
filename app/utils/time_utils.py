import time
from os import path


def is_file_older_cache_time(file, hours=1):
  file_time = path.getmtime(file)
  return (time.time() - file_time) / 3600 > (1 * hours)
