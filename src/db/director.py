import logging
import os
from importlib.metadata import version
from src.db.pool import get_db_pool, DB_FILE
from src.db.migrations import run_migrations
from src.lang.director import humanize
from src.lang.decorators import with_locale

BOT_VERSION = version("anyrun-tg-bot")

@with_locale
async def init_database():
    try:
        logging.debug(f"Initializing database at {DB_FILE}")
        db = await get_db_pool()
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS schema_version (
                version TEXT PRIMARY KEY
            )
        ''')
        
        async with db.execute("SELECT version FROM schema_version") as cursor:
            version_record = await cursor.fetchone()
            if not version_record:
                await db.execute("INSERT INTO schema_version (version) VALUES ('0.0.0')")
                await db.commit()
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                telegram_id BIGINT PRIMARY KEY,
                first_access_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_access_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT FALSE,
                is_banned BOOLEAN DEFAULT FALSE,
                is_deleted BOOLEAN DEFAULT FALSE,
                api_requests_count INTEGER DEFAULT 0
            )
        ''')
        
        admin_id = os.getenv('TELEGRAM_ADMIN_ID')
        if admin_id:
            try:
                admin_id = int(admin_id)
                await db.execute('''
                    INSERT INTO users (telegram_id, is_admin)
                    VALUES (?, TRUE)
                    ON CONFLICT(telegram_id) DO UPDATE SET
                    is_admin = TRUE
                ''', (admin_id,))
                logging.info(f"Admin user {admin_id} added or updated")
            except ValueError:
                logging.error("Invalid TELEGRAM_ADMIN_ID format")
        else:
            logging.warning("TELEGRAM_ADMIN_ID not set")

        await db.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                api_key TEXT PRIMARY KEY,
                telegram_id BIGINT NOT NULL,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                key_name TEXT,
                is_active BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS active_tasks (
                telegram_id BIGINT,
                uuid TEXT PRIMARY KEY,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
            )
        ''')

        await db.commit()
        await run_migrations(BOT_VERSION)
        logging.info("Database initialized and migrated successfully")
    except Exception as e:
        logging.critical(await humanize("DATABASE_INIT_ERROR").format(error=str(e)))
        raise
