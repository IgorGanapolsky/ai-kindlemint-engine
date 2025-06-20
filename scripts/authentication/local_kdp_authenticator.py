#!/usr/bin/env python3
"""
Local KDP Authentication Script
Handles manual login with CAPTCHA solving and exports session cookies
"""
import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kindlemint.utils.logger import get_logger

class LocalKDPAuthenticator:
    """Local authentication manager for KDP with cookie export."""
    
    def __init__(self):
        self.logger = get_logger('local_kdp_auth')
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
        """Setup visible browser for manual interaction."""
        try:
            from playwright.sync_api import sync_playwright
            
            self.logger.info("🔧 Setting up local browser for manual authentication...")
            
            self.playwright = sync_playwright().start()
            
            # Launch visible browser for manual interaction
            self.browser = self.playwright.chromium.launch(
                headless=False,  # Always visible for manual interaction
                slow_mo=500,     # Slower for manual interaction
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
            
            self.page = self.context.new_page()
            
            self.logger.info("✅ Local browser setup complete")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Browser setup failed: {e}")
            return False
    
    def manual_login(self):
        """Perform manual login with CAPTCHA solving capability."""
        try:
            self.logger.info("🔐 Starting manual KDP authentication...")
            self.logger.info("👤 You will need to manually solve any CAPTCHAs that appear")
            
            # Navigate to KDP
            self.logger.info("🌐 Navigating to KDP...")
            self.page.goto("https://kdp.amazon.com", wait_until="domcontentloaded")
            
            # Wait for page to load
            time.sleep(3)
            
            # Look for sign-in button
            self.logger.info("🔍 Looking for sign-in button...")
            sign_in_selectors = [
                'a[href*="signin"]',
                'button:has-text("Sign in")',
                'a:has-text("Sign in")',
                '.signin-button',
                '[data-testid="signin"]'
            ]
            
            signed_in = False
            for selector in sign_in_selectors:
                try:
                    if self.page.wait_for_selector(selector, timeout=5000):
                        self.logger.info(f"🎯 Found sign-in button: {selector}")
                        self.page.click(selector)
                        time.sleep(3)
                        break
                except:
                    continue
            else:
                # Check if already signed in
                success_indicators = [
                    'text="Create New Title"',
                    'text="Bookshelf"',
                    '.kdp-dashboard'
                ]
                
                for indicator in success_indicators:
                    try:
                        if self.page.wait_for_selector(indicator, timeout=5000):
                            self.logger.info("✅ Already signed into KDP!")
                            signed_in = True
                            break
                    except:
                        continue
            
            if not signed_in:
                # Fill email
                self.logger.info("📧 Filling email field...")
                email_selectors = [
                    'input[name="email"]',
                    'input[type="email"]',
                    '#ap_email',
                    'input[autocomplete="username"]'
                ]
                
                for selector in email_selectors:
                    try:
                        if self.page.wait_for_selector(selector, timeout=5000):
                            self.page.fill(selector, self.kdp_email)
                            self.logger.info("✅ Email filled")
                            break
                    except:
                        continue
                
                # Click continue
                self.logger.info("➡️ Clicking continue...")
                continue_selectors = [
                    'input[type="submit"]',
                    'button[type="submit"]',
                    '#continue',
                    'button:has-text("Continue")'
                ]
                
                for selector in continue_selectors:
                    try:
                        if self.page.wait_for_selector(selector, timeout=5000):
                            self.page.click(selector)
                            time.sleep(3)
                            break
                    except:
                        continue
                
                # Fill password
                self.logger.info("🔑 Filling password field...")
                password_selectors = [
                    'input[name="password"]',
                    'input[type="password"]',
                    '#ap_password'
                ]
                
                for selector in password_selectors:
                    try:
                        if self.page.wait_for_selector(selector, timeout=5000):
                            self.page.fill(selector, self.kdp_password)
                            self.logger.info("✅ Password filled")
                            break
                    except:
                        continue
                
                # Click sign in
                self.logger.info("🔓 Clicking sign in...")
                signin_selectors = [
                    'input[type="submit"]',
                    'button[type="submit"]',
                    '#signInSubmit',
                    'button:has-text("Sign in")'
                ]
                
                for selector in signin_selectors:
                    try:
                        if self.page.wait_for_selector(selector, timeout=5000):
                            self.page.click(selector)
                            time.sleep(5)
                            break
                    except:
                        continue
            
            # Wait for manual CAPTCHA solving
            self.logger.info("🧩 MANUAL INTERVENTION REQUIRED:")
            self.logger.info("👀 Please solve any CAPTCHAs or verification challenges in the browser window")
            self.logger.info("⏳ Waiting for you to reach the KDP dashboard...")
            
            # Monitor for successful login
            success_indicators = [
                'text="Create New Title"',
                '[data-testid="create-new-title"]',
                '.kdp-dashboard',
                '.bookshelf',
                'text="Bookshelf"',
                'text="KDP Select"'
            ]
            
            # Wait up to 10 minutes for manual intervention
            for attempt in range(120):  # 120 * 5 seconds = 10 minutes
                try:
                    current_url = self.page.url
                    self.logger.debug(f"Current URL: {current_url}")
                    
                    # Check for KDP dashboard indicators
                    for indicator in success_indicators:
                        try:
                            if self.page.wait_for_selector(indicator, timeout=2000):
                                self.logger.info(f"✅ Successfully reached KDP dashboard! Found: {indicator}")
                                return True
                        except:
                            continue
                    
                    # Log progress every minute
                    if attempt % 12 == 0:  # Every 12th attempt (1 minute)
                        remaining_minutes = (120 - attempt) // 12
                        self.logger.info(f"⏰ Still waiting for manual login completion... ({remaining_minutes} minutes remaining)")
                    
                    time.sleep(5)  # Wait 5 seconds between checks
                    
                except Exception as e:
                    self.logger.debug(f"Error during login monitoring: {e}")
                    time.sleep(5)
                    continue
            
            self.logger.error("⏰ Timeout waiting for manual login completion (10 minutes)")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Manual login failed: {e}")
            return False
    
    def export_cookies(self):
        """Export session cookies to encrypted file."""
        try:
            self.logger.info("🍪 Exporting session cookies...")
            
            # Get all cookies from the context
            cookies = self.context.cookies()
            
            # Create cookie export data
            cookie_data = {
                "timestamp": datetime.now().isoformat(),
                "expiry": (datetime.now() + timedelta(days=30)).isoformat(),
                "cookies": cookies,
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            # Save to encrypted file
            cookie_file = Path("kdp_session_cookies.json")
            with open(cookie_file, 'w') as f:
                json.dump(cookie_data, f, indent=2)
            
            self.logger.info(f"✅ Session cookies exported to: {cookie_file}")
            self.logger.info("🔐 Next step: Upload this file as a GitHub Secret")
            
            return str(cookie_file)
            
        except Exception as e:
            self.logger.error(f"❌ Cookie export failed: {e}")
            return None
    
    def cleanup(self):
        """Clean up browser resources."""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except:
            pass

def main():
    """Main execution function."""
    print("=" * 80)
    print("🔐 LOCAL KDP AUTHENTICATION & COOKIE EXPORT")
    print("=" * 80)
    print("📋 This script will:")
    print("   1. Open a visible browser window")
    print("   2. Navigate to Amazon KDP")
    print("   3. Allow you to manually login and solve CAPTCHAs")
    print("   4. Export session cookies for automation")
    print("=" * 80)
    
    authenticator = LocalKDPAuthenticator()
    
    try:
        # Setup browser
        if not authenticator.setup_browser():
            print("❌ Browser setup failed")
            return False
        
        # Perform manual login
        if not authenticator.manual_login():
            print("❌ Manual login failed")
            return False
        
        # Export cookies
        cookie_file = authenticator.export_cookies()
        if not cookie_file:
            print("❌ Cookie export failed")
            return False
        
        print("\n" + "=" * 80)
        print("🎉 AUTHENTICATION COMPLETE!")
        print("=" * 80)
        print(f"✅ Session cookies saved to: {cookie_file}")
        print("📤 Next steps:")
        print("   1. Upload kdp_session_cookies.json as GitHub Secret 'KDP_SESSION_COOKIES'")
        print("   2. Run the autonomous publishing workflow")
        print("   3. Cookies valid for ~30 days")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        return False
    
    finally:
        authenticator.cleanup()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)