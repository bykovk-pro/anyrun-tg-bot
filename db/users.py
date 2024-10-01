from db.common import get_db_pool, generate_uuid

async def add_user(telegram_id, is_admin=False):
    user_uuid = generate_uuid()
    db = await get_db_pool()
    await db.execute('''
        INSERT OR IGNORE INTO users (user_uuid, telegram_id, is_admin)
        VALUES (?, ?, ?)
    ''', (user_uuid, telegram_id, is_admin))
    await db.commit()
    return user_uuid

async def get_user_by_telegram_id(telegram_id: int):
    db = await get_db_pool()
    async with db.execute('''
        SELECT *
            FROM users
            WHERE telegram_id = ?
            LIMIT 1
        ''', (int(telegram_id),)) as cursor:
        user = await cursor.fetchone()
    
    return dict(user) if user else None

async def get_admins():
    db = await get_db_pool()
    async with db.execute('''
        SELECT *
            FROM users
            WHERE is_admin = 1 AND is_deleted = 0
        ''') as cursor:
        admins = await cursor.fetchall()
    
    return [dict(admin) for admin in admins]

async def update_user_admin_status(user_uuid, is_admin):
    db = await get_db_pool()
    await db.execute('''
        UPDATE users
            SET is_admin = ?
            WHERE user_uuid = ?
    ''', (is_admin, user_uuid))
    await db.commit()

async def delete_user(user_uuid):
    db = await get_db_pool()
    await db.execute('''
        UPDATE users
            SET is_deleted = TRUE
            WHERE user_uuid = ?
    ''', (user_uuid,))
    await db.commit()

async def get_user_uuid(telegram_id):
    db = await get_db_pool()
    async with db.execute('''
        SELECT user_uuid
        FROM users
            WHERE telegram_id = ?
            LIMIT 1
        ''', (telegram_id,)) as cursor:
        result = await cursor.fetchone()
    
    return result[0] if result else None

async def is_user_admin(telegram_id: int):
    db = await get_db_pool()
    async with db.execute('''
        SELECT is_admin
            FROM users
            WHERE telegram_id = ? AND is_deleted = 0
            LIMIT 1
        ''', (telegram_id,)) as cursor:
            result = await cursor.fetchone()
    
    return result[0] if result else False

async def get_non_admin_users():
    db = await get_db_pool()
    async with db.execute('''
        SELECT telegram_id, first_access_date, last_access_date, is_banned
            FROM users
            WHERE is_deleted = 0 AND is_admin = 0
        ''') as cursor:
        users = await cursor.fetchall()
    
    return [dict(user) for user in users]

async def update_user_ban_status(telegram_id: int, is_banned: bool):
    db = await get_db_pool()
    await db.execute('''
        UPDATE users
            SET is_banned = ?
            WHERE telegram_id = ?
    ''', (is_banned, telegram_id))
    await db.commit()