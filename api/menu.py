import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler, Application
from telegram.constants import ParseMode
from lang.director import get as humanize
from lang.context import set_current_language
from functools import wraps
import logging
from db.users import is_user_admin
from db.director import backup_database
from api.bot_utils import check_bot_groups, manage_users

def set_language(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        user_language = user.language_code if user.language_code else 'en'
        set_current_language(user_language)
        return await func(update, context)
    return wrapper

def create_main_menu(is_admin=False):
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_PROFILE"), callback_data='profile')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_SETTINGS"), callback_data='settings')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_HELP"), callback_data='help')]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton(humanize("MENU_BUTTON_ADMIN"), callback_data='admin')])
    return InlineKeyboardMarkup(keyboard)

def create_admin_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("ADMIN_CHECK_BOT_GROUPS"), callback_data='admin_check_groups')],
        [InlineKeyboardButton(humanize("ADMIN_MANAGE_USERS"), callback_data='admin_manage_users')],
        [InlineKeyboardButton(humanize("ADMIN_BACKUP_DB"), callback_data='admin_backup_db')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

@set_language
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_admin = await is_user_admin(user_id)
    menu_text = humanize("MAIN_MENU_TEXT")
    reply_markup = create_main_menu(is_admin)

    if update.callback_query:
        await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(menu_text, reply_markup=reply_markup)

@set_language
async def show_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = humanize("ADMIN_MENU_TEXT")
    reply_markup = create_admin_menu()
    await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)

@set_language
async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    handlers = {
        'profile': show_profile,
        'settings': show_settings,
        'help': handle_help,
        'admin': show_admin_menu,
        'admin_check_groups': admin_check_groups_wrapper,
        'admin_manage_users': admin_manage_users_wrapper,
        'admin_backup_db': admin_backup_db_wrapper,
        'main_menu': show_main_menu
    }

    handler = handlers.get(query.data)
    if handler:
        await handler(update, context)
    else:
        logging.warning(f"Unknown callback data: {query.data}")
        await query.edit_message_text(humanize("UNKNOWN_OPTION"))
        await asyncio.sleep(2)
        await show_main_menu(update, context)

def action_wrapper(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(humanize("PROCESSING_REQUEST"))
        
        try:
            result = await func(update, context)
            await asyncio.sleep(2)
            return result
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {str(e)}")
            await query.edit_message_text(humanize("ERROR_OCCURRED"))
            await asyncio.sleep(2)
        finally:
            await show_main_menu(update, context)
    
    return wrapper

@set_language
@action_wrapper
async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    profile_info = humanize("PROFILE_INFO")
    await update.callback_query.edit_message_text(text=profile_info)

@set_language
@action_wrapper
async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings_info = humanize("SETTINGS_INFO")
    await update.callback_query.edit_message_text(text=settings_info)

@set_language
@action_wrapper
async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = humanize("HELP_MESSAGE")
    await update.callback_query.edit_message_text(text=help_message, parse_mode=ParseMode.MARKDOWN)

@set_language
@action_wrapper
async def show_language_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    current_language = user.language_code if user.language_code else 'en'
    set_current_language(current_language)
    language_info = humanize("CURRENT_LANGUAGE_INFO").format(language=current_language)
    await update.callback_query.edit_message_text(text=language_info)

@set_language
@action_wrapper
async def admin_check_groups_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_bot_groups(update, context)

@set_language
@action_wrapper
async def admin_manage_users_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await manage_users(update, context)

@set_language
@action_wrapper
async def admin_backup_db_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        backup_file = await backup_database()
        if os.path.exists(backup_file):
            with open(backup_file, 'rb') as file:
                await update.callback_query.message.reply_document(
                    document=InputFile(file, filename='database_backup.zip'),
                    caption=humanize("BACKUP_CREATED")
                )
            os.remove(backup_file)
        else:
            await update.callback_query.message.reply_text(humanize("BACKUP_FILE_NOT_FOUND"))
    except Exception as e:
        logging.error(f"Error in backup_database: {str(e)}")
        await update.callback_query.message.reply_text(humanize("BACKUP_ERROR"))

@set_language
async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = humanize("HELP_MESSAGE")
    if update.callback_query:
        await update.callback_query.edit_message_text(text=help_message, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(text=help_message, parse_mode=ParseMode.MARKDOWN)
    await show_main_menu(update, context)

@set_language
async def change_language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    new_language = user.language_code if user.language_code else 'en'
    set_current_language(new_language)
    await update.message.reply_text(humanize("LANGUAGE_UPDATED"))
    await show_main_menu(update, context)

def setup_menu_handlers(application: Application):
    application.add_handler(CallbackQueryHandler(handle_menu_selection))
    application.add_handler(CommandHandler("help", show_help))
    application.add_handler(CommandHandler("start", show_main_menu))
    application.add_handler(CommandHandler("menu", show_main_menu))