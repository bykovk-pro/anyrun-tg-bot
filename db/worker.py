import os
import sqlite3
import zipfile
import time
import logging
from db.common import DB_FILE, generate_uuid
from db.users import add_user, get_user_by_telegram_id, get_admins, update_user_admin_status
from db.api_keys import *
from lang.director import get
from utils.logger import log
from dotenv import load_dotenv

def init_database():
    try:
        if not os.path.exists(DB_FILE):
            conn = sqlite3.connect(DB_FILE)
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_uuid TEXT PRIMARY KEY,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    first_access_date DATETIME NOT NULL,
                    last_access_date DATETIME,
                    is_banned BOOLEAN DEFAULT FALSE,
                    is_deleted BOOLEAN DEFAULT FALSE,
                    is_admin BOOLEAN DEFAULT FALSE
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    key_uuid TEXT PRIMARY KEY,
                    user_uuid TEXT NOT NULL,
                    api_key TEXT NOT NULL,
                    added_date DATETIME NOT NULL,
                    key_name TEXT DEFAULT 'API Key',
                    is_active BOOLEAN DEFAULT FALSE,
                    is_deleted BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_uuid) REFERENCES users(user_uuid),
                    UNIQUE (user_uuid, api_key)
                )
            ''')

            conn.commit()
            conn.close()

            log('DATABASE_CREATED', logging.INFO, path=DB_FILE)
        else:
            log('DATABASE_EXISTS', logging.DEBUG, path=DB_FILE)
    except Exception as e:
        log('DATABASE_INIT_ERROR', logging.CRITICAL, error=str(e))
        raise

def check_and_setup_admin():
    load_dotenv()
    
    admin_id = os.getenv('ANYRUN_SB_ADMIN_ID')
    log('CHECKING_ADMIN', logging.DEBUG, admin_id=admin_id)

    if admin_id:
        try:
            admin_id = int(admin_id)
        except ValueError:
            log('INVALID_ADMIN_ID', logging.ERROR, admin_id=admin_id)
            return
        
        admin_user = get_user_by_telegram_id(admin_id)
        log('ADMIN_USER_CHECK', logging.DEBUG, admin_user=admin_user)
        if not admin_user:
            add_user(telegram_id=admin_id, is_admin=True)
            log('ADMIN_ID_SET_CREATING_ADMIN', logging.INFO)
        elif not admin_user['is_admin'] or admin_user['is_deleted']:
            update_user_admin_status(admin_user['user_uuid'], True)
            log('ADMIN_STATUS_UPDATED', logging.INFO, telegram_id=admin_id)
        return
    
    admins = get_admins()
    
    if len(admins) == 1:
        log('ADMIN_ID_NOT_SET_ADMIN_FOUND', logging.WARNING, telegram_id=admins[0]['telegram_id'])
        return
    
    if len(admins) > 1:
        log('ADMIN_ID_NOT_SET_MULTIPLE_ADMINS', logging.WARNING)
        print(get('CHOOSE_ADMIN_PROMPT'))
        for i, admin in enumerate(admins, 1):
            print(f"{i}. {admin['telegram_id']}")
        
        while True:
            try:
                choice = int(input(get('ENTER_ADMIN_CHOICE')))
                if 1 <= choice <= len(admins):
                    chosen_admin = admins[choice - 1]
                    for admin in admins:
                        update_user_admin_status(admin['user_uuid'], admin['telegram_id'] == chosen_admin['telegram_id'])
                    log('ADMIN_ID_NOT_SET_ADMIN_FOUND', logging.WARNING, telegram_id=chosen_admin['telegram_id'])
                    return
                else:
                    print("Неверный выбор. Пожалуйста, выберите число из списка.")
            except ValueError:
                print("Пожалуйста, введите число.")
    
    print(get('NO_ADMIN_FOUND'))
    exit(1)

def reinitialize_database():
    confirmation = input(get('REINIT_CONFIRMATION'))
    if confirmation == 'REINIT':
        os.remove(DB_FILE)
        print(get('DATABASE_DELETED').format(path=DB_FILE))
        init_database()
        check_and_setup_admin()
    else:
        print(get('REINIT_CANCELED'))

def backup_database():
    timestamp = int(time.time())
    backup_file = os.path.join(os.path.dirname(__file__), f'arsbtlgbot_{timestamp}.zip')

    with zipfile.ZipFile(backup_file, 'w') as zipf:
        zipf.write(DB_FILE, os.path.basename(DB_FILE))

    log('BACKUP_CREATED', logging.INFO, path=backup_file)

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

init_database()
check_and_setup_admin()
