import logging
from telegram import Update
from telegram.ext import ContextTypes
from src.db.api_keys import db_add_api_key
from src.lang.decorators import with_locale, localized_message

@with_locale
async def process_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    api_key = update.message.text.strip()
    user_id = update.effective_user.id
    
    try:
        success = await db_add_api_key(user_id, api_key)
        
        if success:
            await localized_message("API_KEY_SAVED")(update)
            logging.info(f"API key saved for user {user_id}")
        else:
            await localized_message("API_KEY_ERROR")(update)
            logging.error(f"Failed to save API key for user {user_id}")
    except Exception as e:
        logging.error(f"Error processing API key for user {user_id}: {e}")
        await localized_message("API_KEY_ERROR")(update)
