import sys
import logging
import argparse
from utils.director import manage_daemon, log_service_status, view_logs
from utils.logger import setup_logging, get_log_level

def parse_args():
    parser = argparse.ArgumentParser(description="ANY.RUN Sandbox API bot")
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status', 'kill_all', 'logs'])
    parser.add_argument('--log', default='WARNING', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    parser.add_argument('--lines', type=int, default=50)
    return parser.parse_args()

def main():
    args = parse_args()
    log_level = getattr(logging, args.log.upper())
    setup_logging(log_level)

    if args.action in ['start', 'stop', 'restart', 'kill_all']:
        manage_daemon(args.action, log_level)
    elif args.action == 'status':
        log_service_status()
    elif args.action == 'logs':
        print(view_logs(args.lines))

if __name__ == '__main__':
    main()
