# main.py
"""
Multi-user Telegram keyword search bot.

Allows users to authenticate with their own Telegram accounts and search
for keywords across their chats. Each user's session is isolated and secure.

Version: 1.0.0
"""

import os
import logging
from telethon import TelegramClient, connection, events
from dotenv import load_dotenv
from datetime import datetime, timezone
from searcher import search_messages
from session_manager import SessionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables first
load_dotenv()

USER_STATE = {}

api_id = os.getenv("TG_API_ID")
api_hash = os.getenv("TG_API_HASH")
bot_token = os.getenv("TG_BOT_TOKEN")

# Validate required environment variables
if not api_id or not api_hash or not bot_token:
    logger.error("Missing required environment variables: TG_API_ID, TG_API_HASH, or TG_BOT_TOKEN")
    raise ValueError("Missing required environment variables: TG_API_ID, TG_API_HASH, or TG_BOT_TOKEN")

api_id = int(api_id)
logger.info("Environment variables loaded successfully")

proxy_server = os.getenv("MT_PROXY_HOST")
proxy_port = os.getenv("MT_PROXY_PORT")
proxy_secret = os.getenv("MT_PROXY_SECRET")

use_proxy = all([proxy_server, proxy_port, proxy_secret])
proxy = None
conn = None

if use_proxy:
    proxy = (proxy_server, int(proxy_port), proxy_secret)
    conn = connection.ConnectionTcpMTProxyRandomizedIntermediate
    logger.info("MTProto proxy enabled")
else:
    logger.info("Direct connection (no proxy)")

# bot client (interface users talk to)
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

# Initialize session manager for per-user clients
session_manager = SessionManager(api_id, api_hash)
logger.info("Session manager initialized")

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    user_id = event.sender_id
    is_logged_in = session_manager.has_session(user_id)
    
    if is_logged_in:
        await event.respond(
            "👋 Welcome back! You're already logged in.\n\n"
            "🔍 /search - Search for keywords in your chats\n"
            "📊 /status - Check your login status\n"
            "🚪 /logout - Log out from your account"
        )
    else:
        await event.respond(
            "👋 Hi! I'm a keyword search bot.\n\n"
            "To get started, you need to log in with your Telegram account:\n"
            "🔐 /login - Log in with your phone number\n\n"
            "After logging in, you'll be able to:\n"
            "🔍 /search - Search for keywords in YOUR own chats\n"
            "📊 /status - Check your login status\n"
            "🚪 /logout - Log out from your account"
        )


@bot.on(events.NewMessage(pattern="/login"))
async def cmd_login(event):
    """Handle /login command - start authentication flow"""
    user_id = event.sender_id
    logger.info(f"User {user_id} initiated login")
    
    # Check if already logged in
    if session_manager.has_session(user_id):
        logger.info(f"User {user_id} already logged in")
        await event.respond("You're already logged in! Use /logout first if you want to log in with a different account.")
        return
    
    USER_STATE[user_id] = {"step": "awaiting_phone"}
    await event.respond(
        "🔐 Please send your phone number in international format:\n"
        "Example: +1234567890"
    )


@bot.on(events.NewMessage(pattern="/logout"))
async def cmd_logout(event):
    """Handle /logout command - remove user session"""
    user_id = event.sender_id
    logger.info(f"User {user_id} initiated logout")
    
    if not session_manager.has_session(user_id):
        await event.respond("You're not logged in.")
        return
    
    success = await session_manager.logout(user_id)
    if success:
        # Clear any pending state
        if user_id in USER_STATE:
            del USER_STATE[user_id]
        logger.info(f"User {user_id} logged out successfully")
        await event.respond("✅ Successfully logged out!")
    else:
        logger.error(f"Logout failed for user {user_id}")
        await event.respond("❌ Error during logout. Please try again.")


@bot.on(events.NewMessage(pattern="/status"))
async def cmd_status(event):
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


@bot.on(events.NewMessage(pattern="/search"))
async def cmd_search(event):
    user_id = event.sender_id
    
    # Check if user is logged in
    if not session_manager.has_session(user_id):
        await event.respond(
            "⚠️ You need to log in first!\n\n"
            "Use /login to authenticate with your Telegram account."
        )
        return
    
    # Verify session is still valid
    client = await session_manager.get_client(user_id)
    if not client:
        await event.respond(
            "⚠️ Your session has expired. Please /login again."
        )
        return
    
    USER_STATE[user_id] = {"step": "chats"}
    await event.respond(
        "Enter chat/group names to search (comma-separated), or type 'all' to search all chats:"
    )

