import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.api.remote.sb_user import get_user_limits
from src.api.remote.sb_history import get_analysis_history
from src.db.api_keys import db_get_api_keys
from src.api.security import check_user_and_api_key
from src.api.menu_utils import create_sandbox_api_menu  # Импортируйте из нового файла
from src.api.menu import show_sandbox_api_menu  # Импортируйте из menu.py
from src.lang.director import humanize  # Импортируем humanize для получения текстов

async def run_url_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer(text="Run URL Analysis - Placeholder")

async def run_file_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer(text="Run File Analysis - Placeholder")

def create_history_menu(history, skip):
    keyboard = []
    logging.debug("New navigation keyboard created")
    for task in history:
        message_text = (
            f"**Name:** {task['name']}\n"
            f"**Verdict:** {task['verdict']}\n"
            f"**Date:** {task['date']}\n"
            f"**Tags:** {', '.join(task['tags'])}\n"
            f"**SHA256:** {task['hashes']['sha256']}\n"
            f"**UUID:** {task['uuid']}\n"
        )
        keyboard.append([InlineKeyboardButton(message_text, callback_data=f"task_info_{task['uuid']}")])
    
    nav_buttons = []
    logging.debug("New navigation buttons created")
    if skip > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data="show_history_previous"))
    if len(history) == 10:  # Если количество данных равно лимиту, значит, есть еще данные
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data="show_history_next"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
        logging.debug("Navigation buttons added to keyboard")
    
    keyboard.append([InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='sandbox_api')])
    return InlineKeyboardMarkup(keyboard)

async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logging.debug(f"User ID: {user_id} requesting history.")

    api_key, error_message = await check_user_and_api_key(user_id)

    if error_message:
        await update.callback_query.answer(text=error_message)
        logging.error(f"Error checking API key: {error_message}")
        return

    limit = 10
    skip = context.user_data.get('history_skip', 0)  # Получаем текущее значение skip из контекста
    logging.debug(f"Fetching analysis history with params: limit={limit}, skip={skip}")

    logging.debug("Calling get_analysis_history to fetch data from API")
    history = await get_analysis_history(api_key, limit, skip)

    if isinstance(history, dict) and "error" in history:
        await update.callback_query.answer(text=history["error"])
        logging.error(f"Error fetching history: {history['error']}")
        return

    # Логируем полученные данные
    logging.debug(f"Data received: {history}")

    # Проверяем, что history является списком
    if not isinstance(history, list):
        logging.error("Expected history to be a list.")
        await update.callback_query.answer(text="Error: Invalid data format received.")
        return

    # Создаем меню с историей
    reply_markup = create_history_menu(history, skip)
    menu_text = humanize("SHOW_HISTORY_MENU_TEXT")  # Добавьте текст меню
    await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)

async def show_api_limits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    api_key, error_message = await check_user_and_api_key(user_id)

    if error_message:
        await update.callback_query.answer(text=error_message)
        return

    limits_message = await get_user_limits(api_key)

    if isinstance(limits_message, dict) and "error" in limits_message:
        await update.callback_query.answer(text=limits_message["error"])
        return

    await update.callback_query.edit_message_text(limits_message)

    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='sandbox_api')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.reply_text(humanize("CHOOSE_OPTION"), reply_markup=reply_markup)

