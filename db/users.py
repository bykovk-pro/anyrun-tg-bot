import sqlite3
import logging
from db.common import DB_FILE, generate_uuid

def add_user(telegram_id: int, is_admin: bool = False):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        user_uuid = generate_uuid()
        cursor.execute('''
            INSERT INTO users (user_uuid, telegram_id, first_access_date, is_admin)
            VALUES (?, ?, datetime('now'), ?)
        ''', (user_uuid, telegram_id, is_admin))
        conn.commit()
        conn.close()
        logging.info(f'USER_ADDED: telegram_id={telegram_id}, is_admin={is_admin}')
    except sqlite3.IntegrityError:
        logging.warning(f'USER_ALREADY_EXISTS: telegram_id={telegram_id}')
    except Exception as e:
        logging.error(f'USER_ADD_ERROR: telegram_id={telegram_id}', exc_info=True)
        raise

def get_user_by_telegram_id(telegram_id: int):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT *
        FROM users
        WHERE telegram_id = ?
        LIMIT 1
    ''', (int(telegram_id),))

    user = cursor.fetchone()
    conn.close()

    return dict(user) if user else None

def get_admins():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT *
        FROM users
        WHERE is_admin = 1 AND is_deleted = 0
    ''')

    admins = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return admins

def update_user_admin_status(user_uuid, is_admin):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users
        SET is_admin = ?
        WHERE user_uuid = ?
    ''', (is_admin, user_uuid))

    conn.commit()
    conn.close()

def delete_user(user_uuid):
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
