import os
import logging
import argparse
import asyncio
from dotenv import load_dotenv
from src.config import create_config
from src.utils.logger import setup_logging, view_logs
from src.utils.director import run, stop_bot, kill_bot, is_bot_running
from src.db.common import get_db_pool

# Загружаем переменные окружения из .env файла
load_dotenv()

def print_help():
    help_text = """
    ANY.RUN Sandbox API Bot Service

    Usage:
      python3 -m src.main [action] [options]

    Actions:
      start    Start the bot (default if no action is specified)
      stop     Stop the running bot
      restart  Restart the bot
      kill     Force stop all bot processes
      logs     View bot logs
      help     Show this help message

    Options:
      --lines N    Number of log lines to view (default: 50)
      --follow     Continuously follow the log output
      --help       Show this help message

    Examples:
      python3 -m src.main
      python3 -m src.main start
      python3 -m src.main stop
      python3 -m src.main logs --lines 100 --follow
    """
    print(help_text)

def parse_args():
    parser = argparse.ArgumentParser(description='Manage the ANY.RUN Sandbox API bot service.', add_help=False)
    parser.add_argument('action', nargs='?', default='start', choices=['start', 'stop', 'restart', 'kill', 'logs', 'help'], help='Action to perform (default: start)')
    parser.add_argument('--lines', type=int, default=50, help='Number of log lines to view')
    parser.add_argument('--follow', action='store_true', help='Continuously follow the log output')
    parser.add_argument('--help', action='store_true', help='Show this help message')
    return parser

async def main():
    load_dotenv(override=True)
    config = create_config()
    setup_logging(config)
    
    parser = parse_args()
    args = parser.parse_args()

    if args.action == 'help' or args.help:
        print_help()
        return

    try:
        if args.action in ['start', 'restart']:
            logging.debug("- * " * 12)
            logging.debug(f"Starting ANY.RUN Sandbox API Bot")

        if args.action == 'start':
            if is_bot_running():
                message = "Bot is already running. Use 'restart' to restart the bot or 'kill' to force stop all instances."
                print(message)
                logging.warning(message)
                return
            await run(config)
        elif args.action == 'stop':
            success = await stop_bot(config)
            if success:
                print("Bot stopped successfully.")
            else:
                print("Failed to stop the bot.")
        elif args.action == 'restart':
            await stop_bot(config)
            await run(config)
        elif args.action == 'kill':
            if kill_bot(config):
                print("Bot process(es) killed.")
            else:
                print("No bot processes found to kill.")
        elif args.action == 'logs':
            if args.follow:
                view_logs(args.lines, follow=True)
            else:
                print(view_logs(args.lines))
        else:
            print(f"Error: Unknown action '{args.action}'")
            print_help()
    except Exception as e:
        message = f"An unexpected error occurred: {e}"
        logging.exception(message)
        print(message)
        print("Check the log file for more information.")

    if args.action in ['start', 'restart'] and not is_bot_running():
        try:
            db = await get_db_pool()
            await db.close()
        except Exception as db_error:
            logging.error(f"Error closing database connection: {db_error}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logging.exception("Unexpected error:")
