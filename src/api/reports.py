import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
from telegram.ext import ContextTypes
from src.lang.director import humanize
from src.api.remote.sb_reports import get_report_by_uuid
from src.api.security import check_user_and_api_key
from src.api.menu import show_sandbox_api_menu
import validators
from src.api.remote.sb_task_info import process_task_info, ResultType
from src.api.menu_utils import create_report_menu_keyboard

async def handle_get_reports_by_uuid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(humanize("ENTER_UUID_TO_GET_REPORT"))
    else:
        await update.message.reply_text(humanize("ENTER_UUID_TO_GET_REPORT"))

    context.user_data['next_action'] = 'get_reports_by_uuid'

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_action = context.user_data.get('next_action')
    if next_action == 'get_reports_by_uuid':
        await process_uuid_input(update, context)
    else:
        await update.message.reply_text(humanize("UNKNOWN_COMMAND"))
        await show_sandbox_api_menu(update, context)
    
    if 'next_action' in context.user_data:
        del context.user_data['next_action']

async def process_uuid_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        logging.error(f"Invalid update received: {update}")
        await show_sandbox_api_menu(update, context)
        return

    uuid = update.message.text.strip()
    
    if not validators.uuid(uuid):
        await update.message.reply_text(humanize("INVALID_UUID"))
        await show_sandbox_api_menu(update, context)
        return

    api_key = context.user_data.get('api_key')
    if not api_key:
        await update.message.reply_text(humanize("API_KEY_NOT_FOUND"))
        await show_sandbox_api_menu(update, context)
        return

    await update.message.reply_text(humanize("REPORT_LOADING"))

    report = await get_report_by_uuid(api_key, uuid)

    context.user_data['current_report'] = report

    logging.debug(f"Report fetched successfully for UUID: {uuid}")
    await display_report_info(update, context, report)

async def display_report_info(update: Update, context: ContextTypes.DEFAULT_TYPE, report):
    main_object = report.get("content", {}).get("mainObject", {})
    name = main_object.get("filename") if main_object.get("type") == "file" else main_object.get("url", "Unknown")

    verdict = report.get("scores", {}).get("verdict", {}).get("threatLevelText", "Unknown")
    date = report.get("creationText", "")
    uuid = report.get("uuid", "Unknown")
    tags = [tag['tag'] for tag in report.get("tags", []) if 'tag' in tag]

    text_message = process_task_info(verdict, date, name, uuid, tags, ResultType.TEXT)

    await update.message.reply_text(text_message, parse_mode='MarkdownV2')
    await show_report_menu(update, context, report)

async def show_report_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, report):
    reply_markup = create_report_menu_keyboard(report)
    report_message = f"{humanize('GET_REPORTS_FOR_UUID')}"
    
    if update.callback_query:
        await update.callback_query.edit_message_text(report_message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(report_message, reply_markup=reply_markup)

async def handle_show_recorded_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    report = context.user_data.get('current_report')
    if not report:
        logging.error("No report data found in the context.")
        await query.edit_message_text(humanize("NO_REPORT_DATA"))
        return

    video_url = report.get("content", {}).get("video", {}).get("permanentUrl")
    if video_url:
        logging.debug(f"Sending video URL: {video_url}")
        await query.delete_message()
        await context.bot.send_video(chat_id=update.effective_chat.id, video=video_url, caption=humanize("RECORDED_ANALYSIS_VIDEO"), supports_streaming=True)

    reply_markup = create_report_menu_keyboard(report)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=humanize("GET_REPORTS_FOR_UUID"), reply_markup=reply_markup)

async def handle_show_captured_screenshots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    report = context.user_data.get('current_report')
    if not report:
        logging.error("No report data found in the context.")
        await query.edit_message_text(humanize("NO_REPORT_DATA"))
        return

    screenshots = report.get("content", {}).get("screenshots", [])
    if screenshots:
        total_albums = (len(screenshots) + 9) // 10
        await query.delete_message()
        for i in range(0, len(screenshots), 10):
            media_group = [InputMediaPhoto(screenshot["permanentUrl"]) for screenshot in screenshots[i:i + 10]]
            current_album = i // 10 + 1
            caption = humanize("CAPTURED_ANALYSIS_SCREENSHOTS")
            if total_albums > 1:
                caption += f" - Album {current_album}/{total_albums}"
            await context.bot.send_media_group(chat_id=update.effective_chat.id, media=media_group, caption=caption)

    reply_markup = create_report_menu_keyboard(report)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=humanize("GET_REPORTS_FOR_UUID"), reply_markup=reply_markup)
