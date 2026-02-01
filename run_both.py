# run_both.py
"""
Launcher script to run both Telegram Bot and Desktop GUI simultaneously.

This starts the bot in a background thread and the GUI in the main thread.
"""

import threading
import sys
from bot_pkg.main_bot import create_bot_client, setup_handlers
from desktop_app.main_gui import run_gui


def run_bot_thread():
    """Run the Telegram bot in a separate thread."""
    try:
        bot = create_bot_client()
        setup_handlers(bot)
        print("Bot running in background...")
        bot.run_until_disconnected()
    except Exception as e:
        print(f"Bot error: {e}")


if __name__ == "__main__":
    print("Starting Telegram Keyword Search...")
    print("=" * 40)
    
    # Start bot in background thread
    bot_thread = threading.Thread(target=run_bot_thread, daemon=True)
    bot_thread.start()
    print("✅ Telegram bot started in background")
    
    # Run GUI in main thread
    print("✅ Starting desktop application...")
    print("=" * 40)
    run_gui()
