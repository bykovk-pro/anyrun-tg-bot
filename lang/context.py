class LanguageContext:
    _instance = None
    _language = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_language(self, language):
        self._language = language

    def get_language(self):
        return self._language or 'en'

def get_current_language():
    return LanguageContext.get_instance().get_language()

def set_current_language(language):
    LanguageContext.get_instance().set_language(language)

def set_message_getter(getter):
    LanguageContext.get_instance().set_message_getter(getter)

def get_message(key):
    return LanguageContext.get_instance().get_message(key)
