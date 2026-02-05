# bot_pkg/__init__.py
"""
Telegram Bot package for keyword searching.

This package contains the Telegram bot interface that allows users
to search their chats via the bot.
"""

from bot_pkg.main_bot import run_bot

__all__ = ["run_bot"]
