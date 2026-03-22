#!/usr/bin/env python3
"""
Brain RSS Importer - Fetch and import articles from RSS feeds.
Does small batches to save resources.
"""

import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Default tech RSS feeds
RSS_FEEDS = [
    "https://news.ycombinator.com/rss",
    "https://www.bleepingcomputer.com/feed/",
    "https://feeds.arstechnica.com/arstechnica/index",
]

def fetch_rss(feed_url: str, limit: int = 3):
    """Fetch articles from an RSS feed."""
    try:
        import xml.etree.ElementTree as ET
        import urllib.request
        
        with urllib.request.urlopen(feed_url, timeout=10) as response:
            content = response.read()
        
        root = ET.fromstring(content)
        
        # RSS 2.0 format
        items = root.findall('.//item')
        if not items:
            # Atom format
            items = root.findall('.//entry')
        
        articles = []
        for item in items[:limit]:
            if item.tag == 'entry':
                title = item.findtext('title', '')
                link = item.findtext('link', '')
                desc = item.findtext('summary', '') or item.findtext('content', '')
            else:
                title = item.findtext('title', '')
                link = item.findtext('link', '')
                desc = item.findtext('description', '')
            
            articles.append({
                'title': title.strip(),
                'url': link.strip(),
                'description': desc.strip()[:500] if desc else ''
            })
        
        return articles
        
    except Exception as e:
        print(f"  ⚠️ Error fetching {feed_url}: {e}")
        return []

def import_rss_feeds(feeds: list = None, limit_per_feed: int = 2):
    """Import articles from RSS feeds as notes."""
    if not feeds:
        feeds = RSS_FEEDS
    
    from brain import add_note
    
    total_imported = 0
    
    for feed_url in feeds:
        print(f"📡 Fetching: {feed_url[:50]}...")
        articles = fetch_rss(feed_url, limit_per_feed)
        
        for article in articles:
            if article['title']:
                content = f"""**{article['title']}**

Source: {article['url']}

{article['description']}

---
*Imported from RSS*"""
                
                tags = "rss,imported," + feed_url.split('://')[1].split('/')[0].replace('www.', '')
                
                add_note(content, title=article['title'][:100], author="RSS", tags=tags)
                total_imported += 1
    
    print(f"\n✅ Imported {total_imported} articles from {len(feeds)} feeds")
    return total_imported

def main():
    print("📡 Brain RSS Importer")
    print("-" * 30)
    
    imported = import_rss_feeds(limit_per_feed=2)
    
    if imported > 0:
        print("\n💡 Run 'brain.py export' to update browser")

if __name__ == "__main__":
    main()
