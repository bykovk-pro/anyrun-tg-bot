import os
import sys
import signal
import psutil
import daemon
import logging
import time
import tempfile
from daemon import pidfile
from api.telegram import setup_telegram_bot, run_telegram_bot, set_telegram_log_level
from db.worker import init_database
from utils.logger import set_log_level, log, setup_logging, get_log_level

PID_FILE = os.path.join(tempfile.gettempdir(), 'arsbtlgbot.pid')

current_log_level = logging.WARNING

def signal_handler(signum, frame):
    global current_log_level
    set_log_level(current_log_level)
    set_telegram_log_level(current_log_level)
    log('LOG_LEVELS_UPDATED', logging.INFO, log_level=logging.getLevelName(current_log_level))

def run():
    try:
        global current_log_level
        current_log_level = get_log_level()

        log('INITIALIZING_LOGGERS', logging.DEBUG)
        setup_logging(current_log_level)

        log('SERVICE_STARTING', logging.INFO)

        log('SETTING_UP_SIGNAL_HANDLERS', logging.DEBUG)
        signal.signal(signal.SIGUSR1, signal_handler)
        signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))

        log('INITIALIZING_DATABASE', logging.DEBUG)
        init_database()
        
        log('SETTING_UP_TELEGRAM_BOT', logging.DEBUG)
        telegram_bot = setup_telegram_bot()
        log('TELEGRAM_BOT_SETUP_COMPLETE', logging.INFO)
        log('RUNNING_TELEGRAM_BOT', logging.INFO)
        run_telegram_bot(telegram_bot)
    except SystemExit:
        log('SERVICE_STOPPING', logging.INFO)
    except Exception as e:
        log('SERVICE_ERROR', logging.CRITICAL, error=str(e))
        import traceback
        log('SERVICE_ERROR_TRACEBACK', logging.CRITICAL, traceback=traceback.format_exc())
    finally:
        log('SERVICE_STOPPED', logging.INFO)

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
                log('PID_FILE_REMOVED', logging.INFO, pid_file=PID_FILE)
        except (ValueError, IOError) as e:
            log('PID_FILE_READ_ERROR', logging.ERROR, error=str(e))
            os.remove(PID_FILE)

def start_daemon(log_level=logging.WARNING):
    cleanup_pid_file()
    
    log('STARTING_DAEMON', logging.DEBUG, pid_file=PID_FILE)
    
    if os.path.exists(PID_FILE):
        log('DAEMON_ALREADY_RUNNING', logging.ERROR, pid_file=PID_FILE)
        return False

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        log('FORK_FAILED', logging.CRITICAL, error=str(e))
        sys.exit(1)
    
    os.chdir(os.path.expanduser('~'))
    os.setsid()
    os.umask(0)
    
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
    
    try:
        global current_log_level
        current_log_level = log_level
        setup_logging(log_level)
        pid = os.getpid()
        log('DAEMON_STARTED', logging.INFO, pid=pid)
        
        log('INITIALIZING_DATABASE', logging.DEBUG)
        init_database()
        log('DATABASE_INITIALIZED', logging.DEBUG)
        
        log('SETTING_UP_TELEGRAM_BOT', logging.DEBUG)
        telegram_bot = setup_telegram_bot(log_level)
        log('TELEGRAM_BOT_SETUP_COMPLETE', logging.INFO)
        
        log('RUNNING_TELEGRAM_BOT', logging.DEBUG)
        run_telegram_bot(telegram_bot)
    except Exception as e:
        log('DAEMON_RUNTIME_ERROR', logging.CRITICAL, error=str(e))
        import traceback
        log('DAEMON_ERROR_TRACEBACK', logging.DEBUG, traceback=traceback.format_exc())
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        sys.exit(1)

    return True

