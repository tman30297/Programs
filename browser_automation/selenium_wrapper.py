"""
Browser Automation Wrapper using Selenium
Provides easy-to-use browser automation with common patterns.
"""

import time
import logging
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BrowserConfig:
    """Configuration for browser automation."""
    browser_type: str = "chrome"  # chrome, firefox, edge
    headless: bool = True
    implicit_wait: int = 10
    page_load_timeout: int = 30
    window_size: tuple = (1920, 1080)
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    download_dir: Optional[str] = None
    disable_images: bool = False
    disable_js: bool = False


class SeleniumWrapper:
    """
    Wrapper class for Selenium WebDriver with common automation patterns.
    """
    
    def __init__(self, config: Optional[BrowserConfig] = None):
        self.config = config or BrowserConfig()
        self.driver: Optional[webdriver.Remote] = None
        self._setup_driver()
    
    def _setup_driver(self):
        """Initialize the WebDriver based on configuration."""
        if self.config.browser_type.lower() == "chrome":
            options = ChromeOptions()
            if self.config.headless:
                options.add_argument("--headless=new")
            options.add_argument(f"--window-size={self.config.window_size[0]},{self.config.window_size[1]}")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            
            if self.config.user_agent:
                options.add_argument(f"user-agent={self.config.user_agent}")
            if self.config.proxy:
                options.add_argument(f"--proxy-server={self.config.proxy}")
            if self.config.disable_images:
                prefs = {"profile.managed_default_content_settings.images": 2}
                options.add_experimental_option("prefs", prefs)
            
            self.driver = webdriver.Chrome(options=options)
            
        elif self.config.browser_type.lower() == "firefox":
            options = FirefoxOptions()
            if self.config.headless:
                options.add_argument("--headless")
            options.add_argument(f"--width={self.config.window_size[0]}")
            options.add_argument(f"--height={self.config.window_size[1]}")
            
            self.driver = webdriver.Firefox(options=options)
        
        else:
            raise ValueError(f"Unsupported browser: {self.config.browser_type}")
        
        self.driver.implicitly_wait(self.config.implicit_wait)
        self.driver.set_page_load_timeout(self.config.page_load_timeout)
    
    def get(self, url: str, wait_for: Optional[str] = None, timeout: int = 10) -> bool:
        """Navigate to URL and optionally wait for element."""
        try:
            self.driver.get(url)
            if wait_for:
                self.wait_for_element(wait_for, timeout=timeout)
            logger.info(f"Navigated to: {url}")
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    def wait_for_element(self, selector: str, by: str = By.CSS_SELECTOR, 
                         timeout: int = 10, clickable: bool = False):
        """Wait for element to be present or clickable."""
        try:
            condition = EC.element_to_be_clickable((by, selector)) if clickable else EC.presence_of_element_located((by, selector))
            return WebDriverWait(self.driver, timeout).until(condition)
        except TimeoutException:
            logger.warning(f"Element not found: {selector}")
            return None
    
    def find_element(self, selector: str, by: str = By.CSS_SELECTOR):
        """Find a single element."""
        try:
            return self.driver.find_element(by, selector)
        except NoSuchElementException:
            return None
    
    def find_elements(self, selector: str, by: str = By.CSS_SELECTOR) -> List:
        """Find multiple elements."""
        return self.driver.find_elements(by, selector)
    
    def click(self, selector: str, by: str = By.CSS_SELECTOR, 
              retries: int = 3, delay: float = 1.0) -> bool:
        """Click an element with retry logic."""
        for attempt in range(retries):
            try:
                element = self.wait_for_element(selector, by, timeout=5, clickable=True)
                if element:
                    element.click()
                    return True
            except (ElementClickInterceptedException, StaleElementReferenceException) as e:
                logger.warning(f"Click attempt {attempt + 1} failed: {e}")
                time.sleep(delay)
        return False
    
    def type_text(self, selector: str, text: str, clear_first: bool = True,
                  by: str = By.CSS_SELECTOR, delay: float = 0.1) -> bool:
        """Type text into an input field."""
        element = self.wait_for_element(selector, by)
        if element:
            if clear_first:
                element.clear()
            for char in text:
                element.send_keys(char)
                time.sleep(delay)
            return True
        return False
    
    def get_text(self, selector: str, by: str = By.CSS_SELECTOR) -> Optional[str]:
        """Get text content of an element."""
        element = self.find_element(selector, by)
        return element.text if element else None
    
    def get_attribute(self, selector: str, attr: str, by: str = By.CSS_SELECTOR) -> Optional[str]:
        """Get an attribute from an element."""
        element = self.find_element(selector, by)
        return element.get_attribute(attr) if element else None
    
    def scroll_to(self, selector: str, by: str = By.CSS_SELECTOR) -> bool:
        """Scroll element into view."""
        element = self.find_element(selector, by)
        if element:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            return True
        return False
    
    def take_screenshot(self, filepath: str, full_page: bool = False) -> bool:
        """Take a screenshot."""
        try:
            self.driver.save_screenshot(filepath)
            logger.info(f"Screenshot saved: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return False
    
    def execute_script(self, script: str, *args):
        """Execute arbitrary JavaScript."""
        return self.driver.execute_script(script, *args)
    
    def wait_for_page_load(self, timeout: int = 10):
        """Wait for page to fully load."""
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    
    def get_cookies(self) -> List[Dict]:
        """Get all cookies."""
        return self.driver.get_cookies()
    
    def add_cookie(self, name: str, value: str, **kwargs):
        """Add a cookie."""
        cookie = {"name": name, "value": value, **kwargs}
        self.driver.add_cookie(cookie)
    
    def delete_cookie(self, name: str):
        """Delete a cookie."""
        self.driver.delete_cookie(name)
    
    def switch_to_frame(self, selector: str = None, index: int = None):
        """Switch to an iframe."""
        if selector:
            frame = self.wait_for_element(selector)
            if frame:
                self.driver.switch_to.frame(frame)
        elif index is not None:
            self.driver.switch_to.frame(index)
    
    def switch_to_default(self):
        """Switch back to main document."""
        self.driver.switch_to.default_content()
    
    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.close()
    
    def quit(self):
        """Quit the browser entirely."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()
    
    def __del__(self):
        self.quit()


# Convenience functions

def create_browser(**kwargs) -> SeleniumWrapper:
    """Create a browser instance with given options."""
    config = BrowserConfig(**kwargs)
    return SeleniumWrapper(config)


def quick_scrape(url: str, selectors: Dict[str, str], **kwargs) -> Optional[Dict[str, Any]]:
    """
    Quickly scrape data from a page.
    
    Args:
        url: Target URL
        selectors: Dict of {field_name: css_selector}
        **kwargs: Additional BrowserConfig options
    
    Returns:
        Dict of scraped data
    """
    config = BrowserConfig(**kwargs)
    with SeleniumWrapper(config) as browser:
        if browser.get(url):
            results = {}
            for field, selector in selectors.items():
                results[field] = browser.get_text(selector)
            return results
    return None


# Example usage
if __name__ == "__main__":
    # Basic example
    with create_browser(headless=True) as browser:
        browser.get("https://example.com")
        title = browser.get_text("h1")
        print(f"Title: {title}")
        browser.take_screenshot("example.png")
