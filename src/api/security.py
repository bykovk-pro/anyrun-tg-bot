import logging
from telegram import Bot
from src.db.users import db_get_user
from src.db.api_keys import db_get_user_api_key
from src.lang.director import humanize

async def setup_telegram_security(token) -> str:
    if not token:
        error_msg = await humanize("MISSING_ENV_VARS").format(vars="TELEGRAM_TOKEN")
        logging.critical(error_msg)
        raise EnvironmentError(error_msg)
    return token

async def check_user_access(bot: Bot, user_id: int):
    user = await db_get_user(user_id)
    if not user:
        logging.warning(f"User {user_id} not found")
        return False, await humanize("USER_NOT_FOUND")
    if user[4]:
        logging.warning(f"User {user_id} is banned")
        return False, await humanize("USER_BANNED")
    if user[5]:
        logging.warning(f"User {user_id} is deleted")
        return False, await humanize("USER_DELETED")
    
    api_key = await db_get_user_api_key(user_id)
    if not api_key:
        logging.warning(f"No API key found for user {user_id}")
        return False, await humanize("NO_API_KEY")
    
    return True, api_key
