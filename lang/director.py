import os
import json
from api.telegram import get_user_language

# Path to the language files
LANG_DIR = os.path.dirname(os.path.abspath(__file__))

def load_language_file(language_code):
    lang_file = os.path.join(LANG_DIR, f"{language_code}.json")
    try:
        with open(lang_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def get(constant_name):
    from telegram import Update
    update = Update.get_current()
    language_code = get_user_language(update)

    # Load the requested language file
    language_constants = load_language_file(language_code)

    # If the language file doesn't exist or couldn't be loaded, fall back to English
    if language_constants is None:
        language_constants = load_language_file('en_US')

    # If the constant is not in the language file, try to get it from the English file
    if constant_name not in language_constants:
        en_constants = load_language_file('en_US')
        return en_constants.get(constant_name, constant_name)

    # Return the constant from the language file
    return language_constants[constant_name]
