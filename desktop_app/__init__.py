# desktop_app/__init__.py
"""
Desktop GUI Application package for Telegram keyword searching.

This package contains the desktop GUI interface that allows users
to search their chats via a native desktop application.
"""

from desktop_app.main_gui import run_gui

__all__ = ['run_gui']
