import os
import logging
from functools import wraps
from dotenv import load_dotenv
from config import create_config
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.error import Conflict
from lang.context import set_current_language
from lang.director import get as humanize
from api.security import setup_telegram_security, check_bot_in_groups
from api.menu import *
from db.users import get_non_admin_users, update_user_ban_status
from db.director import init_database, backup_database as create_db_backup

load_dotenv()
env_vars = dict(os.environ)
config = create_config(env_vars)

TOKEN = config.get('TELEGRAM_TOKEN')
TELEGRAM_LOG_LEVEL = config.get_log_level('TELEGRAM_LOG_LEVEL')

def set_language(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE = None):
        user = update.effective_user
        user_language = user.language_code if user.language_code else 'en'
        set_current_language(user_language)
        return await func(update, context)
    return wrapper

async def setup_telegram_bot():
    try:
        await init_database()
        TOKEN = setup_telegram_security()
        
        logging.debug(f'Building Telegram application with token: {TOKEN[:5]}...')
        application = Application.builder().token(TOKEN).build()
        logging.debug('Telegram application built successfully')
        
        logging.debug('Adding command handlers')
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
        application.add_handler(CommandHandler("menu", show_main_menu))
        setup_menu_handlers(application)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_selection))
        application.add_handler(CallbackQueryHandler(handle_user_action, pattern='^(ban_users|unban_users|do_nothing)$'))
        logging.debug('Command handlers added successfully')
        
        logging.info('Telegram bot setup completed')
        return application
    except Exception as e:
        logging.error('Error during Telegram bot setup', exc_info=True)
        raise

@set_language
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = humanize("WELCOME_MESSAGE")
    await update.message.reply_text(welcome_message)
    await show_main_menu(update, context)
    logging.debug(f'User started the bot: user_id={update.effective_user.id}')

@set_language
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text(update.message.text)
        logging.debug(f'User sent a message: user_id={update.effective_user.id}, message={update.message.text}')
    except Exception as e:
        logging.error(f'Error in echo handler: {str(e)}, user_id={update.effective_user.id}, message={update.message.text}')

@set_language
async def check_bot_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_groups_check = await check_bot_in_groups(context.bot)
    if bot_groups_check is True:
        await update.callback_query.message.reply_text(humanize("BOT_IN_ALL_GROUPS"))
    else:
        missing_groups = ', '.join(map(str, bot_groups_check))
        await update.callback_query.message.reply_text(humanize("BOT_MISSING_GROUPS").format(groups=missing_groups))
    await show_admin_menu(update, context)

@set_language
async def manage_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = await get_non_admin_users()
    user_list = '\n'.join([f"{user['telegram_id']} - {user['first_access_date']} - {user['last_access_date']} - {'Banned' if user['is_banned'] else 'Not banned'}" for user in users])
    await update.callback_query.message.reply_text(humanize("USER_LIST") + '\n' + user_list)
    await update.callback_query.message.reply_text(humanize("SELECT_USERS_TO_MANAGE"))
    context.user_data['awaiting_user_selection'] = True

@set_language
async def handle_user_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'awaiting_user_selection' not in context.user_data or not context.user_data['awaiting_user_selection']:
        return

    selected_users = update.message.text.split(',')
    valid_users = []
    invalid_users = []

    for user_id in selected_users:
        try:
            user_id = int(user_id.strip())
            if any(user['telegram_id'] == user_id for user in await get_non_admin_users()):
                valid_users.append(user_id)
            else:
                invalid_users.append(user_id)
        except ValueError:
            invalid_users.append(user_id)

    if invalid_users:
        await update.message.reply_text(humanize("INVALID_USER_IDS").format(users=', '.join(map(str, invalid_users))))
        return

    keyboard = [
        [InlineKeyboardButton(humanize("BAN_USERS"), callback_data='ban_users')],
        [InlineKeyboardButton(humanize("UNBAN_USERS"), callback_data='unban_users')],
        [InlineKeyboardButton(humanize("DO_NOTHING"), callback_data='do_nothing')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(humanize("CHOOSE_ACTION"), reply_markup=reply_markup)
    context.user_data['selected_users'] = valid_users
    context.user_data['awaiting_user_selection'] = False

@set_language
async def handle_user_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action = query.data
    selected_users = context.user_data.get('selected_users', [])

    if action == 'ban_users':
        for user_id in selected_users:
            await update_user_ban_status(user_id, True)
        await query.message.reply_text(humanize("USERS_BANNED"))
    elif action == 'unban_users':
        for user_id in selected_users:
            await update_user_ban_status(user_id, False)
        await query.message.reply_text(humanize("USERS_UNBANNED"))
    elif action == 'do_nothing':
        await query.message.reply_text(humanize("NO_ACTION_TAKEN"))

    await show_admin_menu(update, context)

@set_language
async def backup_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        backup_file = await create_db_backup()
        with open(backup_file, 'rb') as file:
            await update.callback_query.message.reply_document(document=file, filename='database_backup.zip')
        await update.callback_query.message.reply_text(humanize("BACKUP_CREATED"))
    except Exception as e:
        logging.error(f"Error creating database backup: {str(e)}")
        await update.callback_query.message.reply_text(humanize("BACKUP_ERROR"))
    
    await show_admin_menu(update, context)
