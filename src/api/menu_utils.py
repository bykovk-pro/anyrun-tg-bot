from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.lang.director import humanize

def create_sandbox_api_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_RUN_URL_ANALYSIS"), callback_data='run_url_analysis')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_GET_REPORT_BY_UUID"), callback_data='get_report_by_uuid')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_GET_HISTORY"), callback_data='get_history')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_SHOW_API_LIMITS"), callback_data='show_api_limits')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_admin_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_CHECK_BOT_GROUPS"), callback_data='check_bot_groups')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_MANAGE_USERS"), callback_data='manage_users')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_MANAGE_BOT"), callback_data='manage_bot')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='settings')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_help_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_SANDBOX_SERVICE"), url='https://app.any.run/')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_API_DOCUMENTATION"), url='https://any.run/api-documentation/')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)
