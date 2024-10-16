import logging
import asyncio
import os
from dotenv import load_dotenv
from src.db.director import init_database, check_and_setup_admin
from src.api.telegram import setup_telegram_bot

def load_config():
    load_dotenv(override=True)
    return {key: value for key, value in os.environ.items()}

async def initialize_application(config):
    logging.debug("Starting initialize_application")
    try:
        await init_database()
        logging.debug("Database initialized")
        await check_and_setup_admin(config)
        logging.debug("Admin setup completed")

        application = await setup_telegram_bot(config)
        logging.debug("Telegram bot setup completed")
        return application
    except Exception as e:
        logging.exception(f"Error in initialize_application: {e}")
        raise

async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.info("- * - * - * - * - * - * - * - * - * -")
    logging.info("- * Starting ANY.RUN for Telegram * -")
    logging.info("- * - * - * - * - * - * - * - * - * -")
    
    config = load_config()
    logging.debug("Configuration loaded from .env file")

    try:
        application = await initialize_application(config)
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        logging.info("Application anyrun-tg-bot started")

        while True:
            await asyncio.sleep(1)
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")
    finally:
        if 'application' in locals():
            await application.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user.")
