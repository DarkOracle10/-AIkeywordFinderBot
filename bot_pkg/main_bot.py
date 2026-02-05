# bot/main_bot.py
"""
Multi-user Telegram keyword search bot.

Allows users to authenticate with their own Telegram accounts and search
for keywords across their chats. Each user's session is isolated and secure.

Version: 1.1.0
"""

import logging
import os
import sys
from datetime import datetime, timezone

from telethon import TelegramClient, connection, events
from telethon.tl.types import KeyboardButton

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from searcher import get_all_folders, parse_chat_filter, search_messages
from session_manager import SessionManager
from utils import generate_message_link, truncate_text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Global state
USER_STATE = {}
bot = None
session_manager = None


def create_bot_client():
    """Create and initialize the bot client."""
    global bot, session_manager

    # Validate configuration
    if not Config.validate_bot():
        logger.error("Missing required environment variables")
        raise ValueError(
            "Missing required environment variables: TG_API_ID, TG_API_HASH, or TG_BOT_TOKEN"
        )

    api_id = Config.get_api_id()
    api_hash = Config.API_HASH
    bot_token = Config.BOT_TOKEN

    logger.info("Environment variables loaded successfully")

    # Proxy configuration
    use_proxy = Config.use_proxy()
    proxy = Config.get_proxy()
    conn = connection.ConnectionTcpMTProxyRandomizedIntermediate if use_proxy else None

    if use_proxy:
        logger.info("MTProto proxy enabled")
    else:
        logger.info("Direct connection (no proxy)")

    # Create bot client
    try:
        if use_proxy:
            bot = TelegramClient(
                "bot_session",
                api_id,
                api_hash,
                connection=conn,
                proxy=proxy,
                timeout=10,
                connection_retries=5,
            ).start(bot_token=bot_token)
        else:
            bot = TelegramClient(
                "bot_session",
                api_id,
                api_hash,
                timeout=10,
                connection_retries=5,
            ).start(bot_token=bot_token)
        logger.info("Bot client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize bot client: {e}")
        raise

    # Initialize session manager
    session_manager = SessionManager(api_id, api_hash)
    logger.info("Session manager initialized")

    return bot


