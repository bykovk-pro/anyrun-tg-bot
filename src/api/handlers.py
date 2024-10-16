from telegram import Update
from telegram.ext import (
    CommandHandler, MessageHandler, CallbackQueryHandler, 
    ConversationHandler, filters, Application, ContextTypes
)
from src.api.menu import (
    show_main_menu, show_sandbox_api_menu, show_settings_menu
)
from src.api.settings import (
    manage_api_key, show_api_keys, add_api_key, delete_api_key,
    change_api_key_name, set_active_api_key, handle_api_key_actions,
    check_access_rights, handle_group_info, handle_text_input as settings_handle_text_input
)
from src.api.help import (
    show_help_menu
)
from src.api.admin import (
    show_admin_panel, show_manage_users_menu, show_manage_bot_menu 
)
from src.api.bot import (
    show_system_info, backup_database,
    restore_database, process_database_restore
)
from src.api.sandbox import (
    get_report_by_uuid, get_history, show_api_limits
)
from src.api.users import (
    show_all_users, ban_user, unban_user, delete_user, process_user_action
)
from src.api.reports import handle_text_input as reports_handle_text_input, handle_show_recorded_video, handle_show_captured_screenshots
from src.lang.director import humanize
import logging
from src.api.threat_intelligence import show_threat_intelligence_menu


def setup_handlers(application: Application):
    application.add_handler(CommandHandler("start", show_main_menu))
    application.add_handler(CommandHandler("menu", show_main_menu))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))

    application.add_handler(CallbackQueryHandler(show_main_menu, pattern='^main_menu$'))
    application.add_handler(CallbackQueryHandler(show_sandbox_api_menu, pattern='^sandbox_api$'))
    application.add_handler(CallbackQueryHandler(show_settings_menu, pattern='^settings$'))
    application.add_handler(CallbackQueryHandler(show_help_menu, pattern='^help$'))

    application.add_handler(CallbackQueryHandler(get_report_by_uuid, pattern='^get_report_by_uuid$'))
    application.add_handler(CallbackQueryHandler(get_history, pattern='^get_history$'))
    application.add_handler(CallbackQueryHandler(show_api_limits, pattern='^show_api_limits$'))

    application.add_handler(CallbackQueryHandler(manage_api_key, pattern='^manage_api_key$'))
    application.add_handler(CallbackQueryHandler(show_api_keys, pattern='^show_api_keys$'))
    application.add_handler(CallbackQueryHandler(add_api_key, pattern='^add_api_key$'))
    application.add_handler(CallbackQueryHandler(delete_api_key, pattern='^delete_api_key$'))
    application.add_handler(CallbackQueryHandler(change_api_key_name, pattern='^change_api_key_name$'))
    application.add_handler(CallbackQueryHandler(set_active_api_key, pattern='^set_active_api_key$'))
    application.add_handler(CallbackQueryHandler(handle_api_key_actions, pattern='^(delete_|rename_|activate_|back_to_manage_api_key)'))

    application.add_handler(CallbackQueryHandler(check_access_rights, pattern='^check_access_rights$'))

    application.add_handler(CallbackQueryHandler(show_admin_panel, pattern='^admin_panel$'))
    application.add_handler(CallbackQueryHandler(show_manage_users_menu, pattern='^manage_users$'))
    application.add_handler(CallbackQueryHandler(show_manage_bot_menu, pattern='^manage_bot$'))

    application.add_handler(CallbackQueryHandler(show_system_info, pattern='^show_system_info$'))
    application.add_handler(CallbackQueryHandler(backup_database, pattern='^backup_database$'))
    application.add_handler(CallbackQueryHandler(restore_database, pattern='^restore_database$'))

    application.add_handler(CallbackQueryHandler(show_all_users, pattern='^show_all_users$'))
    application.add_handler(CallbackQueryHandler(ban_user, pattern='^ban_user$'))
    application.add_handler(CallbackQueryHandler(unban_user, pattern='^unban_user$'))
    application.add_handler(CallbackQueryHandler(delete_user, pattern='^delete_user$'))

    application.add_handler(MessageHandler(filters.Document.ALL, process_database_restore))

    application.add_handler(CallbackQueryHandler(handle_group_info, pattern='^group_info_'))

    application.add_handler(CallbackQueryHandler(handle_show_recorded_video, pattern='^show_recorded_video$'))
    application.add_handler(CallbackQueryHandler(handle_show_captured_screenshots, pattern='^show_captured_screenshots$'))

    application.add_handler(CallbackQueryHandler(show_threat_intelligence_menu, pattern='^threat_intelligence$'))

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_action = context.user_data.get('next_action')
    if next_action in ['add_api_key', 'rename_api_key']:
        await settings_handle_text_input(update, context)
    elif next_action in ['get_reports_by_uuid']:
        await reports_handle_text_input(update, context)
    else:
        logging.warning(f"Unknown next_action in handlers: {next_action}")
        await update.message.reply_text(humanize("UNKNOWN_COMMAND"))
        await show_main_menu(update, context)
