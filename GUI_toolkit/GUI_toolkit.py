#!/usr/bin/env python3
"""
GUI Toolkit - Tony's Ultimate Utility GUI
YouTube | Stocks | Crypto | Weather | Downloaders | Search | Utilities | + More!
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os
import re
import hashlib
import base64
import subprocess
import datetime

try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class GUIToolkit:
    def __init__(self, root):
        self.root = root
        self.root.title("Tony's GUI Toolkit")
        self.root.geometry("800x1000")
        self.root.resizable(True, True)
        
        self.tools = {
            # Downloaders
            "YouTube Download": {"fields": ["Video URL"], "func": self.download_youtube, "cat": "Downloaders"},
            "YouTube MP3": {"fields": ["YouTube URL"], "func": self.download_youtube_mp3, "cat": "Downloaders"},
            "TikTok Download": {"fields": ["TikTok URL"], "func": self.download_tiktok, "cat": "Downloaders"},
            "Twitter/X Download": {"fields": ["Tweet/Video URL"], "func": self.download_twitter, "cat": "Downloaders"},
            "Image Downloader": {"fields": ["Image URL", "Save Name (optional)"], "func": self.download_image, "cat": "Downloaders"},
            
            # Finance
            "Stock Price": {"fields": ["Stock Symbol (e.g., AAPL)"], "func": self.get_stock_price, "cat": "Finance"},
            "Crypto Price": {"fields": ["Crypto Symbol (e.g., BTC)"], "func": self.get_crypto_price, "cat": "Finance"},
            "Currency Converter": {"fields": ["Amount", "From", "To"], "func": self.currency_converter, "cat": "Finance"},
            
            # Search
            "Web Search": {"fields": ["Search Query"], "func": self.web_search, "cat": "Search"},
            "Wikipedia": {"fields": ["Search Topic"], "func": self.wikipedia_search, "cat": "Search"},
            "Dictionary": {"fields": ["Word"], "func": self.dictionary_lookup, "cat": "Search"},
            
            # Weather
            "Weather": {"fields": ["City"], "func": self.get_weather, "cat": "Weather"},
            
            # Utilities
            "URL Shortener": {"fields": ["Long URL"], "func": self.url_shortener, "cat": "Utilities"},
            "QR Code": {"fields": ["Text to encode"], "func": self.qr_code, "cat": "Utilities"},
            "Base64 Encode": {"fields": ["Text"], "func": self.base64_encode, "cat": "Utilities"},
            "Base64 Decode": {"fields": ["Text"], "func": self.base64_decode, "cat": "Utilities"},
            "Hash Generator": {"fields": ["Text", "Type"], "func": self.hash_generator, "cat": "Utilities"},
            "Epoch Converter": {"fields": ["Unix Timestamp"], "func": self.epoch_converter, "cat": "Utilities"},
            "Case Converter": {"fields": ["Text", "Type"], "func": self.case_converter, "cat": "Utilities"},
            "Word Counter": {"fields": ["Text"], "func": self.word_counter, "cat": "Utilities"},
            "Lorem Ipsum": {"fields": ["Paragraphs"], "func": self.lorem_ipsum, "cat": "Utilities"},
            "Unit Converter": {"fields": ["Value", "Category", "From", "To"], "func": self.unit_converter, "cat": "Utilities"},
            
            # Info
            "My IP Address": {"fields": [], "func": self.get_ip, "cat": "Info"},
            "WhoIs Lookup": {"fields": ["Domain"], "func": self.whois_lookup, "cat": "Info"},
            "DNS Lookup": {"fields": ["Domain"], "func": self.dns_lookup, "cat": "Info"},
            
            # Network
            "Ping": {"fields": ["Host"], "func": self.ping_host, "cat": "Network"},
            "Port Scanner": {"fields": ["Host", "Start Port", "End Port"], "func": self.port_scanner, "cat": "Network"},
            "Speed Test": {"fields": [], "func": self.speed_test, "cat": "Network"},
            
            # Files
            "File Info": {"fields": ["File Path"], "func": self.file_info, "cat": "Files"},
            "File Compress": {"fields": ["File/Folder Path"], "func": self.file_compress, "cat": "Files"},
            "File Search": {"fields": ["Name", "Folder (optional)"], "func": self.file_search, "cat": "Files"},
            
            # Images
            "Image Converter": {"fields": ["Image Path", "Format (png/jpg)"], "func": self.image_converter, "cat": "Images"},
            "Image Resize": {"fields": ["Image Path", "Width", "Height"], "func": self.image_resize, "cat": "Images"},
            "Screenshot": {"fields": [], "func": self.take_screenshot, "cat": "Images"},
            
            # System
            "System Info": {"fields": [], "func": self.system_info, "cat": "System"},
            "Process List": {"fields": [], "func": self.process_list, "cat": "System"},
            "Kill Process": {"fields": ["Name or PID"], "func": self.kill_process, "cat": "System"},
        }
        
        self.selected_tool = tk.StringVar(value="YouTube Download")
        self.create_widgets()
        self.root.after(100, self.update_fields)
        
    def create_widgets(self):
        tk.Label(self.root, text="Tony's GUI Toolkit", font=("Helvetica", 24, "bold")).pack(pady=8)
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left - Tools
        left_frame = tk.LabelFrame(main_frame, text="Select Tool", padx=10, pady=10)
        left_frame.pack(side="left", fill="y", padx=(0, 5))
        
        # Scrollbar for tool list
        scrollbar = tk.Scrollbar(left_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Group by category
        categories = {}
        for tool, data in self.tools.items():
            cat = data.get("cat", "Other")
            categories.setdefault(cat, []).append(tool)
        
        self.tool_tree = ttk.Treeview(left_frame, show="tree", height=25, yscrollcommand=scrollbar.set)
        self.tool_tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tool_tree.yview)
        
        for cat in sorted(categories.keys()):
            cat_id = self.tool_tree.insert("", "end", text=cat, open=True)
            for tool in categories[cat]:
                self.tool_tree.insert(cat_id, "end", text=tool)
        
        self.tool_tree.bind("<<TreeviewSelect>>", lambda e: self.on_tool_select())
        
        # Right - Input/Output
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True)
        
        self.input_frame = tk.LabelFrame(right_frame, text="Input", padx=15, pady=10)
        self.input_frame.pack(fill="x", pady=(0, 5))
        self.input_entries = []
        
        tk.Button(right_frame, text="▶ Execute", font=("Helvetica", 14, "bold"), bg="#4CAF50", fg="white",
                 command=self.execute_tool, padx=30, pady=8).pack(pady=5)
        
        # Bind Enter key to execute
        self.root.bind('<Return>', lambda e: self.execute_tool())
        
        self.status_label = tk.Label(right_frame, text="", fg="blue", font=("Helvetica", 10))
        self.status_label.pack()
        
        output_frame = tk.LabelFrame(right_frame, text="Output", padx=10, pady=10)
        output_frame.pack(fill="both", expand=True, pady=(5, 0))
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=40, font=("Consolas", 11))
        self.output_text.pack(fill="both", expand=True)
        
        # Deps warning
        missing = []
        if not YTDLP_AVAILABLE: missing.append("yt-dlp")
        if not REQUESTS_AVAILABLE: missing.append("requests")
        if not QRCODE_AVAILABLE: missing.append("qrcode")
        if not PIL_AVAILABLE: missing.append("pillow")
        if missing:
            tk.Label(self.root, text=f"Missing: {', '.join(missing)}", fg="orange", font=("Helvetica", 9)).pack(pady=3)
    
    def on_tool_select(self):
        sel = self.tool_tree.selection()
        if sel:
            tool = self.tool_tree.item(sel[0])["text"]
            if tool in self.tools:
                self.selected_tool.set(tool)
                self.update_fields()
    
    def update_fields(self):
        try:
            tool = self.selected_tool.get()
            if tool not in self.tools:
                return
        except:
            return
        
        for w in self.input_frame.winfo_children():
            w.destroy()
        self.input_entries = []
        
        # Special handling for Unit Converter - dropdown menus
        if tool == "Unit Converter":
            self.setup_unit_converter_fields()
            return
        
        # Special handling for Currency Converter - dropdown menus
        if tool == "Currency Converter":
            self.setup_currency_converter_fields()
            return
        
        # Special handling for Hash Generator - dropdown
        if tool == "Hash Generator":
            self.setup_hash_generator_fields()
            return
        
        # Special handling for Case Converter - dropdown
        if tool == "Case Converter":
            self.setup_case_converter_fields()
            return
        
        # Special handling for Image Converter - format dropdown
        if tool == "Image Converter":
            self.setup_image_converter_fields()
            return
        
        for field in self.tools[self.selected_tool.get()]["fields"]:
            row = tk.Frame(self.input_frame)
            row.pack(fill="x", pady=(5, 0))
            tk.Label(row, text=field, font=("Helvetica", 11)).pack(anchor="w")
            entry = tk.Entry(row, font=("Helvetica", 11))
            entry.pack(fill="x", pady=3, ipady=4)
            entry.bind('<Control-v>', lambda e: (entry.delete(0, tk.END), entry.insert(0, self.root.clipboard_get()), 'break'))
            tk.Button(row, text="📋 Paste", font=("Helvetica", 9), command=lambda e=entry: self.paste_to(e)).pack(side="right", padx=(5, 0))
            self.input_entries.append(entry)
    
    def setup_unit_converter_fields(self):
        """Setup dropdown menus for unit converter"""
        # Unit categories and their units
        self.unit_categories = {
            "Length": ["meter", "kilometer", "centimeter", "millimeter", "mile", "yard", "foot", "inch"],
            "Weight": ["kilogram", "gram", "milligram", "pound", "ounce", "ton"],
            "Temperature": ["celsius", "fahrenheit", "kelvin"],
            "Volume": ["liter", "milliliter", "gallon", "quart", "pint", "cup", "fluid_ounce"],
            "Data": ["byte", "kilobyte", "megabyte", "gigabyte", "terabyte"],
            "Time": ["second", "minute", "hour", "day", "week"],
        }
        
        # Value input
        row = tk.Frame(self.input_frame)
        row.pack(fill="x", pady=(5, 0))
        tk.Label(row, text="Value", font=("Helvetica", 11)).pack(anchor="w")
        value_entry = tk.Entry(row, font=("Helvetica", 11))
        value_entry.pack(fill="x", pady=3, ipady=4)
        self.input_entries.append(value_entry)
        
        # Category dropdown
        row = tk.Frame(self.input_frame)
        row.pack(fill="x", pady=(5, 0))
        tk.Label(row, text="Category", font=("Helvetica", 11)).pack(anchor="w")
        cat_var = tk.StringVar(value="Length")
        cat_combo = ttk.Combobox(row, textvariable=cat_var, values=list(self.unit_categories.keys()), 
                                 font=("Helvetica", 11), state="readonly")
        cat_combo.pack(fill="x", pady=3, ipady=4)
        cat_combo.bind('<<ComboboxSelected>>', lambda e: self.update_unit_dropdowns(cat_var, from_var, to_var))
        self.input_entries.append(cat_var)  # Store the StringVar
        
        # From unit dropdown
        row = tk.Frame(self.input_frame)
        row.pack(fill="x", pady=(5, 0))
        tk.Label(row, text="From Unit", font=("Helvetica", 11)).pack(anchor="w")
        from_var = tk.StringVar(value="meter")
        from_combo = ttk.Combobox(row, textvariable=from_var, values=self.unit_categories["Length"],
                                  font=("Helvetica", 11), state="readonly")
        from_combo.pack(fill="x", pady=3, ipady=4)
        self.input_entries.append(from_var)
        
        # To unit dropdown
        row = tk.Frame(self.input_frame)
        row.pack(fill="x", pady=(5, 0))
        tk.Label(row, text="To Unit", font=("Helvetica", 11)).pack(anchor="w")
        to_var = tk.StringVar(value="kilometer")
        to_combo = ttk.Combobox(row, textvariable=to_var, values=self.unit_categories["Length"],
                                font=("Helvetica", 11), state="readonly")
        to_combo.pack(fill="x", pady=3, ipady=4)
        self.input_entries.append(to_var)
    
    def update_unit_dropdowns(self, cat_var, from_var, to_var):
        """Update unit dropdowns when category changes"""
        cat = cat_var.get()
        units = self.unit_categories.get(cat, [])
        
        # Find the comboboxes and update them
        for child in self.input_frame.winfo_children():
            for subchild in child.winfo_children():
                if isinstance(subchild, ttk.Combobox):
                    subchild['values'] = units
        
        # Set defaults for new category
        if len(units) >= 1:
            from_var.set(units[0])
        if len(units) >= 2:
            to_var.set(units[1])
    
    def setup_hash_generator_fields(self):
        """Setup dropdown for hash type"""
        # Text input
        row = tk.Frame(self.input_frame)
        row.pack(fill="x", pady=(5, 0))
        tk.Label(row, text="Text to Hash", font=("Helvetica", 11)).pack(anchor="w")
        text_entry = tk.Entry(row, font=("Helvetica", 11))
        text_entry.pack(fill="x", pady=3, ipady=4)
        text_entry.bind('<Control-v>', lambda e: (text_entry.delete(0, tk.END), text_entry.insert(0, self.root.clipboard_get()), 'break'))
        self.input_entries.append(text_entry)
        
        # Hash type dropdown
        row = tk.Frame(self.input_frame)
        row.pack(fill="x", pady=(5, 0))
        tk.Label(row, text="Hash Type", font=("Helvetica", 11)).pack(anchor="w")
        hash_var = tk.StringVar(value="sha256")
        hash_combo = ttk.Combobox(row, textvariable=hash_var, values=["md5", "sha1", "sha256", "sha512"],
                                   font=("Helvetica", 11), state="readonly")
        hash_combo.pack(fill="x", pady=3, ipady=4)
        self.input_entries.append(hash_var)
    
    def setup_case_converter_fields(self):
        """Setup dropdown for case type"""
        # Text input
        row = tk.Frame(self.input_frame)
        row.pack(fill="x", pady=(5, 0))
        tk.Label(row, text="Text", font=("Helvetica", 11)).pack(anchor="w")
        text_entry = tk.Entry(row, font=("Helvetica", 11))
        text_entry.pack(fill="x", pady=3, ipady=4)
        text_entry.bind('<Control-v>', lambda e: (text_entry.delete(0, tk.END), text_entry.insert(0, self.root.clipboard_get()), 'break'))
        self.input_entries.append(text_entry)
        
        # Case type dropdown
        row = tk.Frame(self.input_frame)
        row.pack(fill="x", pady=(5, 0))
        tk.Label(row, text="Convert To", font=("Helvetica", 11)).pack(anchor="w")
        case_var = tk.StringVar(value="lower")
        case_combo = ttk.Combobox(row, textvariable=case_var, values=["UPPER", "lower", "Title Case", "Sentence case"],
                                   font=("Helvetica", 11), state="readonly")
        case_combo.pack(fill="x", pady=3, ipady=4)
        self.input_entries.append(case_var)
    
    def setup_image_converter_fields(self):
        """Setup for image converter"""
        # File path
        row = tk.Frame(self.input_frame)
        row.pack(fill="x", pady=(5, 0))
        tk.Label(row, text="Image Path", font=("Helvetica", 11)).pack(anchor="w")
        path_entry = tk.Entry(row, font=("Helvetica", 11))
        path_entry.pack(fill="x", pady=3, ipady=4)
        path_entry.bind('<Control-v>', lambda e: (path_entry.delete(0, tk.END), path_entry.insert(0, self.root.clipboard_get()), 'break'))
        
        # Paste button
        tk.Button(row, text="📋 Paste", font=("Helvetica", 9), command=lambda: self.paste_to(path_entry)).pack(side="right", padx=(5, 0))
        self.input_entries.append(path_entry)
        
        # Format dropdown
        row = tk.Frame(self.input_frame)
        row.pack(fill="x", pady=(5, 0))
        tk.Label(row, text="Target Format", font=("Helvetica", 11)).pack(anchor="w")
        fmt_var = tk.StringVar(value="png")
        fmt_combo = ttk.Combobox(row, textvariable=fmt_var, values=["png", "jpg", "jpeg", "webp", "bmp"],
                                 font=("Helvetica", 11), state="readonly")
        fmt_combo.pack(fill="x", pady=3, ipady=4)
        self.input_entries.append(fmt_var)
    
    def setup_currency_converter_fields(self):
        """Setup dropdown menus for currency converter"""
        # Major currencies for dropdown
        self.currencies = [
            ("USD", "US Dollar"), ("EUR", "Euro"), ("GBP", "British Pound"), ("JPY", "Japanese Yen"),
            ("AUD", "Australian Dollar"), ("CAD", "Canadian Dollar"), ("CHF", "Swiss Franc"),
            ("CNY", "Chinese Yuan"), ("HKD", "Hong Kong Dollar"), ("NZD", "New Zealand Dollar"),
            ("SEK", "Swedish Krona"), ("KRW", "South Korean Won"), ("SGD", "Singapore Dollar"),
            ("NOK", "Norwegian Krone"), ("MXN", "Mexican Peso"), ("INR", "Indian Rupee"),
            ("RUB", "Russian Ruble"), ("ZAR", "South African Rand"), ("TRY", "Turkish Lira"),
            ("BRL", "Brazilian Real"), ("THB", "Thai Baht"), ("IDR", "Indonesian Rupiah"),
            ("MYR", "Malaysian Ringgit"), ("PHP", "Philippine Peso"), ("PLN", "Polish Zloty"),
            ("DKK", "Danish Krone"), ("ILS", "Israeli Shekel"), ("AED", "UAE Dirham"),
            ("SAR", "Saudi Riyal"), ("TWD", "Taiwan Dollar"), ("VND", "Vietnamese Dong"),
            ("EGP", "Egyptian Pound"), ("PKR", "Pakistani Rupee"), ("NGN", "Nigerian Naira"),
            ("KES", "Kenyan Shilling"), ("BGN", "Bulgarian Lev"), ("RON", "Romanian Leu"),
            ("CZK", "Czech Koruna"), ("HUF", "Hungarian Forint"), ("CLP", "Chilean Peso"),
            ("COP", "Colombian Peso"), ("PEN", "Peruvian Sol"), ("ARS", "Argentine Peso"),
            ("UAH", "Ukrainian Hryvnia"), ("BDT", "Bangladeshi Taka"), ("QAR", "Qatari Riyal"),
            ("KWD", "Kuwaiti Dinar"), ("BHD", "Bahraini Dinar"), ("OMR", "Omani Rial"),
            ("JOD", "Jordanian Dinar"), ("MAD", "Moroccan Dirham"), ("RWF", "Rwandan Franc"),
            ("ETB", "Ethiopian Birr"), ("GHS", "Ghanaian Cedi"), ("TZS", "Tanzanian Shilling"),
        ]
        
        # Currency values for dropdown
        curr_values = [c[0] for c in self.currencies]
        
        # Amount input
        row = tk.Frame(self.input_frame)
        row.pack(fill="x", pady=(5, 0))
        tk.Label(row, text="Amount", font=("Helvetica", 11)).pack(anchor="w")
        amount_entry = tk.Entry(row, font=("Helvetica", 11))
        amount_entry.pack(fill="x", pady=3, ipady=4)
        amount_entry.insert(0, "1")
        self.input_entries.append(amount_entry)
        
        # From currency dropdown
        row = tk.Frame(self.input_frame)
        row.pack(fill="x", pady=(5, 0))
        tk.Label(row, text="From Currency", font=("Helvetica", 11)).pack(anchor="w")
        from_var = tk.StringVar(value="USD")
        from_combo = ttk.Combobox(row, textvariable=from_var, values=curr_values,
                                 font=("Helvetica", 11), state="readonly")
        from_combo.pack(fill="x", pady=3, ipady=4)
        self.input_entries.append(from_var)
        
        # To currency dropdown
        row = tk.Frame(self.input_frame)
        row.pack(fill="x", pady=(5, 0))
        tk.Label(row, text="To Currency", font=("Helvetica", 11)).pack(anchor="w")
        to_var = tk.StringVar(value="EUR")
        to_combo = ttk.Combobox(row, textvariable=to_var, values=curr_values,
                               font=("Helvetica", 11), state="readonly")
        to_combo.pack(fill="x", pady=3, ipady=4)
        self.input_entries.append(to_var)
    
    def paste_to(self, entry):
        try:
            entry.delete(0, tk.END)
            entry.insert(0, self.root.clipboard_get())
        except:
            pass
    
    def execute_tool(self):
        tool = self.selected_tool.get()
        inputs = [e.get().strip() for e in self.input_entries]
        
        if not inputs or not inputs[0]:
            if self.tools[tool]["fields"]:
                messagebox.showwarning("Input Required", "Please fill in all fields")
                return
        
        self.output_text.delete(1.0, tk.END)
        self.status_label.config(text="Running...")
        
        thread = threading.Thread(target=self.tools[tool]["func"], args=inputs)
        thread.daemon = True
        thread.start()
    
    def append(self, text):
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
    
    def done(self):
        self.status_label.config(text="Done!")

    # ==================== DOWNLOADERS ====================
    def download_youtube(self, url):
        """Download YouTube video with quality selection"""
        if not YTDLP_AVAILABLE: 
            self.append("❌ yt-dlp missing. Run: pip install yt-dlp")
            self.done()
            return
        
        self.append(f"🔍 Fetching video info: {url}")
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.expanduser('~/Downloads/%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info first
                info = ydl.extract_info(url, download=False)
                
                self.append(f"\n📹 Video: {info.get('title', 'Unknown')}")
                self.append(f"   👤 Channel: {info.get('uploader', 'Unknown')}")
                self.append(f"   👁️ Views: {info.get('view_count', 0):,}")
                self.append(f"   ⏱️ Duration: {info.get('duration', 0)//60} min")
                self.append(f"   📅 Uploaded: {info.get('upload_date', 'Unknown')}")
                
                if info.get('tags'):
                    self.append(f"   🏷️ Tags: {', '.join(info['tags'][:5])}")
                
                self.append(f"\n⬇️ Downloading...")
                ydl.download([url])
                
            self.append("\n✅ Download complete!")
            self.append(f"   📁 Saved to: ~/Downloads/")
        except Exception as e: 
            self.append(f"❌ Error: {e}")
        self.done()

    def download_youtube_mp3(self, url):
        """Extract audio from YouTube as MP3"""
        if not YTDLP_AVAILABLE: 
            self.append("❌ yt-dlp missing. Run: pip install yt-dlp")
            self.done()
            return
        
        self.append(f"🔍 Fetching video: {url}")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.expanduser('~/Downloads/%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.append(f"📹 Converting to MP3: {info.get('title', 'Unknown')}")
                ydl.download([url])
                
            self.append("\n✅ MP3 extraction complete!")
            self.append(f"   📁 Saved to: ~/Downloads/")
        except Exception as e: 
            self.append(f"❌ Error: {e}")
        self.done()

    def download_tiktok(self, url):
        """Download TikTok video"""
        if not YTDLP_AVAILABLE: 
            self.append("❌ yt-dlp missing. Run: pip install yt-dlp")
            self.done()
            return
        
        self.append(f"🔍 Fetching TikTok: {url}")
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.expanduser('~/Downloads/tiktok_%(title)s.%(ext)s'),
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.append(f"📹 @{info.get('uploader', 'Unknown')}")
                if info.get('description'):
                    desc = info['description'][:100] + "..." if len(info['description']) > 100 else info['description']
                    self.append(f"   📝 {desc}")
                ydl.download([url])
            self.append("\n✅ TikTok download complete!")
        except Exception as e: 
            self.append(f"❌ Error: {e}")
        self.done()

    def download_twitter(self, url):
        """Download Twitter/X video"""
        if not YTDLP_AVAILABLE: 
            self.append("❌ yt-dlp missing. Run: pip install yt-dlp")
            self.done()
            return
        
        self.append(f"🔍 Fetching Twitter/X: {url}")
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.expanduser('~/Downloads/twitter_%(title)s.%(ext)s'),
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.append(f"📹 Tweet by: {info.get('uploader', 'Unknown')}")
                ydl.download([url])
            self.append("\n✅ Twitter/X download complete!")
        except Exception as e: 
            self.append(f"❌ Error: {e}")
        self.done()

    def download_image(self, url, name=""):
        """Download image from URL with metadata"""
        if not REQUESTS_AVAILABLE: 
            self.append("❌ requests missing. Run: pip install requests")
            self.done()
            return
        
        self.append(f"🔍 Fetching: {url}")
        try:
            r = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            r.raise_for_status()
            
            # Get content type and size
            content_type = r.headers.get('content-type', 'image/jpeg')
            size_bytes = len(r.content)
            
            ext_map = {
                'image/jpeg': '.jpg', 'image/png': '.png', 
                'image/gif': '.gif', 'image/webp': '.webp',
                'image/bmp': '.bmp', 'image/svg+xml': '.svg'
            }
            ext = ext_map.get(content_type, '.jpg')
            
            if not name:
                name = f"image_{hash(url) % 10000000}{ext}"
            
            path = os.path.expanduser(f"~/Downloads/{name}")
            with open(path, 'wb') as f:
                f.write(r.content)
            
            self.append(f"✅ Downloaded!")
            self.append(f"   📁 File: {name}")
            self.append(f"   📊 Size: {size_bytes:,} bytes ({size_bytes/1024:.1f} KB)")
            self.append(f"   🖼️ Type: {content_type}")
            self.append(f"   💾 Saved to: {path}")
        except Exception as e: 
            self.append(f"❌ Error: {e}")
        self.done()

    # ==================== FINANCE ====================
    def get_stock_price(self, sym):
        """Get comprehensive stock data from Yahoo Finance - supports US/international stocks"""
        if not REQUESTS_AVAILABLE: 
            self.append("❌ requests missing. Run: pip install requests")
            self.done()
            return
        
        # Popular stock symbols reference
        popular_stocks = {
            # Tech
            'AAPL': 'Apple', 'MSFT': 'Microsoft', 'GOOGL': 'Alphabet (Google)', 'GOOG': 'Alphabet',
            'AMZN': 'Amazon', 'META': 'Meta (Facebook)', 'NVDA': 'NVIDIA', 'AMD': 'AMD',
            'INTC': 'Intel', 'CRM': 'Salesforce', 'ORCL': 'Oracle', 'ADBE': 'Adobe',
            'NFLX': 'Netflix', 'PYPL': 'PayPal', 'UBER': 'Uber', 'LYFT': 'Lyft',
            'SNAP': 'Snapchat', 'TWTR': 'Twitter', 'SQ': 'Block', 'SHOP': 'Shopify',
            # Finance
            'JPM': 'JPMorgan', 'BAC': 'Bank of America', 'WFC': 'Wells Fargo', 'GS': 'Goldman Sachs',
            'MS': 'Morgan Stanley', 'C': 'Citigroup', 'V': 'Visa', 'MA': 'Mastercard',
            'AXP': 'American Express', 'BLK': 'BlackRock', 'SCHW': 'Charles Schwab',
            # Consumer
            'WMT': 'Walmart', 'TGT': 'Target', 'COST': 'Costco', 'HD': 'Home Depot',
            'LOW': "Lowe's", 'NKE': 'Nike', 'SBUX': 'Starbucks', 'MCD': "McDonald's",
            'DIS': 'Disney', 'CMCSA': 'Comcast', 'T': 'AT&T', 'VZ': 'Verizon',
            # Energy
            'XOM': 'Exxon', 'CVX': 'Chevron', 'COP': 'ConocoPhillips', 'SLB': 'Schlumberger',
            # Healthcare
            'JNJ': 'Johnson & Johnson', 'PFE': 'Pfizer', 'UNH': 'UnitedHealth', 'ABBV': 'AbbVie',
            'MRK': 'Merck', 'LLY': 'Eli Lilly', 'TMO': 'Thermo Fisher', 'ABT': 'Abbott',
            # Industrial
            'BA': 'Boeing', 'CAT': 'Caterpillar', 'GE': 'General Electric', 'MMM': '3M',
            # ETFs
            'SPY': 'S&P 500 ETF', 'QQQ': 'Nasdaq 100 ETF', 'DIA': 'Dow Jones ETF',
            'IWM': 'Russell 2000 ETF', 'VTI': 'Vanguard Total Stock', 'ARKK': 'ARK Innovation',
            # Crypto/Fintech
            'COIN': 'Coinbase', 'HOOD': 'Robinhood',
            # International
            'TSLA': 'Tesla', 'BABA': 'Alibaba', 'NIO': 'NIO (China)', 'TCEHY': 'Tencent',
            'SAP': 'SAP (Germany)', 'TSM': 'Taiwan Semiconductor', 'ASML': 'ASML (Netherlands)',
        }
        
        self.append(f"🔍 Fetching: {sym.upper()}")
        
        # Show company name if known
        if sym.upper() in popular_stocks:
            self.append(f"   {popular_stocks[sym.upper()]}")
        
        try:
            # Get quote data
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym.upper()}?interval=1d&range=5d"
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url, headers=headers, timeout=15)
            data = r.json()
            
            if not data.get('chart', {}).get('result'):
                self.append(f"❌ Stock not found: {sym}")
                self.done()
                return
            
            result = data['chart']['result'][0]
            meta = result['meta']
            
            # Get current price data
            price = meta.get('regularMarketPrice', 0)
            prev = meta.get('previousClose', 0)
            open_price = meta.get('regularMarketOpen', 0)
            high = meta.get('regularMarketDayHigh', 0)
            low = meta.get('regularMarketDayLow', 0)
            volume = meta.get('regularMarketVolume', 0)
            mkt_cap = meta.get('marketCap', 0)
            pe_ratio = meta.get('trailingPE', 0)
            
            change = price - prev
            pct_change = (change / prev * 100) if prev else 0
            
            self.append(f"\n📈 {meta.get('shortName', sym.upper())}")
            self.append(f"   {'='*40}")
            self.append(f"   💰 Price:      ${price:,.2f}")
            self.append(f"   📊 Change:     ${change:+.2f} ({pct_change:+.2f}%)")
            self.append(f"   🟢 Open:       ${open_price:,.2f}")
            self.append(f"   🔺 High:       ${high:,.2f}")
            self.append(f"   🔻 Low:        ${low:,.2f}")
            self.append(f"   📦 Volume:     {volume:,}")
            
            if mkt_cap:
                if mkt_cap > 1e12:
                    self.append(f"   🏢 Mkt Cap:    ${mkt_cap/1e12:.2f}T")
                elif mkt_cap > 1e9:
                    self.append(f"   🏢 Mkt Cap:    ${mkt_cap/1e9:.2f}B")
            
            if pe_ratio:
                self.append(f"   📉 P/E Ratio:  {pe_ratio:.2f}")
                
            # Get 5-day trend
            if result.get('indicators') and result['indicators'].get('quote'):
                closes = result['indicators']['quote'][0].get('close', [])
                closes = [c for c in closes if c is not None]
                if closes:
                    self.append(f"\n   📈 5-Day Trend:")
                    for i, c in enumerate(closes[-5:]):
                        self.append(f"      Day {i+1}: ${c:,.2f}")
                        
        except Exception as e: 
            self.append(f"❌ Error: {e}")
        self.done()

    def get_crypto_price(self, sym):
        """Get comprehensive crypto data from CoinGecko"""
        if not REQUESTS_AVAILABLE: 
            self.append("❌ requests missing. Run: pip install requests")
            self.done()
            return
        
        # Comprehensive crypto mapping (100+ coins)
        crypto_map = {
            # Top by Market Cap
            'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin',
            'XRP': 'ripple', 'ADA': 'cardano', 'SOL': 'solana',
            'DOGE': 'dogecoin', 'DOT': 'polkadot', 'TRX': 'tron',
            'MATIC': 'matic-network', 'LINK': 'chainlink', 'SHIB': 'shiba-inu',
            'LTC': 'litecoin', 'AVAX': 'avalanche-2', 'UNI': 'uniswap',
            'ATOM': 'cosmos', 'XLM': 'stellar', 'ETC': 'ethereum-classic',
            'XMR': 'monero', 'ALGO': 'algorand', 'VET': 'vechain',
            'FIL': 'filecoin', 'NEAR': 'near', 'HBAR': 'hedera-hashgraph',
            'APT': 'aptos', 'ARB': 'arbitrum', 'OP': 'optimism',
            'ICP': 'internet-computer', 'GRT': 'the-graph', 'SAND': 'the-sandbox',
            'MANA': 'decentraland', 'AXS': 'axie-infinity', 'AAVE': 'aave',
            'THETA': 'theta-token', 'EOS': 'eos', 'XTZ': 'tezos',
            'MKR': 'maker', 'SNX': 'synthetix-network-token', 'CRV': 'curve-dao-token',
            'LDO': 'lido-dao', 'QNT': 'quant-network', 'RUNE': 'thorchain',
            'KAVA': 'kava', 'MINA': 'mina-protocol', 'FLOW': 'flow',
            'CHZ': 'chiliz', 'XTZ': 'tezos', 'KCS': 'kucoin-shares',
            'RPL': 'rocket-pool', 'GMX': 'gmx', 'INJ': 'injective-protocol',
            'SUI': 'sui', 'SEI': 'sei-network', 'TIA': 'celestia',
            'PEPE': 'pepe', 'WIF': 'dogwifhat', 'BONK': 'bonk',
            'FET': 'fetch-ai', 'RNDR': 'render-token', 'IMX': 'immutable-x',
            'GALA': 'galxe', 'ENS': 'ethereum-name-service', '1INCH': '1inch',
            'ENJ': 'enjincoin', 'FTM': 'fantom', 'ZIL': 'zilliqa',
            'NEO': 'neo', 'KSM': 'kusama', 'ZEC': 'zcash',
            'DASH': 'dash', 'XEM': 'nem', 'COMP': 'compound-governance-token',
            'BAT': 'basic-attention-token', 'HOT': 'hydro-protocol', 'ZRX': '0x',
            'SUSHI': 'sushi', 'YFI': 'yearn-finance', 'BAL': 'balancer',
            'BAND': 'band-protocol', 'SKL': 'skale', 'ANKR': 'ankr',
            # Stablecoins
            'USDT': 'tether', 'USDC': 'usd-coin', 'DAI': 'dai', 
            'BUSD': 'binance-usd', 'TUSD': 'true-usd', 'USDP': 'paxos-standard',
            # Newly popular
            'WLD': 'worldcoin-wld', 'BLUR': 'blur', 'MAGIC': 'magic',
            'ARB': 'arbitrum', 'OP': 'optimism', 'MATIC': 'matic-network',
        }
        
        coin_id = crypto_map.get(sym.upper(), sym.lower())
        self.append(f"🔍 Fetching: {sym.upper()}")
        
        try:
            # Get detailed data
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&community_data=false&developer_data=false"
            r = requests.get(url, timeout=15)
            
            if r.status_code != 200:
                # Try simple price as fallback
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true"
                r = requests.get(url, timeout=15)
                d = r.json()
                if coin_id in d:
                    self.append(f"\n₿ {sym.upper()}")
                    self.append(f"   {'='*40}")
                    self.append(f"   💵 Price:     ${d[coin_id]['usd']:,.6f}")
                    self.append(f"   📊 24h:       {d[coin_id].get('usd_24h_change', 0):+.2f}%")
                    self.append(f"   📦 24h Vol:   ${d[coin_id].get('usd_24h_vol', 0):,.0f}")
                self.done()
                return
            
            d = r.json()
            
            # Extract data
            name = d.get('name', sym.upper())
            symbol = d.get('symbol', sym.upper()).upper()
            price = d.get('market_data', {}).get('current_price', {}).get('usd', 0)
            change_24h = d.get('market_data', {}).get('price_change_percentage_24h', 0)
            change_7d = d.get('market_data', {}).get('price_change_percentage_7d', 0)
            mkt_cap = d.get('market_data', {}).get('market_cap', {}).get('usd', 0)
            volume = d.get('market_data', {}).get('total_volume', {}).get('usd', 0)
            high_24h = d.get('market_data', {}).get('high_24h', {}).get('usd', 0)
            low_24h = d.get('market_data', {}).get('low_24h', {}).get('usd', 0)
            ath = d.get('market_data', {}).get('ath', {}).get('usd', 0)
            ath_change = d.get('market_data', {}).get('ath_change_percentage', {}).get('usd', 0)
            
            self.append(f"\n₿ {name} ({symbol})")
            self.append(f"   {'='*40}")
            self.append(f"   💵 Price:      ${price:,.6f}")
            self.append(f"   📊 24h:        {change_24h:+.2f}%")
            self.append(f"   📊 7d:         {change_7d:+.2f}%")
            self.append(f"   🔺 24h High:   ${high_24h:,.6f}")
            self.append(f"   🔻 24h Low:    ${low_24h:,.6f}")
            
            if mkt_cap:
                self.append(f"   🏢 Mkt Cap:    ${mkt_cap:,.0f}")
            if volume:
                self.append(f"   📦 Volume:     ${volume:,.0f}")
            if ath:
                self.append(f"   🏔️ All-Time-High: ${ath:,.2f}")
                self.append(f"      From ATH:    {ath_change:+.2f}%")
                
            # Rank
            if d.get('market_cap_rank'):
                self.append(f"   🏅 Rank:       #{d['market_cap_rank']}")
                
        except Exception as e: 
            self.append(f"❌ Error: {e}")
        self.done()

    def currency_converter(self, amt, frm, to):
        """Convert currency with rate info - supports 160+ currencies"""
        if not REQUESTS_AVAILABLE: 
            self.append("❌ requests missing. Run: pip install requests")
            self.done()
            return
        
        currency_names = {
            'USD': 'US Dollar', 'EUR': 'Euro', 'GBP': 'British Pound', 'JPY': 'Japanese Yen',
            'AUD': 'Australian Dollar', 'CAD': 'Canadian Dollar', 'CHF': 'Swiss Franc',
            'CNY': 'Chinese Yuan', 'HKD': 'Hong Kong Dollar', 'NZD': 'New Zealand Dollar',
            'SEK': 'Swedish Krona', 'KRW': 'South Korean Won', 'SGD': 'Singapore Dollar',
            'NOK': 'Norwegian Krone', 'MXN': 'Mexican Peso', 'INR': 'Indian Rupee',
            'RUB': 'Russian Ruble', 'ZAR': 'South African Rand', 'TRY': 'Turkish Lira',
            'BRL': 'Brazilian Real', 'TWD': 'Taiwan Dollar', 'DKK': 'Danish Krone',
            'PLN': 'Polish Zloty', 'THB': 'Thai Baht', 'IDR': 'Indonesian Rupiah',
            'HUF': 'Hungarian Forint', 'CZK': 'Czech Koruna', 'ILS': 'Israeli Shekel',
            'CLP': 'Chilean Peso', 'PHP': 'Philippine Peso', 'AED': 'UAE Dirham',
            'COP': 'Colombian Peso', 'SAR': 'Saudi Riyal', 'MYR': 'Malaysian Ringgit',
            'RON': 'Romanian Leu', 'BGN': 'Bulgarian Lev', 'PKR': 'Pakistani Rupee',
            'EGP': 'Egyptian Pound', 'VND': 'Vietnamese Dong', 'NGN': 'Nigerian Naira',
            'BDT': 'Bangladeshi Taka', 'ARS': 'Argentine Peso', 'UAH': 'Ukrainian Hryvnia',
            'PEN': 'Peruvian Sol', 'KZT': 'Kazakhstani Tenge', 'QAR': 'Qatari Riyal',
            'KWD': 'Kuwaiti Dinar', 'BHD': 'Bahraini Dinar', 'OMR': 'Omani Rial',
        }
        
        self.append(f"🔍 Converting: {amt} {frm.upper()} → {to.upper()}")
        
        if frm.upper() in currency_names:
            self.append(f"   {currency_names[frm.upper()]}")
        if to.upper() in currency_names:
            self.append(f"   → {currency_names[to.upper()]}")
        
        try:
            # Try exchangerate-api.com (free, reliable)
            url = f"https://api.exchangerate-api.com/v4/latest/{frm.upper()}"
            r = requests.get(url, timeout=15)
            
            if r.status_code == 200:
                d = r.json()
                rates = d.get('rates', {})
                
                if to.upper() in rates:
                    rate = rates[to.upper()]
                    result = float(amt) * rate
                    
                    self.append(f"\n💱 Conversion Result")
                    self.append(f"   {'='*50}")
                    self.append(f"   💵 {amt} {frm.upper()} = {result:.2f} {to.upper()}")
                    self.append(f"\n   📊 Exchange Rate:")
                    self.append(f"      1 {frm.upper()} = {rate:.6f} {to.upper()}")
                    self.append(f"      1 {to.upper()} = {1/rate:.6f} {frm.upper()}")
                    
                    # Show top exchange rates
                    self.append(f"\n   📋 Top Exchange Rates:")
                    top_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'HKD', 'SGD', 'INR', 'KRW', 'MXN', 'BRL']
                    for curr in top_currencies:
                        if curr in rates and curr != frm.upper():
                            curr_name = currency_names.get(curr, curr)
                            self.append(f"      {curr}: {rates[curr]:.4f} ({curr_name})")
                else:
                    self.append(f"❌ Currency not found: {to.upper()}")
            else:
                self.append(f"❌ API error: {r.status_code}")
        except Exception as e: 
            self.append(f"❌ Error: {e}")
        self.done()

    # ==================== SEARCH ====================
    def web_search(self, q):
        """Web search with detailed results"""
        if not REQUESTS_AVAILABLE: 
            self.append("❌ requests missing. Run: pip install requests")
            self.done()
            return
        
        self.append(f"🔍 Searching: {q}")
        
        try:
            r = requests.get(
                f"https://html.duckduckgo.com/html/?q={q.replace(' ', '+')}", 
                headers={'User-Agent': 'Mozilla/5.0'}, 
                timeout=15
            )
            
            results = re.findall(r'<a class="result__a" href="([^"]+)"[^>]*>(.+?)</a>', r.text)
            
            if not results:
                self.append("❌ No results found")
                self.done()
                return
            
            self.append(f"\n📋 Search Results for '{q}'")
            self.append(f"   {'='*50}\n")
            
            for i, (link, title) in enumerate(results[:15], 1):
                title = re.sub(r'<[^>]+>', '', title).strip()
                # Get snippet
                snippet_match = re.search(r'class="result__snippet"[^>]*>(.+?)</a>', r.text)
                
                self.append(f"{i}. {title}")
                self.append(f"   🔗 {link[:70]}...")
                self.append("")
            
            self.append(f"\n📊 Found {len(results)} results")
            
        except Exception as e: 
            self.append(f"❌ Error: {e}")
        self.done()

    def wikipedia_search(self, topic):
        """Comprehensive Wikipedia search with full details"""
        if not REQUESTS_AVAILABLE: 
            self.append("❌ requests missing. Run: pip install requests")
            self.done()
            return
        
        self.append(f"🔍 Searching Wikipedia: {topic}")
        
        try:
            # Get summary
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic.replace(' ', '_')}"
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            
            if r.status_code != 200:
                self.append(f"❌ Wikipedia article not found: {topic}")
                self.done()
                return
            
            d = r.json()
            
            self.append(f"\n📖 {d.get('title', topic)}")
            self.append(f"   {'='*50}")
            
            if d.get('description'):
                self.append(f"\n📝 {d['description']}")
            
            self.append(f"\n{d.get('extract', 'No summary available.')}")
            
            # Get full content
            try:
                content_url = f"https://en.wikipedia.org/api/rest_v1/page/mobile-sections/{topic.replace(' ', '_')}"
                r2 = requests.get(content_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
                if r2.status_code == 200:
                    content = r2.json()
                    if content.get('lead'):
                        sections = content.get('sections', [])[:5]
                        if sections:
                            self.append(f"\n📑 Key Sections:")
                            for s in sections:
                                self.append(f"   • {s.get('text', '')[:60]}...")
            except:
                pass
            
            # Links
            if d.get('content_urls'):
                self.append(f"\n🔗 Read more:")
                self.append(f"   {d['content_urls']['desktop']['page']}")
                
        except Exception as e: 
            self.append(f"❌ Error: {e}")
        self.done()

    def dictionary_lookup(self, word):
        """Comprehensive dictionary with definitions, synonyms, phonetics"""
        if not REQUESTS_AVAILABLE: 
            self.append("❌ requests missing. Run: pip install requests")
            self.done()
            return
        
        self.append(f"🔍 Looking up: {word}")
        
        try:
            r = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", timeout=15)
            
            if r.status_code != 200:
                self.append(f"❌ Word not found: {word}")
                self.done()
                return
            
            data = r.json()
            if not data:
                self.append(f"❌ No data found: {word}")
                self.done()
                return
            
            d = data[0]
            
            self.append(f"\n📖 {d.get('word', word).upper()}")
            self.append(f"   {'='*50}")
            
            # Phonetics
            if d.get('phonetic'):
                self.append(f"\n🔊 Phonetic: {d['phonetic']}")
            elif d.get('phonetics'):
                for p in d['phonetics']:
                    if p.get('text'):
                        self.append(f"\n🔊 Phonetic: {p['text']}")
                        break
            
            # Meanings
            for idx, meaning in enumerate(d.get('meanings', []), 1):
                pos = meaning.get('partOfSpeech', '')
                self.append(f"\n📌 {pos.upper()}")
                
                # Definitions
                for i, defn in enumerate(meaning.get('definitions', [])[:3], 1):
                    self.append(f"   {i}. {defn.get('definition', '')}")
                    
                    if defn.get('example'):
                        self.append(f'      Example: "{defn["example"]}"')
                    
                    # Synonyms
                    if defn.get('synonyms'):
                        syns = defn['synonyms'][:5]
                        self.append(f'      Synonyms: {", ".join(syns)}')
                
                # Antonyms
                if meaning.get('antonyms'):
                    ants = meaning['antonyms'][:5]
                    self.append(f"      Antonyms: {', '.join(ants)}")
            
            # Origin
            if d.get('origin'):
                self.append(f"\n📜 Etymology:")
                self.append(f"   {d['origin'][:200]}...")
                
        except Exception as e: 
            self.append(f"❌ Error: {e}")
        self.done()

    # ==================== WEATHER ====================
    def get_weather(self, city):
        """Comprehensive weather data"""
        if not REQUESTS_AVAILABLE: 
            self.append("❌ requests missing. Run: pip install requests")
            self.done()
            return
        
        self.append(f"🔍 Getting weather for: {city}")
        
        try:
            # Geocode
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city.replace(' ', '%20')}&count=1"
            r = requests.get(geo_url, timeout=10)
            data = r.json()
            
            if not data.get('results'):
                self.append(f"❌ City not found: {city}")
                self.done()
                return
            
            loc = data['results'][0]
            lat, lon = loc['latitude'], loc['longitude']
            city_name = loc.get('name', city)
            country = loc.get('country', '')
            region = loc.get('admin1', '')
            
            # Get comprehensive weather
            weather_url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                f"&current_weather=true"
                f"&hourly=temperature_2m,relativehumidity_2m,apparent_temperature,precipitation_probability"
                f"&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset,uv_index_max"
                f"&temperature_unit=fahrenheit"
                f"&timezone=auto"
            )
            
            r = requests.get(weather_url, timeout=15)
            w = r.json()
            
            current = w.get('current_weather', {})
            hourly = w.get('hourly', {})
            daily = w.get('daily', {})
            
            # Weather codes
            codes = {
                0: "☀️ Clear sky", 1: "🌤️ Mainly clear", 2: "⛅ Partly cloudy", 
                3: "☁️ Overcast", 45: "🌫️ Foggy", 48: "🌫️ Depositing rime fog",
                51: "🌧️ Light drizzle", 53: "🌧️ Drizzle", 55: "🌧️ Dense drizzle",
                61: "🌧️ Rain", 63: "🌧️ Moderate rain", 65: "🌧️ Heavy rain",
                71: "❄️ Snow", 73: "❄️ Snow", 75: "❄️ Heavy snow",
                80: "🌦️ Rain showers", 81: "🌦️ Rain showers", 82: "🌦️ Heavy showers",
                95: "⛈️ Thunderstorm", 96: "⛈️ Thunderstorm with hail",
            }
            
            code = current.get('weathercode', 0)
            
            self.append(f"\n🌤️ Weather for {city_name}, {region}, {country}")
            self.append(f"   {'='*50}")
            self.append(f"\n   {codes.get(code, f'Code {code}')}")
            self.append(f"   🌡️ Temperature: {current.get('temperature', '?')}°F")
            self.append(f"   💨 Wind: {current.get('windspeed', '?')} km/h")
            self.append(f"   🧭 Wind Direction: {current.get('winddirection', '?')}°")
            
            # Hourly data (next few hours)
            if hourly.get('temperature_2m'):
                self.append(f"\n📊 Next Hours:")
                for i in range(min(6, len(hourly['temperature_2m']))):
                    temp = hourly['temperature_2m'][i]
                    time = hourly['time'][i][-5:]
                    self.append(f"      {time}: {temp}°F")
            
            # Daily forecast
            if daily.get('temperature_2m_max'):
                self.append(f"\n📅 7-Day Forecast:")
                for i in range(min(7, len(daily['temperature_2m_max']))):
                    max_temp = daily['temperature_2m_max'][i]
                    min_temp = daily['temperature_2m_min'][i]
                    date = daily['time'][i][-5:]
                    self.append(f"      {date}: {min_temp:.0f}° - {max_temp:.0f}°F")
            
            # UV Index
            if daily.get('uv_index_max') and daily['uv_index_max'][0]:
                uv = daily['uv_index_max'][0]
                uv_level = "Low" if uv < 3 else "Moderate" if uv < 6 else "High" if uv < 8 else "Very High" if uv < 11 else "Extreme"
                self.append(f"\n   ☀️ UV Index: {uv} ({uv_level})")
                
        except Exception as e: 
            self.append(f"❌ Error: {e}")
        self.done()

    # ==================== UTILITIES ====================
    def url_shortener(self, url):
        if not REQUESTS_AVAILABLE: self.append("❌ requests missing"); self.done(); return
        try:
            r = requests.get("https://is.gd/create.php", params={'format': 'json', 'url': url}, timeout=10)
            d = r.json()
            self.append(f"🔗 {d.get('shorturl', 'Failed')}")
        except Exception as e: self.append(f"❌ {e}")
        self.done()

    def qr_code(self, text):
        if not QRCODE_AVAILABLE: self.append("❌ qrcode missing"); self.done(); return
        try:
            qr = qrcode.QRCode(version=1)
            qr.add_data(text)
            qr.make(fit=True)
            path = os.path.expanduser(f"~/Downloads/qr_{hash(text) % 100000}.png")
            qr.make_image().save(path)
            self.append(f"✅ Saved: {path}")
        except Exception as e: self.append(f"❌ {e}")
        self.done()

    def base64_encode(self, t): self.append(base64.b64encode(t.encode()).decode()); self.done()
    def base64_decode(self, t):
        try: self.append(base64.b64decode(t.encode()).decode())
        except: self.append("❌ Invalid base64")
        self.done()

    def hash_generator(self, text, typ="sha256"):
        h = hashlib.new(typ.lower())
        h.update(text.encode())
        self.append(f"✅ {typ.upper()}:\n{h.hexdigest()}")
        self.done()

    def epoch_converter(self, ts):
        try:
            t = int(ts)
            if t > 1000000000000: t //= 1000
            dt = datetime.datetime.fromtimestamp(t)
            self.append(f"📅 {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e: self.append(f"❌ {e}")
        self.done()

    def case_converter(self, text, typ):
        typ = typ.lower()
        if typ in ["upper"]: r = text.upper()
        elif typ in ["lower"]: r = text.lower()
        elif typ in ["title case"]: r = text.title()
        elif typ in ["sentence case"]: r = text.capitalize()
        else: r = text
        self.append(r)
        self.done()

    def word_counter(self, text):
        self.append(f"Words: {len(text.split())}\nChars: {len(text)}\nLines: {len(text.split(chr(10)))}")
        self.done()

    def lorem_ipsum(self, n):
        if not REQUESTS_AVAILABLE: self.append("❌ requests missing"); self.done(); return
        try:
            r = requests.get(f"https://loripsum.net/api/{n}/plaintext", timeout=10)
            self.append(r.text)
        except Exception as e: self.append(f"❌ {e}")
        self.done()

    def unit_converter(self, val, cat, frm, to):
        # All conversion factors (to base unit)
        conversions = {
            # Length (base: meter)
            "meter": 1, "kilometer": 1000, "centimeter": 0.01, "millimeter": 0.001,
            "mile": 1609.344, "yard": 0.9144, "foot": 0.3048, "inch": 0.0254,
            # Weight (base: kilogram)
            "kilogram": 1, "gram": 0.001, "milligram": 0.000001,
            "pound": 0.453592, "ounce": 0.0283495, "ton": 1000,
            # Volume (base: liter)
            "liter": 1, "milliliter": 0.001,
            "gallon": 3.78541, "quart": 0.946353, "pint": 0.473176, "cup": 0.236588, "fluid_ounce": 0.0295735,
            # Data (base: byte)
            "byte": 1, "kilobyte": 1024, "megabyte": 1048576, "gigabyte": 1073741824, "terabyte": 1099511627776,
            # Time (base: second)
            "second": 1, "minute": 60, "hour": 3600, "day": 86400, "week": 604800,
        }
        
        # Temperature conversions (special)
        def c_to_f(c): return c * 9/5 + 32
        def f_to_c(f): return (f - 32) * 5/9
        def c_to_k(c): return c + 273.15
        def k_to_c(k): return k - 273.15
        
        try:
            v = float(val)
            frm = frm.lower().replace(" ", "_")
            to = to.lower().replace(" ", "_")
            
            # Temperature special handling
            if cat == "Temperature":
                if frm == "celsius" and to == "fahrenheit": r = c_to_f(v)
                elif frm == "fahrenheit" and to == "celsius": r = f_to_c(v)
                elif frm == "celsius" and to == "kelvin": r = c_to_k(v)
                elif frm == "kelvin" and to == "celsius": r = k_to_c(v)
                elif frm == "fahrenheit" and to == "kelvin": r = c_to_k(f_to_c(v))
                elif frm == "kelvin" and to == "fahrenheit": r = c_to_f(k_to_c(v))
                elif frm == to: r = v
                else: self.append("❌ Unsupported temperature"); self.done(); return
            else:
                # Standard conversion through base unit
                if frm in conversions and to in conversions:
                    base = v * conversions[frm]
                    r = base / conversions[to]
                else:
                    self.append("❌ Invalid units"); self.done(); return
            
            self.append(f"✅ {val} {frm} = {r:.6f} {to}")
        except Exception as e: self.append(f"❌ Error: {e}")
        self.done()

    # ==================== INFO ====================
    def get_ip(self):
        if not REQUESTS_AVAILABLE: self.append("❌ requests missing"); self.done(); return
        try:
            ip = requests.get('https://api.ipify.org?format=json', timeout=10).json().get('ip', '?')
            self.append(f"🌐 Your IP: {ip}")
            try: loc = requests.get(f'https://ipapi.co/{ip}/json/', timeout=10).json()
            except: loc = {}
            if loc: self.append(f"📍 {loc.get('city','')}, {loc.get('region','')}, {loc.get('country_name','')}")
        except Exception as e: self.append(f"❌ {e}")
        self.done()

    def whois_lookup(self, domain):
        if not REQUESTS_AVAILABLE: self.append("❌ requests missing"); self.done(); return
        try:
            r = requests.get(f"https://who.is/whois/{domain}", headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            for k in ['Registrar', 'Created Date', 'Expiry Date']:
                m = re.search(f'{k}:\\s*(.+?)(?:\\n|$)', r.text, re.I)
                if m: self.append(f"{k}: {m.group(1).strip()}")
        except Exception as e: self.append(f"❌ {e}")
        self.done()

    def dns_lookup(self, domain):
        """Comprehensive DNS lookup for multiple record types"""
        if not REQUESTS_AVAILABLE: 
            self.append("❌ requests missing. Run: pip install requests")
            self.done()
            return
        
        self.append(f"🔍 DNS Lookup: {domain}")
        
        # Common DNS record types
        record_types = {
            'A': 'IPv4 Address',
            'AAAA': 'IPv6 Address', 
            'CNAME': 'Canonical Name',
            'MX': 'Mail Exchange',
            'TXT': 'Text Record',
            'NS': 'Name Server',
            'SOA': 'Start of Authority',
            'PTR': 'Pointer Record'
        }
        
        try:
            for rtype, rname in record_types.items():
                try:
                    url = f"https://dns.google/resolve?name={domain}&type={rtype}"
                    r = requests.get(url, timeout=10)
                    data = r.json()
                    
                    if data.get('Answer'):
                        self.append(f"\n📋 {rname} ({rtype}):")
                        for ans in data['Answer']:
                            self.append(f"   {ans['data']}")
                    elif data.get('Authority'):
                        self.append(f"\n📋 {rname} ({rtype}):")
                        for ans in data['Authority']:
                            self.append(f"   NS: {ans['data']}")
                except:
                    pass
            
            # Also try Cloudflare DNS
            self.append(f"\n🔄 Trying alternative DNS (Cloudflare)...")
            try:
                url = f"https://cloudflare-dns.com/dns-query?name={domain}&type=A"
                r = requests.get(url, timeout=10, headers={'accept': 'application/dns-json'})
                if r.status_code == 200:
                    data = r.json()
                    if data.get('Answer'):
                        self.append(f"\n📋 Cloudflare Results:")
                        for ans in data['Answer'][:5]:
                            self.append(f"   {ans['data']}")
            except:
                pass
                
        except Exception as e: 
            self.append(f"❌ Error: {e}")
        self.done()

    # ==================== NETWORK ====================
    def ping_host(self, host):
        """Ping host with detailed statistics"""
        self.append(f"🔴 Pinging {host}...")
        
        try:
            # Do 4 pings
            p = subprocess.run(['ping', '-c', '4', host], capture_output=True, text=True, timeout=15)
            
            # Parse output
            lines = p.stdout.split('\n')
            
            self.append(f"\n📊 Ping Results for {host}")
            self.append(f"   {'='*50}")
            
            for line in lines:
                if "PING" in line or "packets" in line or "rtt" in line or "min/avg/max" in line:
                    self.append(f"   {line}")
            
            # Extract stats
            stats_match = re.search(r'(\d+) packets transmitted, (\d+) received', p.stdout)
            if stats_match:
                sent, received = stats_match.groups()
                loss = (int(sent) - int(received)) / int(sent) * 100
                self.append(f"\n   📦 Packets: {sent} sent, {received} received, {loss:.0f}% loss")
            
            # RTT stats
            rtt_match = re.search(r'min/avg/max[/\w]* = ([\d.]+)/([\d.]+)/([\d.]+)', p.stdout)
            if rtt_match:
                min_rtt, avg_rtt, max_rtt = rtt_match.groups()
                self.append(f"   ⏱️ RTT: min={min_rtt}ms, avg={avg_rtt}ms, max={max_rtt}ms")
                
        except Exception as e: 
            self.append(f"❌ Error: {e}")
        self.done()

    def port_scanner(self, host, start=1, end=100):
        """Scan ports with service detection"""
        import socket
        
        # Common ports and services
        common_ports = {
            21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 
            53: 'DNS', 80: 'HTTP', 110: 'POP3', 143: 'IMAP',
            443: 'HTTPS', 465: 'SMTPS', 587: 'SMTP', 993: 'IMAPS',
            995: 'POP3S', 3306: 'MySQL', 5432: 'PostgreSQL',
            6379: 'Redis', 8080: 'HTTP-Alt', 8443: 'HTTPS-Alt',
            27017: 'MongoDB'
        }
        
        self.append(f"🔍 Scanning {host} (ports {start}-{end})...")
        
        open_ports = []
        
        try:
            for port in range(int(start), min(int(end)+1, 10000)):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.5)
                    result = s.connect_ex((host, port))
                    
                    if result == 0:
                        service = common_ports.get(port, "Unknown")
                        open_ports.append((port, service))
                        self.append(f"   ✅ Port {port}/TCP - {service}")
                    
                    s.close()
                except:
                    pass
                    
            if not open_ports:
                self.append("   ❌ No open ports found in range")
            else:
                self.append(f"\n📊 Summary: {len(open_ports)} open port(s) found")
                
        except Exception as e: 
            self.append(f"❌ Error: {e}")
        self.done()

    def speed_test(self):
        """Internet speed test with multiple measurements"""
        if not REQUESTS_AVAILABLE: 
            self.append("❌ requests missing. Run: pip install requests")
            self.done()
            return
        
        self.append("🌐 Running Speed Test...")
        self.append(f"   {'='*50}")
        
        try:
            # Download test
            self.append("\n⬇️ Download Test...")
            sizes = [1000000, 5000000, 10000000]
            speeds = []
            
            for size in sizes:
                url = f"https://speed.cloudflare.com/__down?bytes={size}"
                start = time.time()
                r = requests.get(url, timeout=30)
                duration = time.time() - start
                speed_mbps = (len(r.content) * 8) / duration / 1024 / 1024
                speeds.append(speed_mbps)
                self.append(f"   {size/1024/1024:.1f} MB downloaded in {duration:.2f}s = {speed_mbps:.2f} Mbps")
            
            avg_down = sum(speeds) / len(speeds)
            self.append(f"\n   📊 Average Download: {avg_down:.2f} Mbps")
            
            # Quick upload estimate (using latency)
            start = time.time()
            r = requests.get("https://speed.cloudflare.com/__up", timeout=10)
            upload_time = time.time() - start
            
            self.append(f"   📤 Upload estimate: ~{1/upload_time:.2f} Mbps (based on latency)")
            
            # Latency test
            latencies = []
            for _ in range(5):
                start = time.time()
                requests.get("https://speed.cloudflare.com/__down?bytes=1000", timeout=5)
                latencies.append((time.time() - start) * 1000)
            
            avg_latency = sum(latencies) / len(latencies)
            self.append(f"   ⏱️ Latency: {avg_latency:.0f} ms (avg)")
            
        except Exception as e: 
            self.append(f"❌ Error: {e}")
        self.done()

    # ==================== FILES ====================
    def file_info(self, path):
        """Get comprehensive file information including checksums"""
        import hashlib
        
        try:
            p = os.path.expanduser(path)
            
            if not os.path.exists(p):
                self.append(f"❌ File not found: {path}")
                self.done()
                return
            
            st = os.stat(p)
            basename = os.path.basename(p)
            
            self.append(f"\n📄 File: {basename}")
            self.append(f"   {'='*50}")
            
            # Basic info
            self.append(f"\n📋 Basic Info:")
            self.append(f"   Path: {os.path.abspath(p)}")
            self.append(f"   Type: {'Directory' if os.path.isdir(p) else 'File'}")
            self.append(f"   Size: {st.st_size:,} bytes ({st.st_size/1024:.2f} KB)")
            
            # Human readable size
            size = st.st_size
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024:
                    self.append(f"          {size:.2f} {unit}")
                    break
                size /= 1024
            
            # Timestamps
            self.append(f"\n⏰ Timestamps:")
            self.append(f"   Created:  {datetime.datetime.fromtimestamp(st.st_ctime)}")
            self.append(f"   Modified: {datetime.datetime.fromtimestamp(st.st_mtime)}")
            self.append(f"   Accessed: {datetime.datetime.fromtimestamp(st.st_atime)}")
            
            # Permissions
            mode = st.st_mode
            perms = []
            perms.append('r' if mode & 0o400 else '-')
            perms.append('w' if mode & 0o200 else '-')
            perms.append('x' if mode & 0o100 else '-')
            perms.append('r' if mode & 0o040 else '-')
            perms.append('w' if mode & 0o020 else '-')
            perms.append('x' if mode & 0o010 else '-')
            perms.append('r' if mode & 0o004 else '-')
            perms.append('w' if mode & 0o002 else '-')
            perms.append('x' if mode & 0o001 else '-')
            
            self.append(f"\n🔐 Permissions: {''.join(perms)} (octal: {oct(mode)[-3:]})")
            
            # File checksums (for files only)
            if os.path.isfile(p) and st.st_size < 50 * 1024 * 1024:  # < 50MB
                self.append(f"\n🔑 Checksums (calculating...)")
                
                # MD5
                md5 = hashlib.md5()
                with open(p, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        md5.update(chunk)
                self.append(f"   MD5:    {md5.hexdigest()}")
                
                # SHA256
                sha256 = hashlib.sha256()
                with open(p, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256.update(chunk)
                self.append(f"   SHA256: {sha256.hexdigest()}")
            
            # Directory contents
            if os.path.isdir(p):
                try:
                    items = os.listdir(p)
                    self.append(f"\n📁 Contents: {len(items)} items")
                    for item in sorted(items)[:10]:
                        item_path = os.path.join(p, item)
                        if os.path.isdir(item_path):
                            self.append(f"   📁 {item}/")
                        else:
                            item_size = os.path.getsize(item_path)
                            self.append(f"   📄 {item} ({item_size:,} bytes)")
                    if len(items) > 10:
                        self.append(f"   ... and {len(items) - 10} more")
                except:
                    pass
                    
        except Exception as e: 
            self.append(f"❌ Error: {e}")
        self.done()

    def file_compress(self, path):
        """Compress file or folder with details"""
        import zipfile
        try:
            p = os.path.expanduser(path)
            base = os.path.basename(p.rstrip('/'))
            zip_path = os.path.expanduser(f"~/Downloads/{base}.zip")
            
            self.append(f"📦 Compressing: {path}")
            
            total_size = 0
            file_count = 0
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
                if os.path.isfile(p):
                    z.write(p, base)
                    file_count = 1
                    total_size = os.path.getsize(p)
                else:
                    for root, dirs, files in os.walk(p):
                        for f in files:
                            fp = os.path.join(root, f)
                            arcname = os.path.join(os.path.basename(p), os.path.relpath(fp, p))
                            z.write(fp, arcname)
                            total_size += os.path.getsize(fp)
                            file_count += 1
            
            compressed_size = os.path.getsize(zip_path)
            ratio = (1 - compressed_size/total_size) * 100 if total_size > 0 else 0
            
            self.append(f"\n✅ Compression complete!")
            self.append(f"   📁 Output: {zip_path}")
            self.append(f"   📊 Original: {total_size:,} bytes")
            self.append(f"   🗜️ Compressed: {compressed_size:,} bytes")
            self.append(f"   📉 Saved: {ratio:.1f}%")
            self.append(f"   📄 Files: {file_count}")
            
        except Exception as e: 
            self.append(f"❌ Error: {e}")
        self.done()

    def file_search(self, name, folder=""):
        """Search for files with more details"""
        try:
            path = os.path.expanduser(folder) or os.path.expanduser("~")
            self.append(f"🔍 Searching for '{name}' in {path}...")
            
            matches = []
            for root, dirs, files in os.walk(path):
                for f in files:
                    if name.lower() in f.lower():
                        full_path = os.path.join(root, f)
                        try:
                            size = os.path.getsize(full_path)
                            matches.append((full_path, size))
                        except:
                            matches.append((full_path, 0))
            
            if not matches:
                self.append("❌ No files found")
            else:
                self.append(f"\n📋 Found {len(matches)} match(es):\n")
                for fp, size in matches[:50]:
                    size_str = f"({size:,} bytes)" if size else ""
                    self.append(f"   📄 {fp} {size_str}")
                    
                if len(matches) > 50:
                    self.append(f"\n... and {len(matches) - 50} more")
                    
        except Exception as e: 
            self.append(f"❌ Error: {e}")
        self.done()

    # ==================== IMAGES ====================
    def image_converter(self, path, fmt):
        if not PIL_AVAILABLE: self.append("❌ pillow missing"); self.done(); return
        try:
            p = os.path.expanduser(path)
            base = os.path.splitext(os.path.basename(p))[0]
            out = os.path.expanduser(f"~/Downloads/{base}.{fmt.lower()}")
            Image.open(p).convert('RGB').save(out)
            self.append(f"✅ Saved: {out}")
        except Exception as e: self.append(f"❌ {e}")
        self.done()

    def image_resize(self, path, w, h):
        if not PIL_AVAILABLE: self.append("❌ pillow missing"); self.done(); return
        try:
            p = os.path.expanduser(path)
            base = os.path.splitext(os.path.basename(p))[0]
            out = os.path.expanduser(f"~/Downloads/{base}_resized.png")
            img = Image.open(p)
            img.resize((int(w), int(h))).save(out)
            self.append(f"✅ Saved: {out}")
        except Exception as e: self.append(f"❌ {e}")
        self.done()

    def take_screenshot(self):
        if not PIL_AVAILABLE: self.append("❌ pillow missing"); self.done(); return
        try:
            from PIL import ImageGrab
            path = os.path.expanduser(f"~/Downloads/screenshot_{int(time.time())}.png")
            ImageGrab.grab().save(path)
            self.append(f"✅ Saved: {path}")
        except Exception as e: self.append(f"❌ {e}")
        self.done()

    # ==================== SYSTEM ====================
    def system_info(self):
        try:
            import platform
            try:
                import psutil
                has_psutil = True
            except:
                has_psutil = False
            
            self.append(f"\n🖥️ System Information")
            self.append(f"   {'='*50}")
            self.append(f"\n📋 OS: {platform.system()} {platform.release()}")
            self.append(f"   Machine: {platform.machine()}")
            self.append(f"\n🐍 Python: {platform.python_version()}")
            
            if has_psutil:
                self.append(f"\n⚙️ CPU: {psutil.cpu_count(logical=False)} cores, {psutil.cpu_count(logical=True)} threads")
                cpu_p = psutil.cpu_percent(interval=1, percpu=True)
                self.append(f"   Usage: {sum(cpu_p)/len(cpu_p):.1f}%")
                
                mem = psutil.virtual_memory()
                self.append(f"\n💾 Memory: {mem.used/1024**3:.1f}GB / {mem.total/1024**3:.1f}GB ({mem.percent}%)")
                
                self.append(f"\n💽 Disk:")
                for p in psutil.disk_partitions():
                    try:
                        u = psutil.disk_usage(p.mountpoint)
                        self.append(f"   {p.mountpoint}: {u.used/1024**3:.1f}GB / {u.total/1024**3:.1f}GB ({u.percent}%)")
                    except: pass
                
                net = psutil.net_io_counters()
                self.append(f"\n🌐 Network: {net.bytes_recv/1024**2:.1f}MB in, {net.bytes_sent/1024**2:.1f}MB out")
                
                boot = psutil.boot_time()
                up = time.time() - boot
                self.append(f"\n⏱️ Uptime: {int(up/86400)}d {int(up%86400/3600)}h {int(up%3600/60)}m")
            else:
                if os.path.exists("/proc/meminfo"):
                    with open("/proc/meminfo") as f:
                        for line in f:
                            if line.startswith("MemTotal"): 
                                self.append(f"\n💾 RAM: {int(line.split()[1])//1024} MB")
                                break
                if os.path.exists("/proc/loadavg"):
                    with open("/proc/loadavg") as f:
                        self.append(f"\n📊 Load: {f.read().split()[0]}")
        except Exception as e: self.append(f"❌ {e}")
        self.done()

    def process_list(self):
        try:
            import psutil
            self.append(f"\n📋 Top Processes")
            self.append(f"   {'='*50}")
            
            procs = []
            for p in psutil.process_iter(['pid','name','cpu_percent','memory_percent']):
                try:
                    pi = p.info
                    procs.append({'pid':pi.get('pid',0), 'name':pi.get('name','')[:20], 'cpu':pi.get('cpu_percent',0), 'mem':pi.get('memory_percent',0)})
                except: pass
            
            procs.sort(key=lambda x: x['cpu'], reverse=True)
            self.append(f"\n🔥 Top 15 by CPU:")
            self.append(f"   PID     CPU%   MEM%   Name")
            for pr in procs[:15]:
                self.append(f"   {pr['pid']:<7} {pr['cpu']:<7.1f} {pr['mem']:<7.1f} {pr['name']}")
            
            procs.sort(key=lambda x: x['mem'], reverse=True)
            self.append(f"\n💾 Top 15 by Memory:")
            self.append(f"   PID     MEM%    CPU%   Name")
            for pr in procs[:15]:
                self.append(f"   {pr['pid']:<7} {pr['mem']:<7.1f} {pr['cpu']:<7.1f} {pr['name']}")
                
            self.append(f"\n📊 Total: {len(procs)} processes")
        except ImportError:
            self.append("📋 Processes (psutil needed):")
            try:
                for line in open("/proc/processes").readlines()[:20]:
                    self.append(f"   {line.strip()}")
            except: pass
        except Exception as e: self.append(f"❌ {e}")
        self.done()

    def kill_process(self, name):
        try:
            name = name.strip()
            if name.isdigit():
                os.kill(int(name), 9)
                self.append(f"✅ Killed PID {name}")
            else:
                os.system(f"pkill -9 {name}")
                self.append(f"✅ Killed processes matching '{name}'")
        except Exception as e: self.append(f"❌ {e}")
        self.done()


if __name__ == "__main__":
    root = tk.Tk()
    GUIToolkit(root)
    root.mainloop()
