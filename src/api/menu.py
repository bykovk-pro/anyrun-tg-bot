import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler, Application
from src.lang.director import humanize
from src.db.users import is_user_admin
from src.api.sandbox import run_url_analysis, run_file_analysis, show_history, show_api_limits
from src.api.settings import manage_api_key, change_language, check_access_rights, wipe_user_data
from src.api.admin import show_manage_bot_menu, show_manage_users_menu, show_admin_panel
from src.api.bot import (
    restart_bot, change_log_level, show_bot_logs,
    show_bot_stats, show_system_info, backup_database, restore_database,
    confirm_restart_bot, set_log_level
)
from src.api.help import show_help_menu
from src.api.users import show_all_users, process_user_action

def create_main_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_SANDBOX_API"), callback_data='sandbox_api')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_SETTINGS"), callback_data='settings')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_HELP"), callback_data='help')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_sandbox_api_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_RUN_URL_ANALYSIS"), callback_data='run_url_analysis')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_RUN_FILE_ANALYSIS"), callback_data='run_file_analysis')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_HISTORY"), callback_data='history')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_SHOW_API_LIMITS"), callback_data='show_api_limits')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_settings_menu(is_admin=False):
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_MANAGE_API_KEY"), callback_data='manage_api_key')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_CHANGE_LANGUAGE"), callback_data='change_language')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_CHECK_ACCESS_RIGHTS"), callback_data='check_access_rights')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_WIPE_DATA"), callback_data='wipe_data')]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton(humanize("MENU_BUTTON_ADMIN_PANEL"), callback_data='admin_panel')])
    keyboard.append([InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='main_menu')])
    return InlineKeyboardMarkup(keyboard)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = humanize("MAIN_MENU_TEXT")
    reply_markup = create_main_menu()

    if update.callback_query:
        await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(menu_text, reply_markup=reply_markup)

async def show_sandbox_api_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = humanize("SANDBOX_API_MENU_TEXT")
    reply_markup = create_sandbox_api_menu()
    await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)

async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_admin = await is_user_admin(user_id)
    menu_text = humanize("SETTINGS_MENU_TEXT")
    reply_markup = create_settings_menu(is_admin)
    await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)

async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    handlers = {
        'main_menu': show_main_menu,
        'sandbox_api': show_sandbox_api_menu,
        'settings': show_settings_menu,
        'help': show_help_menu,
        'run_url_analysis': run_url_analysis,
        'run_file_analysis': run_file_analysis,
        'history': show_history,
        'show_api_limits': show_api_limits,
        'manage_api_key': manage_api_key,
        'change_language': change_language,
        'check_access_rights': check_access_rights,
        'wipe_data': wipe_user_data,
        'admin_panel': show_admin_panel,
        'manage_users': show_manage_users_menu,
        'manage_bot': show_manage_bot_menu,
        'restart_bot': restart_bot,
        'confirm_restart_bot': confirm_restart_bot,
        'change_log_level': change_log_level,
        'show_bot_logs': show_bot_logs,
        'show_bot_stats': show_bot_stats,
        'show_system_info': show_system_info,
        'backup_database': backup_database,
        'restore_database': restore_database,
    }

    handler = handlers.get(query.data)
    if handler:
        await handler(update, context)
    else:
        if query.data.startswith('set_log_level_'):
            await set_log_level(update, context)
        elif query.data.startswith('show_users_page_'):
            page = int(query.data.split('_')[-1])
            await show_all_users(update, context, page)
        else:
            logging.warning(f"Unknown callback data: {query.data}")
            await query.edit_message_text(humanize("UNKNOWN_OPTION"))
            await asyncio.sleep(2)
            await show_main_menu(update, context)

def setup_menu_handlers(application: Application):
    application.add_handler(CallbackQueryHandler(handle_menu_selection))
    application.add_handler(CommandHandler("start", show_main_menu))
    application.add_handler(CommandHandler("menu", show_main_menu))