import logging
from telegram import Bot, Chat
import re
from telegram.error import TelegramError
from telegram.constants import ChatMemberStatus, ChatType
import time
from src.db.users import db_get_user, db_is_user_admin
from src.db.api_keys import db_get_api_keys
from src.lang.director import humanize
import os

last_api_call_time = {}

def setup_telegram_security(token) -> str:
    if not token:
        logging.critical('Telegram bot token not found in environment variables')
        raise EnvironmentError('Telegram bot token not found in environment variables')
    
    # Token regex ^\d{8,10}:[a-zA-Z0-9_-]{35}$ may false positive, try ((?<=bot)\d{8,10}:[\w-]{35}|\d{10}:AA[\w-]{33}) instead?
    if not re.match(r'^\d{8,10}:[a-zA-Z0-9_-]{35}$', token):
        logging.error('Invalid Telegram bot token format')
        raise ValueError('Invalid Telegram bot token format')
    
    logging.debug(f'Telegram token validated: {token[:5]}...{token[-5:]}')
    return token

async def check_in_groups(bot: Bot, check_id: int, is_bot: bool = False, required_group_ids: str = None):
    logging.debug(f'check_in_groups called with: check_id={check_id}, is_bot={is_bot}, required_group_ids={required_group_ids}')
    
    if not required_group_ids:
        logging.info('No required group IDs specified, considering access granted')
        return {"no_groups": (True, None, True)}
    
    try:
        required_group_ids = [int(gid.strip()) for gid in required_group_ids.split(',') if gid.strip().replace('-', '').isdigit()]
    except ValueError as e:
        logging.error(f'Error parsing required_group_ids: {str(e)}')
        return {}
    
    logging.debug(f'Parsed required_group_ids: {required_group_ids}')
    
    if not required_group_ids:
        logging.info('No valid required group IDs found after parsing, considering access granted')
        return {"no_groups": (True, None, True)}
    
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
    if "no_groups" in groups_info:
        return True
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

async def check_user_and_api_key(user_id: int):
    api_keys = await db_get_api_keys(user_id)

    active_api_key = next((key for key in api_keys if key[2]), None)

    if not active_api_key:
        return None, "You do not have any active API keys."

    return active_api_key[0], None

async def check_user_access(bot, user_id: int):
    logging.debug(f"Checking access for user {user_id}")
    user = await db_get_user(user_id)
    if not user:
        logging.warning(f"User {user_id} not found")
        return False, humanize("USER_NOT_FOUND")
    if user[4]:
        logging.warning(f"User {user_id} is banned")
        return False, humanize("USER_BANNED")
    if user[5]:
        logging.warning(f"User {user_id} is deleted")
        return False, humanize("USER_DELETED")
    
    api_key, error_message = await check_user_and_api_key(user_id)
    if error_message:
        logging.warning(f"API key error for user {user_id}: {error_message}")
        return False, error_message
    
    logging.debug(f"API Key for user {user_id} (first 5 chars): {api_key[:5]}...")
    
    required_group_ids = os.getenv('REQUIRED_GROUP_IDS', '')
    if not await check_user_groups(bot, user_id, required_group_ids):
        logging.warning(f"User {user_id} not in required groups")
        return False, humanize("NOT_IN_REQUIRED_GROUPS")
    
    return True, api_key
