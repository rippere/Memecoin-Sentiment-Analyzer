"""
Base Scraper Class
==================
Adapted from user's Instagram bot (main.py)
Handles Selenium setup, anti-detection, and common scraping patterns
"""

import logging
import time
import random
from typing import Optional, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class BaseScraper:
    """
    Base scraper class with anti-detection measures
    All platform scrapers inherit from this
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None
        self.setup_driver()
    
    def setup_driver(self):
        """
        Initialize Selenium driver with anti-detection measures
        Based on user's proven Instagram bot approach
        """
        options = webdriver.ChromeOptions()
        
        # ANTI-DETECTION MEASURES (from user's code)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Additional options
        if self.config.get('headless', True):
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        
        # User agent
        user_agent = self.config.get(
            'user_agent', 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        options.add_argument(f"user-agent={user_agent}")
        
        # Window size (important for headless)
        options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            
            # Additional anti-detection JavaScript
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            logging.info(f"✅ {self.__class__.__name__} driver initialized")
            
        except Exception as e:
            logging.error(f"❌ Failed to initialize driver: {e}")
            raise
    
    def wait_for_element(
        self, 
        by: By, 
        selector: str, 
        timeout: int = 10,
        condition=EC.presence_of_element_located
    ):
        """
        Wait for element to appear (from user's code pattern)
        
        Args:
            by: Selenium By locator type
            selector: Element selector
            timeout: Maximum wait time in seconds
            condition: Expected condition (default: presence)
            
        Returns:
            WebElement or None
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                condition((by, selector))
            )
            return element
        except TimeoutException:
            logging.warning(f"⏱️  Timeout waiting for element: {selector}")
            return None
        except Exception as e:
            logging.error(f"❌ Error waiting for element: {e}")
            return None
    
    def random_delay(self, min_sec: float = None, max_sec: float = None):
        """
        Random delay between actions to appear human-like
        Respects rate limits and avoids detection
        
        Args:
            min_sec: Minimum delay (uses config if not provided)
            max_sec: Maximum delay (uses config if not provided)
        """
        min_delay = min_sec if min_sec is not None else self.config.get('min_delay', 2)
        max_delay = max_sec if max_sec is not None else self.config.get('max_delay', 5)
        
        delay = random.uniform(min_delay, max_delay)
        logging.debug(f"⏳ Waiting {delay:.2f} seconds...")
        time.sleep(delay)
    
    def safe_find_element(self, by: By, selector: str) -> Optional[any]:
        """
        Safely find element without throwing exception
        
        Args:
            by: Selenium By locator type
            selector: Element selector
            
        Returns:
            WebElement or None
        """
        try:
            return self.driver.find_element(by, selector)
        except NoSuchElementException:
            return None
        except Exception as e:
            logging.error(f"Error finding element: {e}")
            return None
    
    def safe_find_elements(self, by: By, selector: str) -> list:
        """
        Safely find multiple elements without throwing exception
        
        Args:
            by: Selenium By locator type
            selector: Element selector
            
        Returns:
            List of WebElements (empty if none found)
        """
        try:
            return self.driver.find_elements(by, selector)
        except Exception as e:
            logging.error(f"Error finding elements: {e}")
            return []
    
    def scroll_to_element(self, element):
        """Scroll element into view"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
        except Exception as e:
            logging.error(f"Error scrolling to element: {e}")
    
    def take_screenshot(self, filename: str):
        """Take screenshot for debugging"""
        try:
            os.makedirs('debug_screenshots', exist_ok=True)
            filepath = f"debug_screenshots/{filename}"
            self.driver.save_screenshot(filepath)
            logging.info(f"📸 Screenshot saved: {filepath}")
        except Exception as e:
            logging.error(f"Error taking screenshot: {e}")
    
    def get_page_source(self) -> str:
        """Get current page HTML"""
        try:
            return self.driver.page_source
        except Exception as e:
            logging.error(f"Error getting page source: {e}")
            return ""
    
    def close(self):
        """Clean up and close driver"""
        if self.driver:
            try:
                self.driver.quit()
                logging.info(f"🔒 {self.__class__.__name__} driver closed")
            except Exception as e:
                logging.error(f"Error closing driver: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit - always close driver"""
        self.close()
    
    def __del__(self):
        """Destructor - ensure driver is closed"""
        self.close()
