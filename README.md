# ANY.RUN Sandbox API for Telegram

This Telegram bot provides a simple interface to interact with the ANY.RUN Sandbox API. It allows users to submit files and URLs for analysis, retrieve analysis results, and perform basic operations with the ANY.RUN service directly through Telegram.

## Key Features:

- Submit files and URLs for analysis in ANY.RUN Sandbox
- Retrieve analysis results and reports
- Check the status of ongoing analyses
- Manage API keys within the Telegram interface
- Multi-language support with dynamic language switching
- Flexible logging system with adjustable log levels

This bot simplifies the process of using ANY.RUN's powerful malware analysis capabilities, making it accessible directly from your Telegram client. It's designed for security researchers, malware analysts, and IT professionals who need quick and easy access to sandbox analysis results.

## Getting Started

Follow the setup instructions in this README to configure and run the bot. Once running, you can interact with the ANY.RUN Sandbox API using simple Telegram commands.

For detailed usage instructions and available commands, start a chat with the bot and use the /help command.

## Setup

1. Clone the repository and navigate to the project directory.

2. Create a virtual environment (recommended):
   ```
   python -m venv sbbotenv
   source sbbotenv/bin/activate
   ```

3. Install dependencies:
   - For production:
     ```
     pip install -r requirements.txt
     ```
   - For development:
     ```
     pip install -r requirements-dev.txt
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

To run the bot manually, use the following command:

```
python main.py
```

The bot will start and listen for incoming messages on Telegram.

## Localization

The bot supports multiple languages. To add or modify localized strings, edit the JSON files in the `lang` directory. Users can change their language using the `/language` command.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
