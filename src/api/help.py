from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.lang.director import humanize
import smtplib
from email.mime.text import MIMEText
import os

def create_help_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_SANDBOX_SERVICE"), url='https://app.any.run/')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_THREAT_INTELLIGENCE_SERVICE"), url='https://intelligence.any.run/')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_API_DOCUMENTATION"), url='https://any.run/api-documentation/')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def show_help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = humanize("HELP_MENU_TEXT")
    reply_markup = create_help_menu()
    await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)
