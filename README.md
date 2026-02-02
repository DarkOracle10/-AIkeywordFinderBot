s# Telegram Keyword Search

A multi-user Telegram application that allows users to search for keywords in their own Telegram chats. Available as both a **Telegram Bot** and a **Desktop GUI Application**.

## Features

- 🔐 **Per-User Authentication** - Each user logs in with their own Telegram account
- 🔍 **Keyword Search** - Search for multiple keywords across your chats
- 📅 **Date Range Filtering** - Specify start and end dates for searches
- 💬 **Chat Selection** - Search specific chats/groups or all chats
- 🔒 **Secure Sessions** - User sessions are stored securely and can be logged out anytime
- 🚫 **Auto-Filter** - Automatically excludes "Saved Messages" and bot chats
- 🖥️ **Desktop App** - Native Windows GUI application with Tkinter
- 🤖 **Telegram Bot** - Use directly from Telegram chat

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create `.env` File

Create a `.env` file in the project root:

```env
TG_API_ID=your_api_id
TG_API_HASH=your_api_hash
TG_BOT_TOKEN=your_bot_token  # Only needed for Telegram bot

# Optional: MTProto Proxy settings
MT_PROXY_HOST=proxy_host
MT_PROXY_PORT=proxy_port
MT_PROXY_SECRET=proxy_secret
```

Get your API credentials from: https://my.telegram.org/apps

### 3. Run the Application

**Desktop GUI only:**
```bash
python run_gui.py
```

**Telegram Bot only:**
```bash
python run_bot.py
```

**Both simultaneously:**
```bash
python run_both.py
```

**Legacy (original bot):**
```bash
python main.py
```

## Desktop Application

The desktop application provides a native Windows GUI for searching your Telegram chats.

### Features
- 📱 Login with phone number + verification code + optional 2FA
- 🔍 Search interface with chat selection, keywords, and date range
- 📋 Results view with clickable message links
- 💾 Persistent session storage

### Building Executable (.exe)

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller telegram_search.spec
```

The executable will be created in the `dist/` folder.

## Telegram Bot Usage

### First Time Setup

1. Start a chat with your bot on Telegram
2. Send `/start` to see available commands
3. Send `/login` to begin authentication
4. Enter your phone number in international format (e.g., +1234567890)
5. Enter the verification code sent to your Telegram app
6. If you have 2FA enabled, enter your 2FA password

### Searching

Once logged in:

1. Send `/search` to start a search
2. Enter chat names to search (comma-separated) or type `all` to search all chats
3. Enter keywords (comma-separated, e.g., python,django,remote)
4. Enter start date (YYYY-MM-DD format)
5. Enter end date (YYYY-MM-DD format)
6. Bot will return up to 20 matching messages with direct links

### Available Commands

| Command | Description |
|---------|-------------|
| `/start` | Show welcome message and keyboard |
| `/login` | Log in with your Telegram account |
| `/logout` | Log out and delete your session |
| `/status` | Check your login status |
| `/search` | Search for keywords in your chats |
| `/help` | Show detailed help information |
| `/feedback` | Send feedback to the admin |
| `/cancel` | Cancel current operation |

## Project Structure

```
telegram-keyword-searcher/
├── config.py           # Shared configuration module
├── utils.py            # Shared utility functions
├── searcher.py         # Message search functionality
├── session_manager.py  # Per-user session management
├── main.py             # Legacy bot entry point
├── run_bot.py          # Telegram bot launcher
├── run_gui.py          # Desktop GUI launcher
├── run_both.py         # Combined launcher
├── bot_pkg/            # Telegram bot package
│   ├── __init__.py
│   └── main_bot.py     # Bot logic and handlers
├── desktop_app/        # Desktop GUI package
│   ├── __init__.py
│   ├── main_gui.py     # Tkinter GUI application
│   └── auth.py         # Desktop authentication
├── sessions/           # User session files (git ignored)
├── requirements.txt    # Python dependencies
└── telegram_search.spec # PyInstaller build spec
```

## Architecture

### Multi-User System

The bot uses a per-user session management system:

- **SessionManager** - Handles creating, storing, and managing user sessions
- **sessions/** directory - Stores individual user session files
- Each user has their own `TelegramClient` instance
- Sessions persist between bot restarts
- Users search their own chats, not the bot owner's chats

### File Structure

```
├── main.py              # Main bot logic and handlers
├── session_manager.py   # Per-user session management
├── searcher.py          # Message search functionality
├── .env                 # Environment variables (not in git)
├── sessions/            # User session storage (created automatically)
│   ├── user_123456.session
│   └── user_789012.session
└── README.md
```

## Security Considerations

- User sessions are stored locally in the `sessions/` directory
- Sessions contain authentication tokens - keep this directory secure
- Add `sessions/` to `.gitignore` to prevent committing user data
- Users can delete their session anytime with `/logout`
- The bot owner cannot access user messages directly

## Limitations

- Maximum 20 results displayed per search
- Date filtering requires timezone-aware dates (UTC)
- Large chat histories may take time to search
- Proxy support available but optional

## Troubleshooting

**"Your session expired"**
- Your Telegram session is no longer valid
- Solution: Use `/logout` then `/login` again

**"Invalid phone format"**
- Phone number must be in international format with +
- Example: +1234567890 (not 1234567890)

**"Access restricted" (old error)**
- This error should no longer appear in the multi-user version
- If you see this, ensure you're running the updated code

**2FA Issues**
- Make sure you enter your 2FA password exactly as configured
- The bot will prompt for 2FA if needed during login

## Development

To modify the bot:

- `main.py` - Add new commands or modify bot behavior
- `session_manager.py` - Modify session handling logic
- `searcher.py` - Modify search algorithm or filters

## License

MIT License - Feel free to modify and use as needed.
