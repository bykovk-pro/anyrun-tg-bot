# ANY.RUN Sandbox API for Telegram

This Telegram bot provides a user-friendly interface to interact with the ANY.RUN Sandbox API. It allows users to submit files and URLs for analysis, retrieve analysis results, and perform various operations with the ANY.RUN service directly through Telegram.

## Key Features:

- Submit files and URLs for analysis in ANY.RUN Sandbox
- Retrieve analysis results and reports
- Check the status of ongoing analyses
- Manage API keys within the Telegram interface
- Automatic language detection and support
- Flexible logging system with adjustable log levels
- Asynchronous database operations for improved performance
- Secure database backup with password protection
- Admin panel for user management and system operations

This bot simplifies the process of using ANY.RUN's powerful malware analysis capabilities, making it accessible directly from your Telegram client. It's designed for security researchers, malware analysts, and IT professionals who need quick and easy access to sandbox analysis results.

## Getting Started

Follow the setup instructions in this README to configure and run the bot. Once running, you can interact with the ANY.RUN Sandbox API using simple Telegram commands.

For detailed usage instructions and available commands, start a chat with the bot and use the /help command.

## Setup

1. Clone the repository and navigate to the project directory.

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the environment variables:

   Create a `.env` file in the project root with:

   ```
   TELEGRAM_TOKEN=<your_telegram_token>
   TELEGRAM_ADMIN_ID=<your_telegram_admin_id>
   LOG_LEVEL=<your_log_level>
   TELEGRAM_LOG_LEVEL=<your_telegram_log_level>
   REQUIRED_GROUP_IDS=<comma_separated_group_ids>
   DB_BACKUP_PASSWORD=<your_backup_password>
   ```

   Note: Make sure to replace the placeholder values with your actual values.

## Running the Bot

To run the bot, use the following command:
```
python main.py start
```
The bot will start and run in the foreground. For production use, consider using a process manager to run the bot as a background service.

## Localization

The bot automatically detects and uses the user's language based on their Telegram settings. To add or modify localized strings, edit the JSON files in the `lang` directory.

## Development

For development purposes, you can install the package in editable mode with development dependencies:

```
pip install -e .[dev]
```

This will install additional tools for development.

## Database

The bot uses aiosqlite for asynchronous database operations. The database file is created automatically when the bot is first run. To backup the database, use the admin menu option in the bot interface. The backup is password-protected for security.

## Admin Features

The bot includes an admin panel accessible to authorized users. Admin features include:
- User management (ban/unban users)
- Database backup
- Bot status checks

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.# Test comment
