import os
import psutil
import logging
import tempfile
from api.telegram import setup_telegram_bot, run_telegram_bot
from db.director import init_database

PID_FILE = os.path.join(tempfile.gettempdir(), 'anyrun-tg-bot.pid')
SERVICE_NAME = 'anyrun-tg-bot.service'

def is_bot_running():
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        if psutil.pid_exists(pid):
            return True
    return False

async def run():
    if is_bot_running():
        logging.error("Bot is already running. Use 'restart' to restart the bot or 'kill' to force stop all instances.")
        return

    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
    
    try:
        await init_database()
        telegram_bot = await setup_telegram_bot()
        await run_telegram_bot(telegram_bot)
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)

async def get_status():
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        if psutil.pid_exists(pid):
            process = psutil.Process(pid)
            return {
                'pid': pid,
                'create_time': process.create_time()
            }
    except (FileNotFoundError, ValueError, psutil.NoSuchProcess):
        pass

    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            cmdline = ' '.join(proc.cmdline())
            if 'python' in proc.name().lower() and 'main.py' in cmdline:
                return {
                    'pid': proc.pid,
                    'create_time': proc.create_time()
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None

async def cleanup_pid_file():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                old_pid = int(f.read().strip())
            if not psutil.pid_exists(old_pid):
                os.remove(PID_FILE)
                logging.info(f"Removed stale PID file for non-existent process {old_pid}")
        except (ValueError, IOError):
            os.remove(PID_FILE)
            logging.info("Removed invalid PID file")