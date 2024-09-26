import os
import sqlite3

# Path to the database file
DB_FILE = os.path.join(os.path.dirname(__file__), 'arsbtlgbot.db')

def init_database():
    # Check if the database file exists
    if not os.path.exists(DB_FILE):
        # If the file doesn't exist, create it and set up the database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Create tables (we'll add more tables and their structures later)
        # cursor.execute('''
        #     CREATE TABLE IF NOT EXISTS example_table (
        #         id INTEGER PRIMARY KEY,
        #         name TEXT NOT NULL
        #     )
        # ''')
    
        # Commit changes and close the connection
        conn.commit()
        conn.close()
        print(f"Database created at {DB_FILE}")
    else:
        print(f"Database already exists at {DB_FILE}")

# Function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# Call this function when the module is imported to ensure the database exists
init_database()
