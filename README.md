# 🔍 AI Keyword Finder Bot

> Intelligent keyword search with dual interface: Interactive Telegram bot + Cross-platform desktop GUI, powered by Telegram's search API.

[![Python](https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge)](https://www.python.org)
[![Telegram](https://img.shields.io/badge/telegram-bot-26A5E4?style=for-the-badge)](https://core.telegram.org/bots)
[![Tkinter](https://img.shields.io/badge/Tkinter-GUI-41CD52?style=for-the-badge)](https://docs.python.org/3/library/tkinter.html)
[![Telethon](https://img.shields.io/badge/Telethon-API-0088CC?style=for-the-badge)](https://docs.telethon.dev)

## ✨ Features

### Dual Interface
- 🤖 **Telegram Bot** - Interactive chat interface with inline keyboards
- 🖥️ **Desktop GUI** - Standalone Tkinter application for Windows/Linux/macOS
- 🔄 **Synchronized** - Same core functionality across both interfaces

### Keyword Search Capabilities
- 🔍 **Smart Search** - Search for keywords across all your Telegram chats
- 📅 **Date Range Filter** - Specify start and end dates for targeted searches
- 💬 **Chat Selection** - Search specific chats/groups or all chats at once
- 🔤 **Multiple Keywords** - Search for multiple keywords simultaneously
- 📊 **Ranked Results** - Messages sorted by relevance with direct links
- 💾 **Session Management** - Secure session storage and management

### User Experience
- 🔐 **Per-User Auth** - Each user logs in with their own Telegram account
- ⚡ **Real-Time Processing** - Fast keyword search across chat history
- 🎨 **Modern UI** - Clean, intuitive interface
- 📱 **Cross-Platform** - Works on all major operating systems
- 🔒 **Secure** - Local session storage with logout capability

## 🎬 Demo

### Telegram Bot Interface
> 📸 Coming soon - Bot conversation screenshots

### Desktop GUI
> 📸 Coming soon - Application screenshots

### Live Bot
**Try it now:** [@YourKeywordBot](https://t.me/YourKeywordBot) _(Coming Soon)_

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Telegram API credentials (for both bot and GUI)
- Telegram Bot Token (for bot interface)
- Tkinter (usually included with Python)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/DarkOracle10/-AIkeywordFinderBot.git
cd -AIkeywordFinderBot

# 2. Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Linux/Mac)
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Configuration

#### 1. Get Required API Keys

**Telegram API Credentials:**
1. Visit [Telegram API](https://my.telegram.org/apps)
2. Log in with your phone number
3. Create a new application
4. Copy your `api_id` and `api_hash`

**Telegram Bot Token:**
1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow instructions
3. Copy your bot token (format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### 2. Create .env File

Create `.env` in project root:

```env
# Telegram API Configuration (Required)
TG_API_ID=your_api_id_here
TG_API_HASH=your_api_hash_here

# Telegram Bot Token (Required for bot interface)
TG_BOT_TOKEN=your_telegram_bot_token_here

# Optional: MTProto Proxy settings
# MT_PROXY_HOST=proxy_host
# MT_PROXY_PORT=proxy_port
# MT_PROXY_SECRET=proxy_secret
```

### Running the Applications

**Telegram Bot:**
```bash
python run_bot.py
```

Expected output:
```
🤖 Bot started successfully!
Bot username: @YourKeywordBot
Waiting for messages...
```

**Desktop GUI:**
```bash
python run_gui.py
```

**Both simultaneously:**
```bash
python run_both.py
```

**Legacy bot:**
```bash
python main.py
```

## 📖 Usage Guide

### Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize bot and show welcome message |
| `/login` | Log in with your Telegram account |
| `/logout` | Log out and delete your session |
| `/status` | Check your login status |
| `/search` | Search for keywords in your chats |
| `/help` | Display help and available commands |
| `/feedback` | Send feedback to the admin |
| `/cancel` | Cancel current operation |

### Bot Usage Example

**Initial Setup:**
```
You: /start
Bot: 👋 Welcome to AI Keyword Finder Bot!
     
     Available commands:
     /login - Login with your account
     /search - Search for keywords
     /help - Get help

You: /login
Bot: 📱 Please enter your phone number in international format
     Example: +1234567890

You: +1234567890
Bot: ✅ Code sent! Please enter the verification code:

You: 12345
Bot: ✅ Logged in successfully!
```

**Searching:**
```
You: /search
Bot: Which chats would you like to search?
     (Enter chat names separated by commas, or type 'all')

You: all
Bot: Enter keywords to search (comma-separated):
     Example: python,django,remote

You: artificial intelligence, machine learning
Bot: 📅 Enter start date (YYYY-MM-DD):

You: 2024-01-01
Bot: 📅 Enter end date (YYYY-MM-DD):

You: 2024-12-31
Bot: 🔍 Searching... Please wait.

Bot: ✅ Found 15 messages:
     
     1. Chat: Tech Discussion
        "Artificial intelligence is transforming..."
        🔗 [View Message](https://t.me/c/123456/789)
     
     2. Chat: ML Study Group
        "Machine learning algorithms have..."
        🔗 [View Message](https://t.me/c/234567/890)
     
     ...
```

### Desktop GUI Usage

#### 1. Launch Application
```bash
python run_gui.py
```

#### 2. Login
- Enter phone number in international format
- Enter verification code sent to your Telegram
- Enter 2FA password (if enabled)

#### 3. Configure Search
- **Chat Selection:** Choose specific chats or "All Chats"
- **Keywords:** Enter comma-separated keywords
- **Date Range:** Set start and end dates
- Click "Search" button

#### 4. View Results
- Results displayed in scrollable list
- Click message links to open in Telegram
- View message preview and chat information

#### 5. Session Management
- Sessions persist between application restarts
- Use "Logout" button to clear session

## 🏗️ Project Structure

```
-AIkeywordFinderBot/
├── main.py                # Legacy bot entry point
├── run_bot.py            # Telegram bot launcher
├── run_gui.py            # Desktop GUI launcher
├── run_both.py           # Combined launcher
├── config.py             # Shared configuration
├── utils.py              # Shared utility functions
├── searcher.py           # Message search functionality
├── session_manager.py    # Per-user session management
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── README.md            # This file
├── bot_pkg/             # Telegram bot package
│   ├── __init__.py
│   └── main_bot.py      # Bot logic and handlers
├── desktop_app/         # Desktop GUI package
│   ├── __init__.py
│   ├── main_gui.py      # Tkinter GUI application
│   └── auth.py          # Desktop authentication
├── standalone-app/      # Standalone app resources
├── sessions/            # User session files (git ignored)
├── docs/                # Documentation
│   └── SCREENSHOTS.md   # Screenshot guide
└── telegram_search.spec # PyInstaller build spec
```

## 🎨 GUI Screenshots

### Main Window
![Main Window](docs/screenshots/gui-main.png)
*Main interface with login and search functionality*

### Settings Panel
![Settings](docs/screenshots/gui-settings.png)
*Configuration options for search parameters*

### Results View
![Results](docs/screenshots/gui-results.png)
*Search results with clickable message links*

## 🔧 Configuration Options

### Search Parameters

Modify in code or set via GUI:

```python
SEARCH_PARAMS = {
    'max_results': 20,           # Maximum results to display
    'include_channels': True,    # Include channels in search
    'include_groups': True,      # Include groups in search
    'include_private': True,     # Include private chats
    'exclude_saved': True,       # Exclude "Saved Messages"
    'exclude_bots': True,        # Exclude bot chats
}
```

### Session Configuration

```python
SESSION_CONFIG = {
    'session_dir': 'sessions/',  # Session storage directory
    'timeout': 3600,             # Session timeout (seconds)
    'auto_logout': False,        # Auto logout on exit
}
```

## 🖥️ Building Desktop Executable

### Windows Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller telegram_search.spec

# Output: dist/TelegramSearch.exe
```

### Linux AppImage

```bash
# Install dependencies
pip install pyinstaller

# Build
pyinstaller --onefile run_gui.py

# Output: dist/run_gui
```

### macOS App

```bash
# Install py2app
pip install py2app

# Create setup.py
python setup.py py2app

# Output: dist/KeywordFinder.app
```

## 🔐 Security Considerations

- **Session Storage:** User sessions are stored locally in `sessions/` directory
- **Token Security:** Sessions contain authentication tokens - keep secure
- **User Privacy:** Bot owner cannot access user messages
- **Logout:** Users can delete sessions anytime with `/logout`
- **Git Ignore:** `sessions/` is excluded from version control

⚠️ **Important:** Never commit `.env` file or `sessions/` directory to version control

## 🐛 Troubleshooting

### Common Issues

**Bot not responding:**
- ✅ Verify bot token is correct in `.env`
- ✅ Check internet connection
- ✅ Ensure bot is started: `python run_bot.py`

**GUI won't launch:**
- ✅ Install Tkinter: Usually included with Python
- ✅ Check Python version (3.8+ required)
- ✅ Verify dependencies: `pip install -r requirements.txt`

**"Your session expired":**
- ✅ Session is no longer valid
- ✅ Solution: `/logout` then `/login` again

**"Invalid phone format":**
- ✅ Use international format with +
- ✅ Example: `+1234567890` (not `1234567890`)

**API errors:**
- ✅ Verify API credentials in `.env`
- ✅ Check API limits/quotas
- ✅ Ensure API credentials are valid

**2FA Issues:**
- ✅ Enter 2FA password exactly as configured
- ✅ Bot will prompt if 2FA is enabled

## 🧪 Testing

```bash
# Run tests (if available)
pytest tests/

# Test bot functionality
python -m pytest tests/test_bot.py

# Test GUI components
python -m pytest tests/test_gui.py
```

## 🚀 Deployment

### Telegram Bot (Production)

**Deploy to cloud platform:**

**Railway.app:**
```bash
railway login
railway init
railway up
```

**Heroku:**
```bash
heroku create keyword-bot
git push heroku main
```

**Docker:**
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run_bot.py"]
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Add more search filters
- [ ] Implement message export
- [ ] Add multi-language UI
- [ ] Batch processing
- [ ] Advanced search operators
- [ ] Visualization charts
- [ ] Browser extension

## 📄 License

MIT License - See LICENSE file

## 👤 Author

**Amir Aeiny**

- GitHub: [@DarkOracle10](https://github.com/DarkOracle10)
- Telegram: @YourUsername
- Email: amir.aeiny10@gmail.com

---

⭐ **Star this repo if you find it useful!**

📱 **Try the bot:** [@YourKeywordBot](https://t.me/YourKeywordBot)
