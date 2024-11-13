from telegram import Update
from telegram.ext import (
    CommandHandler, MessageHandler, CallbackQueryHandler, 
    filters, Application, ContextTypes
)
from src.api.menu import (
    show_main_menu, show_sandbox_api_menu, show_settings_menu
)
from src.api.settings import (
    manage_api_key, show_api_keys, add_api_key, delete_api_key,
    change_api_key_name, set_active_api_key, handle_api_key_actions,
    check_access_rights, handle_group_info, handle_text_input as settings_handle_text_input
)
from src.api.help import (
    show_help_menu
)
from src.api.admin import (
    show_admin_panel, show_manage_users_menu, show_manage_bot_menu 
)
from src.api.bot import (
    show_system_info, backup_database,
    restore_database, process_database_restore
)
from src.api.sandbox import (
    get_history, show_api_limits,
    run_url_analysis_handler, run_file_analysis_handler,
    process_url_analysis, process_file_analysis, extract_url
)
from src.api.users import (
    show_all_users, ban_user, unban_user, delete_user
)
from src.api.reports import handle_text_input as reports_handle_text_input, handle_show_recorded_video, handle_show_captured_screenshots, handle_get_reports_by_uuid
from src.lang.director import humanize
import logging
from src.api.threat_intelligence import show_threat_intelligence_menu
import validators
import asyncio
from src.api.remote.sb_analysis import run_url_analysis
from src.api.security import check_user_access
from src.api.sandbox import monitor_analysis_status


def setup_handlers(application: Application):
    application.add_handler(CommandHandler("start", show_main_menu))
    application.add_handler(CommandHandler("menu", show_main_menu))

    application.add_handler(MessageHandler(
        filters.FORWARDED & (filters.Document.ALL | filters.TEXT), 
        handle_forwarded_message
    ), group=1)
    
    application.add_handler(MessageHandler(
        filters.Document.ALL & filters.ChatType.PRIVATE & ~filters.FORWARDED,
        handle_file_input
    ), group=2)

    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & ~filters.FORWARDED, 
        handle_text_input
    ), group=2)

    application.add_handler(CallbackQueryHandler(show_main_menu, pattern='^main_menu$'))
    application.add_handler(CallbackQueryHandler(show_sandbox_api_menu, pattern='^sandbox_api$'))
    application.add_handler(CallbackQueryHandler(show_settings_menu, pattern='^settings$'))
    application.add_handler(CallbackQueryHandler(show_help_menu, pattern='^help$'))

    application.add_handler(CallbackQueryHandler(handle_get_reports_by_uuid, pattern='^get_report_by_uuid$'))
    application.add_handler(CallbackQueryHandler(get_history, pattern='^get_history$'))
    application.add_handler(CallbackQueryHandler(show_api_limits, pattern='^show_api_limits$'))

    application.add_handler(CallbackQueryHandler(manage_api_key, pattern='^manage_api_key$'))
    application.add_handler(CallbackQueryHandler(show_api_keys, pattern='^show_api_keys$'))
    application.add_handler(CallbackQueryHandler(add_api_key, pattern='^add_api_key$'))
    application.add_handler(CallbackQueryHandler(delete_api_key, pattern='^delete_api_key$'))
    application.add_handler(CallbackQueryHandler(change_api_key_name, pattern='^change_api_key_name$'))
    application.add_handler(CallbackQueryHandler(set_active_api_key, pattern='^set_active_api_key$'))
    application.add_handler(CallbackQueryHandler(handle_api_key_actions, pattern='^(delete_|rename_|activate_|back_to_manage_api_key)'))

    application.add_handler(CallbackQueryHandler(check_access_rights, pattern='^check_access_rights$'))

    application.add_handler(CallbackQueryHandler(show_admin_panel, pattern='^admin_panel$'))
    application.add_handler(CallbackQueryHandler(show_manage_users_menu, pattern='^manage_users$'))
    application.add_handler(CallbackQueryHandler(show_manage_bot_menu, pattern='^manage_bot$'))

    application.add_handler(CallbackQueryHandler(show_system_info, pattern='^show_system_info$'))
    application.add_handler(CallbackQueryHandler(backup_database, pattern='^backup_database$'))
    application.add_handler(CallbackQueryHandler(restore_database, pattern='^restore_database$'))

    application.add_handler(CallbackQueryHandler(show_all_users, pattern='^show_all_users$'))
    application.add_handler(CallbackQueryHandler(ban_user, pattern='^ban_user$'))
    application.add_handler(CallbackQueryHandler(unban_user, pattern='^unban_user$'))
    application.add_handler(CallbackQueryHandler(delete_user, pattern='^delete_user$'))

    application.add_handler(MessageHandler(filters.Document.ALL, process_database_restore))

    application.add_handler(CallbackQueryHandler(handle_group_info, pattern='^group_info_'))

    application.add_handler(CallbackQueryHandler(handle_show_recorded_video, pattern='^show_recorded_video$'))
    application.add_handler(CallbackQueryHandler(handle_show_captured_screenshots, pattern='^show_captured_screenshots$'))

    application.add_handler(CallbackQueryHandler(show_threat_intelligence_menu, pattern='^threat_intelligence$'))

    application.add_handler(CallbackQueryHandler(run_url_analysis_handler, pattern='^run_url_analysis$'))
    application.add_handler(CallbackQueryHandler(run_file_analysis_handler, pattern='^run_file_analysis$'))

    application.add_handler(CallbackQueryHandler(show_all_users, pattern=r'^show_users_page_\d+$'))

