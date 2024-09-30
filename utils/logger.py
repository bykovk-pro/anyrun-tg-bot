import os
import logging
from datetime import datetime
from datetime import timedelta

def setup_logging(config):
    log_dir = os.path.join(os.path.expanduser('~'), 'arsbtlgbot_logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_level = config.get_log_level('LOG_LEVEL')
    telegram_log_level = config.get_log_level('TELEGRAM_LOG_LEVEL')
    
    current_date = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"{current_date}.log")
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    
    logging.getLogger('telegram').setLevel(telegram_log_level)
    logging.getLogger('telegram.ext').setLevel(telegram_log_level)
    logging.getLogger('telegram.bot').setLevel(telegram_log_level)
    logging.getLogger('telegram.network').setLevel(telegram_log_level)
    logging.getLogger('telegram.utils.request').setLevel(telegram_log_level)
    logging.getLogger('telegram.error').setLevel(telegram_log_level)
    logging.getLogger('telegram.ext.Application').setLevel(telegram_log_level)
    logging.getLogger('httpx').setLevel(telegram_log_level)

    logging.info(f"Logging setup completed. Log file: {log_file}")

def view_logs(lines=50, days=7):
    log_dir = os.path.join(os.path.expanduser('~'), 'arsbtlgbot_logs')
    log_files = []
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
        log_file = os.path.join(log_dir, f"{date}.log")
        if os.path.exists(log_file):
            log_files.append(log_file)
    
    if not log_files:
        return "No log files found"
    
    all_logs = []
    for file in reversed(log_files):
        with open(file, 'r') as f:
            all_logs.extend(f.readlines())
    
    return ''.join(all_logs[-lines:])
