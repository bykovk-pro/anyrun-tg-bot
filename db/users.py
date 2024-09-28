import sqlite3
from db.worker import DB_FILE, generate_uuid

def add_user(telegram_id, is_banned=False, is_deleted=False, is_admin=False):
    # Add a new user to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO users (user_uuid, telegram_id, first_access_date, last_access_date, is_banned, is_deleted, is_admin)
        VALUES (?, ?, datetime('now'), NULL, ?, ?, ?)
    ''', (generate_uuid(), telegram_id, is_banned, is_deleted, is_admin))

    conn.commit()
    conn.close()

def delete_user(user_uuid):
    # Delete a user by setting is_deleted to True
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users
        SET is_deleted = TRUE
        WHERE user_uuid = ?
    ''', (user_uuid,))

    conn.commit()
    conn.close()

def get_user_uuid(telegram_id):
    # Get user_uuid by telegram_id
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_uuid
        FROM users
        WHERE telegram_id = ?
        LIMIT 1
    ''', (telegram_id,))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None
