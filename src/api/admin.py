from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.lang.director import humanize

def create_admin_panel_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_CHECK_BOT_GROUPS"), callback_data='check_bot_groups')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_MANAGE_USERS"), callback_data='manage_users')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_MANAGE_BOT"), callback_data='manage_bot')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='settings')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_manage_users_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_SHOW_ALL_USERS"), callback_data='show_all_users')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BAN_USER"), callback_data='ban_user')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_UNBAN_USER"), callback_data='unban_user')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_DELETE_USER"), callback_data='delete_user')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='admin_panel')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_manage_bot_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_RESTART_BOT"), callback_data='restart_bot')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_CHANGE_LOG_LEVEL"), callback_data='change_log_level')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_SHOW_BOT_LOGS"), callback_data='show_bot_logs')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_SHOW_BOT_STATS"), callback_data='show_bot_stats')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_SHOW_SYSTEM_INFO"), callback_data='show_system_info')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACKUP_DATABASE"), callback_data='backup_database')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='admin_panel')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = humanize("ADMIN_PANEL_MENU_TEXT")
    reply_markup = create_admin_panel_menu()
    await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)

async def show_manage_users_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = humanize("MANAGE_USERS_MENU_TEXT")
    reply_markup = create_manage_users_menu()
    await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)

async def show_manage_bot_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = humanize("MANAGE_BOT_MENU_TEXT")
    reply_markup = create_manage_bot_menu()
    await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)

# Здесь нужно добавить реализацию остальных функций админ-панели