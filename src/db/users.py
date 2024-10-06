import logging
from src.db.common import get_db_pool

async def add_user(telegram_id: int, lang: str = 'en', is_admin: bool = False):
    try:
        db = await get_db_pool()
        await db.execute('''
            INSERT OR IGNORE INTO users (telegram_id, lang, is_admin)
            VALUES (?, ?, ?)
        ''', (telegram_id, lang, is_admin))
        await db.commit()
    except Exception as e:
        logging.error(f"Error adding user: {e}")
        raise

async def get_user(telegram_id: int):
    try:
        db = await get_db_pool()
        async with db.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,)) as cursor:
            return await cursor.fetchone()
    except Exception as e:
        logging.error(f"Error getting user: {e}")
        raise

async def update_user_language(telegram_id: int, lang: str):
    try:
        db = await get_db_pool()
        await db.execute('UPDATE users SET lang = ? WHERE telegram_id = ?', (lang, telegram_id))
        await db.commit()
    except Exception as e:
        logging.error(f"Error updating user language: {e}")
        raise

async def is_user_admin(telegram_id: int):
    try:
        db = await get_db_pool()
        async with db.execute('SELECT is_admin FROM users WHERE telegram_id = ?', (telegram_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else False
    except Exception as e:
        logging.error(f"Error checking if user is admin: {e}")
        raise