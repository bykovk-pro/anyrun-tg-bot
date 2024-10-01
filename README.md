# ANY.RUN Sandbox API for Telegram

This Telegram bot provides a simple interface to interact with the ANY.RUN Sandbox API. It allows users to submit files and URLs for analysis, retrieve analysis results, and perform basic operations with the ANY.RUN service directly through Telegram.

## Key Features:

- Submit files and URLs for analysis in ANY.RUN Sandbox
- Retrieve analysis results and reports
- Check the status of ongoing analyses
- Manage API keys within the Telegram interface
- Multi-language support with dynamic language switching
- Flexible logging system with adjustable log levels
- Daemon mode for running the bot as a background service

This bot simplifies the process of using ANY.RUN's powerful malware analysis capabilities, making it accessible directly from your Telegram client. It's designed for security researchers, malware analysts, and IT professionals who need quick and easy access to sandbox analysis results.

## Getting Started

Follow the setup instructions in this README to configure and run the bot. Once running, you can interact with the ANY.RUN Sandbox API using simple Telegram commands.

For detailed usage instructions and available commands, start a chat with the bot and use the /help command.

## Setup

1. Clone the repository and navigate to the project directory.

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install .
   ```
   For development, use:
   ```
   pip install -e .[dev]
   ```

4. Set up the environment variables:

   Create a `.env` file in the project root with:

   ```
   TELEGRAM_TOKEN=<your_telegram_token>
   TELEGRAM_ADMIN_ID=<your_telegram_admin_id>
   LOG_LEVEL=<your_log_level>
   TELEGRAM_LOG_LEVEL=<your_telegram_log_level>
   ```

   Note: Make sure to replace the placeholder values with your actual values.

## Running the Bot

To run the bot, use the following commands:

- Start the bot:
  ```
  python main.py start
  ```

- Stop the bot:
  ```
  python main.py stop
  ```

- Restart the bot:
  ```
  python main.py restart
  ```

- Force stop all instances of the bot:
  ```
  python main.py kill
  ```

- View logs:
  ```
  python main.py logs
  ```

The bot will run as a daemon process in the background.

## Localization

The bot supports multiple languages. To add or modify localized strings, edit the JSON files in the `lang` directory. Users can change their language using the `/language` command.

## Development

For development purposes, you can install the package in editable mode with development dependencies:

```
pip install -e .[dev]
```

This will install additional tools like PyInstaller for creating standalone executables.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
