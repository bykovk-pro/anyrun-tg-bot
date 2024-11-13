from telegram import User
from contextvars import ContextVar

user_language = ContextVar('user_language', default='en')

def get_current_language() -> str:
    return user_language.get()

async def set_language_for_user(user: User) -> None:
    supported_languages = {
        'ru': 'ru', 'en': 'en', 'de': 'de', 'fr': 'fr',
        'es': 'es', 'it': 'it', 'pl': 'pl', 'hi': 'hi',
        'sr': 'sr', 'ja': 'ja', 'ar': 'ar', 'tr': 'tr'
    }
    user_lang = user.language_code.lower().split('-')[0] if user.language_code else 'en'
    lang = supported_languages.get(user_lang, 'en')
    user_language.set(lang)
    return lang
