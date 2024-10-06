import logging
from telegram import Bot
import re

def setup_telegram_security(token) -> str:
    if not token:
        logging.critical('Telegram bot token not found in environment variables')
        raise EnvironmentError('Telegram bot token not found in environment variables')
    
    # Check if the token matches the expected pattern
    if not re.match(r'^\d{8,10}:[a-zA-Z0-9_-]{35}$', token):
        logging.error('Invalid Telegram bot token format')
        raise ValueError('Invalid Telegram bot token format')
    
    logging.debug(f'Telegram token validated: {token[:5]}...{token[-5:]}')
    return token

async def check_in_groups(bot: Bot, check_id: int, is_bot: bool = False, required_group_ids: str = None):
    logging.debug(f'check_in_groups called with: check_id={check_id}, is_bot={is_bot}, required_group_ids={required_group_ids}')
    
    if not required_group_ids:
        logging.warning('No required group IDs specified')
        return True
    
    try:
        required_group_ids = [int(gid.strip()) for gid in required_group_ids.split(',') if gid.strip().isdigit()]
    except ValueError as e:
        logging.error(f'Error parsing required_group_ids: {str(e)}')
        return False
    
    logging.debug(f'Parsed required_group_ids: {required_group_ids}')
    
    if not required_group_ids:
        logging.warning('No valid required group IDs found after parsing')
        return True
    
    missing_groups = []
    for group_id in required_group_ids:
        try:
            chat_member = await bot.get_chat_member(chat_id=group_id, user_id=check_id)
            if chat_member.status not in ['member', 'administrator', 'creator']:
                missing_groups.append(group_id)
        except Exception as e:
            entity_type = "bot" if is_bot else "user"
            logging.error(f'Error checking {entity_type} {check_id} membership in group {group_id}: {str(e)}')
            missing_groups.append(group_id)
    
    return True if not missing_groups else missing_groups
