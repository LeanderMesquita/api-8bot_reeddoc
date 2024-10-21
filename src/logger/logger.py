from loguru import logger
import os

log_file = os.path.join('logs', 'console.log')
logger.add('src/logger/log_file', rotation="1 MB", retention="15 days", level='INFO', format="{time} - {level} - {message}")
log = logger
