import logging
import validators
import re
from telegram import Update, User
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import BadRequest, TelegramError
from src.lang.context import set_user_language_getter, set_language_for_user
from src.lang.director import humanize
from src.api.security import setup_telegram_security, check_in_groups
from src.api.menu import show_main_menu, create_main_menu
from src.api.sandbox import run_url_analysis
from src.api.settings import handle_text_input as settings_handle_text_input
from src.db.users import db_add_user

def get_user_language(user: User) -> str:
    return user.language_code if user.language_code else 'en'

set_user_language_getter(get_user_language)

def is_url(text: str) -> bool:
    # Регулярное выражение для проверки URL
    url_pattern = re.compile(
        r'^((?:https?:\/\/)?'  # протокол (опционально)
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # домен
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP адрес
        r'(?::\d+)?'  # порт (опционально)
        r'(?:/?|[/?]\S+))$', re.IGNORECASE)
    
    return bool(url_pattern.match(text))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        set_language_for_user(update.effective_user)
        message_text = update.message.text
        
        # Проверяем, ожидает ли бот ввода для конкретного действия
        next_action = context.user_data.get('next_action')
        if next_action:
            # Если ожидается действие, передаем управление в соответствующий обработчик
            await settings_handle_text_input(update, context)
        elif is_url(message_text):
            # Если это URL, запускаем анализ
            await run_url_analysis(update, context)
        else:
            # Если это не URL и нет ожидаемого действия, отправляем сообщение о неверном вводе
            invalid_input_message = humanize("INVALID_INPUT")
            await update.message.reply_text(invalid_input_message)
            await show_main_menu(update, context)
        
        logging.debug(f'User sent a message: user_id={update.effective_user.id}, message={message_text}')
    except Exception as e:
        logging.error(f'Error in handle_message: {str(e)}, user_id={update.effective_user.id}, message={update.message.text}')

async def setup_telegram_bot(config):
    TOKEN = config.get('TELEGRAM_TOKEN')
    logging.debug(f"Setting up Telegram bot with token: {TOKEN[:5]}...{TOKEN[-5:]}.")
    
    try:
        TOKEN = setup_telegram_security(TOKEN)
        
        logging.debug('Building Telegram application')
        application = Application.builder().token(TOKEN).build()
        logging.debug('Telegram application built successfully')
        
        required_group_ids = config.get('REQUIRED_GROUP_IDS')
        logging.debug(f'Required group IDs: {required_group_ids}')

        await application.initialize()
        await application.bot.initialize()
        
        bot_in_groups = await check_in_groups(application.bot, application.bot.id, is_bot=True, required_group_ids=required_group_ids)
        logging.debug(f'Groups check result: {bot_in_groups}')
        
        if bot_in_groups is not True:
            logging.warning(f'Bot is not in all required groups. Missing groups: {bot_in_groups}')
        
        logging.debug('Adding command handlers')
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(CommandHandler("menu", show_main_menu))
        
        # Импортируем setup_handlers здесь, чтобы избежать циклического импорта
        from src.api.handlers import setup_handlers
        setup_handlers(application)
        
        application.add_error_handler(handle_telegram_error)
        
        logging.debug('Command handlers added successfully')
        
        logging.info('Telegram bot setup completed')
        return application
    except Exception as e:
        logging.exception(f'Error during Telegram bot setup: {e}')
        raise

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.debug(f'User started the bot: user_id={update.effective_user.id}')
    set_language_for_user(update.effective_user)
    
    # Добавляем или обновляем пользователя в базе данных
    try:
        await db_add_user(update.effective_user.id)
    except Exception as e:
        logging.error(f"Error adding/updating user in database: {e}")
    
    welcome_message = humanize("WELCOME_MESSAGE")
    await update.message.reply_text(welcome_message)
    await show_main_menu(update, context)

async def handle_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    set_language_for_user(update.effective_user)

async def handle_telegram_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    error = context.error
    if isinstance(error, BadRequest):
        if "Query is too old" in str(error):
            await update.effective_message.reply_text(humanize("QUERY_EXPIRED"))
            await show_main_menu(update, context)
        else:
            logging.error(f"BadRequest error: {error}")
    elif isinstance(error, TelegramError):
        logging.error(f"TelegramError: {error}")
    else:
        logging.error(f"Unexpected error: {error}")

