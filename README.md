# ANY.RUN Sandbox API for Telegram

This Telegram bot provides a simple interface to interact with the ANY.RUN Sandbox API. It allows users to submit files and URLs for analysis, retrieve analysis results, and perform basic operations with the ANY.RUN service directly through Telegram.

## Key Features:

- Submit files and URLs for analysis in ANY.RUN Sandbox
- Retrieve analysis results and reports
- Check the status of ongoing analyses
- Manage API keys within the Telegram interface
- Multi-language support for a global user base
- Flexible logging system with adjustable log levels

This bot simplifies the process of using ANY.RUN's powerful malware analysis capabilities, making it accessible directly from your Telegram client. It's designed for security researchers, malware analysts, and IT professionals who need quick and easy access to sandbox analysis results.

## Getting Started

Follow the setup instructions in this README to configure and run the bot. Once running, you can interact with the ANY.RUN Sandbox API using simple Telegram commands.

For detailed usage instructions and available commands, start a chat with the bot and use the /help command.

## Setup

1. Set the environment variables:

   ```
   export ANYRUN_SB_API_TOKEN=your_token_here
   export ANYRUN_SB_ADMIN_ID=your_telegram_id_here
   ```

   Or create a `.env` file in the project root with:

   ```
   ANYRUN_SB_API_TOKEN=your_token_here
   ANYRUN_SB_ADMIN_ID=your_telegram_id_here
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Add language files:
   Create JSON files in the `lang` directory for each supported language (e.g., `en.json`, `ru.json`, `sr.json`, `sr-Latn.json`).

## Usage

Control the bot service with the following commands:

- Start: `python main.py start [--log LEVEL]`
- Stop: `python main.py stop`
- Restart: `python main.py restart [--log LEVEL]`
- Check status: `python main.py status`
- Kill all instances: `python main.py kill_all`
- View logs: `python main.py logs [--lines NUMBER]`

Log levels can be set to: DEBUG, INFO, WARNING, ERROR, CRITICAL.

Examples:
```
python main.py start --log INFO
python main.py logs --lines 100
```

## Localization

To add or modify localized strings, edit the corresponding JSON files in the `lang` directory.

## Logging

The bot uses a flexible logging system. Log files are automatically created daily with the format `YYYYMMDD.log` in the user's home directory under `arsbtlgbot_logs/`.

## Database

The bot uses an SQLite database to store user information and other options. The database file is located at `db/arsbtlgbot.db`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
