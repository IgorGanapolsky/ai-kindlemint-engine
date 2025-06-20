#!/usr/bin/env python3
"""
KDP Interface Inspector - Debug what Amazon KDP interface actually shows
"""
import sys
import os
import json
import time
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kindlemint.utils.logger import get_logger

class KDPInterfaceInspector:
    """Debug tool to inspect Amazon KDP interface."""
    
    def __init__(self):
        self.logger = get_logger('kdp_inspector')
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
    
    def setup_browser(self):
        """Setup browser with session cookies."""
        try:
            from playwright.sync_api import sync_playwright
            
            self.logger.info("🔧 Setting up debug browser...")
            
            self.playwright = sync_playwright().start()
            
            self.browser = self.playwright.chromium.launch(
                headless=False,  # Always visible for debugging
                slow_mo=500
            )
            
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Load session cookies
            self._load_session_cookies()
            
            self.page = self.context.new_page()
            self.page.set_default_timeout(30000)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Browser setup failed: {e}")
            return False
    
    def _load_session_cookies(self):
        """Load session cookies from local file."""
        try:
            cookie_file = Path("kdp_session_cookies.json")
            if cookie_file.exists():
                with open(cookie_file, 'r') as f:
                    cookie_data = json.load(f)
                    cookies = cookie_data.get('cookies', [])
                    self.context.add_cookies(cookies)
                    self.logger.info(f"✅ Loaded {len(cookies)} session cookies")
                    return True
            else:
                self.logger.warning("⚠️ No session cookies found")
                return False
        except Exception as e:
            self.logger.error(f"❌ Failed to load session cookies: {e}")
            return False
    
    def inspect_kdp_interface(self):
        """Navigate to KDP and inspect the interface after clicking Create."""
        try:
            self.logger.info("🌐 Navigating to KDP...")
            self.page.goto("https://kdp.amazon.com", wait_until='domcontentloaded')
            time.sleep(3)
            
            self.logger.info("🔍 Looking for Create button...")
            create_selectors = [
                'button:has-text("Create")',
                'text="Create New Title"',
                '[data-testid="create-new-title"]',
                'a[href*="create"]'
            ]
            
            for selector in create_selectors:
                try:
                    if self.page.wait_for_selector(selector, timeout=10000):
                        self.logger.info(f"✅ Found Create button: {selector}")
                        self.page.click(selector)
                        time.sleep(5)
                        break
                except:
                    continue
            
            # Now inspect what's on the page
            self.logger.info("📄 Inspecting page content...")
            
            # Get page text
            page_text = self.page.evaluate("() => document.body.innerText")
            self.logger.info(f"📝 Page text: {page_text[:1000]}...")
            
            # Get page HTML for debugging
            page_html = self.page.content()
            debug_file = Path("debug_kdp_interface.html")
            with open(debug_file, 'w') as f:
                f.write(page_html)
            self.logger.info(f"💾 Saved page HTML to: {debug_file}")
            
            # Take a screenshot
            screenshot_file = Path("debug_kdp_interface.png")
            self.page.screenshot(path=str(screenshot_file), full_page=True)
            self.logger.info(f"📸 Saved screenshot to: {screenshot_file}")
            
            # Look for any buttons/links
            buttons = self.page.evaluate("""
                () => {
                    const buttons = Array.from(document.querySelectorAll('button, a, [role="button"]'));
                    return buttons.map(btn => ({
                        text: btn.innerText.trim(),
                        tag: btn.tagName,
                        classes: btn.className,
                        href: btn.href || '',
                        id: btn.id || ''
                    })).filter(btn => btn.text.length > 0);
                }
            """)
            
            self.logger.info("🔘 Found buttons/links:")
            for i, button in enumerate(buttons[:20]):  # Show first 20
                self.logger.info(f"   {i+1}. [{button['tag']}] '{button['text']}' (classes: {button['classes']})")
            
            # Keep browser open for manual inspection
            input("🔍 Press Enter to close browser after manual inspection...")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Interface inspection failed: {e}")
            return False
        
        finally:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()

def main():
    """Main execution function."""
    print("=" * 80)
    print("🔍 KDP INTERFACE INSPECTOR - DEBUG TOOL")
    print("=" * 80)
    print("📋 This will:")
    print("   1. Load session cookies")
    print("   2. Navigate to KDP")
    print("   3. Click Create button")
    print("   4. Show you what's actually on the page")
    print("=" * 80)
    
    inspector = KDPInterfaceInspector()
    
    if not inspector.setup_browser():
        print("❌ Browser setup failed")
        return False
    
    if not inspector.inspect_kdp_interface():
        print("❌ Interface inspection failed")
        return False
    
    print("✅ Interface inspection complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)