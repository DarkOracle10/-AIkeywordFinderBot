# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-02-02

### Added

- **Persian/Arabic Character Support**: Full normalization of Persian and Arabic text for accurate searching
- **Portfolio PDF Generation**: Automatic creation of professional portfolio PDF with project details
- **Improved UI/UX**: 
  - Enhanced default window sizes and minimum sizes for better visibility
  - Clipboard operations (Ctrl+C, Ctrl+V, Ctrl+X, Ctrl+A) support in all entry fields
  - Persian-friendly font selection (Tahoma) throughout the application
  - Real-time Persian character normalization as user types

### Fixed

- Persian character matching inconsistencies
- Font rendering for right-to-left languages
- GUI window sizing issues

### Changed

- Updated UI fonts from Segoe UI to Tahoma for better Persian support

---

## [1.2.0] - 2026-02-02

### Added

- **Desktop GUI Folder & Exclusion Features**:
  - Support for searching specific Telegram folders using `<folder_name>` syntax
  - Ability to exclude specific chats and folders from searches
  - Folder enumeration and display functionality
  - Combined folder and chat filtering in one search

### Changed

- `.gitignore` updated to exclude portable app environment files
- Standalone app directory structure improved
- PyInstaller spec file updated to output to `standalone-app/` directory

---

## [1.1.0] - 2026-02-01

### Added

- **Code Restructuring & Modularization**:
  - Separated bot logic into `bot_pkg/` package
  - Separated GUI logic into `desktop_app/` package
  - Created shared `config.py` module for configuration management
  - Created shared `utils.py` module for utility functions
  - Per-user session management system (`session_manager.py`)

- **Multi-Interface Launcher Scripts**:
  - `run_bot.py` - Start only the Telegram bot
  - `run_gui.py` - Start only the desktop GUI
  - `run_both.py` - Run bot and GUI simultaneously in separate threads

- **Desktop GUI Features**:
  - Complete Tkinter-based GUI application (`desktop_app/main_gui.py`)
  - Per-user authentication system (`desktop_app/auth.py`)
  - Login flow with phone verification and 2FA support
  - Search interface with chat/folder selection
  - Results display with clickable message links
  - Logout functionality with session management

- **Telegram Bot Enhancements**:
  - Moved to `bot_pkg/main_bot.py` for modularity
  - Enhanced command handlers with better error messages
  - Improved keyboard layout and user experience
  - Folder listing integration
  - Feedback submission system

- **Configuration Management**:
  - Centralized `config.py` for API credentials and proxy settings
  - Support for MTProto proxy configuration
  - Improved environment variable handling

- **Documentation & Distribution**:
  - `standalone-app/` directory for portable distribution
  - `.env.example` template files for configuration
  - Enhanced README.md with setup instructions and feature details
  - PyInstaller spec file for building Windows .exe

### Fixed

- Message link generation for different chat types
- Session persistence across restarts
- Date range filtering logic

### Changed

- Project structure reorganized for better maintainability
- Shared utilities extracted to common modules
- Requirements expanded with PyInstaller support
- Main entry points refactored to launcher scripts

---

## [1.0.0] - 2026-02-01

### Added

- **Multi-user authentication**: Each user logs in with their own Telegram account
- **Per-user sessions**: Individual session files for each user (`sessions/user_{id}.session`)
- **Direct message links**: Clickable links to found messages in chats
  - Support for public channels/groups (`https://t.me/username/message_id`)
  - Support for private chats/groups (`https://t.me/c/chat_id/message_id`)
- **Session management commands**:
  - `/login` - Authenticate with phone number
  - `/logout` - Remove session and log out
  - `/status` - Check login status
  - `/search` - Search keywords in chats
- **Authentication features**:
  - Phone number verification with OTP
  - 2FA (Two-Factor Authentication) support
  - Automatic session expiration handling
- **Search features**:
  - Search by keywords (comma-separated)
  - Filter by specific chats/groups or search all
  - Date range filtering (start and end dates)
  - Timezone-aware date handling (UTC)
- **Auto-filtering**: Automatically excludes "Saved Messages" and bot chats
- **Improved output**:
  - Formatted search results with timestamps
  - Message snippets (80 chars max)
  - Emoji indicators for better UX
- **Comprehensive documentation**:
  - README.md with full feature list
  - SETUP.md with quick start guide
  - MIGRATION.md for upgrading from older versions
  - .env.example template for configuration
- **Code quality**:
  - Type hints for better code clarity
  - Comprehensive docstrings
  - Error handling and validation
  - Logging system with file and console output
  - Proper async/await patterns
- **Project structure**:
  - Separated concerns (main.py, session_manager.py, searcher.py)
  - MIT License for open source
  - .gitignore for sensitive files
  - requirements.txt for dependencies

### Security Features

- Environment variables protected with .gitignore
- User sessions stored securely per-user
- Session validation and expiration
- No hardcoded credentials
- Proper error handling without exposing sensitive info

### Configuration

- MTProto proxy support (optional)
- Configurable sessions directory
- Logging configuration

## Future Roadmap

### v1.1.0 (Planned)

- [ ] Database for search history
- [ ] Advanced filters (search by user, media type)
- [ ] Bulk export results (PDF, JSON, CSV)
- [ ] Message preview images
- [ ] Search performance optimization
- [ ] Rate limiting per user

### v1.2.0 (Planned)

- [ ] Web dashboard
- [ ] Scheduled search tasks
- [ ] Real-time notifications
- [ ] Message tagging/bookmarks
- [ ] Search analytics

### v2.0.0 (Future)

- [ ] Docker support
- [ ] Docker Compose orchestration
- [ ] Database persistence layer
- [ ] REST API
- [ ] Admin panel

## Known Issues

None at this time. Please report issues on GitHub.

## Deprecations

None at this time.

## Security Patches

None at this time.

---

For more information, see [README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md).
