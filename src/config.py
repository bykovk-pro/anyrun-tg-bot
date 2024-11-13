import os
import logging
from dotenv import load_dotenv
from src.lang.director import humanize

async def load_config() -> dict:
    load_dotenv(override=True)
    required_vars = ['TELEGRAM_TOKEN']
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        error_msg = await humanize("MISSING_ENV_VARS").format(vars=', '.join(missing_vars))
        raise EnvironmentError(error_msg)
    
    config = {key: value for key, value in os.environ.items()}
    logging.debug("Configuration loaded successfully")
    return config
