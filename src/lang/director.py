import os
import json
import logging
import threading
from typing import Dict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.lang.context import get_current_language

LANG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lang')

class LanguageFileHandler(FileSystemEventHandler):
    def __init__(self, reload_func):
        self.reload_func = reload_func

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.json'):
            logging.info(f"Language file modified: {event.src_path}")
            self.reload_func()

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.json'):
            logging.info(f"New language file created: {event.src_path}")
            self.reload_func()

class LanguageManager:
    def __init__(self):
        self.languages: Dict[str, Dict[str, str]] = {}
        self.load_all_languages()
        self.setup_file_watcher()

    def load_all_languages(self):
        self.languages.clear()
        for filename in os.listdir(LANG_DIR):
            if filename.endswith('.json'):
                lang_code = filename[:-5]
                self.load_language_file(lang_code)
        logging.info(f"Loaded languages: {', '.join(self.languages.keys())}")

    def load_language_file(self, lang_code):
        lang_file = os.path.join(LANG_DIR, f'{lang_code}.json')
        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.languages[lang_code] = json.load(f)
            logging.info(f"Loaded language file: {lang_file}")
            logging.debug(f"Language {lang_code} contents: {self.languages[lang_code]}")
        except FileNotFoundError:
            logging.warning(f"Language file not found: {lang_file}")
        except json.JSONDecodeError:
            logging.warning(f"Invalid JSON in language file: {lang_file}")

    def setup_file_watcher(self):
        event_handler = LanguageFileHandler(self.load_all_languages)
        observer = Observer()
        observer.schedule(event_handler, LANG_DIR, recursive=False)
        observer.start()
        threading.Thread(target=observer.join, daemon=True).start()

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

def humanize(key: str) -> str:
    language = get_current_language()
    text = language_manager.get_text(key, language)
    logging.debug(f"Humanize: key='{key}', language='{language}', result='{text}'")
    return text

