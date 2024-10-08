from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.lang.director import humanize

def create_history_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_GET_HISTORY"), callback_data='get_history')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_GET_REPORT_BY_UUID"), callback_data='get_report_by_uuid')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='sandbox_api')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def run_url_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer(text="Run URL Analysis - Placeholder")

async def run_file_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer(text="Run File Analysis - Placeholder")

async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Удаляем функцию show_history, так как она больше не нужна
    pass

async def show_api_limits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer(text="Show API Limits - Placeholder")
