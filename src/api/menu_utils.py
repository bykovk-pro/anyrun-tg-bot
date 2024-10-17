from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.lang.director import humanize
import logging
import os

def create_sandbox_api_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_RUN_URL_ANALYSIS"), callback_data='run_url_analysis')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_RUN_FILE_ANALYSIS"), callback_data='run_file_analysis')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_GET_REPORT_BY_UUID"), callback_data='get_report_by_uuid')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_GET_HISTORY"), callback_data='get_history')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_SHOW_API_LIMITS"), callback_data='show_api_limits')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_admin_panel_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_MANAGE_USERS"), callback_data='manage_users')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_MANAGE_BOT"), callback_data='manage_bot')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='settings')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_manage_users_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_SHOW_ALL_USERS"), callback_data='show_all_users')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BAN_USER"), callback_data='ban_user')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_UNBAN_USER"), callback_data='unban_user')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_DELETE_USER"), callback_data='delete_user')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='admin_panel')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_manage_bot_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_SHOW_SYSTEM_INFO"), callback_data='show_system_info')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACKUP_DATABASE"), callback_data='backup_database')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_RESTORE_DATABASE"), callback_data='restore_database')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='admin_panel')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_help_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_SANDBOX_SERVICE"), url='https://app.any.run/')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_THREAT_INTELLIGENCE_SERVICE"), url='https://intelligence.any.run/')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_API_DOCUMENTATION"), url='https://any.run/api-documentation/')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_GITHUB"), url='https://github.com/bykovk-pro/anyrun-tg-bot')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_main_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_SANDBOX_API"), callback_data='sandbox_api')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_THREAT_INTELLIGENCE"), callback_data='threat_intelligence')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_SETTINGS"), callback_data='settings')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_HELP"), callback_data='help')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_settings_menu(is_admin=False):
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_MANAGE_API_KEY"), callback_data='manage_api_key')]
    ]
    
    required_group_ids = os.getenv('REQUIRED_GROUP_IDS', '')
    if required_group_ids.strip():
        keyboard.append([InlineKeyboardButton(humanize("MENU_BUTTON_CHECK_ACCESS_RIGHTS"), callback_data='check_access_rights')])
    
    if is_admin:
        keyboard.append([InlineKeyboardButton(humanize("MENU_BUTTON_ADMIN_PANEL"), callback_data='admin_panel')])
    keyboard.append([InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='main_menu')])
    return InlineKeyboardMarkup(keyboard)

def create_threat_intelligence_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_manage_api_key_menu():
    keyboard = [
        [InlineKeyboardButton(humanize("MENU_BUTTON_SHOW_API_KEYS"), callback_data='show_api_keys')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_ADD_API_KEY"), callback_data='add_api_key')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_DELETE_API_KEY"), callback_data='delete_api_key')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_CHANGE_API_KEY_NAME"), callback_data='change_api_key_name')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_SET_ACTIVE_API_KEY"), callback_data='set_active_api_key')],
        [InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='settings')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_report_menu_keyboard(report):
    keyboard = [
        [InlineKeyboardButton(humanize("ANALYSIS_IN_SANDBOX"), url=report.get("permanentUrl", ""))]
    ]

    media_row = []
    if report.get("content", {}).get("video", {}).get("permanentUrl"):
        media_row.append(InlineKeyboardButton(humanize("SHOW_RECORDED_VIDEO"), callback_data='show_recorded_video'))
    if report.get("content", {}).get("screenshots", []):
        media_row.append(InlineKeyboardButton(humanize("SHOW_CAPTURED_SCREENSHOTS"), callback_data='show_captured_screenshots'))
    if media_row:
        keyboard.append(media_row)

    text_row = []
    text_row.append(InlineKeyboardButton(humanize("REPORT_ANYRUN"), url=f"https://api.any.run/report/{report.get('uuid', '')}/summary/json"))
    text_row.append(InlineKeyboardButton(humanize("TEXT_REPORT"), url=f"https://any.run/report/{report.get('content', {}).get('mainObject', {}).get('hashes', {}).get('sha256', '')}/{report.get('uuid', '')}"))
    text_row.append(InlineKeyboardButton(humanize("REPORT_HTML"), url=report.get("reports", {}).get("HTML", "")))
    if text_row:
        keyboard.append(text_row)

    report_row = []
    if report.get("reports", {}).get("IOC"):
        report_row.append(InlineKeyboardButton(humanize("ALL_IOC"), url=report.get("reports", {}).get("IOC", "")))
    if report.get("reports", {}).get("STIX"):
        report_row.append(InlineKeyboardButton(humanize("REPORT_STIX"), url=report.get("reports", {}).get("STIX", "")))
    if report.get("reports", {}).get("MISP"):
        report_row.append(InlineKeyboardButton(humanize("REPORT_MISP"), url=report.get("reports", {}).get("MISP", "")))
    if report_row:
        keyboard.append(report_row)

    download_row = []
    if report.get("content", {}).get("mainObject", {}).get("type") == "file":
        download_row.append(InlineKeyboardButton(humanize("DOWNLOAD_SAMPLE"), url=report.get("content", {}).get("mainObject", {}).get("permanentUrl", "")))
    if report.get("content", {}).get("pcap", {}).get("present"):
        download_row.append(InlineKeyboardButton(humanize("DOWNLOAD_PCAP"), url=report.get("content", {}).get("pcap", {}).get("permanentUrl", "")))
    if download_row:
        keyboard.append(download_row)

    keyboard.append([InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='sandbox_api')])

    return InlineKeyboardMarkup(keyboard)

def create_show_all_users_menu(users, page=0, users_per_page=10):
    keyboard = []
    start = page * users_per_page
    end = start + users_per_page
    for user in users[start:end]:
        keyboard.append([InlineKeyboardButton(f"{user['telegram_id']} {user['first_access_date']} {user['last_access_date']} {user['is_admin']} {user['is_banned']} {user['is_deleted']}", callback_data=f"user_info_{user['telegram_id']}")])
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f"show_users_page_{page-1}"))
    if end < len(users):
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"show_users_page_{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton(humanize("MENU_BUTTON_BACK"), callback_data='manage_users')])
    return InlineKeyboardMarkup(keyboard)

def escape_markdown(text: str) -> str:
    if not isinstance(text, str):
        logging.error(f"Expected string for escape_markdown, got {type(text)}")
        return str(text)
    
    return text.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]').replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('`', '\\`').replace('>', '\\>').replace('#', '\\#').replace('+', '\\+').replace('-', '\\-').replace('=', '\\=').replace('|', '\\|').replace('{', '\\{').replace('}', '\\}').replace('.', '\\.').replace('!', '\\!')
