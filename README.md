# ANY.RUN for Telegram

A Telegram bot for interacting with the ANY.RUN sandbox service. Submit files and URLs for analysis, retrieve results, and manage your ANY.RUN API access - all through Telegram.

## Features

- File and URL analysis submission
- Real-time analysis status monitoring
- Detailed analysis reports with threat verdicts
- Automatic language detection
- Cross-platform support (Windows, Linux, MacOS)
- Secure API key management
- Database-backed task tracking

## Requirements

- Python 3.10 or higher
- ANY.RUN API key
- Telegram Bot Token

## Installation

1. Clone the repository:
```bash
git clone https://github.com/bykovk-pro/anyrun-tg-bot.git
cd anyrun-tg-bot
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
# or
venv\Scripts\activate     # Windows
```

3. Install the package:
```bash
pip install .
```

## Configuration

1. Create `.env` file in the project root:
```env
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_ADMIN_ID=your_telegram_id
```

2. Start the bot:
```bash
python -m src.main
```

## Usage

1. Start a chat with your bot on Telegram
2. Use `/start` to initialize your account
3. Set your ANY.RUN API key using `/apikey`
4. Send files or URLs for analysis
5. Use `/getreport` to retrieve analysis results by UUID

## Commands

- `/start` - Initialize bot
- `/help` - Show help information
- `/apikey` - Set or update API key
- `/getreport` - Get report by UUID

## Security Features

- Secure API key storage
- User access control
- Request rate limiting
- Input validation
- Error handling

## Development

### Project Structure
```
anyrun-tg-bot/
├── src/
│   ├── api/           # API interaction
│   ├── db/           # Database operations
│   └── lang/         # Localization
├── tests/           # Test suite
└── docs/           # Documentation
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- GitHub Issues: [Report a bug](https://github.com/bykovk-pro/anyrun-tg-bot/issues)
- ANY.RUN Support: [Contact support](https://any.run/support)

## Acknowledgments

- [ANY.RUN](https://any.run) for their excellent sandbox service
- [python-telegram-bot](https://python-telegram-bot.org/) team
