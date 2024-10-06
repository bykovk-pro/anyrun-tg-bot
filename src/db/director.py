import os
import datetime 
import logging
import pyzipper
import tempfile
import shutil
from src.db.common import get_db_pool, DB_FILE, ROOT_DIR
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

async def backup(config): # TODO: В архив не попадает файл с базой данных
    try:
        if not os.path.exists(DB_FILE):
            logging.error(f"Database file does not exist: {DB_FILE}")
            return None
        
        logging.debug(f"Database file exists: {DB_FILE}")
        
        backup_dir = os.path.join(ROOT_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        logging.info(f"Backup directory created/confirmed: {backup_dir}")
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.zip"
        backup_path = os.path.join(backup_dir, backup_filename)
        logging.debug(f"Backup file path: {backup_path}")
        
        password = config.get('DB_PASSWORD', None)
        if password is None:
            logging.error("DB_PASSWORD is not set in the configuration.")
            return None
        
        try:
            with pyzipper.AESZipFile(backup_path, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zipf:
                zipf.setpassword(password.encode())
                logging.debug(f"Attempting to add database file to backup: {DB_FILE}")
                zipf.write(DB_FILE, arcname=os.path.basename(DB_FILE))
        except (PermissionError, FileNotFoundError) as file_error:
            logging.error(f"File access error: {str(file_error)}")
            return None
        except Exception as e:
            logging.error(f"Error during backup process: {str(e)}")
            return None
        
        if os.path.exists(backup_path):
            backup_size = os.path.getsize(backup_path)
            logging.info(f"Backup file created. Size: {backup_size} bytes")
            if backup_size > 0:
                logging.info(f"Database backup created successfully: {backup_path}")
                return backup_path
            else:
                logging.error(f"Created backup file is empty: {backup_path}")
                return None
        else:
            logging.error(f"Backup file was not created: {backup_path}")
            return None
    except Exception as e:
        logging.error(f"Error creating database backup: {str(e)}")
        return None

async def restore(config, backup_file):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            with pyzipper.AESZipFile(backup_file, 'r', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zipf:
                zipf.setpassword(config.get('DB_PASSWORD', '').encode())
                zipf.extractall(temp_dir)
            
            extracted_db = os.path.join(temp_dir, os.path.basename(DB_FILE))
            shutil.copy2(extracted_db, DB_FILE)
        
        logging.info(f"Database restored from backup: {backup_file}")
    except Exception as e:
        logging.error(f"Error restoring database from backup: {str(e)}")
        raise

async def check_and_setup_admin(config):
    admin_id = config.get('TELEGRAM_ADMIN_ID')
    if admin_id:
        await add_user(int(admin_id), is_admin=True)
