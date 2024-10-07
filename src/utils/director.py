import os
import psutil
import logging
import tempfile
import asyncio
from src.db.director import init_database, check_and_setup_admin
from src.api.telegram import setup_telegram_bot

PID_FILE = os.path.join(tempfile.gettempdir(), 'anyrun-tg-bot.pid')
SERVICE_NAME = 'anyrun-tg-bot.service'
BOT_PROCESS_NAME = 'python'
BOT_SCRIPT_NAME = 'src.main'
BOT_ENV_VAR = 'ANYRUN_TG_BOT_INSTANCE'

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

def is_bot_running():
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        if psutil.pid_exists(pid):
            return True
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in proc.name().lower() and 'main.py' in ' '.join(proc.cmdline()):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

async def run(config):
    if is_bot_running():
        logging.error("Bot is already running. Use 'restart' to restart the bot or 'kill' to force stop all instances.")
        return

    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
    
    os.environ[BOT_ENV_VAR] = '1'  # Set the environment variable
    
    try:
        application = await initialize_application(config)
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        logging.info(f"Application anyrun-tg-bot started")
        
        while True:
            await asyncio.sleep(1)
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        os.environ.pop(BOT_ENV_VAR, None)  # Remove the environment variable

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

async def stop_bot(config):
    if not is_bot_running():
        logging.error("Bot is not running.")
        return False

    with open(PID_FILE, 'r') as f:
        pid = int(f.read().strip())

    try:
        process = psutil.Process(pid)
        process.terminate()
        process.wait(timeout=10)
        logging.info(f"Bot (PID: {pid}) has been stopped.")
        return True
    except psutil.NoSuchProcess:
        logging.warning(f"No process found with PID {pid}.")
    except psutil.TimeoutExpired:
        logging.warning(f"Timeout expired while waiting for the bot to stop. It may still be running.")
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    
    return False

def is_our_bot_process(proc):
    try:
        # Check process name
        if BOT_PROCESS_NAME not in proc.name().lower():
            return False
        
        # Check command line arguments
        cmdline = ' '.join(proc.cmdline())
        if BOT_SCRIPT_NAME not in cmdline:
            return False
        
        # Exclude processes running with 'logs' command
        if 'logs' in cmdline:
            return False
        
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False

def kill_bot(config):
    killed_processes = []
    
    # First, check the PID file
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            process = psutil.Process(pid)
            if is_our_bot_process(process):
                process.terminate()
                process.wait(timeout=5)
                killed_processes.append(pid)
                logging.info(f"Terminated bot process with PID: {pid}")
        except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            logging.warning(f"Failed to terminate process from PID file")
    
    # Then, search for other possible bot processes
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if is_our_bot_process(proc):
                proc.terminate()
                proc.wait(timeout=5)
                killed_processes.append(proc.pid)
                logging.info(f"Terminated bot process with PID: {proc.pid}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            pass

    # If any processes were terminated, remove the PID file
    if killed_processes:
        logging.info(f"Terminated bot processes with PIDs: {', '.join(map(str, killed_processes))}")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        return True
    else:
        logging.warning("No running bot processes found to terminate.")
        return False