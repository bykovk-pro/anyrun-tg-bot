import logging
from src.db.pool import get_db_pool
from src.lang.director import humanize
from src.lang.decorators import with_locale

@with_locale
async def db_add_user(telegram_id: int) -> bool:
    try:
        db = await get_db_pool()
        await db.execute('''
            INSERT INTO users (telegram_id, first_access_date, last_access_date)
            VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(telegram_id) DO UPDATE SET
            last_access_date = CURRENT_TIMESTAMP
        ''', (telegram_id,))
        await db.commit()
        logging.info(f"User {telegram_id} added or updated in the database")
        return True
    except Exception as e:
        logging.error(f"Error adding or updating user: {e}")
        return False

@with_locale
async def db_get_user(telegram_id: int) -> tuple:
    try:
        db = await get_db_pool()
        async with db.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,)) as cursor:
            return await cursor.fetchone()
    except Exception as e:
        logging.error(f"Error getting user: {e}")
        return None

@with_locale
async def increment_api_requests_count(telegram_id: int) -> bool:
    try:
        db = await get_db_pool()
        async with db.cursor() as cursor:
            await cursor.execute('''
                UPDATE users 
                SET api_requests_count = api_requests_count + 1 
                WHERE telegram_id = ?
            ''', (telegram_id,))
        await db.commit()
        return True
    except Exception as e:
        logging.error(f"Error incrementing API requests count: {e}")
        return False
