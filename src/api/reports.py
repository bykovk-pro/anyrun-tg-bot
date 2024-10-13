import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
from telegram.ext import ContextTypes
from src.lang.director import humanize
from src.api.remote.sb_reports import get_report_by_uuid
from src.api.security import check_user_and_api_key
from src.api.menu import show_sandbox_api_menu
from src.api.menu_utils import escape_markdown
import validators
from datetime import datetime

async def handle_get_reports_by_uuid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the update is a callback query
    if update.callback_query:
        await update.callback_query.answer()
        # Запрашиваем UUID
        await update.callback_query.edit_message_text(humanize("ENTER_UUID_TO_GET_REPORT"))
    else:
        await update.message.reply_text(humanize("ENTER_UUID_TO_GET_REPORT"))

    context.user_data['next_action'] = 'get_reports_by_uuid'

async def process_uuid_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the update is a message and has text
    if not update.message or not update.message.text:
        logging.error(f"Invalid update received: {update}")
        await show_sandbox_api_menu(update, context)
        return

    uuid = update.message.text.strip()
    
    # Validate UUID
    if not validators.uuid(uuid):
        await update.message.reply_text(humanize("INVALID_UUID"))
        await show_sandbox_api_menu(update, context)
        return

    user_id = update.effective_user.id
    api_key, error_message = await check_user_and_api_key(user_id)
    
    # Check if API key is valid
    if error_message:
        await update.message.reply_text(error_message)
        await show_sandbox_api_menu(update, context)
        return

    # Отправляем сообщение о начале загрузки отчета
    await update.message.reply_text(humanize("REPORT_LOADING"))

    report = await get_report_by_uuid(api_key, uuid)

    # Save report in context for later use
    context.user_data['current_report'] = report

    logging.debug(f"Report fetched successfully for UUID: {uuid}")
    await display_report_info(update, context, report)

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_action = context.user_data.get('next_action')
    if next_action == 'get_reports_by_uuid':
        await process_uuid_input(update, context)
    else:
        await update.message.reply_text(humanize("UNKNOWN_COMMAND"))
        await show_sandbox_api_menu(update, context)
    
    if 'next_action' in context.user_data:
        del context.user_data['next_action']

async def display_report_info(update: Update, context: ContextTypes.DEFAULT_TYPE, report):
    main_object = report.get("content", {}).get("mainObject", {})
    name = main_object.get("filename") if main_object.get("type") == "file" else main_object.get("url", "Unknown")

    icon = {
        "No threats detected": "🔵",
        "Suspicious activity": "🟡",
        "Malicious activity": "🔴"
    }.get(report.get("scores", {}).get("verdict", {}).get("threatLevelText", "Unknown"), "⚪")

    text_message = (
        f"{icon}\u00A0***{escape_markdown(datetime.fromisoformat(report.get('creationText', '')).strftime('%d %B %Y, %H:%M'))}***\n"
        f"📄\u00A0`{escape_markdown(name)}`\n"
        f"🆔\u00A0`{escape_markdown(report.get('uuid', 'Unknown'))}`\n"
    )

    tags = report.get("tags", [])
    tag_strings = [escape_markdown(tag['tag']) for tag in tags if 'tag' in tag]
    if tag_strings:
        text_message += f"🏷️\u00A0\\[***{'***\\] \\[***'.join(tag_strings)}***\\]"

    await update.message.reply_text(text_message, parse_mode='MarkdownV2')
    await show_report_menu(update, context, report)

