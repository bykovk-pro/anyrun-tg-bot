import sqlite3
from db.common import DB_FILE, generate_uuid
from utils.logger import log

def add_api_key(user_uuid, api_key, key_name='API Key', is_active=False, is_deleted=False):
    # Add a new API key for a user
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO api_keys (key_uuid, user_uuid, api_key, added_date, key_name, is_active, is_deleted)
        VALUES (?, ?, ?, datetime('now'), ?, ?, ?)
    ''', (generate_uuid(), user_uuid, api_key, key_name, is_active, is_deleted))

    conn.commit()
    conn.close()

def delete_api_key(user_uuid, key_uuid):
    # Delete an API key by setting is_deleted to True
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE api_keys
        SET is_deleted = TRUE
        WHERE user_uuid = ? AND key_uuid = ?
    ''', (user_uuid, key_uuid))

    conn.commit()
    conn.close()
