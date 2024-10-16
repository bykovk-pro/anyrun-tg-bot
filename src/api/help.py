from telegram import Update
from telegram.ext import ContextTypes
from src.lang.director import humanize
from src.api.menu_utils import create_help_menu

async def show_help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = humanize("HELP_MENU_TEXT")
    reply_markup = create_help_menu()
    await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)
