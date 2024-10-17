from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.lang.director import humanize
from src.db.users import db_is_user_admin
from src.api.menu_utils import create_main_menu, create_settings_menu, create_sandbox_api_menu

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = humanize("MAIN_MENU_TEXT")
    reply_markup = create_main_menu()

    if update.callback_query:
        await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(menu_text, reply_markup=reply_markup)
    
    context.user_data.pop('next_action', None)

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
