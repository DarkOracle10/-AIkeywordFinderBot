# config.py
"""
Shared configuration module for both Telegram bot and Desktop GUI.

Handles loading environment variables and proxy settings.
"""

import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Telegram API credentials
    API_ID = os.getenv("TG_API_ID")
    API_HASH = os.getenv("TG_API_HASH")
    BOT_TOKEN = os.getenv("TG_BOT_TOKEN")

    # Admin settings
    ADMIN_USERNAME = "Amir10Aeini"

    # Proxy settings (optional)
    PROXY_HOST = os.getenv("MT_PROXY_HOST")
    PROXY_PORT = os.getenv("MT_PROXY_PORT")
    PROXY_SECRET = os.getenv("MT_PROXY_SECRET")

    # Directories
    SESSIONS_DIR = "sessions"

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration values."""
        if not cls.API_ID or not cls.API_HASH:
            return False
        return True

    @classmethod
    def validate_bot(cls) -> bool:
        """Validate bot-specific configuration."""
        return cls.validate() and bool(cls.BOT_TOKEN)

    @classmethod
    def get_api_id(cls) -> int:
        """Get API ID as integer."""
        return int(cls.API_ID) if cls.API_ID else 0

    @classmethod
    def use_proxy(cls) -> bool:
        """Check if proxy should be used."""
        return all([cls.PROXY_HOST, cls.PROXY_PORT, cls.PROXY_SECRET])

    @classmethod
    def get_proxy(cls) -> tuple:
        """Get proxy tuple for Telethon."""
        if cls.use_proxy():
            return (cls.PROXY_HOST, int(cls.PROXY_PORT), cls.PROXY_SECRET)
        return None