@bot.on(events.NewMessage)
async def handle_message(event):
    # Ignore command messages
    if event.raw_text.startswith('/'):
        return
    
    # Ignore bot's own messages
    if event.out:
        return
    
    user_id = event.sender_id
    if user_id not in USER_STATE:
        return

    state = USER_STATE[user_id]

    # Handle login flow
    if state["step"] == "awaiting_phone":
        phone = event.raw_text.strip()
        
        # Basic phone validation
        if not phone.startswith('+') or len(phone) < 10:
            await event.respond("❌ Invalid phone format. Please use international format: +1234567890")
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
            await event.respond("❌ Error: Phone number not found. Please start over with /login")
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
            await event.respond(message + "\n\nYou can now use /search to search your chats!")
            del USER_STATE[user_id]
        else:
            await event.respond(message)
            del USER_STATE[user_id]
        return
    
    if state["step"] == "awaiting_2fa":
        password = event.raw_text.strip()
        phone = state.get("phone")
        code = state.get("code", "")
        
        success, message = await session_manager.verify_code(user_id, phone, code, password)
        
        if success:
            await event.respond(message + "\n\nYou can now use /search to search your chats!")
        else:
            await event.respond(message)
        
        del USER_STATE[user_id]
        return

    # Handle search flow (rest of the existing code)
    # 1) chats
    if state["step"] == "chats":
        chats_input = event.raw_text.strip().lower()
        if chats_input == "all":
            state["chats"] = "all"
        else:
            chats = [c.strip() for c in event.raw_text.split(",") if c.strip()]
            if not chats:
                await event.respond("Please enter at least one chat name or 'all'.")
                return
            state["chats"] = chats
        
        state["step"] = "keywords"
        await event.respond("Send keywords separated by commas (e.g. python,django,remote):")
        return

    # 2) keywords
    if state["step"] == "keywords":
        kws = [k.strip() for k in event.raw_text.split(",") if k.strip()]
        if not kws:
            await event.respond("Please send at least one keyword.")
            return

        state["keywords"] = kws
        state["step"] = "start_date"
        await event.respond("Enter start date (YYYY-MM-DD):")
        return

    # 3) start date
    if state["step"] == "start_date":
        try:
            d = datetime.fromisoformat(event.raw_text.strip())
            # make it UTC-aware
            state["start_date"] = d.replace(tzinfo=timezone.utc)
        except ValueError:
            await event.respond("Invalid date. Use YYYY-MM-DD, e.g. 2025-12-31.")
            return

        state["step"] = "end_date"
        await event.respond("Enter end date (YYYY-MM-DD):")
        return

    # 4) end date + run search
    if state["step"] == "end_date":
        try:
            d = datetime.fromisoformat(event.raw_text.strip())
            state["end_date"] = d.replace(tzinfo=timezone.utc)
        except ValueError:
            await event.respond("Invalid date. Use YYYY-MM-DD.")
            return

        chats = state["chats"]
        keywords = state["keywords"]
        start_date = state["start_date"]
        end_date = state["end_date"]

        await event.respond(
            f"Searching for {', '.join(keywords)} from {start_date.date()} to {end_date.date()}..."
        )

        # Get the user's own client
        user_client = await session_manager.get_client(user_id)
        if not user_client:
            await event.respond("❌ Your session expired. Please /login again.")
            del USER_STATE[user_id]
            return

        hits = await search_messages(user_client, keywords, start_date, end_date, chats)

        if not hits:
            await event.respond("No messages found.")
        else:
            lines = []
            for dialog, msg in hits[:20]:
                chat_name = dialog.name or "Unknown chat"
                snippet = (msg.message or "").replace("\n", " ")
                if len(snippet) > 80:
                    snippet = snippet[:77] + "..."
                
                # Generate message link
                entity = dialog.entity
                msg_link = None
                
                # Check if entity has username (public channel/group)
                if hasattr(entity, 'username') and entity.username:
                    msg_link = f"https://t.me/{entity.username}/{msg.id}"
                else:
                    # For private chats/groups, use the c/ format
                    # Get the chat_id without -100 prefix for channels/supergroups
                    chat_id = entity.id
                    if hasattr(entity, 'megagroup') or hasattr(entity, 'broadcast'):
                        # It's a channel or supergroup
                        msg_link = f"https://t.me/c/{chat_id}/{msg.id}"
                    elif hasattr(entity, 'id'):
                        # It's a private chat - use tg:// protocol
                        msg_link = f"tg://openmessage?user_id={chat_id}&message_id={msg.id}"
                
                if msg_link:
                    lines.append(f"📌 {chat_name} | {msg.date.date()}\n{snippet}\n[Open Message]({msg_link})\n")
                else:
                    lines.append(f"📌 {chat_name} | {msg.date.date()}\n{snippet}\n")

            await event.respond("\n".join(lines), link_preview=False)

        del USER_STATE[user_id]
        return
    
async def shutdown():
    """Cleanup on shutdown"""
    print("Shutting down...")
    await session_manager.disconnect_all()
    await bot.disconnect()
    print("Disconnected all clients.")

def main_run():
    print("Bot running...")
    try:
        bot.run_until_disconnected()
    except KeyboardInterrupt:
        print("\nReceived interrupt signal...")
    finally:
        bot.loop.run_until_complete(shutdown())

if __name__ == "__main__":
    main_run()
