import os
import json
import logging
from lang.context import get_current_language

LANG_DIR = os.path.dirname(os.path.abspath(__file__))

def load_language_file(lang_code):
    lang_file = os.path.join(LANG_DIR, f'{lang_code}.json')
    try:
        with open(lang_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"Language file not found: {lang_file}")
        return {}
    except json.JSONDecodeError:
        logging.warning(f"Invalid JSON in language file: {lang_file}")
        return {}

def get(key):
    language = get_current_language()
    lang_data = load_language_file(language)
    
    if key in lang_data:
        return lang_data[key]
    
    # If the key is not found in the current language, try English
    en_data = load_language_file('en')
    return en_data.get(key, key)

