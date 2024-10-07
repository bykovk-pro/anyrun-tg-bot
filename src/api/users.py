from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.lang.director import humanize
from src.db.users import db_get_all_users, db_ban_user_by_id, db_unban_user_by_id, db_delete_user_by_id
from src.api.admin import show_manage_users_menu

def create_show_all_users_menu(users, page=0, users_per_page=10):
    keyboard = []
    start = page * users_per_page
    end = start + users_per_page
    for user in users[start:end]:
        keyboard.append([InlineKeyboardButton(f"{user['telegram_id']} {user['first_access_date']} {user['last_access_date']} {user['is_admin']} {user['is_banned']} {user['is_deleted']}", callback_data=f"user_info_{user['telegram_id']}")])
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f"show_users_page_{page-1}"))
    if end < len(users):
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"show_users_page_{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='manage_users')])
    return InlineKeyboardMarkup(keyboard)

async def show_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE, page=0):
    users = await db_get_all_users()
    menu_text = humanize("SHOW_ALL_USERS_MENU_TEXT")
    reply_markup = create_show_all_users_menu(users, page)
    await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)

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
