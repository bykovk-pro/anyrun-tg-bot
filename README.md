# Telegram Bot Service

A simple Telegram bot service that can be started, stopped, and restarted.

## Setup

1. Set the environment variable for your Telegram bot token:

   ```
   export ANYRUN_SB_API_TOKEN=your_token_here
   ```

   Or create a `.env` file in the project root with:

   ```
   ANYRUN_SB_API_TOKEN=your_token_here
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

## Usage

Control the bot service with the following commands:

- Start:
  ```
  python main.py start
  ```

- Stop:
  ```
  python main.py stop
  ```

- Restart:
  ```
  python main.py restart
  ```

- Kill all instances:
  ```
  python main.py kill_all
  ```

- Status:
  ```
  python main.py status
  ```
