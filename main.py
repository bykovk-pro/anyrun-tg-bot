import sys
import logging
import argparse
from utils.director import manage_daemon, log_service_status, update_log_levels, view_logs
from utils.logger import log, set_log_level, set_console_level

class CustomArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._optionals.title = 'options'

    def error(self, message):
        log('INVALID_COMMAND_OR_OPTION', logging.DEBUG, message=message)
        self.print_help(sys.stderr)
        sys.exit(2)

    def _print_message(self, message, file=None):
        if message:
            if message.count('usage:') > 1:
                message = 'usage:' + message.split('usage:')[-1]
            super()._print_message(message, file)

    def format_help(self):
        formatter = self._get_formatter()
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups)
        formatter.add_text(self.description)
        for action_group in self._action_groups:
            if action_group.title == 'positional arguments':
                continue
            formatter.start_section(action_group.title)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()
        formatter.add_text(self.epilog)
        return formatter.format_help()

def parse_args():
    parser = CustomArgumentParser(add_help=False, usage='%(prog)s {start,stop,restart,status,kill_all,log_level,logs} [options]')
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status', 'kill_all', 'log_level', 'logs'], metavar='action')
    parser.add_argument('--log', default='INFO', type=str.upper, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    parser.add_argument('--echo', default='ERROR', type=str.upper, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    parser.add_argument('--lines', type=int, default=50, help='Number of log lines to display')
    return parser.parse_args()

def main():
    try:
        args = parse_args()

        log_level = getattr(logging, args.log.upper())
        echo_level = getattr(logging, args.echo.upper())

        set_log_level(log_level)
        set_console_level(echo_level)

        log('COMMAND_RECEIVED', logging.DEBUG, action=args.action, log_level=args.log, echo_level=args.echo)

        if args.action in ['start', 'stop', 'restart', 'kill_all']:
            manage_daemon(args.action, log_level, echo_level)
        elif args.action == 'status':
            log_service_status()
        elif args.action == 'log_level':
            update_log_levels(log_level, echo_level)
        elif args.action == 'logs':
            print(view_logs(args.lines))
    except Exception as e:
        log('UNEXPECTED_ERROR', logging.ERROR, error=str(e))
        import traceback
        log('ERROR_TRACEBACK', logging.DEBUG, traceback=traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main()
