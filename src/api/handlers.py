from dataclasses import dataclass
from typing import List
import logging
import asyncio
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from telegram.helpers import escape_markdown
from src.lang.director import humanize
from src.db.users import db_add_user
from src.api.settings import process_api_key
from src.api.remote.sb_analysis import run_file_analysis, run_url_analysis
from src.api.remote.sb_status import get_analysis_status
from src.api.remote.sb_reports import get_report_by_uuid
from src.api.reports import display_report_info
from src.api.security import check_user_access
from src.lang.decorators import with_locale, localized_message

@dataclass
class AnalysisItem:
    type: str
    content: str
    name: str = ''

@with_locale
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await db_add_user(user_id)
    await localized_message("WELCOME_MESSAGE")(update)

@with_locale
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await localized_message("HELP_TEXT")(update)
    await localized_message("GITHUB_LINK")(update)

@with_locale
async def apikey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await localized_message("ENTER_API_KEY")(update)
    context.user_data['next_action'] = 'process_api_key'

@with_locale
async def getreport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await localized_message("ENTER_UUID")(update)
    context.user_data['next_action'] = 'process_report_uuid'

@with_locale
async def process_report_uuid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    access_granted, api_key = await check_user_access(context.bot, update.effective_user.id)
    if not access_granted:
        await update.message.reply_text(api_key)
        return

    uuid = update.message.text.strip()
    report = await get_report_by_uuid(api_key, uuid)
    
    if report.get('error'):
        await update.message.reply_text(report['message'])
        context.user_data.pop('next_action', None)
        return
        
    await display_report_info(update, context, report)
    context.user_data.pop('next_action', None)

@with_locale
async def monitor_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, task_id: str, api_key: str):
    retry_count = 0
    max_retries = 60
    
    while retry_count < max_retries:
        try:
            status_result = await get_analysis_status(api_key, task_id)
            
            if status_result.get('error'):
                logging.error(f"Error getting status: {status_result['error']}")
                await localized_message("STATUS_CHECK_ERROR")(update)
                return
            
            status = status_result.get('status')
            if status == 'completed':
                report = await get_report_by_uuid(api_key, task_id)
                if report.get('error'):
                    await localized_message("REPORT_ERROR")(update)
                else:
                    await display_report_info(update, context, report)
                return
            elif status == 'failed':
                await localized_message("ANALYSIS_FAILED")(update)
                return
            
            await asyncio.sleep(5)
            retry_count += 1
            
        except Exception as e:
            logging.error(f"Error monitoring analysis: {e}")
            await localized_message("MONITORING_ERROR")(update)
            return
    
    await localized_message("ANALYSIS_TIMEOUT")(update)

