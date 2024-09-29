import os
import uuid

DB_FILE = os.path.join(os.path.dirname(__file__), 'arsbtlgbot.db')

def generate_uuid():
    return str(uuid.uuid4())
