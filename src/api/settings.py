import datetime
import re
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Chat
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from src.lang.director import humanize
from src.db.api_keys import (
    db_add_api_key, db_get_api_keys, db_delete_api_key, 
    db_change_api_key_name, db_set_active_api_key
)
from src.api.security import check_in_groups
from telegram.constants import ChatType
from src.api.menu import show_settings_menu

def create_manage_api_key_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_SHOW_API_KEYS"), callback_data='show_api_keys')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_ADD_API_KEY"), callback_data='add_api_key')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_DELETE_API_KEY"), callback_data='delete_api_key')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_CHANGE_API_KEY_NAME"), callback_data='change_api_key_name')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_SET_ACTIVE_API_KEY"), callback_data='set_active_api_key')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='settings')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def manage_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = humanize("MANAGE_API_KEY_MENU_TEXT")
    reply_markup = create_manage_api_key_menu()
    if update.callback_query:
        await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(menu_text, reply_markup=reply_markup)
    logging.debug(f"Displayed manage_api_key menu for user {update.effective_user.id}")

async def check_access_rights(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    required_group_ids = os.getenv('REQUIRED_GROUP_IDS', '')
    
    user_groups = await check_in_groups(context.bot, user_id, is_bot=False, required_group_ids=required_group_ids)
    
    if not user_groups:
        await update.callback_query.answer(humanize("NO_REQUIRED_GROUPS"))
        await update.callback_query.edit_message_text(humanize("NO_REQUIRED_GROUPS"))
        return
    
    keyboard = []
    message_text = humanize("ACCESS_RIGHTS_INFO") + "\n\n"
    
    for group_id, (is_member, chat, bot_is_member) in user_groups.items():
        if chat:
            group_name = chat.title
            status_icon = "✅" if is_member else "❌"
            button_text = f"{status_icon} {group_name}"
            message_text += f"{button_text}\n"
            
            invite_link = chat.invite_link if bot_is_member else None
            if not invite_link and chat.username:
                invite_link = f"https://t.me/{chat.username}"
            elif not invite_link and chat.type == ChatType.SUPERGROUP:
                invite_link = f"https://t.me/c/{str(chat.id)[4:]}"
            
            if invite_link:
                keyboard.append([InlineKeyboardButton(button_text, url=invite_link)])
            else:
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"group_info_{group_id}")])
        else:
            button_text = f"❓ Group {group_id}"
            message_text += f"{button_text}\n"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"group_info_{group_id}")])
    
    if not keyboard:
        message_text += humanize("NO_ACCESSIBLE_GROUPS")
    
    keyboard.append([InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup)

async def show_api_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    api_keys = await db_get_api_keys(user_id)

    if not api_keys:
        await update.callback_query.answer(text=humanize("NO_API_KEYS_FOUND"))
        return

    keys_text = humanize("YOUR_API_KEYS") + "\n\n"
    for key, name, is_active in api_keys:
        status = "✅ " if is_active else ""
        keys_text += f"{status}{name}: {key[:6]}...{key[-6:]}\n"

    await update.callback_query.message.reply_text(keys_text)

    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='back_to_manage_api_key')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.reply_text(humanize("CHOOSE_OPTION"), reply_markup=reply_markup)

async def add_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(humanize("ENTER_NEW_API_KEY_FORMAT"))
    context.user_data['next_action'] = 'add_api_key'

