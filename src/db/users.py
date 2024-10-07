import logging
from src.db.common import get_db_pool

async def db_add_user(telegram_id: int, is_admin: bool = False):
    try:
        db = await get_db_pool()
        await db.execute('''
            INSERT OR IGNORE INTO users (telegram_id, is_admin)
            VALUES (?, ?)
        ''', (telegram_id, is_admin))
        await db.commit()
    except Exception as e:
        logging.error(f"Error adding user: {e}")
        raise

async def db_get_user(telegram_id: int):
    try:
        db = await get_db_pool()
        async with db.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,)) as cursor:
            return await cursor.fetchone()
    except Exception as e:
        logging.error(f"Error getting user: {e}")
        raise

async def db_update_user_language(telegram_id: int, lang: str):
    try:
        db = await get_db_pool()
        await db.execute('UPDATE users SET lang = ? WHERE telegram_id = ?', (lang, telegram_id))
        await db.commit()
    except Exception as e:
        logging.error(f"Error updating user language: {e}")
        raise

async def db_is_user_admin(telegram_id: int):
    try:
        db = await get_db_pool()
        async with db.execute('SELECT is_admin FROM users WHERE telegram_id = ?', (telegram_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else False
    except Exception as e:
        logging.error(f"Error checking if user is admin: {e}")
        raise

async def db_get_all_users():
    try:
        db = await get_db_pool()
        async with db.execute("SELECT * FROM users ORDER BY telegram_id") as cursor:
            users = await cursor.fetchall()
            logging.debug(f"Retrieved {len(users)} users from the database.")
            return users
    except Exception as e:
        logging.error(f"Error getting all users: {e}")
        return []

async def db_ban_user_by_id(user_id):
    try:
        db = await get_db_pool()
        await db.execute("UPDATE users SET is_banned = TRUE WHERE telegram_id = ?", (int(user_id),))
        await db.commit()
        return True
    except Exception as e:
        logging.error(f"Error banning user {user_id}: {e}")
        return False

async def db_unban_user_by_id(user_id):
    try:
        db = await get_db_pool()
        await db.execute("UPDATE users SET is_banned = FALSE WHERE telegram_id = ?", (int(user_id),))
        await db.commit()
        return True
    except Exception as e:
        logging.error(f"Error unbanning user {user_id}: {e}")
        return False

async def db_delete_user_by_id(user_id):
    try:
        db = await get_db_pool()
        await db.execute("UPDATE users SET is_deleted = TRUE WHERE telegram_id = ?", (int(user_id),))
        await db.commit()
        return True
    except Exception as e:
        logging.error(f"Error deleting user {user_id}: {e}")
        return False