import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.api.remote.sb_user import get_user_limits
from src.api.remote.sb_history import get_analysis_history
from src.api.security import check_user_and_api_key
from src.api.menu_utils import create_sandbox_api_menu
from src.api.menu import show_sandbox_api_menu
from src.lang.director import humanize
from datetime import datetime

def escape_markdown(text):
    if text is None:
        return ''
    return text.replace('\\', '\\\\') \
               .replace('*', '\\*') \
               .replace('_', '\\_') \
               .replace('[', '\\[') \
               .replace(']', '\\]') \
               .replace('(', '\\(') \
               .replace(')', '\\)') \
               .replace('~', '\\~') \
               .replace('>', '\\>') \
               .replace('#', '\\#') \
               .replace('+', '\\+') \
               .replace('-', '\\-') \
               .replace('=', '\\=') \
               .replace('|', '\\|') \
               .replace('{', '\\{') \
               .replace('}', '\\}') \
               .replace('.', '\\.') \
               .replace('!', '\\!')

async def run_url_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer(text=humanize("RUN_URL_ANALYSIS_PLACEHOLDER"))

async def run_file_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer(text=humanize("RUN_FILE_ANALYSIS_PLACEHOLDER"))

async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logging.debug(f"User ID: {user_id} requesting history.")

    api_key, error_message = await check_user_and_api_key(user_id)

    if error_message:
        await update.callback_query.answer(text=error_message)
        logging.error(f"Error checking API key: {error_message}")
        return

    limit = 10
    skip = 0
    logging.debug(f"Fetching analysis history with params: limit={limit}, skip={skip}")
    logging.debug("Calling get_analysis_history to fetch data from API")
    history = await get_analysis_history(api_key, limit, skip)

    if isinstance(history, dict) and "error" in history:
        await update.callback_query.answer(text=history["error"])
        logging.error(f"Error fetching history: {history['error']}")
        return

    if not isinstance(history, list):
        logging.error("Expected history to be a list.")
        await update.callback_query.answer(text=humanize("INVALID_DATA_FORMAT"))
        return

    for index, task in enumerate(history):
        if task['verdict'] == 'No threats detected':
            icon = '🔵'
        elif task['verdict'] == 'Suspicious activity':
            icon = '🟡'
        elif task['verdict'] == 'Malicious activity':
            icon = '🔴'
        else:
            icon = '⚪'

        text_message = (
            f"{icon}\u00A0***{escape_markdown(datetime.fromisoformat(task['date']).strftime('%d %B %Y, %H:%M'))}***\n"
            f"📄\u00A0`{task['name']}`\n"
            f"🆔\u00A0`{escape_markdown(task['uuid'])}`\n"
        )
        if task['tags']:
            text_message += f"🏷️\u00A0\\[***{'***\\] \\[***'.join(escape_markdown(tag) for tag in task['tags'])}***\\]"

        if text_message.strip():
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text_message, parse_mode='MarkdownV2')

    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='sandbox_api')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=humanize("CHOOSE_OPTION"), reply_markup=reply_markup)

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