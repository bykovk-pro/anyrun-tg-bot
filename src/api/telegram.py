import logging
from telegram import Update, User
from telegram.ext import Application, ContextTypes
from telegram.error import NetworkError, BadRequest, TelegramError
from src.lang.context import set_language_for_user
from src.lang.director import humanize
from src.api.security import setup_telegram_security
import asyncio
import os

async def setup_telegram_bot():
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    logging.debug("Setting up Telegram bot")
    
    try:
        TOKEN = await setup_telegram_security(TOKEN)
        application = Application.builder().token(TOKEN).build()
        
        from src.api.handlers import setup_handlers
        setup_handlers(application)
        
        application.add_error_handler(handle_telegram_error)
        
        return application
    except Exception as e:
        logging.exception(await humanize("BOT_START_ERROR").format(error=str(e)))
        raise

async def handle_telegram_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    error = context.error
    if isinstance(error, NetworkError):
        logging.error(f"NetworkError: {error}")
        await retry_connection(context)
    elif isinstance(error, BadRequest):
        logging.error(f"BadRequest error: {error}")
    elif isinstance(error, TelegramError):
        logging.error(f"TelegramError: {error}")
    else:
        logging.error(f"Unexpected error: {error}")
        if update and update.effective_message:
            await update.message.reply_text(await humanize("ERROR_OCCURRED"))

async def retry_connection(context: ContextTypes.DEFAULT_TYPE, delay: int = 60):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            await context.bot.get_me()
            logging.info("Reconnected to Telegram successfully")
            return
        except NetworkError as e:
            wait_time = delay * (2 ** attempt)
            logging.warning(f"Retrying in {wait_time} seconds: {e}")
            await asyncio.sleep(wait_time)
    logging.critical("Failed to reconnect after multiple attempts")
