# desktop_app/main_gui.py
"""
Desktop GUI Application for Telegram Keyword Search.

A Tkinter-based desktop application that provides a graphical interface
for searching keywords across Telegram chats.

Version: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import asyncio
import threading
import webbrowser
import logging
from datetime import datetime, timezone
from typing import Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from utils import truncate_text, validate_date_format
from desktop_app.auth import DesktopAuth
from searcher import search_messages, parse_chat_filter, get_all_folders

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('desktop_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TelegramSearchApp:
    """Main desktop application window."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the application."""
        self.root = root
        self.root.title("Telegram Keyword Search")
        self.root.geometry("800x700")
        self.root.minsize(600, 500)
        
        # Authentication handler
        self.auth = DesktopAuth()
        self.is_logged_in = False
        self.user_name = None
        
        # Async loop for Telethon
        self.loop = asyncio.new_event_loop()
        self.async_thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.async_thread.start()
        
        # Build UI
        self._setup_styles()
        self._create_widgets()
        
        # Check existing session on startup
        self._run_async(self._check_session())
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _run_async_loop(self):
        """Run the async event loop in a separate thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def _run_async(self, coro):
        """Run a coroutine in the async thread."""
        return asyncio.run_coroutine_threadsafe(coro, self.loop)
    
    def _setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom button styles
        style.configure('Primary.TButton', font=('Segoe UI', 10))
        style.configure('Success.TButton', font=('Segoe UI', 10))
        style.configure('Danger.TButton', font=('Segoe UI', 10))
    
    def _create_widgets(self):
        """Create all UI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header frame
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="🔍 Telegram Keyword Search",
                                font=('Segoe UI', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Status label
        self.status_label = ttk.Label(header_frame, text="❌ Not logged in",
                                      font=('Segoe UI', 10))
        self.status_label.pack(side=tk.RIGHT)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Login tab
        self.login_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.login_frame, text="🔐 Login")
        self._create_login_tab()
        
        # Search tab
        self.search_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.search_frame, text="🔍 Search")
        self._create_search_tab()
        
        # Results tab
        self.results_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.results_frame, text="📋 Results")
        self._create_results_tab()
    
    def _create_login_tab(self):
        """Create the login tab."""
        # Phone input frame
        phone_frame = ttk.LabelFrame(self.login_frame, text="Step 1: Enter Phone Number", padding="10")
        phone_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(phone_frame, text="Phone (international format):").pack(anchor=tk.W)
        self.phone_entry = ttk.Entry(phone_frame, width=30, font=('Segoe UI', 11))
        self.phone_entry.pack(fill=tk.X, pady=5)
        self.phone_entry.insert(0, "+")
        
        self.send_code_btn = ttk.Button(phone_frame, text="📱 Send Code",
                                        command=self._on_send_code, style='Primary.TButton')
        self.send_code_btn.pack(pady=5)
        
        # Code input frame
        code_frame = ttk.LabelFrame(self.login_frame, text="Step 2: Enter Verification Code", padding="10")
        code_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(code_frame, text="Code from Telegram:").pack(anchor=tk.W)
        self.code_entry = ttk.Entry(code_frame, width=20, font=('Segoe UI', 11))
        self.code_entry.pack(fill=tk.X, pady=5)
        self.code_entry.config(state='disabled')
        
        self.verify_code_btn = ttk.Button(code_frame, text="✓ Verify Code",
                                          command=self._on_verify_code, style='Primary.TButton')
        self.verify_code_btn.pack(pady=5)
        self.verify_code_btn.config(state='disabled')
        
        # 2FA frame
        tfa_frame = ttk.LabelFrame(self.login_frame, text="Step 3: Two-Factor Authentication (if enabled)", padding="10")
        tfa_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(tfa_frame, text="2FA Password:").pack(anchor=tk.W)
        self.tfa_entry = ttk.Entry(tfa_frame, width=20, font=('Segoe UI', 11), show="*")
        self.tfa_entry.pack(fill=tk.X, pady=5)
        self.tfa_entry.config(state='disabled')
        
        self.verify_tfa_btn = ttk.Button(tfa_frame, text="🔐 Verify 2FA",
                                         command=self._on_verify_2fa, style='Primary.TButton')
        self.verify_tfa_btn.pack(pady=5)
        self.verify_tfa_btn.config(state='disabled')
        
        # Logout button
        logout_frame = ttk.Frame(self.login_frame)
        logout_frame.pack(fill=tk.X, pady=20)
        
        self.logout_btn = ttk.Button(logout_frame, text="🚪 Logout",
                                     command=self._on_logout, style='Danger.TButton')
        self.logout_btn.pack()
        self.logout_btn.config(state='disabled')
        
        # Login status message
        self.login_status = ttk.Label(self.login_frame, text="", font=('Segoe UI', 10))
        self.login_status.pack(pady=10)
    
    def _create_search_tab(self):
        """Create the search tab."""
        # Chats frame
        chats_frame = ttk.LabelFrame(self.search_frame, text="Chats & Folders to Search", padding="10")
        chats_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(chats_frame, text="Enter 'all', chat names, or folders with <folder_name> syntax:").pack(anchor=tk.W)
        ttk.Label(chats_frame, text="Examples: all | <Work>, <Friends> | chat1, chat2, <MyFolder>", 
                  font=('Segoe UI', 9, 'italic'), foreground='#666666').pack(anchor=tk.W)
        self.chats_entry = ttk.Entry(chats_frame, width=50, font=('Segoe UI', 11))
        self.chats_entry.pack(fill=tk.X, pady=5)
        self.chats_entry.insert(0, "all")
        
        # Folders button
        self.folders_btn = ttk.Button(chats_frame, text="📁 Show My Folders",
                                      command=self._on_show_folders)
        self.folders_btn.pack(pady=5)

        # Exclude frame
        exclude_frame = ttk.LabelFrame(self.search_frame, text="Exclude (Optional)", padding="10")
        exclude_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(exclude_frame, text="Exclude chats/folders using the same syntax (<folder_name>, chat):").pack(anchor=tk.W)
        ttk.Label(exclude_frame, text="Examples: <Muted>, Ads, <SpamFolder> | leave empty for none",
              font=('Segoe UI', 9, 'italic'), foreground='#666666').pack(anchor=tk.W)
        self.exclude_entry = ttk.Entry(exclude_frame, width=50, font=('Segoe UI', 11))
        self.exclude_entry.pack(fill=tk.X, pady=5)
        
        # Keywords frame
        keywords_frame = ttk.LabelFrame(self.search_frame, text="Keywords", padding="10")
        keywords_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(keywords_frame, text="Keywords (comma-separated):").pack(anchor=tk.W)
        self.keywords_entry = ttk.Entry(keywords_frame, width=50, font=('Segoe UI', 11))
        self.keywords_entry.pack(fill=tk.X, pady=5)
        
        # Date range frame
        date_frame = ttk.LabelFrame(self.search_frame, text="Date Range", padding="10")
        date_frame.pack(fill=tk.X, pady=(0, 10))
        
        dates_row = ttk.Frame(date_frame)
        dates_row.pack(fill=tk.X)
        
        # Start date
        start_frame = ttk.Frame(dates_row)
        start_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        ttk.Label(start_frame, text="Start Date (YYYY-MM-DD):").pack(anchor=tk.W)
        self.start_date_entry = ttk.Entry(start_frame, width=15, font=('Segoe UI', 11))
        self.start_date_entry.pack(fill=tk.X, pady=5)
        
        # End date
        end_frame = ttk.Frame(dates_row)
        end_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
        ttk.Label(end_frame, text="End Date (YYYY-MM-DD):").pack(anchor=tk.W)
        self.end_date_entry = ttk.Entry(end_frame, width=15, font=('Segoe UI', 11))
        self.end_date_entry.pack(fill=tk.X, pady=5)
        
        # Set default dates
        today = datetime.now()
        self.start_date_entry.insert(0, (today.replace(day=1)).strftime("%Y-%m-%d"))
        self.end_date_entry.insert(0, today.strftime("%Y-%m-%d"))
        
        # Search button
        btn_frame = ttk.Frame(self.search_frame)
        btn_frame.pack(pady=20)
        
        self.search_btn = ttk.Button(btn_frame, text="🔍 Search Messages",
                                     command=self._on_search, style='Primary.TButton')
        self.search_btn.pack()
        
        # Progress indicator
        self.progress_var = tk.StringVar(value="")
        self.progress_label = ttk.Label(self.search_frame, textvariable=self.progress_var,
                                        font=('Segoe UI', 10))
        self.progress_label.pack()
    
    def _create_results_tab(self):
        """Create the results tab."""
        # Results count
        self.results_count = ttk.Label(self.results_frame, text="No search performed yet",
                                       font=('Segoe UI', 10))
        self.results_count.pack(anchor=tk.W, pady=(0, 5))
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(
            self.results_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            height=25
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for styling
        self.results_text.tag_configure('header', font=('Segoe UI', 10, 'bold'), foreground='#0066cc')
        self.results_text.tag_configure('link', foreground='#0066cc', underline=True)
        self.results_text.tag_configure('snippet', foreground='#333333')
        
        # Bind click for links
        self.results_text.tag_bind('link', '<Button-1>', self._on_link_click)
        self.results_text.tag_bind('link', '<Enter>', lambda e: self.results_text.config(cursor='hand2'))
        self.results_text.tag_bind('link', '<Leave>', lambda e: self.results_text.config(cursor=''))
        
        # Store link URLs
        self.link_urls = {}
    
    async def _check_session(self):
        """Check for existing session on startup."""
        try:
            is_logged_in, user_name = await self.auth.load_session()
            self.root.after(0, lambda: self._update_login_state(is_logged_in, user_name))
        except Exception as e:
            logger.error(f"Session check error: {e}")
    
    def _update_login_state(self, is_logged_in: bool, user_name: Optional[str] = None):
        """Update UI based on login state."""
        self.is_logged_in = is_logged_in
        self.user_name = user_name
        
        if is_logged_in:
            self.status_label.config(text=f"✅ Logged in as: {user_name}")
            self.login_status.config(text=f"✅ Logged in as {user_name}")
            
            # Disable login fields
            self.phone_entry.config(state='disabled')
            self.send_code_btn.config(state='disabled')
            self.code_entry.config(state='disabled')
            self.verify_code_btn.config(state='disabled')
            self.tfa_entry.config(state='disabled')
            self.verify_tfa_btn.config(state='disabled')
            
            # Enable logout
            self.logout_btn.config(state='normal')
            
            # Enable search
            self.search_btn.config(state='normal')
        else:
            self.status_label.config(text="❌ Not logged in")
            self.login_status.config(text="Please log in to search your chats")
            
            # Enable login fields
            self.phone_entry.config(state='normal')
            self.send_code_btn.config(state='normal')
            
            # Disable others
            self.code_entry.config(state='disabled')
            self.verify_code_btn.config(state='disabled')
            self.tfa_entry.config(state='disabled')
            self.verify_tfa_btn.config(state='disabled')
            self.logout_btn.config(state='disabled')
            self.search_btn.config(state='disabled')
    
    def _on_send_code(self):
        """Handle send code button click."""
        phone = self.phone_entry.get().strip()
        
        if not phone.startswith('+') or len(phone) < 10:
            messagebox.showerror("Error", "Invalid phone number format.\nUse international format: +1234567890")
            return
        
        self.send_code_btn.config(state='disabled')
        self.login_status.config(text="📱 Sending code...")
        
        async def send():
            try:
                await self.auth.send_code(phone)
                self.root.after(0, self._on_code_sent)
            except Exception as e:
                self.root.after(0, lambda: self._on_code_error(str(e)))
        
        self._run_async(send())
    
    def _on_code_sent(self):
        """Handle successful code send."""
        self.login_status.config(text="✅ Code sent! Check your Telegram app.")
        self.code_entry.config(state='normal')
        self.verify_code_btn.config(state='normal')
        self.code_entry.focus_set()
    
    def _on_code_error(self, error: str):
        """Handle code send error."""
        self.send_code_btn.config(state='normal')
        self.login_status.config(text=f"❌ Error: {error}")
        messagebox.showerror("Error", f"Failed to send code:\n{error}")
    
    def _on_verify_code(self):
        """Handle verify code button click."""
        code = self.code_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        if not code:
            messagebox.showerror("Error", "Please enter the verification code.")
            return
        
        self.verify_code_btn.config(state='disabled')
        self.login_status.config(text="🔄 Verifying...")
        
        async def verify():
            success, message = await self.auth.verify_code(phone, code)
            if message == "2FA_REQUIRED":
                self.root.after(0, self._on_2fa_required)
            elif success:
                self.root.after(0, lambda: self._on_login_success(message))
            else:
                self.root.after(0, lambda: self._on_verify_error(message))
        
        self._run_async(verify())
    
    def _on_2fa_required(self):
        """Handle 2FA requirement."""
        self.login_status.config(text="🔐 2FA required. Enter your password.")
        self.tfa_entry.config(state='normal')
        self.verify_tfa_btn.config(state='normal')
        self.tfa_entry.focus_set()
    
    def _on_verify_2fa(self):
        """Handle 2FA verification."""
        password = self.tfa_entry.get().strip()
        
        if not password:
            messagebox.showerror("Error", "Please enter your 2FA password.")
            return
        
        self.verify_tfa_btn.config(state='disabled')
        self.login_status.config(text="🔄 Verifying 2FA...")
        
        async def verify():
            success, message = await self.auth.verify_2fa(password)
            if success:
                self.root.after(0, lambda: self._on_login_success(message))
            else:
                self.root.after(0, lambda: self._on_verify_error(message))
        
        self._run_async(verify())
    
    def _on_login_success(self, message: str):
        """Handle successful login."""
        async def get_name():
            client = self.auth.get_client()
            if client:
                me = await client.get_me()
                name = f"{me.first_name} {me.last_name or ''}".strip()
                self.root.after(0, lambda: self._update_login_state(True, name))
        
        self._run_async(get_name())
        messagebox.showinfo("Success", message)
    
    def _on_verify_error(self, message: str):
        """Handle verification error."""
        self.verify_code_btn.config(state='normal')
        self.verify_tfa_btn.config(state='normal')
        self.login_status.config(text=message)
        messagebox.showerror("Error", message)
    
    def _on_show_folders(self):
        """Show available Telegram folders."""
        if not self.is_logged_in:
            messagebox.showerror("Error", "Please log in first to see your folders.")
            return
        
        self.folders_btn.config(state='disabled')
        
        async def get_folders():
            try:
                client = self.auth.get_client()
                if not client:
                    self.root.after(0, lambda: messagebox.showerror("Error", "Session expired"))
                    return
                
                folders = await get_all_folders(client)
                self.root.after(0, lambda: self._display_folders(folders))
            except Exception as e:
                logger.error(f"Error getting folders: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to get folders: {e}"))
            finally:
                self.root.after(0, lambda: self.folders_btn.config(state='normal'))
        
        self._run_async(get_folders())
    
    def _display_folders(self, folders):
        """Display available folders in a dialog."""
        if not folders:
            messagebox.showinfo("Folders", "No folders found in your Telegram account.")
            return
        
        folder_list = "\n".join([f"• <{f}>" for f in folders])
        message = f"Your Telegram folders:\n\n{folder_list}\n\nUse <folder_name> syntax in the search field."
        messagebox.showinfo("📁 Your Folders", message)
    
    def _on_logout(self):
        """Handle logout button click."""
        if messagebox.askyesno("Confirm", "Are you sure you want to log out?"):
            async def logout():
                await self.auth.logout()
                self.root.after(0, lambda: self._update_login_state(False))
            
            self._run_async(logout())
    
    def _on_search(self):
        """Handle search button click."""
        if not self.is_logged_in:
            messagebox.showerror("Error", "Please log in first.")
            self.notebook.select(0)  # Switch to login tab
            return
        
        # Validate inputs
        chats_input = self.chats_entry.get().strip()
        exclude_input = self.exclude_entry.get().strip()
        keywords_input = self.keywords_entry.get().strip()
        start_date_str = self.start_date_entry.get().strip()
        end_date_str = self.end_date_entry.get().strip()
        
        if not keywords_input:
            messagebox.showerror("Error", "Please enter at least one keyword.")
            return
        
        if not validate_date_format(start_date_str):
            messagebox.showerror("Error", "Invalid start date format. Use YYYY-MM-DD.")
            return
        
        if not validate_date_format(end_date_str):
            messagebox.showerror("Error", "Invalid end date format. Use YYYY-MM-DD.")
            return
        
        # Parse inputs - handle folders with <folder_name> syntax
        folders = None
        chats = None
        
        if chats_input.lower() == "all":
            chats = "all"
        else:
            # Parse folders and chat names
            folders, chat_names = parse_chat_filter(chats_input)
            if chat_names:
                chats = chat_names
            elif not folders:
                chats = "all"  # Default to all if nothing specified
        
        keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

        # Parse exclude filters
        exclude_folders = None
        exclude_chats = None
        if exclude_input and exclude_input.lower() not in ("none", "no", "-"):
            ex_folders, ex_chats = parse_chat_filter(exclude_input)
            exclude_folders = ex_folders if ex_folders else None
            exclude_chats = ex_chats if ex_chats else None
        
        # Disable search while processing
        self.search_btn.config(state='disabled')
        
        # Show what we're searching
        search_desc = []
        if folders:
            search_desc.append(f"folders: {', '.join(folders)}")
        if chats and chats != "all":
            search_desc.append(f"chats: {', '.join(chats)}")
        elif chats == "all" and not folders:
            search_desc.append("all chats")
        if exclude_folders:
            search_desc.append(f"exclude folders: {', '.join(exclude_folders)}")
        if exclude_chats:
            search_desc.append(f"exclude chats: {', '.join(exclude_chats)}")
        self.progress_var.set(f"🔄 Searching {' + '.join(search_desc) if search_desc else 'all chats'}...")
        
        async def search():
            try:
                client = self.auth.get_client()
                if not client:
                    self.root.after(0, lambda: self._on_search_error("Session expired"))
                    return
                
                hits = await search_messages(
                    client,
                    keywords,
                    start_date,
                    end_date,
                    chats,
                    folders,
                    exclude_chats,
                    exclude_folders,
                )
                self.root.after(0, lambda: self._display_results(hits))
            except Exception as e:
                logger.error(f"Search error: {e}")
                self.root.after(0, lambda: self._on_search_error(str(e)))
        
        self._run_async(search())
    
    def _on_search_error(self, error: str):
        """Handle search error."""
        self.search_btn.config(state='normal')
        self.progress_var.set(f"❌ Error: {error}")
        messagebox.showerror("Search Error", error)
    
    def _display_results(self, hits):
        """Display search results."""
        self.search_btn.config(state='normal')
        self.progress_var.set(f"✅ Found {len(hits)} messages")
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        self.link_urls.clear()
        
        if not hits:
            self.results_count.config(text="No messages found matching your criteria.")
            self.results_text.insert(tk.END, "No messages found.\n\nTry:\n• Different keywords\n• Broader date range\n• Searching all chats")
            self.notebook.select(2)  # Switch to results tab
            return
        
        self.results_count.config(text=f"Found {len(hits)} messages (showing up to 50)")
        
        for i, (dialog, msg) in enumerate(hits[:50]):
            chat_name = dialog.name or "Unknown chat"
            snippet = (msg.message or "").replace("\n", " ")
            snippet = truncate_text(snippet, 200)
            date_str = msg.date.strftime("%Y-%m-%d %H:%M")
            
            # Generate message link
            entity = dialog.entity
            msg_link = None
            
            if hasattr(entity, 'username') and entity.username:
                msg_link = f"https://t.me/{entity.username}/{msg.id}"
            else:
                chat_id = entity.id
                if hasattr(entity, 'megagroup') or hasattr(entity, 'broadcast'):
                    msg_link = f"https://t.me/c/{chat_id}/{msg.id}"
            
            # Insert result
            self.results_text.insert(tk.END, f"📌 {chat_name} | {date_str}\n", 'header')
            self.results_text.insert(tk.END, f"{snippet}\n", 'snippet')
            
            if msg_link:
                link_tag = f"link_{i}"
                self.results_text.tag_configure(link_tag, foreground='#0066cc', underline=True)
                self.results_text.insert(tk.END, "🔗 Open Message", link_tag)
                self.results_text.tag_bind(link_tag, '<Button-1>', lambda e, url=msg_link: webbrowser.open(url))
                self.results_text.tag_bind(link_tag, '<Enter>', lambda e: self.results_text.config(cursor='hand2'))
                self.results_text.tag_bind(link_tag, '<Leave>', lambda e: self.results_text.config(cursor=''))
            
            self.results_text.insert(tk.END, "\n" + "-"*60 + "\n\n")
        
        # Switch to results tab
        self.notebook.select(2)
    
    def _on_link_click(self, event):
        """Handle link clicks in results."""
        pass  # Handled by tag-specific bindings
    
    def _on_close(self):
        """Handle window close."""
        async def cleanup():
            await self.auth.disconnect()
        
        self._run_async(cleanup())
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.root.destroy()


def run_gui():
    """Main entry point for the desktop GUI."""
    # Validate configuration
    if not Config.validate():
        messagebox.showerror("Configuration Error", 
                            "Missing TG_API_ID or TG_API_HASH.\n\nPlease create a .env file with your Telegram API credentials.")
        return
    
    root = tk.Tk()
    app = TelegramSearchApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
