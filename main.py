import os
import logging
from dotenv import load_dotenv
import argparse
import asyncio
import signal
from utils.logger import setup_logging, view_logs
from db.director import init_database, check_and_setup_admin
from config import create_config
from db.common import get_db_pool
from api.telegram import setup_telegram_bot

with open("version.txt", "r") as f:
    __version__ = f.read().strip()

def parse_args():
    parser = argparse.ArgumentParser(description='Manage the ANY.RUN Sandbox API bot service.')
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'kill', 'logs'], help='Action to perform')
    parser.add_argument('--lines', type=int, default=50, help='Number of log lines to view')
    return parser.parse_args()

async def main():
    load_dotenv()
    env_vars = dict(os.environ)
    config = create_config(env_vars)
    setup_logging(config)

    args = parse_args()

    try:
        if args.action in ['start', 'restart']:
            await init_database()
            await check_and_setup_admin(config)
            logging.info(f"Application anyrun-tg-bot {__version__} started")

            if args.action == 'start':
                application = await setup_telegram_bot()
                await application.initialize()
                await application.start()
                await application.updater.start_polling()

                def signal_handler(sig, frame):
                    asyncio.create_task(shutdown(application))

                signal.signal(signal.SIGINT, signal_handler)
                signal.signal(signal.SIGTERM, signal_handler)

                while True:
                    await asyncio.sleep(1)

        elif args.action == 'stop':
            pass
        elif args.action == 'kill':
            pass
        elif args.action == 'logs':
            print(view_logs(args.lines))
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        db = await get_db_pool()
        await db.close()

async def shutdown(application):
    await application.stop()
    await application.shutdown()

if __name__ == "__main__":
    asyncio.run(main())