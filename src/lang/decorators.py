from functools import wraps
from typing import Union, Optional
from telegram import Update
from src.lang.context import set_language_for_user
from src.lang.director import humanize

def with_locale(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        update = next((arg for arg in args if isinstance(arg, Update)), None)
        if update:
            await set_language_for_user(update.effective_user)
        return await func(*args, **kwargs)
    return wrapper

def localized_message(key: str, **format_args):
    async def decorator(update: Update, context=None) -> None:
        await set_language_for_user(update.effective_user)
        message = await humanize(key)
        if format_args:
            message = message.format(**format_args)
        await update.message.reply_text(message)
    return decorator 