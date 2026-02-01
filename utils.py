# utils.py
"""
Shared utility functions for both Telegram bot and Desktop GUI.

Provides helper functions for date parsing, message formatting, and more.
"""

from datetime import datetime, timezone


def parse_date(date_str: str) -> datetime:
    """
    Parse date string to datetime object (UTC).
    
    Args:
        date_str: Date in YYYY-MM-DD format
        
    Returns:
        datetime object with UTC timezone
    """
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.replace(tzinfo=timezone.utc)


def format_date(dt: datetime) -> str:
    """
    Format datetime to YYYY-MM-DD string.
    
    Args:
        dt: datetime object
        
    Returns:
        Formatted date string
    """
    return dt.strftime("%Y-%m-%d")


def format_datetime(dt: datetime) -> str:
    """
    Format datetime to full string with time.
    
    Args:
        dt: datetime object
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def validate_date_format(date_str: str) -> bool:
    """
    Check if string is valid YYYY-MM-DD format.
    
    Args:
        date_str: String to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def generate_message_link(username: str, message_id: int) -> str:
    """
    Generate a direct link to a Telegram message.
    
    Args:
        username: Chat username (without @)
        message_id: Message ID
        
    Returns:
        Message link or empty string if no username
    """
    if username:
        return f"https://t.me/{username}/{message_id}"
    return ""


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def is_bot_chat(entity) -> bool:
    """
    Check if an entity is a bot.
    
    Args:
        entity: Telethon entity
        
    Returns:
        True if bot, False otherwise
    """
    return getattr(entity, 'bot', False)


def is_saved_messages(entity, me) -> bool:
    """
    Check if entity is Saved Messages.
    
    Args:
        entity: Telethon entity
        me: Current user entity
        
    Returns:
        True if Saved Messages, False otherwise
    """
    return getattr(entity, 'id', None) == getattr(me, 'id', None)


def get_chat_title(dialog) -> str:
    """
    Get display title for a chat/dialog.
    
    Args:
        dialog: Telethon dialog
        
    Returns:
        Chat title string
    """
    entity = dialog.entity
    if hasattr(entity, 'title'):
        return entity.title
    if hasattr(entity, 'first_name'):
        name = entity.first_name or ""
        if hasattr(entity, 'last_name') and entity.last_name:
            name += f" {entity.last_name}"
        return name
    return "Unknown Chat"
