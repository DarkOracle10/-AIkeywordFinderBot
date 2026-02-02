# searcher.py
import unicodedata
from datetime import datetime
from typing import List, Tuple, Optional, Set

from telethon import TelegramClient
from telethon.tl.custom import Dialog
from telethon.tl.types import Message
from telethon.tl.functions.messages import GetDialogFiltersRequest


# Persian/Arabic character normalization map
PERSIAN_ARABIC_MAP = {
    'ي': 'ی',  # Arabic Yeh to Persian Yeh
    'ك': 'ک',  # Arabic Kaf to Persian Kaf
    'ە': 'ه',  # Kurdish He to Persian He
    '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
    '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
    '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
    '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
}


def normalize_persian(text: str) -> str:
    """
    Normalize Persian/Arabic text for consistent comparison.
    Converts Arabic characters to Persian equivalents.
    """
    if not text:
        return text
    
    # Unicode NFKC normalization
    text = unicodedata.normalize('NFKC', text)
    
    # Apply Persian/Arabic character mapping
    for arabic, persian in PERSIAN_ARABIC_MAP.items():
        text = text.replace(arabic, persian)
    
    return text


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
        
        # Debug: print available folders
        print(f"[DEBUG] Looking for folder: '{folder_name}'")
        
        for dialog_filter in filters.filters:
            # Check if this filter has a title attribute (it's a folder)
            if hasattr(dialog_filter, 'title'):
                # Handle TextWithEntities or plain string
                title = dialog_filter.title
                if hasattr(title, 'text'):
                    # It's a TextWithEntities object
                    title_text = title.text
                else:
                    # It's a plain string
                    title_text = str(title)
                
                print(f"[DEBUG] Found folder: '{title_text}'")
                
                if title_text.lower() == folder_name.lower():
                    print(f"[DEBUG] Matched folder: '{title_text}'")
                    
                    # Get included peers
                    if hasattr(dialog_filter, 'include_peers'):
                        for peer in dialog_filter.include_peers:
                            # Extract ID based on peer type
                            peer_id = None
                            if hasattr(peer, 'channel_id'):
                                peer_id = peer.channel_id
                            elif hasattr(peer, 'chat_id'):
                                peer_id = peer.chat_id
                            elif hasattr(peer, 'user_id'):
                                peer_id = peer.user_id
                            
                            if peer_id:
                                chat_ids.add(peer_id)
                                print(f"[DEBUG] Added peer ID from include_peers: {peer_id}")
                    
                    # Also check pinned peers
                    if hasattr(dialog_filter, 'pinned_peers'):
                        for peer in dialog_filter.pinned_peers:
                            peer_id = None
                            if hasattr(peer, 'channel_id'):
                                peer_id = peer.channel_id
                            elif hasattr(peer, 'chat_id'):
                                peer_id = peer.chat_id
                            elif hasattr(peer, 'user_id'):
                                peer_id = peer.user_id
                            
                            if peer_id:
                                chat_ids.add(peer_id)
                                print(f"[DEBUG] Added peer ID from pinned_peers: {peer_id}")
                    break
        
        print(f"[DEBUG] Total chat IDs in folder '{folder_name}': {len(chat_ids)}")
        print(f"[DEBUG] Chat IDs: {chat_ids}")
        
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
                title = dialog_filter.title
                # Handle TextWithEntities or plain string
                if hasattr(title, 'text'):
                    folders.append(title.text)
                else:
                    folders.append(str(title))
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
    keywords = [normalize_persian(k.lower()) for k in keywords if k]
    results: List[Tuple[Dialog, Message]] = []
    
    # Normalize filters
    include_chat_ids = set()
    exclude_chat_ids = set()
    exclude_chats = [normalize_persian(c.lower()) for c in exclude_chats] if exclude_chats else []

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
        chat_name = normalize_persian((dialog.name or "").lower())
        chat_id = entity.id
        
        # Debug first few dialogs when folder search is active
        if folders and include_chat_ids:
            print(f"[DEBUG] Checking dialog: '{dialog.name}' with ID: {chat_id}")
        
        # Include filter logic
        include_ok = False
        
        # If searching all chats (no folder or chat filter)
        if chats == "all" and not folders:
            include_ok = True
        # If searching specific folders
        elif folders and include_chat_ids:
            if chat_id in include_chat_ids:
                include_ok = True
                print(f"[DEBUG] MATCHED folder chat: '{dialog.name}' ID: {chat_id}")
        # If searching specific chat names
        elif chats and chats != "all":
            if any(normalize_persian(c.lower()) in chat_name for c in chats):
                include_ok = True
        # If only folders specified but no chat IDs found (folder might be empty or not exist)
        elif folders and not include_chat_ids:
            include_ok = False

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

            text = normalize_persian(msg.message.lower())
            if any(k in text for k in keywords):
                results.append((dialog, msg))
                if len(results) >= max_results:
                    return results

    return results
