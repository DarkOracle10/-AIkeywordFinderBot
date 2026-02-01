# searcher.py
from datetime import datetime
from typing import List, Tuple

from telethon import TelegramClient
from telethon.tl.custom import Dialog
from telethon.tl.types import Message


async def search_messages(
    user_client: TelegramClient,
    keywords: List[str],
    start_date: datetime,
    end_date: datetime,
    chats=None,
    max_results: int = 200,
) -> List[Tuple[Dialog, Message]]:
    keywords = [k.lower() for k in keywords if k]
    results: List[Tuple[Dialog, Message]] = []

    async for dialog in user_client.iter_dialogs():
        entity = dialog.entity
        chat_name = (dialog.name or "").lower()
        
        # Skip bot chat and Saved Messages
        if "saved messages" in chat_name or dialog.is_user and getattr(entity, 'bot', False):
            continue
        
        # Filter by chat names if specified
        if chats and chats != "all":
            if not any(c.lower() in chat_name for c in chats):
                continue

        async for msg in user_client.iter_messages(
            entity,
            offset_date=end_date,
        ):
            # iter_messages with offset_date goes backwards from end_date
            if msg.date < start_date:
                break
            if not msg.message:
                continue

            text = msg.message.lower()
            if any(k in text for k in keywords):
                results.append((dialog, msg))
                if len(results) >= max_results:
                    return results

    return results
