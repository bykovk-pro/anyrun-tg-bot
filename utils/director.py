import os
import sys
import psutil
import logging
import tempfile
from api.telegram import setup_telegram_bot, run_telegram_bot
from db.director import init_database

PID_FILE = os.path.join(tempfile.gettempdir(), 'arsbtlgbot.pid')
SERVICE_NAME = 'anyrun-tg-bot.service'


def run():
    init_database()
    telegram_bot = setup_telegram_bot()
    run_telegram_bot(telegram_bot)

def is_running():
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)
        return pid
    except (FileNotFoundError, ProcessLookupError, ValueError):
        return None

def cleanup_pid_file():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            if not psutil.pid_exists(pid):
                os.remove(PID_FILE)
        except (ValueError, IOError) as e:
            os.remove(PID_FILE)

def start_daemon():
    cleanup_pid_file()
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        return False

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        sys.exit(1)
    
    os.chdir(os.path.expanduser('~'))
    os.setsid()
    os.umask(0)
    
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
    
    try:
        pid = os.getpid()
        init_database()
        telegram_bot = setup_telegram_bot()
        run_telegram_bot(telegram_bot)
    except Exception as e:
        import traceback
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        sys.exit(1)

    return True

def stop_daemon():
    logging.info("Stopping the application")
    cleanup_pid_file()
    
    if not os.path.exists(PID_FILE):
        logging.info("Application is not running")
        return True

    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        process = psutil.Process(pid)
        process.terminate()
        
        try:
            process.wait(timeout=10)
            logging.info(f"Application stopped (PID: {pid})")
        except psutil.TimeoutExpired:
            process.kill()
            logging.warning(f"Application forcefully killed (PID: {pid})")
        
        os.remove(PID_FILE)
        return True
    except (ProcessLookupError, psutil.NoSuchProcess):
        logging.info("Application is not running")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        return True
    except Exception as e:
        logging.error(f"Error stopping application: {str(e)}")
        return False

def restart_daemon():
    try:
        stop_daemon()
        return start_daemon()
    except Exception as e:
        raise

def manage_daemon(action):
    if action == 'start':
        start_daemon()
    elif action == 'stop':
        stop_daemon()
    elif action == 'restart':
        stop_daemon()
        start_daemon()
    elif action == 'kill':
        kill_bot()
    else:
        logging.error(f'Invalid action: {action}')

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

def kill_bot():
    try:
        killed = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower() and 'main.py' in ' '.join(proc.info['cmdline']):
                    psutil.Process(proc.info['pid']).terminate()
                    killed = True
                    logging.warning(f'Process killed: pid={proc.info["pid"]}')
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        if not killed:
            logging.info('No processes were killed')
    except Exception as e:
        logging.critical(f'Error killing all instances: {str(e)}')
        raise