async def show_report_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, report):
    content = report.get("content", {})
    main_object = content.get("mainObject", {})
    video_url = content.get("video", {}).get("permanentUrl")
    screenshots = content.get("screenshots", [])

    keyboard = [
        [InlineKeyboardButton(humanize("ANALYSIS_IN_SANDBOX"), url=report.get("permanentUrl", ""))]
    ]

    if video_url:
        keyboard.append([InlineKeyboardButton(humanize("SHOW_RECORDED_VIDEO"), callback_data='show_recorded_video')])
    if screenshots:
        keyboard.append([InlineKeyboardButton(humanize("SHOW_CAPTURED_SCREENSHOTS"), callback_data='show_captured_screenshots')])

    keyboard.extend([
        [InlineKeyboardButton(humanize("TEXT_REPORT"), url=f"https://any.run/report/{main_object.get('hashes', {}).get('sha256', '')}/{report.get('uuid', '')}")],
        [InlineKeyboardButton(humanize("REPORT_HTML"), url=report.get("reports", {}).get("HTML", ""))],
        [InlineKeyboardButton(humanize("REPORT_ANYRUN"), url=f"https://api.any.run/report/{report.get('uuid', '')}/summary/json")],
        [InlineKeyboardButton(humanize("REPORT_STIX"), url=report.get("reports", {}).get("STIX", ""))],
        [InlineKeyboardButton(humanize("REPORT_MISP"), url=report.get("reports", {}).get("MISP", ""))],
        [InlineKeyboardButton(humanize("ALL_IOC"), url=report.get("reports", {}).get("IOC", ""))]
    ])

    if main_object.get("type") == "file":
        keyboard.append([InlineKeyboardButton(humanize("DOWNLOAD_SAMPLE"), url=main_object.get("permanentUrl", ""))])

    if report.get("pcap", {}).get("present") == "true":
        keyboard.append([InlineKeyboardButton(humanize("DOWNLOAD_PCAP"), url=report["pcap"]["permanentUrl"])])

    keyboard.append([InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='sandbox_api')])

    reply_markup = InlineKeyboardMarkup(keyboard)
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

    # Используем функцию для создания клавиатуры
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

    # Используем функцию для создания клавиатуры
    reply_markup = create_report_menu_keyboard(report)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=humanize("GET_REPORTS_FOR_UUID"), reply_markup=reply_markup)

def create_report_menu_keyboard(report):
    keyboard = [
        [InlineKeyboardButton(humanize("ANALYSIS_IN_SANDBOX"), url=report.get("permanentUrl", ""))]
    ]

    video_url = report.get("content", {}).get("video", {}).get("permanentUrl")
    if video_url:
        keyboard.append([InlineKeyboardButton(humanize("SHOW_RECORDED_VIDEO"), callback_data='show_recorded_video')])

    screenshots = report.get("content", {}).get("screenshots", [])
    if screenshots:
        keyboard.append([InlineKeyboardButton(humanize("SHOW_CAPTURED_SCREENSHOTS"), callback_data='show_captured_screenshots')])

    keyboard.extend([
        [InlineKeyboardButton(humanize("TEXT_REPORT"), url=f"https://any.run/report/{report.get('mainObject', {}).get('hashes', {}).get('sha256', '')}/{report.get('uuid', '')}")],
        [InlineKeyboardButton(humanize("REPORT_HTML"), url=report.get("reports", {}).get("HTML", ""))],
        [InlineKeyboardButton(humanize("REPORT_ANYRUN"), url=f"https://app.any.run/report/{report.get('uuid', '')}/summary/json")],
        [InlineKeyboardButton(humanize("REPORT_STIX"), url=report.get("reports", {}).get("STIX", ""))],
        [InlineKeyboardButton(humanize("REPORT_MISP"), url=report.get("reports", {}).get("MISP", ""))],
        [InlineKeyboardButton(humanize("ALL_IOC"), url=report.get("reports", {}).get("IOC", ""))]
    ])

    if report.get("mainObject", {}).get("type") == "file":
        keyboard.append([InlineKeyboardButton(humanize("DOWNLOAD_SAMPLE"), url=report.get("mainObject", {}).get("permanentUrl", ""))])

    if report.get("pcap", {}).get("present") == "true":
        keyboard.append([InlineKeyboardButton(humanize("DOWNLOAD_PCAP"), url=report["pcap"]["permanentUrl"])])

    keyboard.append([InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='sandbox_api')])

    return InlineKeyboardMarkup(keyboard)
