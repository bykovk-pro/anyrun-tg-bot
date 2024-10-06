from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.lang.director import humanize

def create_help_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_SANDBOX_SERVICE"), callback_data='sandbox_service')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_API_DOCUMENTATION"), callback_data='api_documentation')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_SEND_FEEDBACK"), callback_data='send_feedback')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def show_help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = humanize("HELP_MENU_TEXT")
    reply_markup = create_help_menu()
    await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)

async def open_sandbox_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Реализация открытия сервиса ANY.RUN Sandbox
    pass

async def open_api_documentation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Реализация открытия API документации
    pass

async def send_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Реализация отправки обратной связи
    pass
