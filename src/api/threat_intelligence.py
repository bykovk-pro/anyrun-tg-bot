from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.lang.director import humanize

def create_threat_intelligence_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def show_threat_intelligence_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = humanize("THREAT_INTELLIGENCE_MENU_TEXT")
    reply_markup = create_threat_intelligence_menu()
    
    if update.callback_query:
        await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(menu_text, reply_markup=reply_markup)

