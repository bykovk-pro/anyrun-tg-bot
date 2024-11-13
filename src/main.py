import logging
import asyncio
from src.db.director import init_database
from src.api.telegram import setup_telegram_bot
from src.lang.director import humanize

async def shutdown():
    msg = await humanize("BOT_STOP_MESSAGE")
    logging.info(msg)

async def main() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    try:
        await init_database()
        application = await setup_telegram_bot()
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        logging.info("Bot started successfully")

        while True:
            await asyncio.sleep(1)
    except Exception as e:
        msg = await humanize("BOT_START_ERROR")
        logging.exception(msg.format(error=str(e)))
    finally:
        if 'application' in locals():
            await application.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(shutdown())
