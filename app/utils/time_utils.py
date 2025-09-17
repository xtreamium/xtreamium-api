import time
from os import path


def is_file_older_cache_time(file, hours=1):
    if not path.isfile(file):
        return True

    file_mod_time = path.getmtime(file)
    current_time = time.time()
    age_seconds = current_time - file_mod_time
    return age_seconds > hours * 3600
