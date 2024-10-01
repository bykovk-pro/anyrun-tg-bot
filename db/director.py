import os
import datetime 
import logging
import pyminizip
from dotenv import load_dotenv
from db.common import get_db_pool, DB_FILE
from db.users import add_user

# Загружаем переменные окружения
load_dotenv()

async def init_database():
    try:
        db = await get_db_pool()
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_uuid TEXT PRIMARY KEY,
                telegram_id INTEGER UNIQUE,
                first_access_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_access_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT FALSE,
                is_banned BOOLEAN DEFAULT FALSE,
                is_deleted BOOLEAN DEFAULT FALSE
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                key_uuid TEXT PRIMARY KEY,
                user_uuid TEXT,
                api_key TEXT UNIQUE,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                key_name TEXT,
                is_active BOOLEAN DEFAULT FALSE,
                is_deleted BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_uuid) REFERENCES users(user_uuid)
            )
        ''')
        await db.commit()
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.critical(f"Error initializing database: {e}")
        raise

async def backup_database():
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"database_backup_{timestamp}.zip"
        backup_path = os.path.join("backups", backup_filename)

        os.makedirs("backups", exist_ok=True)
        
        compression_level = 9
        password = os.getenv('DB_PASSWORD')
        
        if not password:
            raise ValueError("DB_PASSWORD not set in environment variables")
        
        pyminizip.compress(DB_FILE, None, backup_path, password, compression_level)
        
        return backup_path
    except Exception as e:
        logging.error(f"Error creating database backup: {str(e)}")
        raise

async def check_and_setup_admin(config):
    admin_id = config.get('TELEGRAM_ADMIN_ID')
    if admin_id:
        await add_user(int(admin_id), is_admin=True)
