from telegram import Update
from telegram.ext import ContextTypes
from lang.director import get as humanize
from db.users import get_non_admin_users, update_user_ban_status

async def check_bot_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    pass

async def manage_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = await get_non_admin_users()
    user_list = '\n'.join([f"{user['telegram_id']} - {user['first_access_date']} - {user['last_access_date']} - {'Banned' if user['is_banned'] else 'Not banned'}" for user in users])
    await update.callback_query.message.reply_text(humanize("USER_LIST") + '\n' + user_list)
    await update.callback_query.message.reply_text(humanize("SELECT_USERS_TO_MANAGE"))
    context.user_data['awaiting_user_selection'] = True