@with_locale
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_action = context.user_data.get('next_action')
    if next_action == 'process_api_key':
        context.user_data.pop('next_action', None)
        await process_api_key(update, context)
        return
    elif next_action == 'process_report_uuid':
        context.user_data.pop('next_action', None)
        await process_report_uuid(update, context)
        return
    elif next_action == 'select_item':
        if not update.message.text or not update.message.text.isdigit():
            await localized_message("INVALID_SELECTION")(update)
            return
            
        selection = int(update.message.text)
        items = context.user_data.get('analysis_items', [])
        
        if not items or selection < 1 or selection > len(items):
            await localized_message("INVALID_SELECTION")(update)
            return
            
        selected_item = items[selection - 1]
        context.user_data.pop('next_action', None)
        context.user_data.pop('analysis_items', None)
        
        access_granted, api_key = await check_user_access(context.bot, update.effective_user.id)
        if not access_granted:
            await update.message.reply_text(api_key)
            return
        
        try:
            if selected_item.type == 'file':
                file = selected_item.content
                file_content = await context.bot.get_file(file.file_id)
                file_bytes = await file_content.download_as_bytearray()
                result = await run_file_analysis(api_key, file_bytes, file.file_name, update.effective_user.id)
            else:
                result = await run_url_analysis(api_key, selected_item.content, update.effective_user.id)
                
            if result.get('error'):
                await localized_message("ANALYSIS_ERROR")(update)
            else:
                task_id = result.get('task_id')
                escaped_task_id = escape_markdown(task_id, version=2)
                await update.message.reply_text(
                    (await humanize("ANALYSIS_STARTED")).format(task_id=f"`{escaped_task_id}`"),
                    parse_mode='MarkdownV2'
                )
                asyncio.create_task(monitor_analysis(update, context, task_id, api_key))
                
        except Exception as e:
            logging.error(f"Error during analysis: {e}")
            await localized_message("ANALYSIS_ERROR")(update)
        return
    
    items = []
    
    if update.message.document:
        items.append(
            AnalysisItem('file', update.message.document, update.message.document.file_name)
        )
    
    if update.message.caption_entities or update.message.entities:
        entities = update.message.caption_entities or update.message.entities
        text = update.message.caption or update.message.text or ''
        
        for entity in entities:
            if entity.type == 'text_link':
                items.append(AnalysisItem('url', entity.url))
            elif entity.type == 'url':
                url = text[entity.offset:entity.offset + entity.length]
                items.append(AnalysisItem('url', url))
    
    if update.message.media_group_id:
        if 'media_group' not in context.chat_data:
            context.chat_data['media_group'] = {
                'id': update.message.media_group_id,
                'items': []
            }
        
        for item in items:
            if item not in context.chat_data['media_group']['items']:
                context.chat_data['media_group']['items'].append(item)
        
        if update.message.caption:
            items_to_show = context.chat_data['media_group']['items']
            del context.chat_data['media_group']
            await display_items_list(update, context, items_to_show)
    else:
        await display_items_list(update, context, items)

@with_locale
async def display_items_list(update: Update, context: ContextTypes.DEFAULT_TYPE, items: List[AnalysisItem]):
    if not items:
        await localized_message("NO_ITEMS_TO_ANALYZE")(update)
        return
    
    if len(items) == 1:
        selected_item = items[0]
        access_granted, api_key = await check_user_access(context.bot, update.effective_user.id)
        if not access_granted:
            await update.message.reply_text(api_key)
            return
            
        try:
            if selected_item.type == 'file':
                file = selected_item.content
                file_content = await context.bot.get_file(file.file_id)
                file_bytes = await file_content.download_as_bytearray()
                result = await run_file_analysis(api_key, file_bytes, file.file_name, update.effective_user.id)
            else:
                result = await run_url_analysis(api_key, selected_item.content, update.effective_user.id)
                
            if result.get('error'):
                await localized_message("ANALYSIS_ERROR")(update)
            else:
                task_id = result.get('task_id')
                escaped_task_id = escape_markdown(task_id, version=2)
                await update.message.reply_text(
                    (await humanize("ANALYSIS_STARTED")).format(task_id=f"`{escaped_task_id}`"),
                    parse_mode='MarkdownV2'
                )
                asyncio.create_task(monitor_analysis(update, context, task_id, api_key))
        except Exception as e:
            logging.error(f"Error during analysis: {e}")
            await localized_message("ANALYSIS_ERROR")(update)
        return
    
    items_list = []
    files = [item for item in items if item.type == 'file']
    urls = [item for item in items if item.type == 'url']
    
    for i, item in enumerate(files, 1):
        items_list.append(f"{i}. [FILE] {item.name}")
    
    for i, item in enumerate(urls, len(files) + 1):
        items_list.append(f"{i}. [URL] {item.content}")
    
    items_text = "\n".join(items_list)
    logging.debug(f"Prepared items list: {items_text}")
    
    await update.message.reply_text(
        (await humanize("MULTIPLE_ITEMS_FOUND")) + "\n\n" + items_text + "\n\n" + 
        (await humanize("SELECT_ITEM_NUMBER")),
        disable_web_page_preview=True
    )
    context.user_data['next_action'] = 'select_item'
    context.user_data['analysis_items'] = items

def setup_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("apikey", apikey))
    application.add_handler(CommandHandler("getreport", getreport))

    application.add_handler(MessageHandler(
        filters.Document.ALL & ~filters.COMMAND,
        handle_message
    ))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    ))

    logging.debug("Handlers setup completed")
