# desktop_app/auth.py
"""
Authentication module for Desktop GUI.

Handles Telegram login flow for the desktop application.
"""

import os
import logging
from typing import Optional, Tuple
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

logger = logging.getLogger(__name__)


class DesktopAuth:
    """
    Handles authentication for the desktop application.

    Manages a single user session for the desktop app.
    """

    def __init__(self):
        """Initialize desktop authentication handler."""
        self.client: Optional[TelegramClient] = None
        self.session_path = os.path.join(Config.SESSIONS_DIR, "desktop_user")
        self.phone_code_hash = None

        # Create sessions directory if needed
        os.makedirs(Config.SESSIONS_DIR, exist_ok=True)

    def has_session(self) -> bool:
        """Check if a valid session exists."""
        return os.path.exists(f"{self.session_path}.session")

    async def create_client(self) -> TelegramClient:
        """Create and connect a TelegramClient."""
        if self.client and self.client.is_connected():
            return self.client

        self.client = TelegramClient(
            self.session_path,
            Config.get_api_id(),
            Config.API_HASH,
            timeout=10,
            connection_retries=5,
        )

        await self.client.connect()
        return self.client

    async def send_code(self, phone: str) -> bool:
        """
        Send verification code to phone number.

        Args:
            phone: Phone number in international format

        Returns:
            True if code sent successfully
        """
        try:
            if not self.client:
                await self.create_client()

            result = await self.client.send_code_request(phone)
            self.phone_code_hash = result.phone_code_hash
            logger.info(f"Code sent to {phone}")
            return True
        except Exception as e:
            logger.error(f"Failed to send code: {e}")
            raise

    async def verify_code(self, phone: str, code: str) -> Tuple[bool, str]:
        """
        Verify the authentication code.

        Args:
            phone: Phone number
            code: Verification code

        Returns:
            Tuple of (success, message or "2FA_REQUIRED")
        """
        try:
            await self.client.sign_in(phone, code, phone_code_hash=self.phone_code_hash)

            me = await self.client.get_me()
            logger.info(f"Logged in as {me.first_name}")
            return True, f"✅ Logged in as {me.first_name} {me.last_name or ''}"

        except SessionPasswordNeededError:
            return False, "2FA_REQUIRED"
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False, f"❌ Error: {str(e)}"

    async def verify_2fa(self, password: str) -> Tuple[bool, str]:
        """
        Verify 2FA password.

        Args:
            password: 2FA password

        Returns:
            Tuple of (success, message)
        """
        try:
            await self.client.sign_in(password=password)

            me = await self.client.get_me()
            logger.info(f"2FA verified for {me.first_name}")
            return True, f"✅ Logged in as {me.first_name} {me.last_name or ''}"

        except Exception as e:
            logger.error(f"2FA verification failed: {e}")
            return False, f"❌ Error: {str(e)}"

    async def load_session(self) -> Tuple[bool, Optional[str]]:
        """
        Load existing session and get user info.

        Returns:
            Tuple of (is_logged_in, user_name or None)
        """
        if not self.has_session():
            return False, None

        try:
            await self.create_client()

            if await self.client.is_user_authorized():
                me = await self.client.get_me()
                name = f"{me.first_name} {me.last_name or ''}".strip()
                return True, name
            else:
                return False, None
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return False, None

    async def logout(self) -> bool:
        """
        Log out and delete session.

        Returns:
            True if successful
        """
        try:
            if self.client:
                await self.client.log_out()
                await self.client.disconnect()
                self.client = None

            # Delete session file
            session_file = f"{self.session_path}.session"
            if os.path.exists(session_file):
                os.remove(session_file)

            logger.info("Desktop user logged out")
            return True
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False

    async def disconnect(self):
        """Disconnect client without logging out."""
        if self.client:
            await self.client.disconnect()

    def get_client(self) -> Optional[TelegramClient]:
        """Get the current client instance."""
        return self.client
