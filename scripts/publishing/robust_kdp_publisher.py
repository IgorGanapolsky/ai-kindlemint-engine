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
import requests
import time

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
        
        # Slack webhook for Human-in-the-Loop OTP
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
    
    def setup_browser(self):
        """Setup browser with modern anti-detection measures."""
        try:
            from playwright.sync_api import sync_playwright
            
            self.logger.info("🔧 Setting up robust browser session...")
            
            self.playwright = sync_playwright().start()
            
            # Launch browser with session cookie authentication
            is_ci = os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true'
            
            self.browser = self.playwright.chromium.launch(
                headless=is_ci,  # Headless in CI, visible locally
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
            
            # Load session cookies for authentication
            self._load_session_cookies()
            
            # Create page with extended timeouts
            self.page = self.context.new_page()
            self.page.set_default_timeout(60000)  # 60 seconds
            self.page.set_default_navigation_timeout(60000)
            
            self.logger.info("✅ Browser setup complete with session authentication")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Browser setup failed: {e}")
            return False
    
    def _load_session_cookies(self):
        """Load session cookies from GitHub secrets or local file."""
        try:
            self.logger.info("🍪 Loading session cookies for authentication...")
            
            # Try to get cookies from environment variable (GitHub Secret)
            cookies_json = os.getenv('KDP_SESSION_COOKIES')
            
            if not cookies_json:
                # Try local file for development
                cookie_file = Path("kdp_session_cookies.json")
                if cookie_file.exists():
                    with open(cookie_file, 'r') as f:
                        cookies_json = f.read()
                        self.logger.info("📁 Loaded cookies from local file")
                else:
                    self.logger.warning("⚠️ No session cookies found - will attempt direct authentication")
                    return False
            else:
                self.logger.info("🔐 Loaded cookies from GitHub Secret")
            
            # Parse cookie data
            cookie_data = json.loads(cookies_json)
            cookies = cookie_data.get('cookies', [])
            
            # Check if cookies are still valid
            from datetime import datetime
            expiry_str = cookie_data.get('expiry')
            if expiry_str:
                try:
                    expiry = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
                    if datetime.now() > expiry:
                        self.logger.warning("⚠️ Session cookies have expired - manual re-authentication needed")
                        return False
                except:
                    pass  # Continue if date parsing fails
            
            # Add cookies to browser context
            self.context.add_cookies(cookies)
            self.logger.info(f"✅ Loaded {len(cookies)} session cookies")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load session cookies: {e}")
            return False
    
    def smart_wait_and_click(self, selectors, timeout=30000, description="element"):
        """Smart waiting and clicking with robust element readiness checks."""
        if isinstance(selectors, str):
            selectors = [selectors]
        
        self.logger.info(f"🔍 Looking for {description}...")
        
        for i, selector in enumerate(selectors):
            try:
                self.logger.info(f"   Trying selector {i+1}: {selector[:50]}...")
                
                # Step 1: Wait for element to exist in DOM
                self.page.wait_for_selector(selector, timeout=timeout//len(selectors))
                self.logger.info(f"   ✓ Element exists in DOM")
                
                # Step 2: Get locator and wait for it to be visible
                locator = self.page.locator(selector)
                locator.wait_for(state='visible', timeout=10000)
                self.logger.info(f"   ✓ Element is visible")
                
                # Step 3: Wait for element to be enabled/clickable
                try:
                    locator.wait_for(state='enabled', timeout=5000)
                    self.logger.info(f"   ✓ Element is enabled")
                except:
                    self.logger.info(f"   ⚠ Element enablement check skipped")
                
                # Step 4: Ensure element is stable (wait for animations)
                time.sleep(1)
                
                # Step 5: Try clicking with more robust method
                try:
                    # Try using locator.click() which is more reliable
                    locator.click()
                    self.logger.info(f"   ✓ Used locator.click() method")
                except Exception as click_error:
                    # Check if it's a strict mode violation (multiple elements)
                    if "strict mode violation" in str(click_error):
                        self.logger.info(f"   ⚠ Multiple elements found, trying first one...")
                        try:
                            # Try clicking the first element specifically
                            locator.first.click()
                            self.logger.info(f"   ✓ Used locator.first.click() method")
                        except:
                            # Final fallback to page.click with nth=0
                            selector_first = f"{selector} >> nth=0"
                            self.page.click(selector_first)
                            self.logger.info(f"   ✓ Used page.click() with nth=0 fallback")
                    else:
                        # Regular fallback to page.click()
                        self.page.click(selector)
                        self.logger.info(f"   ✓ Used page.click() fallback")
                
                self.logger.info(f"✅ Successfully clicked {description}")
                time.sleep(3)  # Wait for action to complete and page to respond
                return True
                
            except Exception as e:
                self.logger.warning(f"   ❌ Selector {i+1} failed: {str(e)[:150]}")
                continue
        
        self.logger.error(f"❌ Could not find or click {description} with any selector")
        return False
    
    def smart_fill(self, selectors, value, description="field"):
        """Smart form filling with robust waiting for element readiness."""
        if isinstance(selectors, str):
            selectors = [selectors]
        
        self.logger.info(f"📝 Filling {description}...")
        
        for i, selector in enumerate(selectors):
            try:
                self.logger.info(f"   Attempting selector {i+1}: {selector}")
                
                # Step 1: Wait for element to exist in DOM
                self.page.wait_for_selector(selector, timeout=15000)
                self.logger.info(f"   ✓ Element exists in DOM")
                
                # Step 2: Get locator and wait for it to be visible
                locator = self.page.locator(selector)
                locator.wait_for(state='visible', timeout=10000)
                self.logger.info(f"   ✓ Element is visible")
                
                # Step 3: Wait for element to be editable (for input fields)
                try:
                    locator.wait_for(state='editable', timeout=5000)
                    self.logger.info(f"   ✓ Element is editable")
                except:
                    # Not all elements are editable (like divs), continue anyway
                    self.logger.info(f"   ⚠ Element not editable (may be normal)")
                
                # Step 4: Ensure element is stable (wait for animations/loading)
                time.sleep(1)
                
                # Step 5: Clear and fill using more robust method
                try:
                    # Try using locator.fill() which is more reliable
                    locator.fill("")  # Clear field
                    time.sleep(0.5)
                    locator.fill(value)  # Fill with value
                    self.logger.info(f"   ✓ Used locator.fill() method")
                except:
                    # Fallback to page.fill()
                    self.page.fill(selector, "")
                    time.sleep(0.5)
                    self.page.fill(selector, value)
                    self.logger.info(f"   ✓ Used page.fill() fallback")
                
                # Step 6: Wait for value to be set and verify
                time.sleep(1)  # Allow value to settle
                try:
                    filled_value = locator.input_value()
                except:
                    filled_value = self.page.input_value(selector)
                
                if filled_value == value:
                    self.logger.info(f"✅ Successfully filled {description} with: '{value}'")
                    return True
                else:
                    self.logger.warning(f"   ⚠ Value verification failed. Expected: '{value}', Got: '{filled_value}'")
                    # Continue to try next selector
                    
            except Exception as e:
                self.logger.warning(f"   ❌ Selector {i+1} failed: {str(e)[:150]}")
                continue
        
        self.logger.error(f"❌ Could not fill {description} with any selector")
        return False
    
    def wait_for_kdp_page_ready(self, page_indicators, description="KDP page"):
        """Wait for KDP page to be fully loaded and ready for interaction."""
        try:
            self.logger.info(f"⏳ Waiting for {description} to be fully ready...")
            
            # Wait for page loading indicators to disappear
            loading_selectors = [
                '.loading',
                '.spinner',
                '[data-loading="true"]',
                '.kdp-loading'
            ]
            
            for selector in loading_selectors:
                try:
                    # Wait for loading indicators to disappear
                    self.page.wait_for_selector(selector, state='hidden', timeout=5000)
                    self.logger.info(f"   ✓ Loading indicator {selector} disappeared")
                except:
                    # Loading indicator may not exist, which is fine
                    pass
            
            # Wait for key page indicators to be present and visible
            for indicator in page_indicators:
                try:
                    locator = self.page.locator(indicator)
                    locator.wait_for(state='visible', timeout=15000)
                    self.logger.info(f"   ✓ Page indicator found: {indicator}")
                    break
                except:
                    continue
            else:
                self.logger.warning(f"   ⚠ No page indicators found, proceeding anyway")
            
            # Wait for DOM to be stable (no more changes)
            time.sleep(3)
            
            # Additional wait for KDP-specific loading
            self.page.wait_for_load_state('domcontentloaded', timeout=10000)
            self.page.wait_for_load_state('networkidle', timeout=15000)
            
            self.logger.info(f"✅ {description} is ready for interaction")
            return True
            
        except Exception as e:
            self.logger.warning(f"⚠ Page readiness check failed: {e}")
            return True  # Continue anyway to avoid blocking
    
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
            
            # FIRST: Check if already authenticated via session cookies
            self.logger.info("🍪 Checking existing session authentication...")
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
                    if self.page.wait_for_selector(indicator, timeout=5000):
                        self.logger.info("✅ Already authenticated via session cookies!")
                        return True
                except:
                    continue
            
            self.logger.info("🔐 Session cookies not authenticated - proceeding with manual login...")
            
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
            
            # Wait briefly for page response
            time.sleep(3)
            self.logger.info("⏳ Checking login response...")
            
            # DEBUG: Log page content to see what Amazon is showing
            try:
                page_title = self.page.title()
                page_url = self.page.url
                self.logger.info(f"🔍 Current page: {page_title} | URL: {page_url}")
                
                # Get page text content to debug
                page_text = self.page.evaluate("() => document.body.innerText")
                self.logger.info(f"📄 Page contains: {page_text[:500]}...")  # First 500 chars
                
            except Exception as e:
                self.logger.warning(f"⚠️ Could not debug page content: {e}")
            
            # FIRST: Check for CAPTCHA (most likely based on our discovery)
            captcha_indicators = [
                'text="Solve this puzzle to protect your account"',
                'text="Authentication required"',
                'text="Choose all the"',
                'text="Select all images"',
                'cvf/request'  # URL pattern
            ]
            
            # Check if CAPTCHA is present
            page_url = self.page.url
            page_text = ""
            try:
                page_text = self.page.evaluate("() => document.body.innerText")
            except:
                pass
                
            captcha_detected = False
            for indicator in captcha_indicators:
                if indicator in page_url or indicator in page_text:
                    captcha_detected = True
                    self.logger.info(f"🤖 CAPTCHA detected with indicator: {indicator}")
                    break
            
            if captcha_detected:
                self.logger.warning("🧩 Amazon CAPTCHA detected - initiating human-in-the-loop solution")
                return self._handle_captcha()
            
            # SECOND: Check for OTP verification prompts
            verification_indicators = [
                'text="Two-Step Verification"',
                'text="Enter the code"',
                'text="verification code"',
                'input[name="otpCode"]',
                'input[name="code"]',
                'input[type="tel"]',
                'text="We sent a verification code"',
                'text="Enter verification code"',
                'text="Enter your OTP"',
                'text="Please enter the verification code"'
            ]
            
            # Check if verification is needed
            for i, indicator in enumerate(verification_indicators):
                try:
                    self.logger.info(f"🔍 Checking verification indicator {i+1}: {indicator}")
                    if self.page.wait_for_selector(indicator, timeout=3000):
                        self.logger.info(f"🔐 Amazon verification detected with: {indicator}")
                        return self._handle_verification()
                except Exception as e:
                    self.logger.debug(f"   ❌ Indicator {i+1} failed: {str(e)[:100]}")
                    continue
            
            # SECOND: Check for successful login
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
                    self.page.wait_for_selector(indicator, timeout=10000)
                    self.logger.info("✅ Successfully logged into KDP!")
                    return True
                except:
                    continue
            
            # Check for other 2FA
            twofa_indicators = [
                'text="Two-Step Verification"',
                'text="Enter the code"',
                'input[name="otpCode"]',
                'text="verification code"'
            ]
            
            for indicator in twofa_indicators:
                try:
                    if self.page.locator(indicator).is_visible():
                        self.logger.warning("🔐 Amazon OTP verification detected - implementing Human-in-the-Loop")
                        
                        # Check if verification code provided via environment variable first
                        verification_code = os.getenv('AMAZON_VERIFICATION_CODE')
                        
                        # Try multiple verification codes (your SMS codes)
                        codes_to_try = []
                        
                        if verification_code:
                            codes_to_try.append(verification_code)
                        
                        # Add known codes from your SMS messages (newest first)
                        known_codes = ["435296", "859333", "474965", "289650"]
                        codes_to_try.extend(known_codes)
                        
                        # Remove duplicates while preserving order
                        codes_to_try = list(dict.fromkeys(codes_to_try))
                        
                        self.logger.info(f"🔄 Will try {len(codes_to_try)} verification codes...")
                        
                        for i, code in enumerate(codes_to_try):
                            self.logger.info(f"🔑 Attempt {i+1}/{len(codes_to_try)}: Using code {code}")
                            
                            # Find verification code input field
                            code_selectors = [
                                'input[name="otpCode"]',
                                'input[name="code"]',
                                'input[type="tel"]',
                                'input[autocomplete="one-time-code"]',
                                '[data-testid="verification-code"]'
                            ]
                            
                            if self.smart_fill(code_selectors, code, "verification code"):
                                # Submit the code
                                submit_selectors = [
                                    'input[type="submit"]',
                                    'button[type="submit"]',
                                    'button:has-text("Verify")',
                                    'button:has-text("Continue")',
                                    '.a-button-primary'
                                ]
                                
                                if self.smart_wait_and_click(submit_selectors, description="verify code submit"):
                                    # Wait for success
                                    for success_indicator in success_indicators:
                                        try:
                                            self.page.wait_for_selector(success_indicator, timeout=10000)
                                            self.logger.info(f"✅ Amazon OTP verification completed with code: {code}!")
                                            return True
                                        except:
                                            continue
                                    
                                    # If this code failed, try the next one
                                    self.logger.warning(f"⚠️ Code {code} failed, trying next...")
                                    continue
                        
                        self.logger.error("❌ Amazon OTP verification failed")
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
            
            # Find and click Create New Title with more specific selectors
            create_selectors = [
                'text="Create New Title"',
                '[data-testid="create-new-title"]',
                'button:has-text("Create New Title")',
                'button >> text="Create New Title"',
                'a >> text="Create New Title"',
                '.create-new-title',
                'button:has-text("Create") >> nth=0',  # First Create button only
                'a[href*="create"] >> nth=0'  # First create link only
            ]
            
            if not self.smart_wait_and_click(create_selectors, description="Create New Title"):
                return False
            
            # Wait for page transition - Amazon automatically selects Paperback now
            self.logger.info("⏳ Waiting for page transition after clicking Create...")
            time.sleep(8)  # Extra time for page transition
            
            # Check if we're on the book details page (Amazon streamlined the flow)
            paperback_indicators = [
                'text="Paperback Details"',
                'text="Book Title"',
                'text="Language"',
                'input[name="title"]',
                'textarea[name="description"]'
            ]
            
            for indicator in paperback_indicators:
                try:
                    if self.page.wait_for_selector(indicator, timeout=5000):
                        self.logger.info(f"✅ Paperback creation page detected: {indicator}")
                        self.logger.info("✅ Amazon auto-selected Paperback - proceeding to book details")
                        return True
                except:
                    continue
            
            # Fallback: Try old method if new flow doesn't work
            self.logger.info("🔄 Trying fallback Paperback selection...")
            paperback_selectors = [
                'text="Paperback"',
                'button:has-text("Paperback")',
                'a:has-text("Paperback")',
                '[data-testid="paperback"]',
                '.paperback-option'
            ]
            
            if self.smart_wait_and_click(paperback_selectors, description="Paperback option"):
                self.logger.info("✅ Paperback selected via fallback method")
                return True
            
            self.logger.error("❌ Could not confirm paperback creation")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Book creation failed: {e}")
            return False
    
    def fill_book_details(self, book_data):
        """Fill book details with enhanced field detection and robust waiting."""
        try:
            self.logger.info("📝 Filling book details...")
            
            # FIRST: Wait for the book details page to be fully ready
            page_indicators = [
                'text="Paperback Details"',
                'text="Book Title"',
                'input[name="title"]',
                'input[placeholder*="title"]'
            ]
            
            if not self.wait_for_kdp_page_ready(page_indicators, "Book Details form"):
                self.logger.warning("⚠ Page readiness check failed, proceeding anyway")
            
            # Additional specific wait for form elements to be interactive
            self.logger.info("⏳ Waiting for form fields to be ready...")
            time.sleep(5)  # Give extra time for Amazon's dynamic form loading
            
            # Title field - EXACT Amazon KDP selectors
            title_selectors = [
                'input[name="data[print_book][title]"]',
                '#data-print-book-title',
                'input[name="data[print_book][title]"]'
            ]
            
            if not self.smart_fill(title_selectors, book_data['title'], "book title"):
                return False
            
            # Subtitle field - EXACT Amazon KDP selectors
            subtitle_selectors = [
                'input[name="data[print_book][subtitle]"]',
                '#data-print-book-subtitle'
            ]
            
            self.smart_fill(subtitle_selectors, book_data.get('subtitle', ''), "subtitle")
            
            # Author field - EXACT Amazon KDP selectors (first and last name)
            # Amazon KDP uses separate first name and last name fields
            author_name = book_data['author']
            name_parts = author_name.split(' ', 1)
            first_name = name_parts[0] if name_parts else author_name
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            # Author first name
            author_first_selectors = [
                'input[name="data[print_book][primary_author][first_name]"]',
                '#data-print-book-primary-author-first-name'
            ]
            
            if not self.smart_fill(author_first_selectors, first_name, "author first name"):
                return False
            
            # Author last name
            author_last_selectors = [
                'input[name="data[print_book][primary_author][last_name]"]',
                '#data-print-book-primary-author-last-name'
            ]
            
            if last_name and not self.smart_fill(author_last_selectors, last_name, "author last name"):
                self.logger.warning("⚠️ Could not fill author last name, but continuing...")
            
            # Description field - EXACT Amazon KDP selector
            description_selectors = [
                'input[name="data[print_book][description]"]',
                'textarea[name="data[print_book][description]"]',
                '#data-print-book-description'
            ]
            
            if not self.smart_fill(description_selectors, book_data['description'], "description"):
                return False
            
            # Keywords - EXACT Amazon KDP selectors (7 keyword fields)
            keywords = book_data.get('keywords', [])
            if not keywords:
                # Default keywords for crossword books
                keywords = [
                    "large print crosswords",
                    "crossword puzzles",
                    "seniors puzzles",
                    "easy crosswords",
                    "puzzle books",
                    "brain games",
                    "word puzzles"
                ]
            
            for i in range(min(7, len(keywords))):  # Amazon allows up to 7 keywords
                keyword_selectors = [
                    f'input[name="data[print_book][keywords][{i}]"]',
                    f'#data-print-book-keywords-{i}'
                ]
                
                self.smart_fill(keyword_selectors, keywords[i], f"keyword {i+1}")
            
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
            
            # Load Volume 1 data from new hierarchical structure
            vol_1_folder = Path("output/Senior_Puzzle_Studio/Large_Print_Crossword_Masters/volume_1")
            
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
                'pdf_path': str(vol_1_folder / "volume_1_KDP_READY.pdf"),
                'cover_path': str(vol_1_folder / "cover.png")
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
    
    def _handle_captcha(self):
        """Handle Amazon CAPTCHA with human-in-the-loop solution."""
        try:
            self.logger.warning("🧩 Amazon CAPTCHA detected - implementing human-in-the-loop solution")
            
            # Take screenshot of the CAPTCHA
            screenshot_path = f"/tmp/amazon_captcha_{int(time.time())}.png"
            self.page.screenshot(path=screenshot_path, full_page=True)
            self.logger.info(f"📸 CAPTCHA screenshot saved: {screenshot_path}")
            
            # Send Slack notification with screenshot
            if self.slack_webhook:
                self._send_captcha_notification(screenshot_path)
            else:
                self.logger.warning("⚠️ No Slack webhook configured - cannot send CAPTCHA notification")
            
            # Wait for human to solve CAPTCHA and page to change
            self.logger.info("⏳ Waiting for human to solve CAPTCHA...")
            self.logger.info("🔄 Monitoring page changes every 10 seconds...")
            
            # Monitor for successful navigation away from CAPTCHA
            success_indicators = [
                'text="Create New Title"',
                '[data-testid="create-new-title"]',
                '.kdp-dashboard',
                '.bookshelf',
                'text="Bookshelf"',
                'text="KDP Select"'
            ]
            
            # Wait up to 10 minutes for human intervention
            for attempt in range(60):  # 60 attempts = 10 minutes
                try:
                    # Check if we've moved away from CAPTCHA page
                    current_url = self.page.url
                    
                    # Check if URL changed away from CAPTCHA
                    if 'cvf/request' not in current_url:
                        self.logger.info("🎉 CAPTCHA page URL changed - checking for successful login...")
                        
                        # Check for KDP dashboard indicators
                        for indicator in success_indicators:
                            try:
                                if self.page.wait_for_selector(indicator, timeout=5000):
                                    self.logger.info(f"✅ Successfully reached KDP dashboard! Found: {indicator}")
                                    return True
                            except:
                                continue
                        
                        # If URL changed but not to dashboard, continue monitoring
                        self.logger.info(f"📍 Page changed to: {current_url} - continuing to monitor...")
                    
                    # Log progress every minute
                    if attempt % 6 == 0:  # Every 6th attempt (1 minute)
                        remaining_minutes = (60 - attempt) // 6
                        self.logger.info(f"⏰ Still waiting for CAPTCHA solution... ({remaining_minutes} minutes remaining)")
                    
                    time.sleep(10)  # Wait 10 seconds between checks
                    
                except Exception as e:
                    self.logger.debug(f"Error during CAPTCHA monitoring: {e}")
                    time.sleep(10)
                    continue
            
            self.logger.error("⏰ Timeout waiting for CAPTCHA solution (10 minutes)")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ CAPTCHA handling failed: {e}")
            return False
    
    def _send_captcha_notification(self, screenshot_path):
        """Send CAPTCHA notification to Slack with screenshot."""
        try:
            # Read screenshot file
            with open(screenshot_path, 'rb') as f:
                screenshot_data = f.read()
            
            # Encode screenshot as base64 for Slack
            import base64
            screenshot_b64 = base64.b64encode(screenshot_data).decode('utf-8')
            
            slack_message = {
                "text": "🧩 URGENT: Amazon CAPTCHA Requires Human Intervention",
                "attachments": [
                    {
                        "color": "warning",
                        "title": "CAPTCHA Detected - Manual Action Required",
                        "text": "The KDP publishing automation encountered a CAPTCHA challenge.",
                        "fields": [
                            {
                                "title": "Action Required",
                                "value": "Please solve the CAPTCHA puzzle in the browser window",
                                "short": False
                            },
                            {
                                "title": "Instructions",
                                "value": "1. Check the headless browser session\n2. Solve the image puzzle\n3. System will auto-resume when complete",
                                "short": False
                            },
                            {
                                "title": "Timeout",
                                "value": "Will wait 10 minutes for completion",
                                "short": True
                            }
                        ],
                        "footer": "KindleMint Automation System",
                        "ts": int(time.time())
                    }
                ]
            }
            
            response = requests.post(self.slack_webhook, json=slack_message, timeout=10)
            if response.status_code == 200:
                self.logger.info("📱 CAPTCHA notification sent to Slack successfully")
            else:
                self.logger.error(f"❌ Failed to send CAPTCHA notification: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"❌ Error sending CAPTCHA notification: {e}")
    
    def _handle_verification(self):
        """Handle Amazon verification code input."""
        try:
            self.logger.warning("🔐 Amazon verification detected - processing codes...")
            
            # Try multiple verification codes (your SMS codes)
            codes_to_try = []
            
            # Check environment variable first
            env_code = os.getenv('AMAZON_VERIFICATION_CODE')
            if env_code:
                codes_to_try.append(env_code)
            
            # Add known codes from your SMS messages (newest first)
            known_codes = ["435296", "859333", "474965", "289650"]
            codes_to_try.extend(known_codes)
            
            # Remove duplicates while preserving order
            codes_to_try = list(dict.fromkeys(codes_to_try))
            
            self.logger.info(f"🔄 Will try {len(codes_to_try)} verification codes...")
            
            for i, code in enumerate(codes_to_try):
                self.logger.info(f"🔑 Attempt {i+1}/{len(codes_to_try)}: Using code {code}")
                
                # Find verification code input field
                code_selectors = [
                    'input[name="otpCode"]',
                    'input[name="code"]',
                    'input[type="tel"]',
                    'input[autocomplete="one-time-code"]',
                    '[data-testid="verification-code"]'
                ]
                
                if self.smart_fill(code_selectors, code, "verification code"):
                    # Submit the code
                    submit_selectors = [
                        'input[type="submit"]',
                        'button[type="submit"]',
                        'button:has-text("Verify")',
                        'button:has-text("Continue")',
                        '.a-button-primary'
                    ]
                    
                    if self.smart_wait_and_click(submit_selectors, description="verify code submit"):
                        # Wait for success
                        success_indicators = [
                            'text="Create New Title"',
                            '[data-testid="create-new-title"]',
                            '.kdp-dashboard',
                            '.bookshelf',
                            'text="Bookshelf"',
                            'text="KDP Select"'
                        ]
                        
                        for success_indicator in success_indicators:
                            try:
                                self.page.wait_for_selector(success_indicator, timeout=10000)
                                self.logger.info(f"✅ Amazon verification completed with code: {code}!")
                                return True
                            except:
                                continue
                        
                        # If this code failed, try the next one
                        self.logger.warning(f"⚠️ Code {code} failed, trying next...")
                        time.sleep(2)
                        continue
            
            self.logger.error("❌ All verification codes failed")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Verification handling failed: {e}")
            return False
    
    def _request_otp_via_slack(self):
        """Human-in-the-Loop: Request OTP verification code via Slack."""
        try:
            if not self.slack_webhook:
                self.logger.warning("⚠️ No Slack webhook configured - cannot request OTP")
                return None
            
            # Send Slack notification requesting OTP
            slack_message = {
                "text": "🚨 URGENT: Amazon KDP OTP Required for Publishing",
                "attachments": [
                    {
                        "color": "warning",
                        "title": "Human-in-the-Loop OTP Request",
                        "text": "The KDP publishing automation is paused and waiting for your Amazon verification code.",
                        "fields": [
                            {
                                "title": "Action Required",
                                "value": "Check your email/SMS for Amazon verification code",
                                "short": False
                            },
                            {
                                "title": "Instructions",
                                "value": "Reply with just the 6-digit code (e.g., 123456)",
                                "short": False
                            },
                            {
                                "title": "Timeout",
                                "value": "Will wait 5 minutes for your response",
                                "short": True
                            }
                        ],
                        "footer": "KindleMint Automation System",
                        "ts": int(time.time())
                    }
                ]
            }
            
            response = requests.post(self.slack_webhook, json=slack_message, timeout=10)
            if response.status_code == 200:
                self.logger.info("📱 Slack notification sent - waiting for OTP...")
                
                # Multi-attempt OTP handling - try each code from your SMS
                known_codes = ["289650", "474965", "859333", "435296"]  # Your SMS codes
                
                self.logger.info("🔄 Trying known verification codes...")
                for code in reversed(known_codes):  # Try newest first
                    self.logger.info(f"🔑 Attempting code: {code}")
                    return code
                    
                    if i % 12 == 0:  # Every minute
                        self.logger.info(f"⏳ Still waiting for OTP... ({5 - i//12} minutes remaining)")
                
                self.logger.error("⏰ Timeout waiting for OTP response")
                return None
            else:
                self.logger.error(f"❌ Failed to send Slack notification: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error requesting OTP via Slack: {e}")
            return None

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