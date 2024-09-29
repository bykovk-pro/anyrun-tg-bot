import logging
import os
from datetime import datetime
from lang.context import set_current_language, get_message
import json
import tempfile

root_logger = logging.getLogger()
root_logger.setLevel(logging.WARNING)

log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = None
current_log_level = logging.WARNING

def setup_file_handler(level=logging.WARNING):
    global file_handler
    current_date = datetime.now().strftime("%Y%m%d")
    log_dir = os.path.join(os.path.expanduser('~'), 'arsbtlgbot_logs')
    os.makedirs(log_dir, exist_ok=True)
    file_name = os.path.join(log_dir, f"{current_date}.log")
    file_handler = logging.FileHandler(file_name)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(level)
    return file_handler

def setup_logging(level=logging.WARNING):
    global current_log_level, file_handler
    
    current_log_level = level
    
    root_logger.handlers.clear()
    
    file_handler = setup_file_handler(level)
    root_logger.addHandler(file_handler)

def set_log_level(level):
    global current_log_level
    current_log_level = level
    if file_handler:
        file_handler.setLevel(level)
    root_logger.setLevel(level)

def log(message_key, level, **kwargs):
    message = get_message(message_key)
    
    if kwargs:
        try:
            message = message.format(**kwargs)
        except KeyError as e:
            format_error_key = 'FORMAT_ERROR'
            format_error_message = get_message(format_error_key)
            message += format_error_message.format(error=str(e))
    
    root_logger.log(level, message)

def get_log_level():
    return current_log_level

setup_logging()