async def handle_forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle any forwarded message (file or text with URL)."""
    message = update.message
    try:
        # Проверяем сначала на наличие файла
        if message.document:
            logging.info(f"Processing forwarded file: {message.document.file_name}")
            await process_forwarded_file(update, context, message.document)
            return

        # Если нет файла, проверяем на наличие URL
        message_text = message.text or message.caption or ''
        
        # Проверяем entities на наличие URL
        url = None
        if message.entities:
            for entity in message.entities:
                if entity.type == 'text_link' and hasattr(entity, 'url'):
                    url = entity.url
                    break
                elif entity.type == 'url' and message.text:
                    url_text = message.text[entity.offset:entity.offset + entity.length]
                    url = url_text
                    break
        
        # Если URL не найден в entities, ищем в тексте
        if not url and message_text:
            url = extract_url(message_text)
        
        if url and validators.url(url):
            logging.info(f"Found valid URL in forwarded message: {url}")
            await process_forwarded_url(update, context, url)
            return
        
        logging.debug("Forwarded message contains neither file nor URL")
        
    except Exception as e:
        logging.error(f"Error processing forwarded message: {e}")
        await update.message.reply_text(humanize("ERROR_OCCURRED"))

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text input based on next_action."""
    next_action = context.user_data.get('next_action')
    
    if next_action == 'run_url_analysis':
        await process_url_analysis(update, context)
    elif next_action in ['add_api_key', 'rename_api_key']:
        await settings_handle_text_input(update, context)
    elif next_action in ['get_reports_by_uuid']:
        await reports_handle_text_input(update, context)
    else:
        logging.debug(f"No next_action found in context. Current user_data: {context.user_data}")
        await update.message.reply_text(humanize("UNKNOWN_COMMAND"))
        await show_main_menu(update, context)

async def handle_file_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular file input based on next_action."""
    next_action = context.user_data.get('next_action')
    
    if next_action == 'run_file_analysis':
        await process_file_analysis(update, context)
    elif next_action == 'restore_database':
        await process_database_restore(update, context)
    else:
        logging.warning(f"Received file without specific next_action. Ignoring.")
        await update.message.reply_text(humanize("UNEXPECTED_FILE_UPLOAD"))

async def process_forwarded_url(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    """Process URL from forwarded message without disrupting current menu state."""
    access_granted, api_key = await check_user_access(context.bot, update.effective_user.id)
    if not access_granted:
        await update.message.reply_text(api_key)
        return

    logging.info(f"Processing forwarded URL analysis for user {update.effective_user.id}: {url}")
    result = await run_url_analysis(api_key, url, update.effective_user.id)

    if 'error' in result:
        logging.error(f"URL analysis error for user {update.effective_user.id}: {result['error']}")
        await update.message.reply_text(humanize("URL_ANALYSIS_ERROR").format(error=result['error']))
    else:
        logging.info(f"URL analysis submitted for user {update.effective_user.id}, task_id: {result['task_id']}")
        await update.message.reply_text(humanize("URL_ANALYSIS_SUBMITTED_CHECK_ACTIVE").format(uuid=result['task_id']))
        asyncio.create_task(monitor_analysis_status(update, context, api_key, result['task_id']))

async def process_forwarded_file(update: Update, context: ContextTypes.DEFAULT_TYPE, document):
    """Process file from forwarded message without disrupting current menu state."""
    access_granted, api_key = await check_user_access(context.bot, update.effective_user.id)
    if not access_granted:
        await update.message.reply_text(api_key)
        return

    logging.info(f"Processing forwarded file analysis for user {update.effective_user.id}: {document.file_name}")
    
    try:
        file = await context.bot.get_file(document.file_id)
        file_content = await file.download_as_bytearray()
        
        result = await run_file_analysis(api_key, file_content, document.file_name, update.effective_user.id)

        if 'error' in result:
            logging.error(f"File analysis error for user {update.effective_user.id}: {result['error']}")
            await update.message.reply_text(humanize("FILE_ANALYSIS_ERROR").format(error=result['error']))
        else:
            logging.info(f"File analysis submitted for user {update.effective_user.id}, task_id: {result['task_id']}")
            await update.message.reply_text(humanize("FILE_ANALYSIS_SUBMITTED_CHECK_ACTIVE").format(uuid=result['task_id']))
            asyncio.create_task(monitor_analysis_status(update, context, api_key, result['task_id']))
    
    except Exception as e:
        logging.error(f"Error processing forwarded file: {e}")
        await update.message.reply_text(humanize("ERROR_OCCURRED"))
