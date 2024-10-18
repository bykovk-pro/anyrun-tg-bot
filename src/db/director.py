import os
import datetime 
import logging
import pyzipper
import tempfile
import shutil
from importlib.metadata import version
from src.db.common import get_db_pool, DB_FILE, ROOT_DIR
from src.db.users import db_add_user
from src.db.migrations import run_migrations
from src.config import load_config

BOT_VERSION = version("anyrun-tg-bot")

async def init_database():
    try:
        logging.debug(f"Initializing database at {DB_FILE}")
        db = await get_db_pool()
        logging.debug("Database connection established")
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                telegram_id BIGINT PRIMARY KEY,
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
        
        await run_migrations(BOT_VERSION)
        
        logging.info("Database initialized and migrated successfully")
    except Exception as e:
        logging.critical(f"Error initializing database: {e}")
        raise

async def backup():
    try:
        db_file_abs_path = os.path.abspath(DB_FILE)
        logging.debug(f"Absolute path to database file: {db_file_abs_path}")
        
        if not os.path.exists(db_file_abs_path):
            logging.error(f"Database file does not exist: {db_file_abs_path}")
            return None
        
        db_file_size = os.path.getsize(db_file_abs_path)
        logging.debug(f"Database file size: {db_file_size} bytes")
        
        if db_file_size == 0:
            logging.error(f"Database file is empty: {db_file_abs_path}")
            return None
        
        logging.debug(f"Database file exists and is readable: {db_file_abs_path}")
        
        backup_dir = os.path.join(ROOT_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        if not os.access(backup_dir, os.W_OK):
            logging.error(f"No write access to backup directory: {backup_dir}")
            return None
        
        logging.info(f"Backup directory created/confirmed and writable: {backup_dir}")
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.zip"
        backup_path = os.path.join(backup_dir, backup_filename)
        logging.debug(f"Backup file path: {backup_path}")
        
        password = load_config().get('DB_PASSWORD', None)
        if password is None:
            logging.error("DB_PASSWORD is not set in the configuration.")
            return None
        
        logging.debug(f"Password length: {len(password)}")
        encoded_password = password.encode()
        logging.debug(f"Encoded password length: {len(encoded_password)}")
        
        try:
            with pyzipper.AESZipFile(backup_path, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zipf:
                zipf.setpassword(encoded_password)
                logging.debug(f"Attempting to add database file to backup: {db_file_abs_path}")
                zipf.write(db_file_abs_path, arcname=os.path.basename(db_file_abs_path))
                logging.debug(f"File added to archive: {os.path.basename(db_file_abs_path)}")
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
                try:
                    with pyzipper.AESZipFile(backup_path, 'r', encryption=pyzipper.WZ_AES) as check_zip:
                        check_zip.setpassword(encoded_password)
                        file_list = check_zip.namelist()
                        logging.debug(f"Files in the archive: {file_list}")
                        if file_list:
                            logging.info(f"Database backup created successfully: {backup_path}")
                            return backup_path
                        else:
                            logging.error(f"Created backup file is empty (no files inside): {backup_path}")
                            return None
                except Exception as check_error:
                    logging.error(f"Error checking backup file: {str(check_error)}")
                    return None
            else:
                logging.error(f"Created backup file is empty: {backup_path}")
                return None
        else:
            logging.error(f"Backup file was not created: {backup_path}")
            return None
    except Exception as e:
        logging.error(f"Error creating database backup: {str(e)}")
        return None

async def restore(backup_file):
    try:
        logging.info(f"Starting database restore from backup: {backup_file}")
        
        if not os.path.exists(backup_file):
            logging.error(f"Backup file does not exist: {backup_file}")
            return False

        password = load_config().get('DB_PASSWORD', '')
        if not password:
            logging.error("DB_PASSWORD is not set in the configuration.")
            return False

        with tempfile.TemporaryDirectory() as temp_dir:
            logging.debug(f"Created temporary directory: {temp_dir}")
            
            try:
                with pyzipper.AESZipFile(backup_file, 'r', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zipf:
                    zipf.setpassword(password.encode())
                    zipf.extractall(temp_dir)
                    logging.debug("Successfully extracted backup archive")
            except Exception as e:
                logging.error(f"Error extracting backup archive: {str(e)}")
                return False

            extracted_db = os.path.join(temp_dir, os.path.basename(DB_FILE))
            if not os.path.exists(extracted_db):
                logging.error(f"Extracted database file not found: {extracted_db}")
                return False

            current_db_backup = f"{DB_FILE}.bak"
            if os.path.exists(DB_FILE):
                shutil.copy2(DB_FILE, current_db_backup)
                logging.info(f"Created backup of current database: {current_db_backup}")

            try:
                shutil.copy2(extracted_db, DB_FILE)
                logging.info(f"Successfully restored database from backup")
                return True
            except Exception as e:
                logging.error(f"Error copying restored database: {str(e)}")
                if os.path.exists(current_db_backup):
                    shutil.move(current_db_backup, DB_FILE)
                    logging.info("Reverted to original database due to restore failure")
                return False

    except Exception as e:
        logging.error(f"Error restoring database from backup: {str(e)}")
        return False

async def check_and_setup_admin():
    admin_id = load_config().get('TELEGRAM_ADMIN_ID')
    if admin_id:
        await db_add_user(int(admin_id), is_admin=True)
