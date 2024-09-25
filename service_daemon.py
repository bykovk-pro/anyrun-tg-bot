import os
import signal
import psutil
import daemon
from daemon import pidfile
from api.telegram.api_telegram import setup_telegram_bot, run_telegram_bot

# Path to the PID file
PID_FILE = '/tmp/arsbtlgbot.pid'

def run():
    # Set up and run the Telegram bot
    telegram_bot = setup_telegram_bot()
    run_telegram_bot(telegram_bot)

def is_running():
    # Check if the daemon is already running
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)  # Check if the process is alive
        return pid
    except (FileNotFoundError, ProcessLookupError, ValueError):
        return None

def start_daemon():
    # Start the daemon if it's not already running
    pid = is_running()
    if pid:
        return pid
    
    # Create a daemon context and run the bot
    with daemon.DaemonContext(
        pidfile=pidfile.TimeoutPIDLockFile(PID_FILE),
    ):
        run()
    
    return is_running()

def stop_daemon():
    # Stop the daemon if it's running
    pid = is_running()
    if not pid:
        return
    
    try:
        os.kill(pid, signal.SIGTERM)  # Send termination signal
    except ProcessLookupError:
        pass

def restart_daemon():
    # Restart the daemon
    stop_daemon()
    return start_daemon()

def manage_daemon(action):
    # Manage daemon based on the given action
    if action in [None, "start"]:
        return start_daemon()
    elif action == "stop":
        stop_daemon()
    elif action == "restart":
        return restart_daemon()
    elif action == "kill_all":
        kill_all_instances()
    elif action == "status":
        pids = get_status()
        if pids:
            print(f"Service is running. PIDs: {', '.join(map(str, pids))}")
        else:
            print("Service is not running.")
    return None

def get_status():
    # Check the PID file first
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        if psutil.pid_exists(pid):
            return [pid]
    except (FileNotFoundError, ValueError):
        pass

    # If PID file check fails, search for the process
    pids = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.cmdline())
            if 'python' in proc.name().lower() and 'service_daemon.py' in cmdline:
                pids.append(proc.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return pids

def kill_all_instances():
    # Find all Python processes
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Check if the process is running our script
            if 'python' in proc.info['name'].lower() and 'service_daemon.py' in ' '.join(proc.info['cmdline']):
                # Kill the process
                psutil.Process(proc.info['pid']).terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
