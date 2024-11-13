from src.db.pool import get_db_pool
import logging
from src.lang.director import humanize
from src.lang.decorators import with_locale

@with_locale
async def add_active_task(telegram_id: int, uuid: str) -> bool:
    try:
        db = await get_db_pool()
        async with db.cursor() as cursor:
            await cursor.execute('''
                INSERT INTO active_tasks (telegram_id, uuid)
                VALUES (?, ?)
            ''', (telegram_id, uuid))
        await db.commit()
        logging.debug(f"Added active task: {uuid} for user {telegram_id}")
        return True
    except Exception as e:
        logging.error(f"Error adding active task: {e}")
        return False

@with_locale
async def set_task_inactive(uuid: str) -> bool:
    try:
        db = await get_db_pool()
        async with db.cursor() as cursor:
            await cursor.execute('''
                UPDATE active_tasks
                SET is_active = FALSE
                WHERE uuid = ?
            ''', (uuid,))
        await db.commit()
        logging.debug(f"Set task {uuid} as inactive")
        return True
    except Exception as e:
        logging.error(f"Error setting task inactive: {e}")
        return False
