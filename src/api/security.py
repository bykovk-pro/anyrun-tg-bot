import logging
from telegram import Bot, Chat
import re
from telegram.error import TelegramError
from telegram.constants import ChatMemberStatus, ChatType

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
    
    groups_info = {}
    for group_id in required_group_ids:
        try:
            chat = await bot.get_chat(chat_id=group_id)
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
            logging.error(f'Error getting info for group {group_id}: {str(e)}')
            # Попытка получить информацию о публичной группе
            try:
                public_chat = await bot.get_chat(f"@any_run_community")
                if public_chat and public_chat.id == group_id:
                    groups_info[group_id] = (False, public_chat, False)
                else:
                    groups_info[group_id] = (False, None, False)
            except TelegramError:
                groups_info[group_id] = (False, None, False)
    
    return groups_info
