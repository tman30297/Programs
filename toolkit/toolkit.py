#!/usr/bin/env python3
"""
Tony's Utility Toolkit - CLI
YouTube Downloader | Stock Checker | Crypto Tracker | SMS Sender | Weather

Usage:
    python toolkit.py youtube <url>
    python toolkit.py stock <symbol>
    python toolkit.py crypto <symbol>
    python toolkit.py sms <to_number> <message>
    python toolkit.py weather <city>
"""

from __future__ import annotations

import argparse
import sys
import os
from typing import Optional

# Try importing optional dependencies
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


def download_youtube(url: str):
    """Download YouTube video/audio using yt-dlp"""
    if not YTDLP_AVAILABLE:
        print("❌ yt-dlp not installed. Run: pip install yt-dlp")
        return
    
    print(f"📥 Downloading: {url}")
    
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.expanduser('~/Downloads/%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("✅ Download complete!")
    except Exception as e:
        print(f"❌ Error: {e}")


def get_stock_price(symbol: str):
    """Get current stock price using Yahoo Finance (free API)"""
    if not REQUESTS_AVAILABLE:
        print("❌ requests not installed. Run: pip install requests")
        return
    
    try:
        # Using Yahoo Finance free API
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol.upper()}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
            result = data['chart']['result'][0]
            meta = result['meta']
            price = meta.get('regularMarketPrice', 'N/A')
            prev = meta.get('previousClose', 'N/A')
            change = price - prev if price != 'N/A' and prev != 'N/A' else 0
            pct = (change / prev * 100) if prev else 0
            
            print(f"📈 {symbol.upper()}")
            print(f"   Price: ${price}")
            print(f"   Change: ${change:+.2f} ({pct:+.2f}%)")
        else:
            print(f"❌ Could not find stock: {symbol}")
    except Exception as e:
        print(f"❌ Error: {e}")


def get_crypto_price(symbol: str):
    """Get cryptocurrency price using CoinGecko (free API)"""
    if not REQUESTS_AVAILABLE:
        print("❌ requests not installed. Run: pip install requests")
        return
    
    # Map common symbols to CoinGecko IDs
    crypto_map = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'DOGE': 'dogecoin',
        'XRP': 'ripple',
        'ADA': 'cardano',
        'SOL': 'solana',
        'DOT': 'polkadot',
        'MATIC': 'matic-network',
        'LINK': 'chainlink',
        'AVAX': 'avalanche-2',
    }
    
    coin_id = crypto_map.get(symbol.upper(), symbol.lower())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
    
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if coin_id in data:
            price = data[coin_id]['usd']
            change = data[coin_id].get('usd_24h_change', 0)
            print(f"₿ {symbol.upper()}")
            print(f"   Price: ${price:,.2f}")
            print(f"   24h Change: {change:+.2f}%")
        else:
            print(f"❌ Could not find crypto: {symbol}")
    except Exception as e:
        print(f"❌ Error: {e}")


def send_sms(to_number: str, message: str) -> None:
    """Send SMS via Twilio"""
    # Check for Twilio credentials
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_PHONE_NUMBER')
    
    if not all([account_sid, auth_token, from_number]):
        print("❌ Twilio not configured!")
        print("   Set environment variables:")
        print("   - TWILIO_ACCOUNT_SID")
        print("   - TWILIO_AUTH_TOKEN")
        print("   - TWILIO_PHONE_NUMBER")
        return
    
    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        
        msg = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        print(f"✅ SMS sent! SID: {msg.sid}")
    except ImportError:
        print("❌ Twilio not installed. Run: pip install twilio")
    except Exception as e:
        print(f"❌ Error: {e}")


def get_weather(city: str) -> None:
    """Get weather using Open-Meteo (free, no API key needed)"""
    if not REQUESTS_AVAILABLE:
        print("❌ requests not installed. Run: pip install requests")
        return
    
    # First geocode the city
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city.replace(' ', '%20')}&count=1"
    
    try:
        resp = requests.get(geo_url, timeout=10)
        data = resp.json()
        
        if 'results' not in data or not data['results']:
            print(f"❌ City not found: {city}")
            return
        
        location = data['results'][0]
        lat, lon = location['latitude'], location['longitude']
        city_name = location['name']
        country = location.get('country', '')
        
        # Get weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&temperature_unit=fahrenheit"
        resp = requests.get(weather_url, timeout=10)
        data = resp.json()
        
        if 'current_weather' in data:
            weather = data['current_weather']
            temp = weather['temperature']
            wind = weather['windspeed']
            code = weather['weathercode']
            
            # Simple weather description
            descriptions = {
                0: "Clear sky",
                1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                45: "Foggy", 48: "Depositing rime fog",
                51: "Light drizzle", 53: "Drizzle", 55: "Dense drizzle",
                61: "Rain", 63: "Rain", 65: "Heavy rain",
                71: "Snow", 73: "Snow", 75: "Heavy snow",
                80: "Showers", 81: "Showers", 82: "Heavy showers",
                95: "Thunderstorm", 96: "Thunderstorm with hail",
            }
            desc = descriptions.get(code, f"Code {code}")
            
            print(f"🌤️  {city_name}, {country}")
            print(f"   {desc}")
            print(f"   Temp: {temp}°F")
            print(f"   Wind: {wind} km/h")
        else:
            print(f"❌ Could not fetch weather data")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Tony's Utility Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python toolkit.py youtube https://youtu.be/...
  python toolkit.py stock AAPL
  python toolkit.py crypto BTC
  python toolkit.py sms +1234567890 "Hello from CLI!"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # YouTube command
    yt_parser = subparsers.add_parser('youtube', help='Download YouTube video')
    yt_parser.add_argument('url', help='YouTube URL')
    
    # Stock command
    stock_parser = subparsers.add_parser('stock', help='Check stock price')
    stock_parser.add_argument('symbol', help='Stock symbol (e.g., AAPL)')
    
    # Crypto command
    crypto_parser = subparsers.add_parser('crypto', help='Check crypto price')
    crypto_parser.add_argument('symbol', help='Crypto symbol (e.g., BTC)')
    
    # SMS command
    sms_parser = subparsers.add_parser('sms', help='Send SMS via Twilio')
    sms_parser.add_argument('to', help='Phone number (e.g., +1234567890)')
    sms_parser.add_argument('message', help='Message to send')
    
    # Weather command
    weather_parser = subparsers.add_parser('weather', help='Check weather')
    weather_parser.add_argument('city', help='City name (e.g., "New York")')
    
    args = parser.parse_args()
    
    if args.command == 'youtube':
        download_youtube(args.url)
    elif args.command == 'stock':
        get_stock_price(args.symbol)
    elif args.command == 'crypto':
        get_crypto_price(args.symbol)
    elif args.command == 'sms':
        send_sms(args.to, args.message)
    elif args.command == 'weather':
        get_weather(args.city)


if __name__ == '__main__':
    main()
