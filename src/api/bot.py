import logging
import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.lang.director import humanize
from src.db.director import backup, restore
from src.config import get_config
from src.api.admin import show_manage_bot_menu

async def restart_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    confirm_keyboard = [
        [InlineKeyboardButton(humanize("YES"), callback_data='confirm_restart_bot')],
        [InlineKeyboardButton(humanize("NO"), callback_data='manage_bot')]
    ]
    reply_markup = InlineKeyboardMarkup(confirm_keyboard)
    await update.callback_query.edit_message_text(humanize("CONFIRM_RESTART_BOT"), reply_markup=reply_markup)

async def confirm_restart_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(humanize("BOT_RESTARTING"))
    await show_manage_bot_menu(update, context)

async def change_log_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_level = logging.getLogger().level
    levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
    level_names = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    keyboard = [[InlineKeyboardButton(name, callback_data=f'set_log_level_{level}') for name, level in zip(level_names, levels)]]
    keyboard.append([InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='manage_bot')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        humanize("CHANGE_LOG_LEVEL_PROMPT").format(current_level=logging.getLevelName(current_level)),
        reply_markup=reply_markup
    )

async def set_log_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    level = int(query.data.split('_')[-1])
    logging.getLogger().setLevel(level)
    await query.answer(humanize("LOG_LEVEL_CHANGED"))
    await show_manage_bot_menu(update, context)

async def show_bot_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Здесь должна быть логика получения последних 50 строк логов
    logs = "Last 50 lines of bot logs will be shown here"
    await update.callback_query.edit_message_text(logs)
    # Добавить кнопку "Назад"
    keyboard = [[InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='manage_bot')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(logs, reply_markup=reply_markup)

async def show_bot_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Здесь должна быть логика получения статистики бота
    stats = "Bot statistics will be shown here"
    keyboard = [[InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='manage_bot')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(stats, reply_markup=reply_markup)

async def show_system_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Здесь должна быть логика получения системной информации
    system_info = "System information will be shown here"
    keyboard = [[InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='manage_bot')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(system_info, reply_markup=reply_markup)

async def backup_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.debug("Starting database backup process")
    config = get_config()
    try:
        backup_path = await backup(config)
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
        await show_manage_bot_menu(update, context)

async def restore_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(humanize("RESTORE_DATABASE_PROMPT"))
    context.user_data['next_action'] = 'restore_database'

async def process_database_restore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text(humanize("INVALID_BACKUP_FILE"))
        await show_manage_bot_menu(update, context)
        return

    file = await context.bot.get_file(update.message.document.file_id)
    file_path = f"temp_backup_{update.effective_user.id}.zip"
    await file.download_to_drive(file_path)

    config = get_config()
    try:
        await restore(config, file_path)
        await update.message.reply_text(humanize("DATABASE_RESTORED"))
    except Exception as e:
        logging.error(f"Error restoring database: {str(e)}")
        await update.message.reply_text(humanize("RESTORE_ERROR"))

    import os
    os.remove(file_path)

    del context.user_data['next_action']
    await show_manage_bot_menu(update, context)
