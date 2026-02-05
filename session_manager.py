# session_manager.py
"""
Session management for per-user Telegram client authentication.

This module handles creating, storing, and managing individual TelegramClient
instances for each bot user, enabling multi-user functionality where each
user authenticates with their own Telegram account.
"""

import logging
import os
from typing import Dict, Optional, Tuple

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages per-user Telegram sessions and client instances.

    Each user gets their own TelegramClient instance and session file,
    allowing them to authenticate with their own Telegram account and
    search their own chats independently.

    Attributes:
        api_id (int): Telegram API ID
        api_hash (str): Telegram API hash
        sessions_dir (str): Directory to store session files
        clients (Dict[int, TelegramClient]): Cached client instances by user_id
    """

    def __init__(
        self, api_id: int, api_hash: str, sessions_dir: str = "sessions"
    ) -> None:
        """
        Initialize the session manager.

        Args:
            api_id: Telegram API ID from https://my.telegram.org/apps
            api_hash: Telegram API hash from https://my.telegram.org/apps
            sessions_dir: Directory to store user session files (default: "sessions")
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.sessions_dir = sessions_dir
        self.clients: Dict[int, TelegramClient] = {}

        # Create sessions directory if it doesn't exist
        os.makedirs(sessions_dir, exist_ok=True)
        logger.info(f"SessionManager initialized with sessions_dir: {sessions_dir}")

    def get_session_path(self, user_id: int) -> str:
        """
        Get the session file path for a specific user.

        Args:
            user_id: Telegram user ID

        Returns:
            str: Full path to the user's session file
        """
        return os.path.join(self.sessions_dir, f"user_{user_id}.session")

    def has_session(self, user_id: int) -> bool:
        """
        Check if a user has an existing valid session file.

        Args:
            user_id: Telegram user ID

        Returns:
            bool: True if session file exists, False otherwise
        """
        session_path = self.get_session_path(user_id)
        return os.path.exists(session_path)

    async def get_client(self, user_id: int) -> Optional[TelegramClient]:
        """
        Get or load a TelegramClient for a user.

        If the client is cached in memory, returns it immediately.
        Otherwise, loads the client from the user's session file and validates
        that the session is still authorized.

        Args:
            user_id: Telegram user ID

        Returns:
            Optional[TelegramClient]: The user's client if available, None if session
                                     doesn't exist or has expired
        """
        # Return cached client if exists
        if user_id in self.clients:
            return self.clients[user_id]

        # Check if session file exists
        if not self.has_session(user_id):
            return None

        # Create and connect client from existing session
        session_path = self.get_session_path(user_id)
        client = TelegramClient(session_path, self.api_id, self.api_hash)

        try:
            await client.connect()
            if not await client.is_user_authorized():
                await client.disconnect()
                # Session expired, remove it
                if os.path.exists(session_path):
                    os.remove(session_path)
                logger.warning(f"Session expired for user {user_id}")
                return None

            self.clients[user_id] = client
            logger.debug(f"Loaded client for user {user_id}")
            return client
        except Exception as e:
            logger.error(f"Error connecting client for user {user_id}: {e}")
            await client.disconnect()
            return None

    async def create_client(
        self, user_id: int, phone: str
    ) -> Tuple[TelegramClient, bool]:
        """
        Create a new client for a user and initiate phone authentication.

        Sends a verification code to the user's Telegram account which they
        must provide in the next step.

        Args:
            user_id: Telegram user ID
            phone: Phone number in international format (e.g., +1234567890)

        Returns:
            Tuple[TelegramClient, bool]: (client instance, True indicating code is needed)

        Raises:
            Exception: If phone sending fails
        """
        session_path = self.get_session_path(user_id)
        client = TelegramClient(session_path, self.api_id, self.api_hash)

        await client.connect()

        # Send code request
        await client.send_code_request(phone)
        logger.info(f"Verification code sent to {phone} for user {user_id}")

        # Store client temporarily (not fully authorized yet)
        self.clients[user_id] = client

        return client, True

    async def verify_code(
        self, user_id: int, phone: str, code: str, password: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Verify the authentication code (and password if 2FA is enabled).

        Args:
            user_id: Telegram user ID
            phone: Phone number used during sign up
            code: Verification code sent by Telegram
            password: 2FA password if account has 2FA enabled

        Returns:
            Tuple[bool, str]: (success, message) where message is:
                - "✅ Successfully logged in!" on success
                - "2FA_REQUIRED" if 2FA password is needed
                - Error message if verification fails
        """
        if user_id not in self.clients:
            return False, "No pending authentication. Please start with /login"

        client = self.clients[user_id]

        try:
            await client.sign_in(phone, code)
            logger.info(f"User {user_id} successfully authenticated")
            return True, "✅ Successfully logged in!"
        except SessionPasswordNeededError:
            logger.debug(f"2FA required for user {user_id}")
            if password:
                try:
                    await client.sign_in(password=password)
                    logger.info(f"User {user_id} authenticated with 2FA")
                    return True, "✅ Successfully logged in with 2FA!"
                except Exception as e:
                    logger.error(f"2FA password incorrect for user {user_id}: {e}")
                    return False, f"❌ 2FA password incorrect: {str(e)}"
            else:
                return False, "2FA_REQUIRED"
        except Exception as e:
            # Clean up on error
            logger.error(f"Verification failed for user {user_id}: {e}")
            await client.disconnect()
            if user_id in self.clients:
                del self.clients[user_id]
            session_path = self.get_session_path(user_id)
            if os.path.exists(session_path):
                os.remove(session_path)
            return False, f"❌ Verification failed: {str(e)}"

    async def logout(self, user_id: int) -> bool:
        """
        Log out a user and securely remove their session.

        Disconnects the client, clears it from memory, and deletes the
        session file to ensure no data persists after logout.

        Args:
            user_id: Telegram user ID

        Returns:
            bool: True if logout successful, False otherwise
        """
        try:
            # Disconnect client if exists
            if user_id in self.clients:
                client = self.clients[user_id]
                await client.log_out()
                await client.disconnect()
                del self.clients[user_id]

            # Remove session file
            session_path = self.get_session_path(user_id)
            if os.path.exists(session_path):
                os.remove(session_path)

            logger.info(f"User {user_id} logged out successfully")
            return True
        except Exception as e:
            logger.error(f"Error logging out user {user_id}: {e}")
            return False

    async def disconnect_all(self) -> None:
        """
        Disconnect all clients and prepare for shutdown.

        Called during bot shutdown to ensure all connections are properly
        closed and resources are freed.
        """
        logger.info(f"Disconnecting {len(self.clients)} clients...")
        for user_id, client in self.clients.items():
            try:
                await client.disconnect()
                logger.debug(f"Disconnected client for user {user_id}")
            except Exception as e:
                logger.error(f"Error disconnecting user {user_id}: {e}")
        self.clients.clear()
        logger.info("All clients disconnected")
