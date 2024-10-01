import os
import sys
import signal
import logging
from functools import wraps
from dotenv import load_dotenv
from config import create_config
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import Conflict
from lang.context import set_current_language
from lang.director import get as humanize
from api.menu import show_main_menu, setup_menu_handlers, change_language_command

load_dotenv()
env_vars = dict(os.environ)
config = create_config(env_vars)

TOKEN = config.get('TELEGRAM_TOKEN')
TELEGRAM_LOG_LEVEL = config.get_log_level('TELEGRAM_LOG_LEVEL')

def setup_telegram_bot():
    if not TOKEN:
        logging.critical('Telegram bot token not found in environment variables')
        raise EnvironmentError('Telegram bot token not found in environment variables')
    
    try:
        logging.debug(f'Building Telegram application with token: {TOKEN[:5]}...')
        application = Application.builder().token(TOKEN).build()
        logging.debug('Telegram application built successfully')
        
        logging.debug('Adding command handlers')
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("language", change_language_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
        application.add_handler(CommandHandler("menu", show_main_menu))
        setup_menu_handlers(application)
        logging.debug('Command handlers added successfully')
        
        logging.info('Telegram bot setup completed')
        return application
    except Exception as e:
        logging.error('Error during Telegram bot setup', exc_info=True)
        raise

def set_language(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE = None):
        user = update.effective_user
        user_language = user.language_code if user.language_code else 'en'
        set_current_language(user_language)
        return await func(update, context)
    return wrapper

@set_language
async def send_message(update: Update, message_key: str, **kwargs) -> None:
    try:
        message = humanize(message_key)
        await update.message.reply_text(message, **kwargs)
    except Exception as e:
        logging.error(f'Error sending message: {str(e)}, message_key: {message_key}')

@set_language
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_message(update, 'WELCOME_MESSAGE')
    await show_main_menu(update, context)
    logging.debug(f'User started the bot: user_id={update.effective_user.id}')

@set_language
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text(update.message.text)
        logging.debug(f'User sent a message: user_id={update.effective_user.id}, message={update.message.text}')
    except Exception as e:
        logging.error(f'Error in echo handler: {str(e)}, user_id={update.effective_user.id}, message={update.message.text}')

def signal_handler(signum, frame):
    print("Received signal to terminate. Stopping bot...")
    sys.exit(0)

def run_telegram_bot(bot):
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        bot.run_polling(allowed_updates=Update.ALL_TYPES)
    except Conflict:
        logging.error("Another instance of the bot is already running. Please stop it before starting a new one.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An error occurred while running the bot: {e}")
        sys.exit(1)