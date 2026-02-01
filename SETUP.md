# Quick Setup Guide

## Prerequisites

- Python 3.8+
- A Telegram account
- A Telegram bot token (create via [@BotFather](https://t.me/botfather))

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/telegram-keyword-search-bot.git
   cd telegram-keyword-search-bot
   ```

2. **Create virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install telethon python-dotenv
   ```

4. **Get your API credentials**
   - Go to https://my.telegram.org/apps
   - Sign in with your Telegram account
   - Create an app or use existing one
   - Copy your `API_ID` and `API_HASH`

5. **Create bot token**
   - Chat with [@BotFather](https://t.me/botfather) on Telegram
   - Use `/newbot` command
   - Copy the token provided

6. **Setup environment**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and fill in:
   - `TG_API_ID` - Your API ID
   - `TG_API_HASH` - Your API Hash
   - `TG_BOT_TOKEN` - Your bot token

7. **Run the bot**
   ```bash
   python main.py
   ```

The bot will start and you can message it on Telegram!

## First Steps in Telegram

1. Start a chat with your bot
2. Send `/start` to see options
3. Send `/login` to authenticate
4. Follow the authentication prompts
5. Use `/search` to search your chats!

## Need Help?

- Check [README.md](README.md) for full documentation
- Check [MIGRATION.md](MIGRATION.md) if upgrading from an older version
- See troubleshooting section in README.md
