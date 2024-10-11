import os
import aiosqlite
import logging

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_FILE = os.path.join(ROOT_DIR, 'anyrun-tg-bot.db')

async def get_db():
    return await aiosqlite.connect(DB_FILE)

db_pool = None

async def init_db_pool():
    global db_pool
    if db_pool is None:
        logging.debug(f"Creating new database connection to {DB_FILE}")
        db_pool = await aiosqlite.connect(DB_FILE)
        logging.debug("Database connection created")
    return db_pool

async def get_db_pool():
    if db_pool is None:
        logging.debug("Database pool not initialized, initializing now")
        await init_db_pool()
    return db_pool
