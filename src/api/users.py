from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.lang.director import humanize
from src.db.users import db_get_all_users, db_ban_user_by_id, db_unban_user_by_id, db_delete_user_by_id
from src.api.admin import show_manage_users_menu
import logging

def create_navigation_buttons(page, total_users, users_per_page):
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f"show_users_page_{page-1}"))
    if (page + 1) * users_per_page < total_users:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"show_users_page_{page+1}"))
    return nav_buttons

async def show_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE, page=0):
    users = await db_get_all_users()
    if not users:
        await update.callback_query.edit_message_text(humanize("NO_USERS_FOUND"))
        return

    users_per_page = 2
    start = page * users_per_page
    end = start + users_per_page
    user_messages = []

    for user in users[start:end]:
        user_info = (
            f"ID: `{user['telegram_id']}`\n"
            f"First seen: {user['first_access_date']}\n"
            f"Last seen: {user['last_access_date']}\n"
            f"Admin: {user['is_admin']}\n"
            f"Banned: {user['is_banned']}\n"
            "----------------------\n"
        )
        user_messages.append(user_info)

    menu_text = humanize("SHOW_ALL_USERS_MENU_TEXT") + "\n\n" + "".join(user_messages)
    nav_buttons = create_navigation_buttons(page, len(users), users_per_page)
    keyboard = [nav_buttons] if nav_buttons else []
    keyboard.append([InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='manage_users')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    current_message = update.callback_query.message.text
    if current_message != menu_text:
        await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)
    else:
        logging.debug("Message content is the same, not updating.")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(humanize("BAN_USER_PROMPT"))
    context.user_data['next_action'] = 'ban_user'

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(humanize("UNBAN_USER_PROMPT"))
    context.user_data['next_action'] = 'unban_user'

async def delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(humanize("DELETE_USER_PROMPT"))
    context.user_data['next_action'] = 'delete_user'

async def process_user_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.text
    action = context.user_data.get('next_action')
    
    if action == 'ban_user':
        result = await db_ban_user_by_id(user_id)
    elif action == 'unban_user':
        result = await db_unban_user_by_id(user_id)
    elif action == 'delete_user':
        result = await db_delete_user_by_id(user_id)
    else:
        result = False
    
    if result:
        await update.message.reply_text(humanize(f"{action.upper()}_SUCCESS"))
    else:
        await update.message.reply_text(humanize(f"{action.upper()}_FAILURE"))
    
    del context.user_data['next_action']
    await show_manage_users_menu(update, context)
