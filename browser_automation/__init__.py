"""
Browser Automation Package
"""

from .selenium_wrapper import (
    SeleniumWrapper,
    BrowserConfig,
    create_browser,
    quick_scrape
)

__all__ = [
    "SeleniumWrapper",
    "BrowserConfig", 
    "create_browser",
    "quick_scrape"
]
