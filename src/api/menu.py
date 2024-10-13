from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.lang.director import humanize
from src.db.users import db_is_user_admin
from src.api.menu_utils import create_sandbox_api_menu, create_admin_menu, create_help_menu
from src.api.threat_intelligence import show_threat_intelligence_menu

def create_main_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_SANDBOX_API"), callback_data='sandbox_api')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_THREAT_INTELLIGENCE"), callback_data='threat_intelligence')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_SETTINGS"), callback_data='settings')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_HELP"), callback_data='help')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_settings_menu(is_admin=False):
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_MANAGE_API_KEY"), callback_data='manage_api_key')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_CHECK_ACCESS_RIGHTS"), callback_data='check_access_rights')]
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
    
    context.user_data.pop('next_action', None)  # Очищаем next_action при возврате в главное меню

async def show_sandbox_api_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = humanize("SANDBOX_API_MENU_TEXT")
    reply_markup = create_sandbox_api_menu()
    if update.callback_query:
        await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(menu_text, reply_markup=reply_markup)
    context.user_data.pop('next_action', None)

async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_admin = await db_is_user_admin(user_id)
    menu_text = humanize("SETTINGS_MENU_TEXT")
    reply_markup = create_settings_menu(is_admin)
    if update.callback_query:
        await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(menu_text, reply_markup=reply_markup)
    context.user_data.pop('next_action', None)
