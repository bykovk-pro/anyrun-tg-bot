import os
import logging
from dotenv import load_dotenv

def load_config():
    load_dotenv(override=True)
    config = {key: value for key, value in os.environ.items()}
    logging.debug("Configuration loaded from .env file")
    return config
