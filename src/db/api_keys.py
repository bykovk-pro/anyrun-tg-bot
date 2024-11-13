from src.db.pool import get_db_pool
import sqlite3
import logging
from src.lang.director import humanize
from src.lang.decorators import with_locale

@with_locale
async def db_add_api_key(telegram_id: int, api_key: str) -> bool:
    db = await get_db_pool()
    try:
        async with db.cursor() as cursor:
            await cursor.execute('DELETE FROM api_keys WHERE telegram_id = ?', (telegram_id,))
            await cursor.execute('''
                INSERT INTO api_keys (telegram_id, api_key, key_name, is_active)
                VALUES (?, ?, ?, TRUE)
            ''', (telegram_id, api_key, "Main API Key"))
        await db.commit()
        logging.info(f"API key added for user {telegram_id}")
        return True
    except Exception as e:
        logging.error(f"Error adding API key: {e}")
        return False

@with_locale
async def db_get_user_api_key(telegram_id: int) -> str:
    db = await get_db_pool()
    try:
        async with db.cursor() as cursor:
            await cursor.execute('''
                SELECT api_key
                FROM api_keys
                WHERE telegram_id = ?
            ''', (telegram_id,))
            result = await cursor.fetchone()
            return result[0] if result else None
    except Exception as e:
        logging.error(f"Error getting API key: {e}")
        return None
