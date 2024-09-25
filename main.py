import sys
from service_daemon import manage_daemon

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else None
    manage_daemon(action)

if __name__ == '__main__':
    main()
