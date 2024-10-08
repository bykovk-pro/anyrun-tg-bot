from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.lang.director import humanize
import smtplib
from email.mime.text import MIMEText
import os

def create_help_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_SANDBOX_SERVICE"), url='https://app.any.run/')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_API_DOCUMENTATION"), url='https://any.run/api-documentation/')],
        # [InlineKeyboardButton(humanize("MENU_BUTTON_SEND_FEEDBACK"), callback_data='send_feedback')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def show_help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = humanize("HELP_MENU_TEXT")
    reply_markup = create_help_menu()
    await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)

#async def open_sandbox_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    await update.callback_query.answer()
#    await context.bot.send_message(chat_id=update.effective_chat.id, text="Opening ANY.RUN Sandbox: https://app.any.run/")

#async def open_api_documentation(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    await update.callback_query.answer()
#    await context.bot.send_message(chat_id=update.effective_chat.id, text="Opening API documentation: https://any.run/api-documentation/")

#async def send_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    await update.callback_query.edit_message_text(humanize("SEND_FEEDBACK_PROMPT"))
#    context.user_data['next_action'] = 'send_feedback'

#async def process_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    feedback_message = update.message.text
#    user_id = update.effective_user.id
#    user_username = update.effective_user.username
#
#    subject = "ANY.RUN Bot feedback"
#    body = f"Message: {feedback_message}\nUser ID: {user_id}\nUsername: {user_username}"
#
#    try:
#        sender_email = os.getenv('AUTHOR_EMAIL')
#        receiver_email = sender_email
#        msg = MIMEText(body)
#        msg['Subject'] = subject
#        msg['From'] = sender_email
#        msg['To'] = receiver_email
#
#        with smtplib.SMTP('smtp.example.com', 587) as server:
#            server.starttls()
#            server.login(sender_email, os.getenv('EMAIL_PASSWORD'))
#            server.sendmail(sender_email, receiver_email, msg.as_string())
#
#        await update.message.reply_text(humanize("FEEDBACK_SENT"))
#    except Exception as e:
#        await update.message.reply_text(humanize("FEEDBACK_ERROR") + f"\n\nDetails: {str(e)}")

#async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    next_action = context.user_data.get('next_action')
#    if next_action == 'send_feedback':
#        await process_feedback(update, context)
#        del context.user_data['next_action']