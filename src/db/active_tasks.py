from src.db.common import get_db_pool

async def add_active_task(telegram_id: int, uuid: str):
    db = await get_db_pool()
    async with db.cursor() as cursor:
        await cursor.execute('''
            INSERT INTO active_tasks (telegram_id, uuid)
            VALUES (?, ?)
        ''', (telegram_id, uuid))
    await db.commit()

#async def get_active_tasks(telegram_id: int):
#    db = await get_db_pool()
#    async with db.cursor() as cursor:
#        await cursor.execute('''
#            SELECT TOP 1 uuid FROM active_tasks
#            WHERE telegram_id = ? AND is_active = TRUE
#            ORDER BY created_at DESC
#        ''', (telegram_id,))
#        return [row[0] for row in await cursor.fetchall()]

async def set_task_inactive(uuid: str):
    db = await get_db_pool()
    async with db.cursor() as cursor:
        await cursor.execute('''
            UPDATE active_tasks
            SET is_active = FALSE
            WHERE uuid = ?
        ''', (uuid,))
    await db.commit()
