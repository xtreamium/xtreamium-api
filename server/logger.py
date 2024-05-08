import logging
import sys

formatter = logging.Formatter(
    fmt='%(levelname)s %(asctime)s %(message)s'
)
stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("/tmp/xtreamium.log")
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.handlers = [stream_handler, file_handler]
