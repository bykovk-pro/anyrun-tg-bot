from typing import Optional
from telegram import User
from contextvars import ContextVar

user_language = ContextVar('user_language', default='en')

class LanguageContext:
    _instance = None
    _language = 'en'
    _user_language_getter = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_user_language_getter(self, getter):
        self._user_language_getter = getter

    def get_language(self) -> str:
        return user_language.get()

def get_current_language() -> str:
    return LanguageContext.get_instance().get_language()

def set_user_language_getter(getter):
    LanguageContext.get_instance().set_user_language_getter(getter)

def set_language_for_user(user: User):
    if LanguageContext.get_instance()._user_language_getter:
        lang = LanguageContext.get_instance()._user_language_getter(user)
        user_language.set(lang)
