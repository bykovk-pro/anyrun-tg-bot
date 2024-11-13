import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import BadRequest
from src.api.remote.sb_user import get_user_limits
from src.api.remote.sb_history import get_analysis_history
from src.api.reports import display_report_info
from src.api.security import check_user_access
from src.lang.director import humanize
from src.api.remote.sb_task_info import process_task_info, ResultType
from src.api.remote.sb_analysis import run_url_analysis, run_file_analysis
from src.api.menu_utils import create_sandbox_api_menu
from src.api.remote.sb_status import get_analysis_status
from src.api.remote.sb_reports import get_report_by_uuid as remote_get_report_by_uuid
from src.db.active_tasks import set_task_inactive
import validators
import asyncio
import json
import re
from typing import Optional

def extract_url(text: str, max_url_length: int = 2048) -> Optional[str]:
    """Extract first URL from text using regex pattern, supporting both plain URLs and markdown links."""
    if not text or len(text) > 10000:  # Reasonable limit for input text
        return None
        
    # Pattern for markdown links [text](url)
    markdown_pattern = r'\[([^\]]+)\]\((https?://[^\s\)]{1,2048})\)'
    # Pattern for plain URLs
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2})){1,2048}[^\s]*'
    
    # First try to find markdown links
    markdown_match = re.search(markdown_pattern, text)
    if markdown_match:
        url = markdown_match.group(2)
        return url if len(url) <= max_url_length else None
    
    # If no markdown links found, look for plain URLs
    url_match = re.search(url_pattern, text)
    if url_match:
        url = url_match.group(0)
        return url if len(url) <= max_url_length else None
    
    return None

async def sandbox_api_action(update: Update, context: ContextTypes.DEFAULT_TYPE, action_func):
    user_id = update.effective_user.id
    logging.debug(f"User ID: {user_id} requesting sandbox API action: {action_func.__name__}")

    access_granted, api_key = await check_user_access(context.bot, user_id)
    if not access_granted:
        await update.callback_query.answer(text=api_key)
        logging.info(f"Access denied for user {user_id}: {api_key}")
        return

    logging.debug(f"Access granted for user {user_id}, executing {action_func.__name__}")
    await action_func(update, context, api_key)

async def run_url_analysis_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await sandbox_api_action(update, context, _run_url_analysis)

async def run_file_analysis_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await sandbox_api_action(update, context, _run_file_analysis)

async def _run_url_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, api_key: str):
    await update.callback_query.edit_message_text(humanize("ENTER_URL_TO_ANALYZE"))
    context.user_data['next_action'] = 'run_url_analysis'
    context.user_data['api_key'] = api_key

async def _run_file_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, api_key: str):
    await update.callback_query.edit_message_text(humanize("UPLOAD_FILE_TO_ANALYZE"))
    context.user_data['next_action'] = 'run_file_analysis'
    context.user_data['api_key'] = api_key

async def process_url_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    
    # Detailed debug logging
    logging.debug("=" * 50)
    logging.debug("Processing message:")
    logging.debug(f"Message ID: {message.message_id}")
    logging.debug(f"From user: {update.effective_user.id}")
    logging.debug(f"Raw message text: '{message.text}'")
    
    # Get text from message considering different message types
    message_text = ''
    
    try:
        # First check for entities with URLs
        if message.entities:
            for entity in message.entities:
                if entity.type == 'text_link' and hasattr(entity, 'url'):
                    message_text = entity.url
                    logging.debug(f"Found URL in text_link entity: {message_text}")
                    break
                elif entity.type == 'url' and message.text:
                    url_text = message.text[entity.offset:entity.offset + entity.length]
                    message_text = url_text
                    logging.debug(f"Found URL in url entity: {message_text}")
                    break
        
        # If no URL found in entities, try regular text
        if not message_text and message.text:
            message_text = message.text.strip()
            logging.debug(f"Using plain message text: {message_text}")
        
        if not message_text:
            logging.warning(f"No text found in message from user {update.effective_user.id}")
            await update.message.reply_text(humanize("INVALID_INPUT"))
            return

        # Extract URL from message text
        url = extract_url(message_text)
        logging.debug(f"Extracted URL: {url}")
        
        if not url:
            logging.info(f"User {update.effective_user.id} provided text without URL: {message_text}")
            await update.message.reply_text(humanize("INVALID_INPUT"))
            return

        # Validate extracted URL
        if not validators.url(url):
            logging.warning(f"User {update.effective_user.id} provided invalid URL: {url}")
            await update.message.reply_text(humanize("INVALID_INPUT"))
            return

        access_granted, api_key = await check_user_access(context.bot, update.effective_user.id)
        if not access_granted:
            logging.warning(f"Access denied for user {update.effective_user.id}")
            await update.message.reply_text(api_key)
            return

        logging.info(f"Processing URL analysis for user {update.effective_user.id}: {url}")
        result = await run_url_analysis(api_key, url, update.effective_user.id)

        if 'error' in result:
            logging.error(f"URL analysis error for user {update.effective_user.id}: {result['error']}")
            await update.message.reply_text(humanize("URL_ANALYSIS_ERROR").format(error=result['error']))
        else:
            logging.info(f"URL analysis submitted for user {update.effective_user.id}, task_id: {result['task_id']}")
            await update.message.reply_text(humanize("URL_ANALYSIS_SUBMITTED_CHECK_ACTIVE").format(uuid=result['task_id']))
            asyncio.create_task(monitor_analysis_status(update, context, api_key, result['task_id']))

        await show_sandbox_api_menu(update, context)
            
    except AttributeError as e:
        logging.error(f"Error accessing message attributes: {e}")
        await update.message.reply_text(humanize("INVALID_INPUT"))
        return

