from src.db.common import get_db_pool

async def add_active_task(telegram_id: int, uuid: str):
    db = await get_db_pool()
    async with db.cursor() as cursor:
        await cursor.execute('''
            INSERT INTO active_tasks (telegram_id, uuid)
            VALUES (?, ?)
        ''', (telegram_id, uuid))
    await db.commit()

async def set_task_inactive(uuid: str):
    db = await get_db_pool()
    async with db.cursor() as cursor:
        await cursor.execute('''
            UPDATE active_tasks
            SET is_active = FALSE
            WHERE uuid = ?
        ''', (uuid,))
    await db.commit()
