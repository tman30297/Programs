# GUI Toolkit

Tony's Ultimate Utility GUI - All-in-one tool for downloading, searching, converting, and more!

## Requirements

```bash
pip install yt-dlp requests qrcode[pil] pillow psutil
```

## Usage

```bash
python GUI_toolkit.py
```

## Features (Enhanced!)

### Downloaders
- **YouTube Download** - Video info + MP4 download with title, channel, views, duration
- **YouTube MP3** - Extract audio as high-quality MP3
- **TikTok Download** - Download TikTok videos with description
- **Twitter/X Download** - Download Twitter/X videos
- **Image Downloader** - Download with metadata (size, type)

### Finance (Comprehensive)
- **Stock Price** - Full quote: price, change, open, high, low, volume, market cap, P/E ratio, 5-day trend
- **Crypto Price** - Price, 24h/7d change, high/low, market cap, volume, all-time-high, rank
- **Currency Converter** - Convert with exchange rates for major currencies

### Search/Lookup
- **Web Search** - DuckDuckGo results (15 results)
- **Wikipedia** - Full summary, sections, links
- **Dictionary** - Phonetics, definitions, examples, synonyms, antonyms, etymology

### Weather (Detailed)
- Current conditions + 7-day forecast + hourly + UV index

### Utilities
- **URL Shortener** (is.gd)
- **QR Code Generator**
- **Base64 Encode/Decode**
- **Hash Generator** (MD5, SHA1, SHA256, SHA512)
- **Epoch Converter**
- **Case Converter** (UPPER, lower, Title, Sentence)
- **Word Counter** (words, chars, lines)
- **Lorem Ipsum Generator**
- **Unit Converter** - Length, Weight, Temperature, Volume, Data, Time

### Info Tools
- **My IP Address** + location + ISP
- **WhoIs Lookup** - Registrar, dates
- **DNS Lookup** - A, AAAA, CNAME, MX, TXT, NS, SOA records

### Network (Enhanced)
- **Ping** - Stats with packet loss, RTT min/avg/max
- **Port Scanner** - With service detection (common ports)
- **Speed Test** - Download speed, latency measurement

### Files (Enhanced)
- **File Info** - Size, timestamps, permissions, checksums (MD5, SHA256)
- **File Compress** - ZIP with compression ratio
- **File Search** - With file sizes

### Images
- **Image Converter** (PNG/JPG/WebP/BMP)
- **Image Resize**
- **Screenshot**

### System (Enhanced)
- **System Info** - OS, CPU, Memory, Disk, Network, Uptime (via psutil)
- **Process List** - Top 15 by CPU and Memory with usage stats
- **Kill Process** - By PID or name

## How to Use

1. Select a tool from the category tree on the left
2. Fill in the required field(s) or use dropdowns
3. Click "Execute"
4. View detailed results in the output area

## Notes

- Downloads saved to ~/Downloads/
- Most APIs are free (no key needed)
- Install psutil for full system info: `pip install psutil`
