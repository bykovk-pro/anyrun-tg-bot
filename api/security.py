import os
import logging
from typing import List, Union
from dotenv import load_dotenv
from config import create_config
from telegram import Bot

load_dotenv()
env_vars = dict(os.environ)
config = create_config(env_vars)

def get_telegram_token():
    token = config.get('TELEGRAM_TOKEN')
    if not token:
        logging.critical('Telegram bot token not found in environment variables')
        raise EnvironmentError('Telegram bot token not found in environment variables')
    return token

def validate_telegram_token(token):
    if not token or len(token) != 46:
        logging.error('Invalid Telegram bot token')
        raise ValueError('Invalid Telegram bot token')
    
    if not token[:5].isdigit():
        logging.warning('Telegram bot token has an unusual format')
    
    logging.debug(f'Telegram token validated: {token[:5]}...')
    return True

def setup_telegram_security():
    
    token = get_telegram_token()
    validate_telegram_token(token)
    return token

async def check_bot_in_groups(bot: Bot) -> Union[bool, List[int]]:
    group_ids_str = config.get('REQUIRED_GROUP_IDS', '')
    required_group_ids = [int(gid.strip()) for gid in group_ids_str.split(',') if gid.strip()]
    
    if not required_group_ids:
        logging.warning('No required group IDs specified')
        return True
    
    missing_groups = []
    for group_id in required_group_ids:
        try:
            chat_member = await bot.get_chat_member(chat_id=group_id, user_id=bot.id)
            if chat_member.status not in ['member', 'administrator', 'creator']:
                missing_groups.append(group_id)
        except Exception as e:
            logging.error(f'Error checking bot membership in group {group_id}: {str(e)}')
            missing_groups.append(group_id)
    
    return True if not missing_groups else missing_groups

async def check_user_in_groups(bot: Bot, user_id: int) -> Union[bool, List[int]]:
    group_ids_str = config.get('REQUIRED_GROUP_IDS', '')
    required_group_ids = [int(gid.strip()) for gid in group_ids_str.split(',') if gid.strip()]
    
    if not required_group_ids:
        logging.warning('No required group IDs specified')
        return True
    
    missing_groups = []
    for group_id in required_group_ids:
        try:
            chat_member = await bot.get_chat_member(chat_id=group_id, user_id=user_id)
            if chat_member.status not in ['member', 'administrator', 'creator']:
                missing_groups.append(group_id)
        except Exception as e:
            logging.error(f'Error checking user {user_id} membership in group {group_id}: {str(e)}')
            missing_groups.append(group_id)
    
    return True if not missing_groups else missing_groups
