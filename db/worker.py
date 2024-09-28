import os
import sqlite3
import uuid
import zipfile
import time
from db.users import *
from db.api_keys import *
from lang.director import get_constant

# Path to the database file
DB_FILE = os.path.join(os.path.dirname(__file__), 'arsbtlgbot.db')

def generate_uuid():
    # Generate a new UUID
    return str(uuid.uuid4())

def init_database():
    # Check if the database file exists
    if not os.path.exists(DB_FILE):
        # If the file doesn't exist, create it and set up the database
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

        # Create API keys table
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

        # Commit changes and close the connection
        conn.commit()
        conn.close()

        # Add the admin user from environment variable
        admin_id = os.getenv('ANYRUN_SB_ADMIN_ID')
        if admin_id is None:
            print("Error: Environment variable ANYRUN_SB_ADMIN_ID is not set.")
            exit(1)

        add_user(telegram_id=admin_id, is_admin=True)

        print(f"Database created at {DB_FILE}")
    else:
        print(f"Database already exists at {DB_FILE}")

def reinitialize_database():
    # Reinitialize the database after user confirmation
    confirmation = input("Type 'REINIT' to confirm reinitialization: ")
    if confirmation == 'REINIT':
        os.remove(DB_FILE)
        print("Database deleted.")
        init_database()
    else:
        print("Reinitialization canceled.")

def backup_database():
    # Create a backup of the database
    timestamp = int(time.time())
    backup_file = os.path.join(os.path.dirname(__file__), f'arsbtlgbot_{timestamp}.zip')

    with zipfile.ZipFile(backup_file, 'w') as zipf:
        zipf.write(DB_FILE, os.path.basename(DB_FILE))

    print(f"Backup created at {backup_file}")

# Function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# Call this function when the module is imported to ensure the database exists
init_database()
