from src.db.common import get_db_pool
import sqlite3

async def db_add_api_key(telegram_id: int, api_key: str, key_name: str):
    db = await get_db_pool()
    try:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT 1 FROM api_keys WHERE api_key = ?', (api_key,))
            if await cursor.fetchone():
                return False, "API_KEY_ALREADY_EXISTS"
            
            await cursor.execute('''
                UPDATE api_keys SET is_active = FALSE
                WHERE telegram_id = ?
            ''', (telegram_id,))
            await cursor.execute('''
                INSERT INTO api_keys (telegram_id, api_key, key_name, is_active)
                VALUES (?, ?, ?, TRUE)
            ''', (telegram_id, api_key, key_name))
        await db.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "API_KEY_ALREADY_EXISTS"
    except Exception as e:
        return False, str(e)

async def db_delete_api_key(telegram_id: int, api_key: str):
    db = await get_db_pool()
    async with db.cursor() as cursor:
        await cursor.execute('''
            DELETE FROM api_keys
            WHERE telegram_id = ? AND api_key = ?
        ''', (telegram_id, api_key))
        await cursor.execute('''
            UPDATE api_keys SET is_active = TRUE
            WHERE telegram_id = ? AND api_key = (
                SELECT api_key FROM api_keys
                WHERE telegram_id = ?
                LIMIT 1
            )
        ''', (telegram_id, telegram_id))
    await db.commit()

async def db_get_api_keys(telegram_id: int):
    db = await get_db_pool()
    async with db.cursor() as cursor:
        await cursor.execute('''
            SELECT api_key, key_name, is_active
            FROM api_keys
            WHERE telegram_id = ?
            ORDER BY is_active DESC, key_name ASC
        ''', (telegram_id,))
        return await cursor.fetchall()

async def db_change_api_key_name(telegram_id: int, api_key: str, new_key_name: str):
    db = await get_db_pool()
    async with db.cursor() as cursor:
        await cursor.execute('''
            UPDATE api_keys
            SET key_name = ?
            WHERE telegram_id = ? AND api_key = ?
        ''', (new_key_name, telegram_id, api_key))
    await db.commit()

async def db_set_active_api_key(telegram_id: int, api_key: str):
    db = await get_db_pool()
    async with db.cursor() as cursor:
        await cursor.execute('''
            UPDATE api_keys SET is_active = FALSE
            WHERE telegram_id = ?
        ''', (telegram_id,))
        await cursor.execute('''
            UPDATE api_keys SET is_active = TRUE
            WHERE telegram_id = ? AND api_key = ?
        ''', (telegram_id, api_key))
    await db.commit()

async def db_get_active_api_key(telegram_id: int):
    db = await get_db_pool()
    async with db.cursor() as cursor:
        await cursor.execute('''
            SELECT api_key
            FROM api_keys
            WHERE telegram_id = ? AND is_active = TRUE
        ''', (telegram_id,))
        result = await cursor.fetchone()
    return result[0] if result else None
