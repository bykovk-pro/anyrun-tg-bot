from telegram import Update
from telegram.ext import ContextTypes
from src.lang.director import humanize
from src.api.menu_utils import create_admin_panel_menu, create_manage_users_menu, create_manage_bot_menu


async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = humanize("ADMIN_PANEL_MENU_TEXT")
    reply_markup = create_admin_panel_menu()
    await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)

async def show_manage_users_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = humanize("MANAGE_USERS_MENU_TEXT")
    reply_markup = create_manage_users_menu()
    await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)

async def show_manage_bot_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, new_message: bool = False):
    menu_text = humanize("MANAGE_BOT_MENU_TEXT")
    reply_markup = create_manage_bot_menu()
    
    if new_message:
        if update.callback_query:
            await update.callback_query.message.reply_text(menu_text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(menu_text, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)
