from db.common import get_db, generate_uuid

async def add_api_key(user_uuid, api_key, key_name='API Key', is_active=False, is_deleted=False):
    async with await get_db() as db:
        await db.execute('''
            INSERT INTO api_keys (key_uuid, user_uuid, api_key, added_date, key_name, is_active, is_deleted)
            VALUES (?, ?, ?, datetime('now'), ?, ?, ?)
        ''', (generate_uuid(), user_uuid, api_key, key_name, is_active, is_deleted))
        await db.commit()

async def delete_api_key(user_uuid, key_uuid):
    async with await get_db() as db:
        await db.execute('''
            UPDATE api_keys
            SET is_deleted = TRUE
            WHERE user_uuid = ? AND key_uuid = ?
        ''', (user_uuid, key_uuid))
        await db.commit()
