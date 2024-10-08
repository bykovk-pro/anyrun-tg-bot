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
    handle_text_input, check_access_rights, handle_group_info
)
from src.api.help import (
    show_help_menu
)
from src.api.admin import (
    show_admin_panel, show_manage_users_menu, show_manage_bot_menu, 
    check_bot_groups
)
from src.api.bot import (
    restart_bot, confirm_restart_bot, change_log_level, set_log_level,
    show_bot_logs, show_bot_stats, show_system_info, backup_database,
    restore_database, process_database_restore
)
from src.api.sandbox import (
    run_url_analysis, run_file_analysis, show_history, show_api_limits
)
from src.api.users import (
    show_all_users, ban_user, unban_user, delete_user, process_user_action
)

def setup_handlers(application: Application):
    # Основные команды
    application.add_handler(CommandHandler("start", show_main_menu))
    application.add_handler(CommandHandler("menu", show_main_menu))

    # Обработчик текстовых сообщений
    # Импортируем handle_message здесь, чтобы избежать циклического импорта
    from src.api.telegram import handle_message
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Обработчики для меню
    application.add_handler(CallbackQueryHandler(show_main_menu, pattern='^main_menu$'))
    application.add_handler(CallbackQueryHandler(show_sandbox_api_menu, pattern='^sandbox_api$'))
    application.add_handler(CallbackQueryHandler(show_settings_menu, pattern='^settings$'))
    application.add_handler(CallbackQueryHandler(show_help_menu, pattern='^help$'))

    # Обработчики для Sandbox API
    application.add_handler(CallbackQueryHandler(run_url_analysis, pattern='^run_url_analysis$'))
    application.add_handler(CallbackQueryHandler(run_file_analysis, pattern='^run_file_analysis$'))
    application.add_handler(CallbackQueryHandler(show_history, pattern='^history$'))
    application.add_handler(CallbackQueryHandler(show_api_limits, pattern='^show_api_limits$'))

    # Обработчики для управления API ключами
    application.add_handler(CallbackQueryHandler(manage_api_key, pattern='^manage_api_key$'))
    application.add_handler(CallbackQueryHandler(show_api_keys, pattern='^show_api_keys$'))
    application.add_handler(CallbackQueryHandler(add_api_key, pattern='^add_api_key$'))
    application.add_handler(CallbackQueryHandler(delete_api_key, pattern='^delete_api_key$'))
    application.add_handler(CallbackQueryHandler(change_api_key_name, pattern='^change_api_key_name$'))
    application.add_handler(CallbackQueryHandler(set_active_api_key, pattern='^set_active_api_key$'))
    application.add_handler(CallbackQueryHandler(handle_api_key_actions, pattern='^(delete_|rename_|activate_|back_to_manage_api_key)'))

    # Обработчики для настроек
    application.add_handler(CallbackQueryHandler(check_access_rights, pattern='^check_access_rights$'))

    # Обработчики для меню помощи
    # application.add_handler(CallbackQueryHandler(open_sandbox_service, pattern='^sandbox_service$'))
    # application.add_handler(CallbackQueryHandler(open_api_documentation, pattern='^api_documentation$'))
    # application.add_handler(CallbackQueryHandler(send_feedback, pattern='^send_feedback$'))

    # Обработчики для админ-панели
    application.add_handler(CallbackQueryHandler(show_admin_panel, pattern='^admin_panel$'))
    application.add_handler(CallbackQueryHandler(show_manage_users_menu, pattern='^manage_users$'))
    application.add_handler(CallbackQueryHandler(show_manage_bot_menu, pattern='^manage_bot$'))
    application.add_handler(CallbackQueryHandler(check_bot_groups, pattern='^check_bot_groups$'))

    # Обработчики для управления ботом
    application.add_handler(CallbackQueryHandler(restart_bot, pattern='^restart_bot$'))
    application.add_handler(CallbackQueryHandler(confirm_restart_bot, pattern='^confirm_restart_bot$'))
    application.add_handler(CallbackQueryHandler(change_log_level, pattern='^change_log_level$'))
    application.add_handler(CallbackQueryHandler(set_log_level, pattern='^set_log_level_'))
    application.add_handler(CallbackQueryHandler(show_bot_logs, pattern='^show_bot_logs$'))
    application.add_handler(CallbackQueryHandler(show_bot_stats, pattern='^show_bot_stats$'))
    application.add_handler(CallbackQueryHandler(show_system_info, pattern='^show_system_info$'))
    application.add_handler(CallbackQueryHandler(backup_database, pattern='^backup_database$'))
    application.add_handler(CallbackQueryHandler(restore_database, pattern='^restore_database$'))

    # Обработчики для управления пользователями
    application.add_handler(CallbackQueryHandler(show_all_users, pattern='^show_all_users$'))
    application.add_handler(CallbackQueryHandler(ban_user, pattern='^ban_user$'))
    application.add_handler(CallbackQueryHandler(unban_user, pattern='^unban_user$'))
    application.add_handler(CallbackQueryHandler(delete_user, pattern='^delete_user$'))

    # Обработчик для действий с пользователями (бан, разбан, удаление)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_user_action))

    # Обработчик для восстановления базы данных
    application.add_handler(MessageHandler(filters.Document.ALL, process_database_restore))

    # Обработчик для неизвестных callback-запросов
    application.add_handler(CallbackQueryHandler(handle_unknown_callback))

    # Обработчик для информации о группе
    application.add_handler(CallbackQueryHandler(handle_group_info, pattern='^group_info_'))

async def handle_unknown_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await show_main_menu(update, context)