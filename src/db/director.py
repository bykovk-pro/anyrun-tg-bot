import os
import datetime 
import logging
import pyzipper
from src.db.common import get_db_pool, DB_FILE
from src.db.users import add_user

async def init_database():
    try:
        logging.debug(f"Initializing database at {DB_FILE}")
        db = await get_db_pool()
        logging.debug("Database connection established")
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                telegram_id BIGINT PRIMARY KEY,
                lang TEXT NOT NULL DEFAULT 'en',
                first_access_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_access_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT FALSE,
                is_banned BOOLEAN DEFAULT FALSE,
                is_deleted BOOLEAN DEFAULT FALSE
            )
        ''')
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
            CREATE TRIGGER IF NOT EXISTS ensure_single_active_key
            AFTER INSERT ON api_keys
            BEGIN
                UPDATE api_keys SET is_active = FALSE
                WHERE telegram_id = NEW.telegram_id AND api_key != NEW.api_key;
            END;
        ''')
        await db.commit()
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.critical(f"Error initializing database: {e}")
        raise

async def backup(config):
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{timestamp}.zip"
        backup_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backups", backup_filename)

        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        compression_level = 9 
        password = config.get('DB_PASSWORD')
        
        if not password:
            raise ValueError("DB_PASSWORD not set in environment variables")
        
        with pyzipper.AESZipFile(backup_path, 'w', compression=pyzipper.ZIP_LZMA, 
                                 encryption=pyzipper.WZ_AES, compresslevel=compression_level) as zf:
            zf.setpassword(password.encode())
            zf.write(DB_FILE, os.path.basename(DB_FILE))
        
        logging.info(f"Database backup created: {backup_path}")
        return backup_path
    except Exception as e:
        logging.error(f"Error creating database backup: {str(e)}")
        raise

async def check_and_setup_admin(config):
    admin_id = config.get('TELEGRAM_ADMIN_ID')
    if admin_id:
        await add_user(int(admin_id), is_admin=True)
