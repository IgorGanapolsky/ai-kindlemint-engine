#!/usr/bin/env python3
"""
Robust KDP Publisher - Adaptive Interface Automation
Built to handle KDP interface changes and modern web elements
"""
import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kindlemint.utils.logger import get_logger

class RobustKDPPublisher:
    """Enhanced KDP publisher with adaptive interface handling."""
    
    def __init__(self):
        self.logger = get_logger('robust_kdp')
        self.page = None
        self.browser = None
        self.context = None
        self.playwright = None
        
        # Load credentials
        self._load_credentials()
        
    def _load_credentials(self):
        """Load credentials from .env file."""
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#') and '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        
        self.kdp_email = os.getenv('KDP_EMAIL')
        self.kdp_password = os.getenv('KDP_PASSWORD')
        
        if not self.kdp_email or not self.kdp_password:
            raise ValueError("KDP credentials not found in environment")
    
    def setup_browser(self):
        """Setup browser with modern anti-detection measures."""
        try:
            from playwright.sync_api import sync_playwright
            
            self.logger.info("🔧 Setting up robust browser session...")
            
            self.playwright = sync_playwright().start()
            
            # Launch browser with modern settings
            self.browser = self.playwright.chromium.launch(
                headless=False,  # Visible for monitoring
                slow_mo=1000,    # Slower for reliability
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions',
                    '--no-first-run',
                    '--disable-default-apps'
                ]
            )
            
            # Create context with realistic settings
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York'
            )
            
            # Create page with extended timeouts
            self.page = self.context.new_page()
            self.page.set_default_timeout(60000)  # 60 seconds
            self.page.set_default_navigation_timeout(60000)
            
            self.logger.info("✅ Browser setup complete")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Browser setup failed: {e}")
            return False
    
    def smart_wait_and_click(self, selectors, timeout=30000, description="element"):
        """Smart waiting with multiple selector fallbacks."""
        if isinstance(selectors, str):
            selectors = [selectors]
        
        self.logger.info(f"🔍 Looking for {description}...")
        
        for i, selector in enumerate(selectors):
            try:
                self.logger.info(f"   Trying selector {i+1}: {selector[:50]}...")
                
                # Wait for element and check visibility
                self.page.wait_for_selector(selector, timeout=timeout//len(selectors))
                
                # Use page.click() method directly
                self.page.click(selector)
                self.logger.info(f"✅ Found and clicked {description} with selector {i+1}")
                time.sleep(2)  # Wait for action to complete
                return True
                
            except Exception as e:
                self.logger.warning(f"   Selector {i+1} failed: {str(e)[:100]}")
                continue
        
        self.logger.error(f"❌ Could not find {description} with any selector")
        return False
    
    def smart_fill(self, selectors, value, description="field"):
        """Smart form filling with multiple selector fallbacks."""
        if isinstance(selectors, str):
            selectors = [selectors]
        
        self.logger.info(f"📝 Filling {description}...")
        
        for i, selector in enumerate(selectors):
            try:
                # Wait for element to be visible
                self.page.wait_for_selector(selector, timeout=10000)
                
                # Clear and fill using page methods
                self.page.fill(selector, "")  # Clear field
                time.sleep(0.5)  # Brief pause
                self.page.fill(selector, value)  # Fill with value
                
                # Verify the value was entered
                filled_value = self.page.input_value(selector)
                if filled_value == value:
                    self.logger.info(f"✅ Filled {description}")
                    return True
                else:
                    self.logger.warning(f"   Value verification failed for {description}")
                    
            except Exception as e:
                self.logger.warning(f"   Fill attempt {i+1} failed: {str(e)[:100]}")
                continue
        
        self.logger.error(f"❌ Could not fill {description}")
        return False
    
    def adaptive_login(self):
        """Adaptive login handling for modern KDP interface."""
        try:
            self.logger.info("🔐 Starting adaptive KDP login...")
            
            # Navigate to KDP with multiple URL attempts
            kdp_urls = [
                'https://kdp.amazon.com',
                'https://kdp.amazon.com/en_US',
                'https://kdp.amazon.com/signin'
            ]
            
            for url in kdp_urls:
                try:
                    self.logger.info(f"🌐 Trying URL: {url}")
                    self.page.goto(url, wait_until='domcontentloaded')
                    time.sleep(3)
                    break
                except Exception as e:
                    self.logger.warning(f"URL {url} failed: {e}")
                    continue
            
            # Look for sign-in elements with modern selectors
            signin_selectors = [
                'a[href*="signin"]',
                'button:has-text("Sign in")',
                'a:has-text("Sign in")',
                '.sign-in-button',
                '#signin-button',
                '[data-testid="signin"]',
                'button[type="submit"]:has-text("Sign")',
                'a[href*="auth"]'
            ]
            
            if self.smart_wait_and_click(signin_selectors, description="sign-in button"):
                time.sleep(3)
            
            # Email field with modern selectors
            email_selectors = [
                'input[name="email"]',
                'input[type="email"]',
                '#ap_email',
                'input[autocomplete="email"]',
                'input[placeholder*="email"]',
                'input[aria-label*="email"]',
                '[data-testid="email"]'
            ]
            
            if not self.smart_fill(email_selectors, self.kdp_email, "email field"):
                return False
            
            # Continue/Next button after email
            continue_selectors = [
                'input[type="submit"]',
                'button[type="submit"]',
                '#continue',
                'button:has-text("Continue")',
                'button:has-text("Next")',
                '.a-button-primary'
            ]
            
            self.smart_wait_and_click(continue_selectors, description="continue button")
            time.sleep(3)
            
            # Password field
            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                '#ap_password',
                'input[autocomplete="current-password"]',
                '[data-testid="password"]'
            ]
            
            if not self.smart_fill(password_selectors, self.kdp_password, "password field"):
                return False
            
            # Sign in button
            signin_submit_selectors = [
                'input[type="submit"]',
                'button[type="submit"]',
                '#signInSubmit',
                'button:has-text("Sign in")',
                '.a-button-primary'
            ]
            
            if not self.smart_wait_and_click(signin_submit_selectors, description="sign-in submit"):
                return False
            
            # Wait for dashboard or handle 2FA
            self.logger.info("⏳ Waiting for login completion...")
            
            # Check for successful login indicators
            success_indicators = [
                'text="Create New Title"',
                '[data-testid="create-new-title"]',
                '.kdp-dashboard',
                '.bookshelf',
                'text="Bookshelf"',
                'text="KDP Select"'
            ]
            
            for indicator in success_indicators:
                try:
                    self.page.wait_for_selector(indicator, timeout=15000)
                    self.logger.info("✅ Successfully logged into KDP!")
                    return True
                except:
                    continue
            
            # Check for 2FA
            twofa_indicators = [
                'text="Two-Step Verification"',
                'text="Enter the code"',
                'input[name="otpCode"]',
                'text="verification code"'
            ]
            
            for indicator in twofa_indicators:
                try:
                    if self.page.locator(indicator).is_visible():
                        self.logger.warning("🔐 2FA detected - manual intervention required")
                        self.logger.info("📱 Please enter your 2FA code in the browser")
                        self.logger.info("⏳ Waiting for 2FA completion...")
                        
                        # Wait for 2FA completion
                        for success_indicator in success_indicators:
                            try:
                                self.page.wait_for_selector(success_indicator, timeout=120000)  # 2 minute timeout
                                self.logger.info("✅ 2FA completed, login successful!")
                                return True
                            except:
                                continue
                        
                        self.logger.error("❌ 2FA timeout")
                        return False
                except:
                    continue
            
            self.logger.error("❌ Login verification failed")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Adaptive login failed: {e}")
            return False
    
    def create_paperback_book(self, book_data):
        """Create new paperback book with adaptive interface handling."""
        try:
            self.logger.info("📚 Creating new paperback book...")
            
            # Find and click Create New Title
            create_selectors = [
                'text="Create New Title"',
                '[data-testid="create-new-title"]',
                'button:has-text("Create")',
                '.create-new-title',
                'a[href*="create"]'
            ]
            
            if not self.smart_wait_and_click(create_selectors, description="Create New Title"):
                return False
            
            # Select Paperback
            paperback_selectors = [
                'text="Paperback"',
                'button:has-text("Paperback")',
                'a:has-text("Paperback")',
                '[data-testid="paperback"]',
                '.paperback-option'
            ]
            
            if not self.smart_wait_and_click(paperback_selectors, description="Paperback option"):
                return False
            
            self.logger.info("✅ Paperback book creation initiated")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Book creation failed: {e}")
            return False
    
    def fill_book_details(self, book_data):
        """Fill book details with enhanced field detection."""
        try:
            self.logger.info("📝 Filling book details...")
            
            # Title field
            title_selectors = [
                'input[name="title"]',
                '#title',
                '[data-testid="title"]',
                'input[placeholder*="title"]',
                'input[aria-label*="title"]'
            ]
            
            if not self.smart_fill(title_selectors, book_data['title'], "book title"):
                return False
            
            # Subtitle field
            subtitle_selectors = [
                'input[name="subtitle"]',
                '#subtitle',
                '[data-testid="subtitle"]',
                'input[placeholder*="subtitle"]'
            ]
            
            self.smart_fill(subtitle_selectors, book_data.get('subtitle', ''), "subtitle")
            
            # Author field
            author_selectors = [
                'input[name="author"]',
                '#author',
                '[data-testid="author"]',
                'input[placeholder*="author"]'
            ]
            
            if not self.smart_fill(author_selectors, book_data['author'], "author name"):
                return False
            
            # Description field
            description_selectors = [
                'textarea[name="description"]',
                '#description',
                '[data-testid="description"]',
                'textarea[placeholder*="description"]'
            ]
            
            if not self.smart_fill(description_selectors, book_data['description'], "description"):
                return False
            
            self.logger.info("✅ Book details filled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to fill book details: {e}")
            return False
    
    def publish_volume_1(self):
        """Complete Volume 1 publishing workflow."""
        try:
            # Setup browser
            if not self.setup_browser():
                return False
            
            # Login with adaptive handling
            if not self.adaptive_login():
                return False
            
            # Load Volume 1 data
            vol_1_folder = Path("output/generated_books/large_print_crossword_masters_vol_1_final")
            
            with open(vol_1_folder / "metadata.json", 'r') as f:
                metadata = json.load(f)
            
            with open(vol_1_folder / "KDP_PUBLISHING_GUIDE.txt", 'r') as f:
                guide_content = f.read()
            
            # Extract description
            desc_start = guide_content.find("→ Description:") + len("→ Description:")
            desc_end = guide_content.find("\n4. KEYWORDS")
            description = guide_content[desc_start:desc_end].strip()
            
            book_data = {
                'title': "Large Print Crossword Masters: Volume 1",
                'subtitle': "Easy Large Print Crosswords for Seniors",
                'author': "Senior Puzzle Studio",
                'description': description,
                'price': 7.99,
                'pdf_path': str(vol_1_folder / "large_print_crossword_masters_vol_1_final_KDP_READY.pdf"),
                'cover_path': str(vol_1_folder / "cover_vol_1.png")
            }
            
            # Create book
            if not self.create_paperback_book(book_data):
                return False
            
            # Fill details
            if not self.fill_book_details(book_data):
                return False
            
            self.logger.info("🎉 Volume 1 setup completed!")
            self.logger.info("📋 Manual steps required:")
            self.logger.info("   1. Upload PDF manuscript")
            self.logger.info("   2. Upload cover image")
            self.logger.info("   3. Set keywords and categories")
            self.logger.info("   4. Configure pricing")
            self.logger.info("   5. Review and publish")
            
            # Keep browser open for manual completion
            input("\n📋 Press Enter when you've completed the manual steps...")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Publishing workflow failed: {e}")
            return False
        
        finally:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()

def main():
    """Main execution function."""
    print("=" * 80)
    print("🤖 ROBUST KDP PUBLISHER - ADAPTIVE AUTOMATION")
    print("=" * 80)
    print("📚 Publishing: Large Print Crossword Masters: Volume 1")
    print("🔧 Enhanced interface adaptation")
    print("🛡️ Modern anti-detection measures")
    print("=" * 80)
    
    try:
        publisher = RobustKDPPublisher()
        success = publisher.publish_volume_1()
        
        if success:
            print("\n🎉 ROBUST PUBLISHING WORKFLOW COMPLETED!")
            print("✅ Book setup successful")
        else:
            print("\n❌ PUBLISHING WORKFLOW FAILED!")
            print("💡 Check logs for details")
        
        return success
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)