from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.lang.director import humanize

def create_manage_api_key_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_SHOW_API_KEYS"), callback_data='show_api_keys')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_ADD_API_KEY"), callback_data='add_api_key')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_DELETE_API_KEY"), callback_data='delete_api_key')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_CHANGE_API_KEY_NAME"), callback_data='change_api_key_name')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_SET_ACTIVE_API_KEY"), callback_data='set_active_api_key')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='settings')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_change_language_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_AUTO_DETECT_LANGUAGE"), callback_data='auto_detect_language')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_SET_LANGUAGE"), callback_data='set_language')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='settings')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def manage_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = humanize("MANAGE_API_KEY_MENU_TEXT")
    reply_markup = create_manage_api_key_menu()
    await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = humanize("CHANGE_LANGUAGE_MENU_TEXT")
    reply_markup = create_change_language_menu()
    await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)

async def check_access_rights(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Реализация проверки прав доступа
    pass

async def wipe_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Реализация удаления данных пользователя
    pass