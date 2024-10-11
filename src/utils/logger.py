import os
import logging
import time
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')

class DailyRotatingFileHandler(logging.Handler):
    def __init__(self, filename, mode='a', encoding=None):
        super().__init__()
        self.filename = filename
        self.mode = mode
        self.encoding = encoding
        self.current_date = datetime.now().date()
        self.file_handler = self._get_file_handler()

    def _get_file_handler(self):
        log_file = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y-%m-%d')}.txt")
        handler = logging.FileHandler(log_file, mode=self.mode, encoding=self.encoding)
        handler.setFormatter(self.formatter)  # Применяем форматтер к внутреннему обработчику
        return handler

    def setFormatter(self, fmt):
        super().setFormatter(fmt)
        self.file_handler.setFormatter(fmt)  # Также устанавливаем форматтер для текущего file_handler

    def emit(self, record):
        if datetime.now().date() != self.current_date:
            self.file_handler.close()
            self.file_handler = self._get_file_handler()
            self.current_date = datetime.now().date()
        self.file_handler.emit(record)

def setup_logging(config):
    log_level = config.get_log_level('LOG_LEVEL')
    telegram_log_level = config.get_log_level('TELEGRAM_LOG_LEVEL')
    sqlite_log_level = config.get_log_level('SQLITE_LOG_LEVEL')
    print(f"Setting up logging with levels: LOG_LEVEL={logging.getLevelName(log_level)}, "
          f"TELEGRAM_LOG_LEVEL={logging.getLevelName(telegram_log_level)}, "
          f"SQLITE_LOG_LEVEL={logging.getLevelName(sqlite_log_level)}")
    
    os.makedirs(LOG_DIR, exist_ok=True)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    file_handler = DailyRotatingFileHandler(os.path.join(LOG_DIR, "log"))
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s', 
                                  datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Устанавливаем уровень логирования для основного приложения
    logging.getLogger('').setLevel(log_level)

    # Устанавливаем уровень логирования для Telegram-связанных модулей
    telegram_related_loggers = ['telegram', 'httpcore', 'httpx', 'aiohttp']
    for logger_name in telegram_related_loggers:
        logging.getLogger(logger_name).setLevel(telegram_log_level)

    # Устанавливаем уровень логирования для SQLite
    logging.getLogger('aiosqlite').setLevel(sqlite_log_level)

    print(f"Logging setup completed. Log file: {file_handler.filename}")
    print(f"Application log level: {logging.getLevelName(log_level)}")
    print(f"Telegram-related modules log level: {logging.getLevelName(telegram_log_level)}")
    print(f"SQLite log level: {logging.getLevelName(sqlite_log_level)}")

    # Добавим тестовые логи для проверки
    logging.info("Main application logging initialized")
    for logger_name in telegram_related_loggers:
        logging.getLogger(logger_name).info(f"{logger_name} logging initialized")
    logging.getLogger('aiosqlite').info("SQLite logging initialized")

def view_logs(lines=50, days=7, follow=False):
    log_files = []
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        log_file = os.path.join(LOG_DIR, f"log_{date}.txt")
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
