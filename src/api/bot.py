import logging
import os
import platform
import psutil
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.lang.director import humanize
from src.db.director import backup, restore
from src.api.admin import show_manage_bot_menu

async def show_system_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    system_info = f"""
{humanize("SYSTEM_INFO_OS")}: {platform.system()} {platform.release()}
{humanize("SYSTEM_INFO_PYTHON")}: {platform.python_version()}
{humanize("SYSTEM_INFO_PROCESSOR")}: {platform.processor()}
{humanize("SYSTEM_INFO_CPU_CORES")}: {psutil.cpu_count()}
{humanize("SYSTEM_INFO_CPU_USAGE")}: {psutil.cpu_percent()}%
{humanize("SYSTEM_INFO_TOTAL_MEMORY")}: {psutil.virtual_memory().total / (1024 * 1024):.2f} MB
{humanize("SYSTEM_INFO_USED_MEMORY")}: {psutil.virtual_memory().used / (1024 * 1024):.2f} MB
{humanize("SYSTEM_INFO_FREE_MEMORY")}: {psutil.virtual_memory().free / (1024 * 1024):.2f} MB
{humanize("SYSTEM_INFO_DISK_USAGE")}: {psutil.disk_usage('/').percent}%
    """
    
    keyboard = [[InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='manage_bot')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(system_info, reply_markup=reply_markup)

async def backup_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.debug("Starting database backup process")
    try:
        backup_path = await backup()
        logging.debug(f"Backup function returned path: {backup_path}")
        
        if backup_path is None:
            raise ValueError("Backup function returned None")
        
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file does not exist: {backup_path}")
        
        file_size = os.path.getsize(backup_path)
        logging.debug(f"Backup file exists. Size: {file_size} bytes")
        
        if file_size == 0:
            raise ValueError(f"Backup file is empty: {backup_path}")
        
        with open(backup_path, 'rb') as file:
            try:
                await update.callback_query.message.reply_document(
                    document=file,
                    filename=os.path.basename(backup_path),
                    caption=humanize("BACKUP_CREATED")
                )
                logging.info("Backup file sent successfully")
            except Exception as send_error:
                logging.error(f"Error sending backup file: {str(send_error)}")
                raise
    except Exception as e:
        error_message = f"Error creating or sending database backup: {str(e)}"
        logging.error(error_message)
        await update.callback_query.message.reply_text(humanize("BACKUP_ERROR") + f"\n\nDetails: {error_message}")
    
    finally:
        await show_manage_bot_menu(update, context, new_message=True)

async def restore_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(humanize("RESTORE_DATABASE_PROMPT"))
    context.user_data['next_action'] = 'restore_database'

async def process_database_restore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text(humanize("INVALID_BACKUP_FILE"))
        await show_manage_bot_menu(update, context, new_message=True)
        return

    file = await context.bot.get_file(update.message.document.file_id)
    file_path = f"temp_backup_{update.effective_user.id}.zip"
    await file.download_to_drive(file_path)

    try:
        restore_success = await restore(file_path)
        if restore_success:
            await update.message.reply_text(humanize("DATABASE_RESTORED"))
        else:
            await update.message.reply_text(humanize("RESTORE_ERROR"))
    except Exception as e:
        logging.error(f"Error restoring database: {str(e)}")
        await update.message.reply_text(humanize("RESTORE_ERROR"))

    os.remove(file_path)

    del context.user_data['next_action']
    await show_manage_bot_menu(update, context, new_message=True)
