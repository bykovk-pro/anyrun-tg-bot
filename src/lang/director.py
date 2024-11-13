import os
import json
import logging
from typing import Dict
from src.lang.context import get_current_language

LANG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lang')

class LanguageManager:
    def __init__(self):
        self.languages: Dict[str, Dict[str, str]] = {}
        self.load_all_languages()

    def load_all_languages(self) -> None:
        self.languages.clear()
        for filename in os.listdir(LANG_DIR):
            if filename.endswith('.json'):
                lang_code = filename[:-5]
                self.load_language_file(lang_code)
        logging.info(f"Loaded languages: {', '.join(self.languages.keys())}")

    def load_language_file(self, lang_code: str) -> None:
        lang_file = os.path.join(LANG_DIR, f'{lang_code}.json')
        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.languages[lang_code] = json.load(f)
            logging.debug(f"Loaded language file: {lang_file}")
        except Exception as e:
            logging.error(f"Error loading language file {lang_file}: {e}")
            self.languages[lang_code] = {}

    def get_text(self, key: str, lang_code: str) -> str:
        lang_data = self.languages.get(lang_code, {})
        if key in lang_data:
            return lang_data[key]
        
        en_data = self.languages.get('en', {})
        if key in en_data:
            return en_data[key]
        
        logging.warning(f"Translation key not found: {key}")
        return key

language_manager = LanguageManager()

async def humanize(key: str) -> str:
    language = get_current_language()
    return language_manager.get_text(key, language)

