# Telegram Keyword Search - Standalone Application

This folder contains the **standalone executable version** of the Telegram Keyword Search application. No Python installation required!

## 🚀 Quick Start

### 1. Setup Configuration
Copy `.env.example` to `.env` and fill in your Telegram API credentials:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```
TG_API_ID=your_api_id_here
TG_API_HASH=your_api_hash_here
```

### 2. Run the Application
Simply double-click `TelegramKeywordSearch.exe` to launch the desktop GUI application.

## 📋 Requirements

- Windows 10 or later
- Internet connection (for Telegram API)
- No Python installation needed - everything is bundled!

## 🔐 Configuration Files

- **`.env`** - Your personal Telegram API credentials (DO NOT SHARE - in .gitignore)
- **`.env.example`** - Template for configuration (safe to share)
- **`sessions/`** - Local user session storage (per-user authentication)

## 📸 Features

- Dual-interface: Telegram bot + Desktop GUI
- Per-user authentication (your own Telegram account)
- Multi-keyword search with date filtering
- Folder and chat filtering
- Direct message links for quick navigation
- MTProto proxy support

## 🆘 Troubleshooting

If the `.exe` doesn't start:
1. Ensure `.env` file exists with valid API credentials
2. Check internet connection
3. Try running from command prompt to see error messages
4. See main README.md for detailed setup instructions

## 📚 Full Documentation

For complete documentation, setup instructions, and development info, see the main `README.md` in the parent directory.

---

**Ready to search?** Start by running `TelegramKeywordSearch.exe`!
