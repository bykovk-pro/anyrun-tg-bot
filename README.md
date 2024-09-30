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

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Set up the environment variables:

   Create a `.env` file in the project root with:

   ```
   TELEGRAM_TOKEN=<your_telegram_token >
   TELEGRAM_ADMIN_ID=<your_telegram_admin_id>
   LOG_LEVEL=<your_log_level>
   TELEGRAM_LOG_LEVEL=<your_telegram_log_level>
   ```

   Note: Make sure to replace the placeholder values with your actual values.

## Setting up the System Service

To run the ANY.RUN Sandbox API for Telegram bot as a system service, follow these steps:

1. Create a service configuration file:
   ```
   sudo nano /etc/systemd/system/anyrun-tg-bot.service
   ```

2. Insert the following content, adapting the paths and user as necessary:
   ```
   [Unit]
   Description=ANY.RUN Sandbox API for Telegram
   After=network.target

   [Service]
   ExecStart=/usr/bin/python3 /path/to/your/bot/main.py
   WorkingDirectory=/path/to/your/bot
   User=your_username
   Group=your_group
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. Save the file and exit the editor.

4. Reload systemd:
   ```
   sudo systemctl daemon-reload
   ```

5. Enable the service to start on boot:
   ```
   sudo systemctl enable anyrun-tg-bot.service
   ```

6. Start the service:
   ```
   sudo systemctl start anyrun-tg-bot.service
   ```

7. Check the service status:
   ```
   sudo systemctl status anyrun-tg-bot.service
   ```

The bot will now automatically start on system boot and restart in case of failures.

To view the logs, use the following command:
```
journalctl -u anyrun-tg-bot.service
```

To view the last 50 lines of logs:
```
journalctl -u anyrun-tg-bot.service -n 50 --no-pager
```

## Usage

To run the bot manually, use the following command:

```
python main.py
```

The bot will start and listen for incoming messages on Telegram.

## Localization

The bot supports multiple languages. To add or modify localized strings, edit the JSON files in the `lang` directory. Users can change their language using the `/language` command.

## Logging

The bot uses a system logging mechanism. Logs can be viewed using the `journalctl` command:

```
journalctl -u anyrun-tg-bot.service
```

To view the last 50 lines of logs:
```
journalctl -u anyrun-tg-bot.service -n 50 --no-pager
```

## Database

The bot uses an SQLite database to store user information and other options. The database file is located at `db/arsbtlgbot.db`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
