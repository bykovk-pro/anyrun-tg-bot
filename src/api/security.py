import logging
from telegram import Bot, Chat
import re
from telegram.error import TelegramError
from telegram.constants import ChatMemberStatus, ChatType
import time
from src.db.users import db_get_user, db_is_user_admin
from src.db.api_keys import db_get_api_keys

last_api_call_time = {}

def setup_telegram_security(token) -> str:
    if not token:
        logging.critical('Telegram bot token not found in environment variables')
        raise EnvironmentError('Telegram bot token not found in environment variables')
    
    if not re.match(r'^\d{8,10}:[a-zA-Z0-9_-]{35}$', token):
        logging.error('Invalid Telegram bot token format')
        raise ValueError('Invalid Telegram bot token format')
    
    logging.debug(f'Telegram token validated: {token[:5]}...{token[-5:]}')
    return token

async def check_in_groups(bot: Bot, check_id: int, is_bot: bool = False, required_group_ids: str = None):
    logging.debug(f'check_in_groups called with: check_id={check_id}, is_bot={is_bot}, required_group_ids={required_group_ids}')
    
    if not required_group_ids:
        logging.warning('No required group IDs specified')
        return {}
    
    try:
        required_group_ids = [int(gid.strip()) for gid in required_group_ids.split(',') if gid.strip().replace('-', '').isdigit()]
    except ValueError as e:
        logging.error(f'Error parsing required_group_ids: {str(e)}')
        return {}
    
    logging.debug(f'Parsed required_group_ids: {required_group_ids}')
    
    if not required_group_ids:
        logging.warning('No valid required group IDs found after parsing')
        return {}
    
    logging.debug(f"Checking if bot is in required groups: {required_group_ids}")
    groups_info = {}
    for group_id in required_group_ids:
        try:
            chat = await bot.get_chat(chat_id=group_id)
            logging.debug(f"Bot is in group: {chat.title} (ID: {group_id})")
            bot_is_member = True
            try:
                bot_member = await bot.get_chat_member(chat_id=group_id, user_id=bot.id)
                bot_is_member = bot_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
            except TelegramError:
                bot_is_member = False
            
            if is_bot:
                groups_info[group_id] = (bot_is_member, chat, True)
            else:
                try:
                    user_member = await bot.get_chat_member(chat_id=group_id, user_id=check_id)
                    user_is_member = user_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
                except TelegramError:
                    user_is_member = False
                groups_info[group_id] = (user_is_member, chat, bot_is_member)
        except TelegramError as e:
            logging.warning(f"Bot is not in group with ID: {group_id}. Error: {e}")
            try:
                public_chat = await bot.get_chat(f"@any_run_community")
                if public_chat and public_chat.id == group_id:
                    groups_info[group_id] = (False, public_chat, False)
                else:
                    groups_info[group_id] = (False, None, False)
            except TelegramError:
                groups_info[group_id] = (False, None, False)
    
    return groups_info

async def check_user_groups(bot: Bot, user_id: int, required_group_ids: str):
    if await db_is_user_admin(user_id):
        return True

    user = await db_get_user(user_id)
    if not user:
        logging.warning(f"User {user_id} not found in the database.")
        return False

    groups_info = await check_in_groups(bot, user_id, is_bot=False, required_group_ids=required_group_ids)
    if not any(info[0] for info in groups_info.values()):
        logging.warning(f"User {user_id} is not in any required groups.")
        return False
    return True

async def check_user_api_keys(user_id: int):
    api_keys = await db_get_api_keys(user_id)
    if not api_keys:
        logging.warning(f"No API keys found for user {user_id}.")
        return False

    return any(key[2] for key in api_keys)

async def rate_limiter(user_id: int):
    if await db_is_user_admin(user_id):
        return True

    global last_api_call_time
    current_time = time.time()
    if user_id in last_api_call_time:
        if current_time - last_api_call_time[user_id] < 30:
            return False
    last_api_call_time[user_id] = current_time
    return True

async def check_user_and_api_key(user_id: int):
    api_keys = await db_get_api_keys(user_id)

    active_api_key = next((key for key in api_keys if key[2]), None)

    if not active_api_key:
        return None, "You do not have any active API keys."

    return active_api_key[0], None