async def process_file_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text(humanize("INVALID_INPUT"))
        return

    access_granted, api_key = await check_user_access(context.bot, update.effective_user.id)
    if not access_granted:
        await update.message.reply_text(api_key)
        return

    file = await context.bot.get_file(update.message.document.file_id)
    file_content = await file.download_as_bytearray()

    result = await run_file_analysis(api_key, file_content, update.message.document.file_name, update.effective_user.id)

    if 'error' in result:
        await update.message.reply_text(humanize("FILE_ANALYSIS_ERROR").format(error=result['error']))
    else:
        await update.message.reply_text(humanize("FILE_ANALYSIS_SUBMITTED_CHECK_ACTIVE").format(uuid=result['task_id']))
        asyncio.create_task(monitor_analysis_status(update, context, api_key, result['task_id']))

    await show_sandbox_api_menu(update, context)

async def monitor_analysis_status(update: Update, context: ContextTypes.DEFAULT_TYPE, api_key: str, task_id: str):
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=humanize("ANALYSIS_STATUS").format(status=humanize("ANALYSIS_STATUS_RUNNING"))
    )

    last_status = None
    max_attempts = 60
    for _ in range(max_attempts):
        status = await get_analysis_status(api_key, task_id)
        
        if 'error' in status:
            logging.error(f"Error getting analysis status: {status['error']}")
            await message.edit_text(humanize("API_REQUEST_FAILED"))
            return

        if status != last_status:
            try:
                await message.edit_text(humanize("ANALYSIS_STATUS").format(status=status['message']))
                last_status = status
            except BadRequest as e:
                if "Message is not modified" not in str(e):
                    logging.error(f"Error updating message: {e}")

        if status['status'] in ['completed', 'failed']:
            await set_task_inactive(task_id)
            if status['status'] == 'completed':
                report = await remote_get_report_by_uuid(api_key, task_id)
                if report:
                    context.user_data['current_report'] = report
                    await display_report_info(update, context, report)
                else:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=humanize("ANALYSIS_COMPLETED_NO_REPORT").format(uuid=task_id)
                    )
            return

        await asyncio.sleep(5)

    await message.edit_text(humanize("ANALYSIS_TAKING_LONG").format(uuid=task_id))

async def get_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await sandbox_api_action(update, context, _show_history)

async def _show_history(update: Update, context: ContextTypes.DEFAULT_TYPE, api_key: str):
    user_id = update.effective_user.id
    logging.debug(f"User ID: {user_id} requesting history.")
    logging.debug(f"API Key (first 5 chars): {api_key[:5]}...")

    limit = 10
    skip = 0
    logging.debug(f"Fetching analysis history with params: limit={limit}, skip={skip}")
    history = await get_analysis_history(api_key, limit, skip)

    if isinstance(history, dict) and "error" in history:
        await update.callback_query.answer(text=history["error"])
        logging.error(f"Error fetching history: {history['error']}")
        return

    if not isinstance(history, list):
        logging.error(f"Expected history to be a list, but got {type(history)}.")
        await update.callback_query.answer(text=humanize("INVALID_DATA_FORMAT"))
        return

    if not history:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=humanize("NO_ANALYSIS_HISTORY"))
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=humanize("LAST_TEN_REPORTS"))
        
        for analysis in history:
            verdict = analysis.get('verdict', 'Unknown')
            date = analysis.get('date', '')
            name = analysis.get('name', '')
            uuid = analysis.get('uuid', '')
            tags = analysis.get('tags', [])
            status = analysis.get('status', 'unknown')

            text_message = process_task_info(verdict, date, name, uuid, tags, status, ResultType.TEXT)

            if text_message.strip():
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text_message, parse_mode='MarkdownV2')

    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='sandbox_api')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=humanize("CHOOSE_OPTION"), reply_markup=reply_markup)

async def show_api_limits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await sandbox_api_action(update, context, _show_api_limits)

async def _show_api_limits(update: Update, context: ContextTypes.DEFAULT_TYPE, api_key: str):
    user_id = update.effective_user.id
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

async def show_sandbox_api_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    access_granted, api_key = await check_user_access(context.bot, update.effective_user.id)
    if not access_granted:
        await send_message(update, api_key)
        return

    reply_markup = create_sandbox_api_menu()
    await send_message(update, humanize("SANDBOX_API_MENU_TEXT"), reply_markup=reply_markup)

async def send_message(update: Update, text: str, reply_markup=None, parse_mode=None):
    try:
        if update.callback_query:
            return await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        else:
            return await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        logging.error(f"Error sending message: {str(e)}")
        return await send_message(update, text, reply_markup=reply_markup, parse_mode=None)
