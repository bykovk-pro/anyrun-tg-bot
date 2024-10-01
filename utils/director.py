import os
import sys
import psutil
import logging
import tempfile
import time
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

def run():
    if is_bot_running():
        logging.error("Bot is already running. Use 'restart' to restart the bot or 'kill' to force stop all instances.")
        sys.exit(1)
    
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
    
    try:
        init_database()
        telegram_bot = setup_telegram_bot()
        run_telegram_bot(telegram_bot)
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)

def start_daemon():
    if is_bot_running():
        logging.error("Bot is already running. Use 'restart' to restart the bot or 'kill' to force stop all instances.")
        return False

    try:
        pid = os.fork()
        if pid > 0:
            time.sleep(1)
            return True
    except OSError as e:
        logging.error(f"Fork failed: {e}")
        return False

    os.chdir(os.path.expanduser('~'))
    os.setsid()
    os.umask(0)

    run()
    sys.exit(0)

def stop_daemon():
    logging.info("Stopping the application")
    if not is_bot_running():
        logging.info("Application was not running")
        return True

    with open(PID_FILE, 'r') as f:
        pid = int(f.read().strip())
    
    try:
        process = psutil.Process(pid)
        process.terminate()
        process.wait(timeout=10)
        logging.info(f"Application stopped (PID: {pid})")
    except psutil.NoSuchProcess:
        logging.info(f"Process {pid} not found")
    except psutil.TimeoutExpired:
        logging.warning(f"Process {pid} did not terminate gracefully, forcing...")
        process.kill()
    
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
    
    return True

def restart_daemon():
    stop_daemon()
    time.sleep(2)
    return start_daemon()

def manage_daemon(action):
    if action == 'start':
        start_daemon()
    elif action == 'stop':
        stop_daemon()
    elif action == 'restart':
        restart_daemon()
    elif action == 'kill':
        kill_bot()
    else:
        logging.error(f'Invalid action: {action}')

def kill_bot():
    killed = False
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as f:
            try:
                pid = int(f.read().strip())
                os.kill(pid, 9)
                killed = True
                logging.warning(f'Process forcefully killed: pid={pid}')
            except (ValueError, ProcessLookupError):
                pass
        os.remove(PID_FILE)
    
    if not killed:
        logging.info('No processes were killed')
    return killed

def get_status():
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

def cleanup_pid_file():
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