async def delete_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    api_keys = await db_get_api_keys(user_id)
    
    if not api_keys:
        await update.callback_query.answer(humanize("NO_API_KEYS_TO_DELETE"))
        return

    keyboard = []
    for key, name, is_active in api_keys:
        status = "✅ " if is_active else ""
        button_text = f"{status}{name}: {key[:6]}...{key[-6:]}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"delete_{key}")])
    
    keyboard.append([InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='back_to_manage_api_key')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(humanize("SELECT_API_KEY_TO_DELETE"), reply_markup=reply_markup)

async def change_api_key_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    api_keys = await db_get_api_keys(user_id)
    
    if not api_keys:
        await update.callback_query.answer(humanize("NO_API_KEYS_TO_RENAME"))
        return

    keyboard = []
    for key, name, is_active in api_keys:
        status = "✅ " if is_active else ""
        button_text = f"{status}{name}: {key[:6]}...{key[-6:]}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"rename_{key}")])
    
    keyboard.append([InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='back_to_manage_api_key')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(humanize("SELECT_API_KEY_TO_RENAME"), reply_markup=reply_markup)

async def set_active_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    api_keys = await db_get_api_keys(user_id)
    
    if not api_keys:
        await update.callback_query.answer(humanize("NO_API_KEYS_TO_ACTIVATE"))
        return

    keyboard = []
    for key, name, is_active in api_keys:
        status = "✅ " if is_active else ""
        button_text = f"{status}{name}: {key[:6]}...{key[-6:]}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"activate_{key}")])
    
    keyboard.append([InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='back_to_manage_api_key')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(humanize("SELECT_API_KEY_TO_ACTIVATE"), reply_markup=reply_markup)

async def handle_api_key_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    logging.debug(f"handle_api_key_actions called with data: {query.data}")

    if query.data.startswith('delete_'):
        api_key = query.data.split('_', 1)[1]
        await db_delete_api_key(update.effective_user.id, api_key)
        await query.edit_message_text(humanize("API_KEY_DELETED"))
        await manage_api_key(update, context)
    elif query.data.startswith('rename_'):
        api_key = query.data.split('_', 1)[1]
        context.user_data['api_key_to_rename'] = api_key
        context.user_data['next_action'] = 'rename_api_key'
        await query.edit_message_text(humanize("ENTER_NEW_API_KEY_NAME"))
        logging.debug(f"Set next_action to rename_api_key for user {update.effective_user.id}")
    elif query.data.startswith('activate_'):
        api_key = query.data.split('_', 1)[1]
        await db_set_active_api_key(update.effective_user.id, api_key)
        await query.edit_message_text(humanize("API_KEY_ACTIVATED"))
        await manage_api_key(update, context)
    elif query.data == 'back_to_manage_api_key':
        await manage_api_key(update, context)
    
    logging.debug(f"Context user_data after handle_api_key_actions: {context.user_data}")

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_action = context.user_data.get('next_action')
    logging.debug(f"settings.handle_text_input called with next_action: {next_action}")
    logging.debug(f"Full context user_data: {context.user_data}")
    
    if next_action == 'add_api_key':
        await process_add_api_key(update, context)
    elif next_action == 'rename_api_key':
        await process_rename_api_key(update, context)
    else:
        logging.warning(f"Unknown next_action in settings: {next_action}")
        await update.message.reply_text(humanize("UNKNOWN_COMMAND"))
        await manage_api_key(update, context)
    
    logging.debug(f"Clearing next_action for user {update.effective_user.id}")
    context.user_data.pop('next_action', None)
    logging.debug(f"Context user_data after handling: {context.user_data}")

async def process_add_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    input_text = update.message.text.strip()
    
    match = re.match(r'^(\S+)\s*(.*)$', input_text)
    if match:
        new_key = match.group(1)
        key_name = match.group(2).strip()
    else:
        new_key = input_text
        key_name = ""
    
    if not key_name:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        key_name = f"New API Key {timestamp}"
    
    key_name = re.sub(r'[^\w\s-]', '', key_name).strip()
    if not key_name:
        key_name = "Unnamed Key"
    
    success, error_message = await db_add_api_key(user_id, new_key, key_name)
    if success:
        await update.message.reply_text(humanize("API_KEY_ADDED"))
    else:
        if error_message == "API_KEY_ALREADY_EXISTS":
            await update.message.reply_text(humanize("API_KEY_ALREADY_EXISTS"))
        else:
            await update.message.reply_text(humanize("ERROR_ADDING_API_KEY"))
    
    await manage_api_key(update, context)

async def process_rename_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    api_key = context.user_data.get('api_key_to_rename')
    new_name = update.message.text.strip()
    
    logging.debug(f"process_rename_api_key called for user {user_id}")
    logging.debug(f"API key to rename: {api_key}")
    logging.debug(f"New name: {new_name}")
    
    new_name = re.sub(r'[^\w\s-]', '', new_name).strip()
    if not new_name:
        new_name = "Unnamed Key"
    
    if api_key:
        await db_change_api_key_name(user_id, api_key, new_name)
        await update.message.reply_text(humanize("API_KEY_RENAMED"))
        logging.debug(f"API key renamed successfully for user {user_id}")
    else:
        logging.error(f"No API key to rename for user {user_id}")
        await update.message.reply_text(humanize("ERROR_RENAMING_API_KEY"))
    
    logging.debug(f"Calling manage_api_key after renaming for user {user_id}")
    await manage_api_key(update, context)

async def handle_group_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    group_id = query.data.split('_')[-1]
    await query.answer(humanize("GROUP_LINK_NOT_AVAILABLE"))
