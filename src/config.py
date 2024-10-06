import os
import logging
from typing import Optional

class Config:
    def __init__(self):
        self.env = dict(os.environ)

    def get(self, key, default=None):
        return self.env.get(key, default)

    def get_log_level(self, key):
        level_str = self.get(key, 'INFO').upper()
        logging.info(f"Getting log level for {key}: {level_str}")
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return level_map.get(level_str, logging.INFO)

_config: Optional[Config] = None

def create_config():
    global _config
    if _config is None:
        _config = Config()
    return _config

def get_config() -> Config:
    global _config
    if _config is None:
        raise RuntimeError("Config not initialized. Call create_config first.")
    return _config