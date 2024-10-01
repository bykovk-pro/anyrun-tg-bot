import os
import uuid
import aiosqlite

DB_FILE = os.path.join(os.path.dirname(__file__), 'anyrun-tg-bot.db')

async def get_db():
    return await aiosqlite.connect(DB_FILE)

db_pool = None

async def init_db_pool():
    global db_pool
    if db_pool is None:
        db_pool = await aiosqlite.connect(DB_FILE)
    return db_pool

async def get_db_pool():
    if db_pool is None:
        await init_db_pool()
    return db_pool

def generate_uuid():
    return str(uuid.uuid4())