def setup_handlers(bot_client):
    """Set up all event handlers for the bot."""

    @bot_client.on(events.NewMessage(pattern="/start"))
    async def start(event):
        """Handle /start command with keyboard markup"""
        user_id = event.sender_id
        is_logged_in = session_manager.has_session(user_id)

        if is_logged_in:
            buttons = [
                [KeyboardButton("/search"), KeyboardButton("/status")],
                [KeyboardButton("/help"), KeyboardButton("/feedback")],
                [KeyboardButton("/logout")],
            ]
            message = (
                "👋 Welcome back! You're already logged in.\n\n"
                "Use the buttons below or type commands:"
            )
        else:
            buttons = [
                [KeyboardButton("/login")],
                [KeyboardButton("/help"), KeyboardButton("/feedback")],
            ]
            message = (
                "👋 Hi! I'm a keyword search bot.\n\n"
                "To get started, click /login to authenticate with your Telegram account."
            )

        await event.respond(message, buttons=buttons)

    @bot_client.on(events.NewMessage(pattern="/login"))
    async def cmd_login(event):
        """Handle /login command - start authentication flow"""
        user_id = event.sender_id
        logger.info(f"User {user_id} initiated login")

        if session_manager.has_session(user_id):
            logger.info(f"User {user_id} already logged in")
            await event.respond(
                "You're already logged in! Use /logout first if you want to log in with a different account."
            )
            return

        USER_STATE[user_id] = {"step": "awaiting_phone"}
        await event.respond(
            "🔐 Please send your phone number in international format:\n"
            "Example: +1234567890"
        )

    @bot_client.on(events.NewMessage(pattern="/logout"))
    async def cmd_logout(event):
        """Handle /logout command - remove user session"""
        user_id = event.sender_id
        logger.info(f"User {user_id} initiated logout")

        if not session_manager.has_session(user_id):
            await event.respond("You're not logged in.")
            return

        success = await session_manager.logout(user_id)
        if success:
            if user_id in USER_STATE:
                del USER_STATE[user_id]
            logger.info(f"User {user_id} logged out successfully")
            await event.respond("✅ Successfully logged out!")
        else:
            logger.error(f"Logout failed for user {user_id}")
            await event.respond("❌ Error during logout. Please try again.")

    @bot_client.on(events.NewMessage(pattern="/status"))
    async def cmd_status(event):
        """Check login status"""
        user_id = event.sender_id

        if session_manager.has_session(user_id):
            client = await session_manager.get_client(user_id)
            if client:
                me = await client.get_me()
                await event.respond(
                    f"✅ Logged in as: {me.first_name} {me.last_name or ''}\n"
                    f"📱 Phone: {me.phone}\n"
                    f"🆔 ID: {me.id}"
                )
            else:
                await event.respond("⚠️ Session expired. Please /login again.")
        else:
            await event.respond("❌ Not logged in. Use /login to get started.")

    @bot_client.on(events.NewMessage(pattern="/help"))
    async def cmd_help(event):
        """Show help information"""
        help_text = (
            "📚 **HELP & COMMANDS**\n\n"
            "🔐 **Authentication:**\n"
            "/login - Log in with your phone number\n"
            "/logout - Log out and delete your session\n"
            "/status - Check your current login status\n\n"
            "🔍 **Search:**\n"
            "/search - Search for keywords in your chats\n\n"
            "**How to Search:**\n"
            "1. Use /search\n"
            "2. Enter chat names or 'all'\n"
            "3. Enter keywords (comma-separated)\n"
            "4. Enter start date (YYYY-MM-DD)\n"
            "5. Enter end date (YYYY-MM-DD)\n"
            "6. Get results with direct message links\n\n"
            "💬 **Support:**\n"
            "/feedback - Send feedback or report issues\n"
            "/help - Show this help message\n\n"
            "**Date Format:** YYYY-MM-DD (e.g., 2026-02-01)\n"
            "**Keywords:** Comma-separated (e.g., python,django,web)"
        )
        await event.respond(help_text)

    @bot_client.on(events.NewMessage(pattern="/feedback"))
    async def cmd_feedback(event):
        """Handle feedback command - start feedback flow"""
        user_id = event.sender_id
        logger.info(f"User {user_id} initiated feedback")

        USER_STATE[user_id] = {"step": "awaiting_feedback"}
        await event.respond(
            "💬 **Send Your Feedback**\n\n"
            "Please type your feedback, bug report, or suggestion below.\n"
            "Your message will be sent with your user ID for follow-up.\n\n"
            "Type /cancel to cancel."
        )

    @bot_client.on(events.NewMessage(pattern="/search"))
    async def cmd_search(event):
        user_id = event.sender_id

        if not session_manager.has_session(user_id):
            await event.respond(
                "⚠️ You need to log in first!\n\n"
                "Use /login to authenticate with your Telegram account."
            )
            return

        client = await session_manager.get_client(user_id)
        if not client:
            await event.respond("⚠️ Your session has expired. Please /login again.")
            return

        # Get user's folders
        folders = await get_all_folders(client)
        folder_list = (
            ", ".join([f"<{f}>" for f in folders]) if folders else "No folders found"
        )

        USER_STATE[user_id] = {"step": "chats"}
        await event.respond(
            "📂 **Enter where to search:**\n\n"
            "• Type `all` to search all chats\n"
            "• Enter chat names (comma-separated)\n"
            "• Use `<folder_name>` to search a folder\n"
            "• Mix both: `<Work>, John, <Crypto>`\n\n"
            f"📁 **Your folders:** {folder_list}"
        )

    @bot_client.on(events.NewMessage)
    async def handle_message(event):
        # Ignore command messages
        if event.raw_text.startswith("/"):
            if event.raw_text == "/cancel":
                user_id = event.sender_id
                if user_id in USER_STATE:
                    del USER_STATE[user_id]
                    await event.respond("❌ Cancelled. Use /start to begin.")
            return

        if event.out:
            return

        user_id = event.sender_id
        if user_id not in USER_STATE:
            return

        state = USER_STATE[user_id]

        # Handle feedback submission
        if state["step"] == "awaiting_feedback":
            feedback_text = event.raw_text
            logger.info(f"Feedback from user {user_id}: {feedback_text}")

            try:
                admin_username = Config.ADMIN_USERNAME
                feedback_message = (
                    f"📬 **New Feedback**\n\n"
                    f"👤 **User ID:** {user_id}\n"
                    f"💬 **Message:**\n{feedback_text}"
                )
                await bot_client.send_message(admin_username, feedback_message)
                await event.respond(
                    "✅ Thank you for your feedback! It has been sent to the admin.\n\n"
                    "Use /start to return to the main menu."
                )
                logger.info(f"Feedback sent to admin for user {user_id}")
            except Exception as e:
                logger.error(f"Failed to send feedback: {e}")
                await event.respond(
                    "❌ Failed to send feedback. Please try again later.\n\n"
                    "Use /start to return to the main menu."
                )

            del USER_STATE[user_id]
            return

        # Handle login flow
        if state["step"] == "awaiting_phone":
            phone = event.raw_text.strip()

            if not phone.startswith("+") or len(phone) < 10:
                await event.respond(
                    "❌ Invalid phone format. Please use international format: +1234567890"
                )
                return

            try:
                client, needs_code = await session_manager.create_client(user_id, phone)
                state["phone"] = phone
                state["step"] = "awaiting_code"
                await event.respond(
                    "📱 A verification code has been sent to your Telegram app.\n"
                    "Please send the code here:"
                )
            except Exception as e:
                await event.respond(f"❌ Error: {str(e)}")
                del USER_STATE[user_id]
            return

        if state["step"] == "awaiting_code":
            code = event.raw_text.strip()
            phone = state.get("phone")

            if not phone:
                await event.respond(
                    "❌ Error: Phone number not found. Please start over with /login"
                )
                del USER_STATE[user_id]
                return

            success, message = await session_manager.verify_code(user_id, phone, code)

            if message == "2FA_REQUIRED":
                state["step"] = "awaiting_2fa"
                await event.respond(
                    "🔐 Your account has 2FA enabled.\n"
                    "Please send your 2FA password:"
                )
                return

            if success:
                await event.respond(
                    message + "\n\nYou can now use /search to search your chats!"
                )
                del USER_STATE[user_id]
            else:
                await event.respond(message)
                del USER_STATE[user_id]
            return

        if state["step"] == "awaiting_2fa":
            password = event.raw_text.strip()
            phone = state.get("phone")
            code = state.get("code", "")

            success, message = await session_manager.verify_code(
                user_id, phone, code, password
            )

            if success:
                await event.respond(
                    message + "\n\nYou can now use /search to search your chats!"
                )
            else:
                await event.respond(message)

            del USER_STATE[user_id]
            return

        # Handle search flow
        if state["step"] == "chats":
            chats_input = event.raw_text.strip()
            if chats_input.lower() == "all":
                state["chats"] = "all"
                state["folders"] = None
            else:
                # Parse for folders (<folder_name>) and chat names
                folders, chats = parse_chat_filter(chats_input)

                if not folders and not chats:
                    await event.respond(
                        "Please enter at least one chat name, folder, or 'all'."
                    )
                    return

                state["chats"] = chats if chats else None
                state["folders"] = folders if folders else None

            state["step"] = "exclude_chats"
            await event.respond(
                "Optional: exclude chats/folders (comma-separated) or type 'none'.\n"
                "Examples: <Muted>, Ads, <SpamFolder>"
            )
            return

        if state["step"] == "exclude_chats":
            exclude_input = event.raw_text.strip()
            if exclude_input.lower() in ("none", "no", "skip", "-"):
                state["exclude_chats"] = None
                state["exclude_folders"] = None
            else:
                ex_folders, ex_chats = parse_chat_filter(exclude_input)
                state["exclude_chats"] = ex_chats if ex_chats else None
                state["exclude_folders"] = ex_folders if ex_folders else None

            state["step"] = "keywords"
            await event.respond(
                "Send keywords separated by commas (e.g. python,django,remote):"
            )
            return

        if state["step"] == "keywords":
            kws = [k.strip() for k in event.raw_text.split(",") if k.strip()]
            if not kws:
                await event.respond("Please send at least one keyword.")
                return

            state["keywords"] = kws
            state["step"] = "start_date"
            await event.respond("Enter start date (YYYY-MM-DD):")
            return

        if state["step"] == "start_date":
            try:
                d = datetime.fromisoformat(event.raw_text.strip())
                state["start_date"] = d.replace(tzinfo=timezone.utc)
            except ValueError:
                await event.respond("Invalid date. Use YYYY-MM-DD, e.g. 2025-12-31.")
                return

            state["step"] = "end_date"
            await event.respond("Enter end date (YYYY-MM-DD):")
            return

        if state["step"] == "end_date":
            try:
                d = datetime.fromisoformat(event.raw_text.strip())
                state["end_date"] = d.replace(tzinfo=timezone.utc)
            except ValueError:
                await event.respond("Invalid date. Use YYYY-MM-DD.")
                return

            chats = state.get("chats")
            folders = state.get("folders")
            exclude_chats = state.get("exclude_chats")
            exclude_folders = state.get("exclude_folders")
            keywords = state["keywords"]
            start_date = state["start_date"]
            end_date = state["end_date"]

            # Build search info message
            search_in = []
            if folders:
                search_in.append(f"folders: {', '.join(folders)}")
            if chats:
                search_in.append(
                    f"chats: {', '.join(chats) if isinstance(chats, list) else chats}"
                )
            if not search_in:
                search_in.append("all chats")

            if exclude_folders:
                search_in.append(f"exclude folders: {', '.join(exclude_folders)}")
            if exclude_chats:
                search_in.append(f"exclude chats: {', '.join(exclude_chats)}")

            await event.respond(
                f"🔍 Searching for {', '.join(keywords)}\n"
                f"📂 In: {', '.join(search_in)}\n"
                f"📅 From {start_date.date()} to {end_date.date()}..."
            )

            user_client = await session_manager.get_client(user_id)
            if not user_client:
                await event.respond("❌ Your session expired. Please /login again.")
                del USER_STATE[user_id]
                return

            hits = await search_messages(
                user_client,
                keywords,
                start_date,
                end_date,
                chats,
                folders,
                exclude_chats,
                exclude_folders,
            )

            if not hits:
                await event.respond("No messages found.")
            else:
                lines = []
                for dialog, msg in hits[:20]:
                    chat_name = dialog.name or "Unknown chat"
                    snippet = (msg.message or "").replace("\n", " ")
                    snippet = truncate_text(snippet, 80)

                    entity = dialog.entity
                    msg_link = None

                    if hasattr(entity, "username") and entity.username:
                        msg_link = f"https://t.me/{entity.username}/{msg.id}"
                    else:
                        chat_id = entity.id
                        if hasattr(entity, "megagroup") or hasattr(entity, "broadcast"):
                            msg_link = f"https://t.me/c/{chat_id}/{msg.id}"
                        elif hasattr(entity, "id"):
                            msg_link = f"tg://openmessage?user_id={chat_id}&message_id={msg.id}"

                    if msg_link:
                        lines.append(
                            f"📌 {chat_name} | {msg.date.date()}\n{snippet}\n[Open Message]({msg_link})\n"
                        )
                    else:
                        lines.append(f"📌 {chat_name} | {msg.date.date()}\n{snippet}\n")

                await event.respond("\n".join(lines), link_preview=False)

            del USER_STATE[user_id]
            return


async def shutdown():
    """Cleanup on shutdown"""
    global bot, session_manager
    print("Shutting down...")
    if session_manager:
        await session_manager.disconnect_all()
    if bot:
        await bot.disconnect()
    print("Disconnected all clients.")


def run_bot():
    """Main entry point to run the bot."""
    global bot

    bot = create_bot_client()
    setup_handlers(bot)

    print("Bot running...")
    try:
        bot.run_until_disconnected()
    except KeyboardInterrupt:
        print("\nReceived interrupt signal...")
    finally:
        bot.loop.run_until_complete(shutdown())


if __name__ == "__main__":
    run_bot()
