"""
KDP Publisher Agent - Automated Book Publishing
The "shipping department" that gets our intelligent books onto Amazon KDP.

PURPOSE: Bridge the GAP between our intelligent factory and revenue generation.
BUSINESS IMPACT: Transform perfect books in parking lot into live, revenue-generating assets.
"""

import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BookAssets:
    """Container for all book publishing assets."""
    book_id: str
    title: str
    subtitle: Optional[str]
    description: str
    keywords: List[str]
    categories: List[str]
    manuscript_path: str
    cover_path: str
    author_name: str
    price: float
    niche: str


@dataclass
class PublishingResult:
    """Result of KDP publishing attempt."""
    success: bool
    book_id: str
    kdp_url: Optional[str]
    asin: Optional[str]
    errors: List[str]
    warnings: List[str]
    publishing_timestamp: str


class KDPPublisherAgent:
    """
    Automated KDP publishing agent using Playwright.
    
    This is the critical "shipping department" that transforms our intelligent
    book generation into actual revenue by automatically publishing to Amazon KDP.
    """
    
    def __init__(
        self,
        headless: bool = False,
        timeout: int = 30000,
        slow_mo: int = 1000,
        kdp_email: Optional[str] = None,
        kdp_password: Optional[str] = None
    ):
        """
        Initialize the KDP Publisher Agent.
        
        Args:
            headless: Run browser in headless mode (True for production)
            timeout: Default timeout for page operations (ms)
            slow_mo: Slow down operations for stability (ms)
            kdp_email: KDP account email (or set KDP_EMAIL env var)
            kdp_password: KDP account password (or set KDP_PASSWORD env var)
        """
        self.headless = headless
        self.timeout = timeout
        self.slow_mo = slow_mo
        
        # Get KDP credentials from environment or parameters
        self.kdp_email = kdp_email or os.getenv('KDP_EMAIL')
        self.kdp_password = kdp_password or os.getenv('KDP_PASSWORD')
        
        if not self.kdp_email or not self.kdp_password:
            raise ValueError("KDP credentials not provided. Set KDP_EMAIL and KDP_PASSWORD environment variables.")
        
        # Initialize Playwright components
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        logger.info("KDP Publisher Agent initialized")
    
    def __enter__(self):
        """Context manager entry."""
        self.start_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_browser()
    
    def start_browser(self):
        """Start Playwright browser session."""
        try:
            logger.info("Starting browser session...")
            self.playwright = sync_playwright().start()
            
            # Launch Chromium browser
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            # Create browser context with realistic user agent
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            # Create new page
            self.page = self.context.new_page()
            self.page.set_default_timeout(self.timeout)
            
            logger.info("Browser session started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise
    
    def close_browser(self):
        """Close Playwright browser session."""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            
            logger.info("Browser session closed")
            
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")
    
    def login_to_kdp(self) -> bool:
        """
        Login to Amazon KDP account.
        
        Returns:
            True if login successful, False otherwise
        """
        try:
            logger.info("Logging into KDP...")
            
            # Navigate to KDP login page
            self.page.goto('https://kdp.amazon.com/')
            
            # Wait for and click sign-in button
            self.page.wait_for_selector('a[href*="signin"]', timeout=10000)
            self.page.click('a[href*="signin"]')
            
            # Enter email
            self.page.wait_for_selector('input[name="email"]', timeout=10000)
            self.page.fill('input[name="email"]', self.kdp_email)
            self.page.click('input[type="submit"], button[type="submit"]')
            
            # Enter password
            self.page.wait_for_selector('input[name="password"]', timeout=10000)
            self.page.fill('input[name="password"]', self.kdp_password)
            self.page.click('input[type="submit"], button[type="submit"]')
            
            # Wait for successful login (dashboard or bookshelf)
            try:
                self.page.wait_for_selector('[data-testid="bookshelf"], .dashboard, .kdp-bookshelf', timeout=20000)
                logger.info("✓ Successfully logged into KDP")
                return True
            except:
                # Check for 2FA or other verification
                if self.page.locator('text=Enter the code').is_visible():
                    logger.warning("2FA verification required - manual intervention needed")
                    return False
                else:
                    logger.error("Login failed - unknown error")
                    return False
                    
        except Exception as e:
            logger.error(f"KDP login failed: {e}")
            return False
    
    def create_new_book(self, book_assets: BookAssets) -> PublishingResult:
        """
        Create a new book on KDP with all assets.
        
        This is the core method that bridges our intelligent factory to revenue.
        """
        errors = []
        warnings = []
        
        try:
            logger.info(f"Creating new book: {book_assets.title}")
            
            # Navigate to create new book
            self.page.goto('https://kdp.amazon.com/en_US/bookshelf')
            
            # Click "Create new book" button
            self.page.wait_for_selector('[data-testid="create-new-title"], .create-new-title, a[href*="create"]', timeout=10000)
            self.page.click('[data-testid="create-new-title"], .create-new-title, a[href*="create"]')
            
            # Select Kindle eBook
            self.page.wait_for_selector('text=Kindle eBook', timeout=10000)
            self.page.click('text=Kindle eBook')
            
            # Fill book details
            result = self._fill_book_details(book_assets, errors, warnings)
            if not result:
                return PublishingResult(
                    success=False,
                    book_id=book_assets.book_id,
                    kdp_url=None,
                    asin=None,
                    errors=errors,
                    warnings=warnings,
                    publishing_timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
                )
            
            # Upload manuscript
            result = self._upload_manuscript(book_assets, errors, warnings)
            if not result:
                return PublishingResult(
                    success=False,
                    book_id=book_assets.book_id,
                    kdp_url=None,
                    asin=None,
                    errors=errors,
                    warnings=warnings,
                    publishing_timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
                )
            
            # Upload cover
            result = self._upload_cover(book_assets, errors, warnings)
            if not result:
                return PublishingResult(
                    success=False,
                    book_id=book_assets.book_id,
                    kdp_url=None,
                    asin=None,
                    errors=errors,
                    warnings=warnings,
                    publishing_timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
                )
            
            # Set pricing and distribution
            result = self._set_pricing_and_distribution(book_assets, errors, warnings)
            if not result:
                return PublishingResult(
                    success=False,
                    book_id=book_assets.book_id,
                    kdp_url=None,
                    asin=None,
                    errors=errors,
                    warnings=warnings,
                    publishing_timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
                )
            
            # Get the KDP URL and ASIN
            kdp_url = self.page.url
            asin = self._extract_asin_from_page()
            
            logger.info(f"✓ Book created successfully: {book_assets.title}")
            return PublishingResult(
                success=True,
                book_id=book_assets.book_id,
                kdp_url=kdp_url,
                asin=asin,
                errors=errors,
                warnings=warnings,
                publishing_timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
            )
            
        except Exception as e:
            logger.error(f"Failed to create book: {e}")
            errors.append(f"Book creation failed: {str(e)}")
            
            return PublishingResult(
                success=False,
                book_id=book_assets.book_id,
                kdp_url=None,
                asin=None,
                errors=errors,
                warnings=warnings,
                publishing_timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
            )
    
    def _fill_book_details(self, book_assets: BookAssets, errors: List[str], warnings: List[str]) -> bool:
        """Fill in book metadata on KDP form."""
        try:
            logger.info("Filling book details...")
            
            # Book title
            title_selector = 'input[name="title"], #title, [data-testid="title-input"]'
            self.page.wait_for_selector(title_selector, timeout=10000)
            self.page.fill(title_selector, book_assets.title)
            
            # Subtitle (if available)
            if book_assets.subtitle:
                subtitle_selector = 'input[name="subtitle"], #subtitle, [data-testid="subtitle-input"]'
                try:
                    self.page.fill(subtitle_selector, book_assets.subtitle)
                except:
                    warnings.append("Could not fill subtitle field")
            
            # Author name
            author_selector = 'input[name="author"], #author, [data-testid="author-input"]'
            self.page.fill(author_selector, book_assets.author_name)
            
            # Description - Amazon KDP uses CKEditor with iframe
            try:
                # Wait for CKEditor to load
                self.page.wait_for_selector('.cke_wysiwyg_frame', timeout=15000)
                logger.info("Found CKEditor iframe for description")
                
                # Get the iframe and fill the description
                iframe = self.page.frame_locator('.cke_wysiwyg_frame')
                iframe.locator('body').fill(book_assets.description)
                logger.info("✓ Description filled successfully using CKEditor iframe")
                
            except Exception as e:
                # Fallback to alternative selectors for description
                logger.warning(f"CKEditor approach failed: {e}")
                fallback_selectors = [
                    '.editor[data-path*="description"]',
                    '#cke_editor1',
                    'input[name="data[print_book][description]"]',
                    'textarea[name="description"]',
                    '#description',
                    '[data-testid="description-textarea"]'
                ]
                
                filled = False
                for selector in fallback_selectors:
                    try:
                        if self.page.locator(selector).is_visible():
                            self.page.fill(selector, book_assets.description)
                            logger.info(f"✓ Description filled using fallback selector: {selector}")
                            filled = True
                            break
                    except:
                        continue
                
                if not filled:
                    warnings.append("Could not fill description field - all selectors failed")
                    logger.warning("❌ All description selectors failed")
            
            # Keywords
            if book_assets.keywords:
                keywords_text = ', '.join(book_assets.keywords[:7])  # KDP allows up to 7 keywords
                keywords_selector = 'input[name="keywords"], #keywords, [data-testid="keywords-input"]'
                try:
                    self.page.fill(keywords_selector, keywords_text)
                except:
                    warnings.append("Could not fill keywords field")
            
            # Categories (this varies by KDP interface)
            # TODO: Implement category selection logic
            
            logger.info("✓ Book details filled")
            return True
            
        except Exception as e:
            logger.error(f"Failed to fill book details: {e}")
            errors.append(f"Failed to fill book details: {str(e)}")
            return False
    
    def _upload_manuscript(self, book_assets: BookAssets, errors: List[str], warnings: List[str]) -> bool:
        """Upload manuscript file to KDP."""
        try:
            logger.info("Uploading manuscript...")
            
            # Navigate to content tab
            content_tab = 'a[href*="content"], text=Content, [data-testid="content-tab"]'
            self.page.click(content_tab)
            
            # Upload manuscript file
            manuscript_upload = 'input[type="file"][accept*=".doc"], input[type="file"][name*="manuscript"]'
            self.page.wait_for_selector(manuscript_upload, timeout=10000)
            self.page.set_input_files(manuscript_upload, book_assets.manuscript_path)
            
            # Wait for upload to complete
            self.page.wait_for_selector('text=Upload complete, text=Processing, [data-testid="upload-success"]', timeout=60000)
            
            logger.info("✓ Manuscript uploaded")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload manuscript: {e}")
            errors.append(f"Failed to upload manuscript: {str(e)}")
            return False
    
    def _upload_cover(self, book_assets: BookAssets, errors: List[str], warnings: List[str]) -> bool:
        """Upload cover image to KDP."""
        try:
            logger.info("Uploading cover...")
            
            # Cover upload
            cover_upload = 'input[type="file"][accept*="image"], input[type="file"][name*="cover"]'
            self.page.wait_for_selector(cover_upload, timeout=10000)
            self.page.set_input_files(cover_upload, book_assets.cover_path)
            
            # Wait for cover upload to complete
            self.page.wait_for_selector('text=Cover uploaded, [data-testid="cover-success"]', timeout=30000)
            
            logger.info("✓ Cover uploaded")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload cover: {e}")
            errors.append(f"Failed to upload cover: {str(e)}")
            return False
    
    def _set_pricing_and_distribution(self, book_assets: BookAssets, errors: List[str], warnings: List[str]) -> bool:
        """Set book pricing and distribution settings."""
        try:
            logger.info("Setting pricing and distribution...")
            
            # Navigate to pricing tab
            pricing_tab = 'a[href*="pricing"], text=Pricing, [data-testid="pricing-tab"]'
            self.page.click(pricing_tab)
            
            # Set price
            price_input = 'input[name="price"], #price, [data-testid="price-input"]'
            self.page.wait_for_selector(price_input, timeout=10000)
            self.page.fill(price_input, str(book_assets.price))
            
            # Select territories (usually all territories)
            all_territories = 'input[value="all_territories"], text=All territories'
            try:
                self.page.click(all_territories)
            except:
                warnings.append("Could not select all territories")
            
            # Set DRM settings (usually no DRM)
            no_drm = 'input[value="no_drm"], text=No DRM'
            try:
                self.page.click(no_drm)
            except:
                warnings.append("Could not set DRM settings")
            
            logger.info("✓ Pricing and distribution set")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set pricing: {e}")
            errors.append(f"Failed to set pricing: {str(e)}")
            return False
    
    def _extract_asin_from_page(self) -> Optional[str]:
        """Extract ASIN from the current KDP page."""
        try:
            # Look for ASIN in various places on the page
            asin_patterns = [
                r'ASIN:\s*([A-Z0-9]{10})',
                r'asin["\']:\s*["\']([A-Z0-9]{10})["\']',
                r'/dp/([A-Z0-9]{10})',
            ]
            
            page_content = self.page.content()
            
            import re
            for pattern in asin_patterns:
                match = re.search(pattern, page_content)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            logger.warning(f"Could not extract ASIN: {e}")
            return None
    
    def publish_book_from_assets(self, assets_path: str) -> PublishingResult:
        """
        Convenience method to publish a book from a directory of assets.
        
        Expected directory structure:
        assets_path/
        ├── book_metadata.json
        ├── manuscript.docx (or .pdf)
        ├── cover.png (or .jpg)
        └── marketing/
            ├── description.txt
            └── keywords.txt
        """
        try:
            assets_dir = Path(assets_path)
            
            # Load book metadata
            import json
            with open(assets_dir / 'book_metadata.json', 'r') as f:
                metadata = json.load(f)
            
            # Find manuscript file
            manuscript_files = list(assets_dir.glob('manuscript.*')) + list(assets_dir.glob('*.docx')) + list(assets_dir.glob('*.pdf'))
            if not manuscript_files:
                raise ValueError("No manuscript file found")
            manuscript_path = str(manuscript_files[0])
            
            # Find cover file
            cover_files = list(assets_dir.glob('cover.*')) + list(assets_dir.glob('*.png')) + list(assets_dir.glob('*.jpg'))
            if not cover_files:
                raise ValueError("No cover file found")
            cover_path = str(cover_files[0])
            
            # Load marketing content
            description = ""
            if (assets_dir / 'marketing' / 'description.txt').exists():
                with open(assets_dir / 'marketing' / 'description.txt', 'r') as f:
                    description = f.read().strip()
            
            keywords = []
            if (assets_dir / 'marketing' / 'keywords.txt').exists():
                with open(assets_dir / 'marketing' / 'keywords.txt', 'r') as f:
                    keywords = [kw.strip() for kw in f.read().split(',')]
            
            # Create BookAssets object
            book_assets = BookAssets(
                book_id=metadata.get('book_id', 'unknown'),
                title=metadata.get('title', metadata.get('topic', 'Untitled')),
                subtitle=metadata.get('subtitle'),
                description=description or metadata.get('description', ''),
                keywords=keywords,
                categories=metadata.get('categories', []),
                manuscript_path=manuscript_path,
                cover_path=cover_path,
                author_name=metadata.get('author', 'AI Generated'),
                price=float(metadata.get('price', 2.99)),
                niche=metadata.get('niche', 'general')
            )
            
            # Login and publish
            if not self.login_to_kdp():
                raise Exception("Failed to login to KDP")
            
            return self.create_new_book(book_assets)
            
        except Exception as e:
            logger.error(f"Failed to publish book from assets: {e}")
            return PublishingResult(
                success=False,
                book_id="unknown",
                kdp_url=None,
                asin=None,
                errors=[str(e)],
                warnings=[],
                publishing_timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
            )


# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='KDP Publisher Agent - Automated Book Publishing')
    parser.add_argument('assets_path', help='Path to book assets directory')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--email', help='KDP email (or set KDP_EMAIL env var)')
    parser.add_argument('--password', help='KDP password (or set KDP_PASSWORD env var)')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        with KDPPublisherAgent(headless=args.headless, kdp_email=args.email, kdp_password=args.password) as agent:
            result = agent.publish_book_from_assets(args.assets_path)
            
            print(f"\n{'='*60}")
            print("PUBLISHING RESULT")
            print('='*60)
            print(f"Success: {'✅' if result.success else '❌'}")
            print(f"Book ID: {result.book_id}")
            if result.asin:
                print(f"ASIN: {result.asin}")
            if result.kdp_url:
                print(f"KDP URL: {result.kdp_url}")
            
            if result.errors:
                print(f"\nErrors:")
                for error in result.errors:
                    print(f"  ❌ {error}")
            
            if result.warnings:
                print(f"\nWarnings:")
                for warning in result.warnings:
                    print(f"  ⚠️ {warning}")
                    
    except Exception as e:
        print(f"❌ Publishing failed: {e}")
        exit(1)