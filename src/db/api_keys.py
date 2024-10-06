from src.db.common import get_db

async def add_api_key(telegram_id: int, api_key: str, key_name: str):
    db = await get_db()
    async with db.transaction():
        # Деактивируем все существующие ключи пользователя
        await db.execute('''
            UPDATE api_keys SET is_active = FALSE
            WHERE telegram_id = ?
        ''', (telegram_id,))
        # Добавляем новый ключ как активный
        await db.execute('''
            INSERT INTO api_keys (telegram_id, api_key, key_name, is_active)
            VALUES (?, ?, ?, TRUE)
        ''', (telegram_id, api_key, key_name))

async def delete_api_key(telegram_id: int, api_key: str):
    db = await get_db()
    async with db.transaction():
        # Удаляем ключ
        await db.execute('''
            DELETE FROM api_keys
            WHERE telegram_id = ? AND api_key = ?
        ''', (telegram_id, api_key))
        # Если это был активный ключ, активируем другой (если есть)
        await db.execute('''
            UPDATE api_keys SET is_active = TRUE
            WHERE telegram_id = ? AND api_key = (
                SELECT api_key FROM api_keys
                WHERE telegram_id = ?
                LIMIT 1
            )
        ''', (telegram_id, telegram_id))

async def get_api_keys(telegram_id: int):
    db = await get_db()
    cursor = await db.execute('''
        SELECT api_key, key_name, is_active
        FROM api_keys
        WHERE telegram_id = ?
    ''', (telegram_id,))
    return await cursor.fetchall()

async def change_api_key_name(telegram_id: int, api_key: str, new_key_name: str):
    db = await get_db()
    await db.execute('''
        UPDATE api_keys
        SET key_name = ?
        WHERE telegram_id = ? AND api_key = ?
    ''', (new_key_name, telegram_id, api_key))

async def set_active_api_key(telegram_id: int, api_key: str):
    db = await get_db()
    async with db.transaction():
        # Деактивируем все ключи пользователя
        await db.execute('''
            UPDATE api_keys SET is_active = FALSE
            WHERE telegram_id = ?
        ''', (telegram_id,))
        # Активируем выбранный ключ
        await db.execute('''
            UPDATE api_keys SET is_active = TRUE
            WHERE telegram_id = ? AND api_key = ?
        ''', (telegram_id, api_key))

async def get_active_api_key(telegram_id: int):
    db = await get_db()
    cursor = await db.execute('''
        SELECT api_key
        FROM api_keys
        WHERE telegram_id = ? AND is_active = TRUE
    ''', (telegram_id,))
    result = await cursor.fetchone()
    return result[0] if result else None
