#!/usr/bin/env python3
"""
Web Scraper Template
Configurable scraper with rate limiting, retries, and storage.
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class ScraperConfig:
    base_url: str
    output_file: str
    delay_seconds: float = 1.0
    max_retries: int = 3
    timeout: int = 30


class WebScraper:
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; Bot/1.0)"})
        self.results: List[Dict] = []
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a page with retry logic."""
        for attempt in range(self.config.max_retries):
            try:
                response = self.session.get(url, timeout=self.config.timeout)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                time.sleep(self.config.delay_seconds * (attempt + 1))
        return None
    
    def parse_page(self, html: str) -> List[Dict]:
        """Parse HTML - customize for your target site."""
        soup = BeautifulSoup(html, "html.parser")
        results = []
        # Add your parsing logic here
        # Example: for item in soup.select('.item-class'): ...
        return results
    
    def save_results(self):
        """Save results to file."""
        output_path = Path(self.config.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if output_path.suffix == ".json":
            with open(output_path, "w") as f:
                json.dump(self.results, f, indent=2)
        elif output_path.suffix == ".csv":
            if self.results:
                with open(output_path, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
                    writer.writeheader()
                    writer.writerows(self.results)
        logger.info(f"Saved {len(self.results)} results to {output_path}")
    
    def run(self, urls: List[str]):
        """Run scraper across URLs."""
        for i, url in enumerate(urls, 1):
            logger.info(f"Scraping {i}/{len(urls)}: {url}")
            html = self.fetch_page(url)
            if html:
                items = self.parse_page(html)
                self.results.extend(items)
            time.sleep(self.config.delay_seconds)
        self.save_results()


if __name__ == "__main__":
    config = ScraperConfig(
        base_url="https://example.com",
        output_file="output/results.json",
        delay_seconds=2.0
    )
    scraper = WebScraper(config)
    scraper.run(["https://example.com/page1", "https://example.com/page2"])