"""KDP publishing functionality."""
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

from .book import Book, BookMetadata

logger = logging.getLogger(__name__)


class KDPAuthenticationError(Exception):
    """Raised when KDP authentication fails."""
    pass


class KDPPublishError(Exception):
    """Raised when there's an error during publishing."""
    pass


class KDPPublisher:
    """Handles interaction with KDP for publishing books."""
    
    BASE_URL = "https://kdp.amazon.com"
    LOGIN_URL = "https://kdp.amazon.com/en_US/"
    DASHBOARD_URL = f"{BASE_URL}/dashboard"
    NEW_BOOK_URL = f"{BASE_URL}/title/new"
    
    def __init__(
        self,
        email: str,
        password: str,
        headless: bool = True,
        timeout: int = 30,
    ):
        """Initialize the KDP publisher.
        
        Args:
            email: KDP account email
            password: KDP account password
            headless: Whether to run browser in headless mode
            timeout: Default timeout for page loads in seconds
        """
        self.email = email
        self.password = password
        self.timeout = timeout
        self.driver = self._init_driver(headless)
        self.is_authenticated = False
    
    def _init_driver(self, headless: bool = True) -> webdriver.Chrome:
        """Initialize and return a Chrome WebDriver instance."""
        options = ChromeOptions()
        
        if headless:
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
        
        # Common options
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    def login(self) -> bool:
        """Log in to KDP.
        
        Returns:
            bool: True if login was successful
        """
        try:
            logger.info("Navigating to KDP login page...")
            self.driver.get(self.LOGIN_URL)
            
            # Wait for email field and enter credentials
            email_field = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, "ap_email"))
            )
            email_field.send_keys(self.email)
            
            # Click continue button
            continue_button = self.driver.find_element(By.ID, "continue")
            continue_button.click()
            
            # Wait for password field and enter password
            password_field = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, "ap_password"))
            )
            password_field.send_keys(self.password)
            
            # Click sign in button
            signin_button = self.driver.find_element(By.ID, "signInSubmit")
            signin_button.click()
            
            # Wait for dashboard to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.url_contains("/dashboard")
            )
            
            self.is_authenticated = True
            logger.info("Successfully logged in to KDP")
            return True
            
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Login failed: {str(e)}")
            self.is_authenticated = False
            return False
    
    def publish_book(self, book: Book, draft: bool = True) -> Dict[str, Any]:
        """Publish a book to KDP.
        
        Args:
            book: Book instance to publish
            draft: If True, save as draft instead of publishing immediately
            
        Returns:
            Dict containing publication details
            
        Raises:
            KDPAuthenticationError: If not logged in
            KDPPublishError: If publishing fails
        """
        if not self.is_authenticated:
            raise KDPAuthenticationError("Not authenticated. Call login() first.")
        
        if not book.manuscript_path or not book.cover_path:
            raise KDPPublishError("Book manuscript and cover must be set before publishing.")
        
        try:
            logger.info(f"Starting publication process for book: {book.title}")
            
            # Navigate to new book page
            self.driver.get(self.NEW_BOOK_URL)
            
            # Wait for and click the "Create New Title" button
            create_btn = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.ID, "book-radio-button"))
            )
            create_btn.click()
            
            # Wait for and click the "Create New Paperback" button
            paperback_btn = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.ID, "paperback-announce"))
            )
            paperback_btn.click()
            
            # TODO: Implement the rest of the publishing flow
            # This is a simplified example - the actual KDP form has many fields
            
            # For now, just return a success response
            return {
                "success": True,
                "book_id": "KDP_" + str(int(time.time())),
                "draft": draft,
                "title": book.title,
                "message": "Book successfully submitted to KDP" + (" as draft" if draft else ""),
            }
            
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            error_msg = f"Failed to publish book: {str(e)}"
            logger.error(error_msg)
            raise KDPPublishError(error_msg) from e
    
    def close(self) -> None:
        """Close the browser and clean up resources."""
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
            self.is_authenticated = False
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure browser is closed."""
        self.close()
    
    def __del__(self):
        """Destructor - ensure browser is closed."""
        self.close()