def stop_daemon():
    cleanup_pid_file()
    
    if not os.path.exists(PID_FILE):
        log('DAEMON_NOT_RUNNING', logging.INFO)
        return True

    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        process = psutil.Process(pid)
        process.terminate()
        
        try:
            process.wait(timeout=10)
        except psutil.TimeoutExpired:
            process.kill()
        
        os.remove(PID_FILE)
        log('DAEMON_STOPPED', logging.INFO, pid=pid)
        return True
    except (ProcessLookupError, psutil.NoSuchProcess):
        log('DAEMON_NOT_FOUND', logging.WARNING)
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        return True
    except Exception as e:
        log('DAEMON_STOP_ERROR', logging.ERROR, error=str(e))
        return False

def restart_daemon(log_level=logging.INFO):
    try:
        stop_daemon()
        return start_daemon(log_level)
    except Exception as e:
        log('DAEMON_RESTART_ERROR', logging.CRITICAL, error=str(e))
        raise

def update_log_levels(log_level=logging.INFO):
    try:
        global current_log_level
        current_log_level = log_level

        pid = is_running()
        if not pid:
            log('SERVICE_NOT_RUNNING', logging.ERROR)
            return
        
        os.kill(pid, signal.SIGUSR1)
        
        set_log_level(current_log_level)
        set_telegram_log_level(current_log_level)
        
        log('LOG_LEVELS_UPDATED', logging.INFO, log_level=logging.getLevelName(current_log_level))
    except Exception as e:
        log('LOG_LEVELS_UPDATE_ERROR', logging.ERROR, error=str(e))
        raise

def manage_daemon(action, log_level=logging.INFO):
    try:
        if action == 'start':
            result = start_daemon(log_level)
            if result:
                log('DAEMON_START_SUCCESS', logging.INFO)
            else:
                log('DAEMON_START_FAILED', logging.ERROR)
            log('START_DAEMON_RESULT', logging.DEBUG, result=result)
        elif action == 'stop':
            if stop_daemon():
                log('DAEMON_STOP_SUCCESS', logging.WARNING)
            else:
                log('DAEMON_STOP_FAILED', logging.ERROR)
        elif action == 'restart':
            stop_daemon()
            time.sleep(2)
            if start_daemon(log_level):
                log('DAEMON_RESTART_SUCCESS', logging.WARNING)
            else:
                log('DAEMON_RESTART_FAILED', logging.ERROR)
        elif action == 'kill_all':
            kill_all_instances()
        else:
            log('INVALID_ACTION', logging.ERROR, action=action)
    except Exception as e:
        log('DAEMON_MANAGE_ERROR', logging.ERROR, error=str(e), action=action)

def get_status():
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        if psutil.pid_exists(pid):
            process = psutil.Process(pid)
            return {
                'pid': pid,
                'log_level': current_log_level,
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
                    'log_level': current_log_level,
                    'create_time': proc.create_time()
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None

def kill_all_instances():
    try:
        killed = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower() and 'main.py' in ' '.join(proc.info['cmdline']):
                    psutil.Process(proc.info['pid']).terminate()
                    killed = True
                    log('PROCESS_KILLED', logging.WARNING, pid=proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        if not killed:
            log('NO_PROCESSES_KILLED', logging.INFO)
    except Exception as e:
        log('KILL_ALL_INSTANCES_ERROR', logging.CRITICAL, error=str(e))
        raise

def log_service_status():
    status = get_status()
    if status:
        log('SERVICE_RUNNING', logging.INFO, 
            pid=status['pid'], 
            log_level=logging.getLevelName(status['log_level']), 
            uptime=int(time.time() - status['create_time']))
    else:
        log('SERVICE_NOT_RUNNING', logging.INFO)
    return status is not None

import os
from datetime import datetime

def view_logs(lines=50):
    log_dir = os.path.join(os.path.expanduser('~'), 'arsbtlgbot_logs')
    current_date = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"{current_date}.log")
    
    if not os.path.exists(log_file):
        log('LOG_FILE_NOT_FOUND', logging.DEBUG, log_file=log_file)
        return ''
    
    with open(log_file, 'r') as f:
        log_lines = f.readlines()
    
    log('LOGS_VIEWED', logging.DEBUG, lines=lines)
    log('LOG_CONTENT', logging.DEBUG, content=''.join(log_lines[-lines:]))
    return ''.join(log_lines[-lines:])