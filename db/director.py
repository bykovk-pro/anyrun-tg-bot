import os
import sqlite3
import zipfile
import time
import logging
from db.common import DB_FILE
from db.users import add_user, get_admins, update_user_admin_status
from db.api_keys import *

def init_database():
    try:
        if not os.path.exists(DB_FILE):
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

            logging.info('Database created successfully')
        else:
            logging.debug('Database already exists')
    except Exception as e:
        logging.critical(f'Error initializing database: {str(e)}')
        raise

def check_and_setup_admin(config):
    admin_id = config.get('TELEGRAM_ADMIN_ID')
    logging.info('Checking admin configuration')

    if not admin_id:
        logging.warning('Admin ID not set in configuration')
    else:
        logging.info('Admin ID found in configuration')

    existing_admins = get_admins()
    
    if existing_admins:
        if len(existing_admins) > 1 or (admin_id and str(existing_admins[0]['telegram_id']) != str(admin_id)):
            while True:
                logging.warning('Multiple admins found or admin mismatch')
                print("Please choose an admin from the following list:")
                for i, admin in enumerate(existing_admins, 1):
                    print(f"{i}. {admin['telegram_id']}")
                
                choice = input("Enter the number of your choice (or 'q' to quit): ")
                if choice.lower() == 'q':
                    logging.warning('Admin choice cancelled by user')
                    print("Admin selection cancelled.")
                    return
                
                try:
                    choice = int(choice)
                    if 1 <= choice <= len(existing_admins):
                        chosen_admin = existing_admins[choice - 1]
                        for admin in existing_admins:
                            update_user_admin_status(admin['user_uuid'], admin['telegram_id'] == chosen_admin['telegram_id'])
                        logging.info(f"Admin status updated: {chosen_admin['telegram_id']} is now the sole admin")
                        print(f"Admin updated successfully. Telegram ID {chosen_admin['telegram_id']} is now the sole admin.")
                        return
                    else:
                        print("Invalid choice. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
    elif admin_id:
        add_user(admin_id, is_admin=True)
        logging.info(f"Admin user added with ID: {admin_id}")
        print(f"Admin user added successfully with Telegram ID: {admin_id}")
    else:
        logging.warning('No admin configured and no existing admins found')
        print("No admin is configured, and no existing admins were found. Please set an admin ID in the configuration.")

def reinitialize_database():
    confirmation = input("Are you sure you want to reinitialize the database? (yes/no): ")
    if confirmation.lower() == 'yes':
        os.remove(DB_FILE)
        logging.info('Database deleted')
        init_database()
        check_and_setup_admin()
    else:
        print("Database reinitialization canceled.")

def backup_database():
    timestamp = int(time.time())
    backup_file = os.path.join(os.path.dirname(__file__), f'anyrun-tg-bot_{timestamp}.zip')

    with zipfile.ZipFile(backup_file, 'w') as zipf:
        zipf.write(DB_FILE, os.path.basename(DB_FILE))

    logging.info('Backup created')

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

init_database()