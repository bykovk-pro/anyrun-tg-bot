import os
import sys
import logging
from dotenv import load_dotenv
import argparse
from utils.logger import setup_logging, view_logs
from utils.director import manage_daemon
from db.director import init_database, check_and_setup_admin
from config import create_config
from importlib.metadata import version, PackageNotFoundError

with open("version.txt", "r") as f:
    __version__ = f.read().strip()

def parse_args():
    parser = argparse.ArgumentParser(description='Manage the ANY.RUN Sandbox API bot service.')
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'kill', 'logs'], help='Action to perform')
    parser.add_argument('--lines', type=int, default=50, help='Number of log lines to view')
    return parser.parse_args()

def main():
    load_dotenv()
    env_vars = dict(os.environ)
    config = create_config(env_vars)
    setup_logging(config)

    args = parse_args()

    try:
        if args.action in ['start', 'restart']:
            init_database()
            check_and_setup_admin(config)
            logging.info(f"Application anyrun-tg-bot {__version__} started")

        if args.action in ['start', 'stop', 'restart', 'kill']:
            manage_daemon(args.action)
        elif args.action == 'logs':
            print(view_logs(args.lines))
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()