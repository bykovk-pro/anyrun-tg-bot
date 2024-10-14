# ANY.RUN for Telegram

This Telegram bot provides a user-friendly interface to interact with the ANY.RUN API. It allows users to submit files and URLs for analysis, retrieve analysis results, and perform various operations with the ANY.RUN service directly through Telegram.

## Key Features

- Submit files and URLs for analysis in ANY.RUN Sandbox
- Retrieve analysis results and reports
- Check the status of ongoing analyses
- Manage API keys within the Telegram interface
- Automatic language detection and support
- Flexible logging system with adjustable log levels
- Asynchronous database operations for improved performance
- Secure database backup with password protection
- Admin panel for user management and system operations

## Getting Started

Follow these instructions to set up and run the bot.

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/bykovk-pro/ANY.RUN-for-Telegram.git
   cd ANY.RUN-for-Telegram
   ```

2. **Create a virtual environment (recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the bot**:
   ```bash
   pip install .
   ```

### Configuration

1. **Set up the environment variables**:

   Create a `.env` file in the project root with the following content:

   ```plaintext
   TELEGRAM_TOKEN=<your_telegram_token>
   TELEGRAM_ADMIN_ID=<your_telegram_admin_id>
   REQUIRED_GROUP_IDS=<comma_separated_group_ids>
   LOG_LEVEL=<your_log_level>
   TELEGRAM_LOG_LEVEL=<your_telegram_log_level>
   SQLITE_LOG_LEVEL=<your_sqlite_log_level>
   DB_PASSWORD=<your_backup_password>
   ```

   Replace the placeholder values with your actual values.

### Running the Bot

To run the bot, use the following command:

```bash
anyrun-tg-bot start
```

The bot will start and run in the foreground. For production use, consider using a process manager to run the bot as a background service.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
