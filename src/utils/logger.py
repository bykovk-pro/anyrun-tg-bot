import os
import logging
import time
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')

def setup_logging(config):
    log_level = config.get_log_level('LOG_LEVEL')
    telegram_log_level = config.get_log_level('TELEGRAM_LOG_LEVEL')
    logging.info(f"Setting up logging with levels: LOG_LEVEL={logging.getLevelName(log_level)}, TELEGRAM_LOG_LEVEL={logging.getLevelName(telegram_log_level)}")
    
    os.makedirs(LOG_DIR, exist_ok=True)
    
    current_date = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(LOG_DIR, f"{current_date}.log")
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    
    for logger_name in logging.root.manager.loggerDict:
        if not logger_name.startswith('telegram'):
            logger = logging.getLogger(logger_name)
            logger.setLevel(log_level)
            logger.propagate = False 
    
    telegram_loggers = [
        'telegram', 'telegram.ext', 'telegram.bot', 'telegram.network',
        'telegram.utils.request', 'telegram.error', 'telegram.ext.Application',
        'httpx'
    ]
    for logger_name in telegram_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(telegram_log_level)
        logger.propagate = False  

    logging.getLogger().setLevel(log_level)

    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.INFO)
    if log_level <= logging.INFO:
        logging.info(f"Logging setup completed. Log file: {log_file}")
        logging.info(f"Application log level: {logging.getLevelName(log_level)}")
        logging.info(f"Telegram log level: {logging.getLevelName(telegram_log_level)}")

def view_logs(lines=50, days=7, follow=False):
    log_files = []
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
        log_file = os.path.join(LOG_DIR, f"{date}.log")
        if os.path.exists(log_file):
            log_files.append(log_file)
    
    if not log_files:
        return "No log files found"
    
    if not follow:
        all_logs = []
        for file in reversed(log_files):
            with open(file, 'r') as f:
                all_logs.extend(f.readlines())
        return ''.join(all_logs[-lines:])
    else:
        latest_log_file = log_files[0]
        with open(latest_log_file, 'r') as f:
            f.seek(0, 2)  # Go to the end of the file
            while True:
                line = f.readline()
                if line:
                    print(line, end='')
                else:
                    time.sleep(0.1)  # Sleep briefly to avoid busy waiting
