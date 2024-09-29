import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from lang.context import set_current_language
from lang.director import get as lang_get
from functools import wraps
from utils.logger import log
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the token from the environment variable
TOKEN = os.getenv('ANYRUN_SB_API_TOKEN')

# Function to determine the user's language
def get_user_language(user):
    if user.language_code:
        return user.language_code
    return "en"

def set_language(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_language = update.effective_user.language_code
        set_current_language(user_language)
        return await func(update, context)
    return wrapper

@set_language
async def send_message(update: Update, message_key: str, **kwargs) -> None:
    try:
        # Send a localized message to the user.
        message = lang_get(message_key)
        await update.message.reply_text(message, **kwargs)
    except Exception as e:
        log('SEND_MESSAGE_ERROR', logging.ERROR, error=str(e), message_key=message_key)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_message(update, 'WELCOME_MESSAGE')
    log('USER_STARTED_BOT', logging.DEBUG, user_id=update.effective_user.id)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Here we're not using localization, so we can just reply directly
       await update.message.reply_text(update.message.text)
       log('USER_SENT_MESSAGE', logging.DEBUG, user_id=update.effective_user.id, message=update.message.text)
    except Exception as e:
        log('ECHO_ERROR', logging.ERROR, error=str(e), user_id=update.effective_user.id, message=update.message.text)

def setup_telegram_bot():
    if not TOKEN:
        log('BOT_TOKEN_NOT_FOUND', logging.CRITICAL)
        raise EnvironmentError(lang_get('BOT_TOKEN_NOT_FOUND'))
    
    try:
        log('BUILDING_APPLICATION', logging.DEBUG, token=TOKEN[:5] + '...')
        application = Application.builder().token(TOKEN).build()
        log('APPLICATION_BUILT', logging.DEBUG)
        
        log('ADDING_HANDLERS', logging.DEBUG)
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
        log('HANDLERS_ADDED', logging.DEBUG)
        
        log('BOT_SETUP_COMPLETE', logging.INFO)
        return application
    except Exception as e:
        log('BOT_SETUP_ERROR', logging.ERROR, error=str(e))
        raise

def run_telegram_bot(application):  
    try:
        log('BOT_STARTING', logging.INFO)
        log('STARTING_POLLING', logging.DEBUG)
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        log('POLLING_STARTED', logging.INFO)
    except Exception as e:
        log('BOT_RUN_ERROR', logging.CRITICAL, error=str(e))
        import traceback
        log('BOT_RUN_ERROR_TRACEBACK', logging.DEBUG, traceback=traceback.format_exc())
        raise

