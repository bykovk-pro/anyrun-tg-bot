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

async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    api_key, error_message = await check_user_and_api_key(user_id)

    if error_message:
        await update.callback_query.answer(text=error_message)
        return

    # Получаем текущий сдвиг для пагинации
    limit = 10
    skip = context.user_data.get('history_skip', 0)  # Получаем текущий сдвиг

    # Получаем историю с API
    history = await get_analysis_history(api_key, limit, skip)

    if isinstance(history, dict) and "error" in history:
        await update.callback_query.answer(text=history["error"])
        return

    # Формируем текст сообщения
    messages = []
    for task in history:
        date = task['date']  # Assuming the date is in the correct format
        name = task['name']
        verdict = task['verdict']
        tags = ', '.join(task['tags'])  # Assuming tags is a list
        sha256 = task['hashes']['sha256']
        uuid = task['uuid']

        message_text = (
            f"**Name:** {name}\n"
            f"**Verdict:** {verdict}\n"
            f"**Date:** {date}\n"
            f"**Tags:** {tags}\n"
            f"**SHA256:** {sha256}\n"
            f"**UUID:** {uuid}\n"
        )
        messages.append(message_text)

    # Отправляем сообщения
    if messages:
        await update.callback_query.message.reply_text("\n\n".join(messages))

    # Создаем кнопки для пагинации
    keyboard = []
    if skip > 0:
        keyboard.append([InlineKeyboardButton("Previous", callback_data='history_previous')])
    if len(history) == limit:  # Only show "Next" if there are more results
        keyboard.append([InlineKeyboardButton("Next", callback_data='history_next')])
    keyboard.append([InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='sandbox_api')])  # Back button added

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем кнопки
    await update.callback_query.message.reply_text(humanize("CHOOSE_OPTION"), reply_markup=reply_markup)

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

    # Удаляем меню перед показом лимитов
    await update.callback_query.edit_message_text(limits_message)

    # Создаем кнопку "Back to Sandbox API Menu"
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='sandbox_api')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем кнопку
    await update.callback_query.message.reply_text(humanize("CHOOSE_OPTION"), reply_markup=reply_markup)

async def handle_history_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Получаем текущий сдвиг
    skip = context.user_data.get('history_skip', 0)

    if query.data == 'history_previous':
        skip = max(0, skip - 10)  # Уменьшаем сдвиг, но не меньше 0
    elif query.data == 'history_next':
        skip += 10  # Увеличиваем сдвиг на 10

    context.user_data['history_skip'] = skip  # Сохраняем новый сдвиг
    await show_history(update, context)  # Показать историю с новым сдвигом
