import os
import uuid

# Path to the database file
DB_FILE = os.path.join(os.path.dirname(__file__), 'arsbtlgbot.db')

def generate_uuid():
    # Generate a new UUID
    return str(uuid.uuid4())
