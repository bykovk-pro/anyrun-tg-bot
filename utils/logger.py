import logging
import os
from datetime import datetime
from lang.context import set_current_language, get_message
import json
import tempfile

# Root logger setup
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)  # Set to lowest level to catch all messages

# Log formatters
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Global handlers
file_handler = None
console_handler = None

def setup_file_handler(level=logging.INFO):
    global file_handler
    current_date = datetime.now().strftime("%Y%m%d")
    # Изменяем путь для лог-файлов
    log_dir = os.path.join(os.path.expanduser('~'), 'arsbtlgbot_logs')
    os.makedirs(log_dir, exist_ok=True)
    file_name = os.path.join(log_dir, f"{current_date}.log")
    file_handler = logging.FileHandler(file_name)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(level)
    return file_handler

def setup_console_handler(level=logging.ERROR):
    global console_handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(level)
    return console_handler

def initialize_loggers(file_level=logging.INFO, console_level=logging.ERROR):
    global file_handler, console_handler
    
    # Преобразуйте уровни логирования в строки для логирования
    log('DEBUG_INITIALIZE_LOGGERS', logging.DEBUG, file_level=logging.getLevelName(file_level), console_level=logging.getLevelName(console_level))
    
    root_logger.handlers.clear()  # Clear existing handlers
    
    file_handler = setup_file_handler(file_level)
    console_handler = setup_console_handler(console_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

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

def set_log_level(level: int):
    if file_handler:
        file_handler.setLevel(level)

def set_console_level(level: int):
    if console_handler:
        console_handler.setLevel(level)

# File to store log levels
LOG_LEVELS_FILE = os.path.join(tempfile.gettempdir(), 'arsbtlgbot_log_levels.json')

def save_log_levels(log_level, echo_level):
    with open(LOG_LEVELS_FILE, 'w') as f:
        json.dump({
            'log_level': logging.getLevelName(log_level),
            'echo_level': logging.getLevelName(echo_level)
        }, f)

def load_log_levels():
    try:
        with open(LOG_LEVELS_FILE, 'r') as f:
            levels = json.load(f)
        # Преобразуем числовые значения уровней логирования в строки
        log_level = logging.getLevelName(int(levels['log_level']))
        echo_level = logging.getLevelName(int(levels['echo_level']))
        return getattr(logging, log_level), getattr(logging, echo_level)
    except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
        return logging.INFO, logging.ERROR

# Initialize loggers when the module is imported
initialize_loggers()