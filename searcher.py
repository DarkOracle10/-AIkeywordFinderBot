# searcher.py
from datetime import datetime
from typing import List, Tuple, Optional, Set

from telethon import TelegramClient
from telethon.tl.custom import Dialog
from telethon.tl.types import Message
from telethon.tl.functions.messages import GetDialogFiltersRequest


async def get_folder_chat_ids(user_client: TelegramClient, folder_name: str) -> Set[int]:
    """
    Get chat IDs that belong to a specific Telegram folder.
    
    Args:
        user_client: Authenticated TelegramClient
        folder_name: Name of the folder to search
        
    Returns:
        Set of chat IDs in the folder
    """
    chat_ids = set()
    
    try:
        # Get all dialog filters (folders)
        filters = await user_client(GetDialogFiltersRequest())
        
        for dialog_filter in filters.filters:
            # Check if this filter has a title attribute (it's a folder)
            if hasattr(dialog_filter, 'title') and dialog_filter.title.lower() == folder_name.lower():
                # Get included peers
                if hasattr(dialog_filter, 'include_peers'):
                    for peer in dialog_filter.include_peers:
                        if hasattr(peer, 'channel_id'):
                            chat_ids.add(peer.channel_id)
                        elif hasattr(peer, 'chat_id'):
                            chat_ids.add(peer.chat_id)
                        elif hasattr(peer, 'user_id'):
                            chat_ids.add(peer.user_id)
                
                # Also check pinned peers
                if hasattr(dialog_filter, 'pinned_peers'):
                    for peer in dialog_filter.pinned_peers:
                        if hasattr(peer, 'channel_id'):
                            chat_ids.add(peer.channel_id)
                        elif hasattr(peer, 'chat_id'):
                            chat_ids.add(peer.chat_id)
                        elif hasattr(peer, 'user_id'):
                            chat_ids.add(peer.user_id)
                break
    except Exception as e:
        print(f"Error getting folder chats: {e}")
    
    return chat_ids


async def get_all_folders(user_client: TelegramClient) -> List[str]:
    """
    Get list of all folder names.
    
    Args:
        user_client: Authenticated TelegramClient
        
    Returns:
        List of folder names
    """
    folders = []
    
    try:
        filters = await user_client(GetDialogFiltersRequest())
        
        for dialog_filter in filters.filters:
            if hasattr(dialog_filter, 'title'):
                folders.append(dialog_filter.title)
    except Exception as e:
        print(f"Error getting folders: {e}")
    
    return folders


def parse_chat_filter(filter_input: str) -> Tuple[List[str], List[str]]:
    """
    Parse chat filter input to separate folders and chat names.
    
    Folders use <folder_name> syntax.
    Chat names are plain text, comma-separated.
    
    Args:
        filter_input: Raw input string
        
    Returns:
        Tuple of (folder_names, chat_names)
    """
    import re
    
    folders = []
    chats = []
    
    # Find all folder references: <folder_name>
    folder_pattern = r'<([^>]+)>'
    folder_matches = re.findall(folder_pattern, filter_input)
    folders.extend([f.strip() for f in folder_matches if f.strip()])
    
    # Remove folder references from input
    remaining = re.sub(folder_pattern, '', filter_input)
    
    # Parse remaining as chat names
    chat_parts = [c.strip() for c in remaining.split(',') if c.strip()]
    chats.extend(chat_parts)
    
    return folders, chats


async def search_messages(
    user_client: TelegramClient,
    keywords: List[str],
    start_date: datetime,
    end_date: datetime,
    chats=None,
    folders: Optional[List[str]] = None,
    exclude_chats: Optional[List[str]] = None,
    exclude_folders: Optional[List[str]] = None,
    max_results: int = 200,
) -> List[Tuple[Dialog, Message]]:
    """
    Search messages across chats with optional folder filtering.
    
    Args:
        user_client: Authenticated TelegramClient
        keywords: List of keywords to search
        start_date: Start date for search
        end_date: End date for search
        chats: Chat names to search (list or "all")
        folders: Folder names to search (optional)
        max_results: Maximum number of results
        
    Returns:
        List of (Dialog, Message) tuples
    """
    keywords = [k.lower() for k in keywords if k]
    results: List[Tuple[Dialog, Message]] = []
    
    # Normalize filters
    include_chat_ids = set()
    exclude_chat_ids = set()
    exclude_chats = [c.lower() for c in exclude_chats] if exclude_chats else []

    # Get chat IDs from include folders if specified
    if folders:
        for folder_name in folders:
            ids = await get_folder_chat_ids(user_client, folder_name)
            include_chat_ids.update(ids)

    # Get chat IDs from exclude folders if specified
    if exclude_folders:
        for folder_name in exclude_folders:
            ids = await get_folder_chat_ids(user_client, folder_name)
            exclude_chat_ids.update(ids)

    async for dialog in user_client.iter_dialogs():
        entity = dialog.entity
        chat_name = (dialog.name or "").lower()
        chat_id = entity.id
        
        # Skip bot chat and Saved Messages
        if "saved messages" in chat_name or dialog.is_user and getattr(entity, 'bot', False):
            continue
        
        # Include filter
        include_ok = False
        if chats == "all" and not folders:
            include_ok = True
        else:
            if folders and include_chat_ids and chat_id in include_chat_ids:
                include_ok = True
            if chats and chats != "all" and any(c.lower() in chat_name for c in chats):
                include_ok = True

        if not include_ok:
            continue

        # Exclude filter
        if exclude_chat_ids and chat_id in exclude_chat_ids:
            continue
        if exclude_chats and any(c in chat_name for c in exclude_chats):
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
