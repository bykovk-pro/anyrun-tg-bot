import os
import json
import logging
from lang.context import get_current_language, set_message_getter
from utils.logger import log

# Path to the language files
LANG_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LANGUAGE = "en"

def load_language_file(language_code):
    lang_file = os.path.join(LANG_DIR, f"{language_code}.json")
    try:
        with open(lang_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        if language_code != DEFAULT_LANGUAGE:
            log('LANGUAGE_FILE_NOT_FOUND', logging.WARNING, language=language_code, file=lang_file)
            return load_language_file(DEFAULT_LANGUAGE)
        else:
            log('DEFAULT_LANGUAGE_FILE_NOT_FOUND', logging.ERROR, file=lang_file)
            return {}
    except json.JSONDecodeError:
        log('INVALID_LANGUAGE_FILE', logging.ERROR, language=language_code, file=lang_file)
        if language_code != DEFAULT_LANGUAGE:
            return load_language_file(DEFAULT_LANGUAGE)
        else:
            return {}

def get(message_key):
    language = get_current_language()
    if language is None:
        language = DEFAULT_LANGUAGE
    language_data = load_language_file(language)
    if language_data and message_key in language_data:
        return language_data[message_key]
    else:
        log('MESSAGE_KEY_NOT_FOUND', logging.WARNING, key=str(message_key), language=str(language))
        return language_data.get('MISSING_MESSAGE_KEY', '').format(key=message_key)

set_message_getter(get)

