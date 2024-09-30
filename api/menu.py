from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
from lang.director import get as humanize
from lang.context import set_current_language
from functools import wraps
import logging

def set_language(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        user_language = user.language_code if user.language_code else 'en'
        set_current_language(user_language)
        return await func(update, context)
    return wrapper

def create_main_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_PROFILE"), callback_data='profile')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_SETTINGS"), callback_data='settings')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_HELP"), callback_data='help')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_LANGUAGE"), callback_data='language')]
    ]
    return InlineKeyboardMarkup(keyboard)

@set_language
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = humanize("MAIN_MENU_TEXT")
    reply_markup = create_main_menu()

    if update.callback_query:
        await update.callback_query.message.reply_text(menu_text, reply_markup=reply_markup)
    elif update.message:
        await update.message.reply_text(menu_text, reply_markup=reply_markup)
    else:
        logging.error("Unexpected update type in show_main_menu")

@set_language
async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'profile':
        await query.edit_message_text(humanize("PROFILE_INFO"))
    elif query.data == 'settings':
        await query.edit_message_text(humanize("SETTINGS_INFO"))
    elif query.data == 'help':
        await query.edit_message_text(humanize("HELP_MESSAGE"))
        await show_main_menu(update, context)
    elif query.data == 'language':
        await change_language_callback(update, context)
    else:
        logging.warning(f"Unknown callback data: {query.data}")
        await query.edit_message_text(humanize("UNKNOWN_OPTION"))

@set_language
async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(humanize("HELP_MESSAGE"))
    await show_main_menu(update, context)

@set_language
async def change_language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.debug("change_language_command function called")
    user = update.effective_user
    new_language = user.language_code if user.language_code else 'en'
    set_current_language(new_language)
    await update.message.reply_text(humanize("LANGUAGE_UPDATED"))
    await show_main_menu(update, context)

async def change_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.debug("change_language_callback function called")
    query = update.callback_query
    user = query.from_user
    new_language = user.language_code if user.language_code else 'en'
    set_current_language(new_language)
    await query.answer()
    await query.edit_message_text(humanize("LANGUAGE_UPDATED"))
    await show_main_menu(update, context)

def setup_menu_handlers(application):
    application.add_handler(CallbackQueryHandler(handle_menu_selection))
    application.add_handler(CommandHandler("help", show_help))
    application.add_handler(CommandHandler("start", show_main_menu))
    application.add_handler(CommandHandler("menu", show_main_menu))
    application.add_handler(CommandHandler("language", change_language_command))
