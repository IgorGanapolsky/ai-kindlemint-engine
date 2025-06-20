#!/usr/bin/env python3
"""
Simple KDP Inspector - Load cookies and open KDP for manual inspection
"""
import sys
import os
import json
import time
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kindlemint.utils.logger import get_logger

class SimpleKDPInspector:
    """Simple inspector to manually find KDP selectors."""
    
    def __init__(self):
        self.logger = get_logger('kdp_selector_inspector')
        self.page = None
        self.browser = None
        self.context = None
        self.playwright = None
        
    def setup_browser(self):
        """Setup browser with session cookies."""
        try:
            from playwright.sync_api import sync_playwright
            
            self.logger.info("🔧 Setting up inspector browser...")
            
            self.playwright = sync_playwright().start()
            
            self.browser = self.playwright.chromium.launch(
                headless=False,  # Always visible for inspection
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
    
    def inspect_kdp_selectors(self):
        """Navigate to KDP and allow manual inspection."""
        try:
            self.logger.info("🌐 Navigating to KDP...")
            self.page.goto("https://kdp.amazon.com", wait_until='domcontentloaded')
            time.sleep(3)
            
            # Try to navigate to book creation form
            self.logger.info("📚 Attempting to navigate to book creation form...")
            
            create_selectors = [
                'text="Create New Title"',
                'button:has-text("Create New Title")',
                'button:has-text("Create") >> nth=0'
            ]
            
            for selector in create_selectors:
                try:
                    if self.page.wait_for_selector(selector, timeout=5000):
                        self.page.click(selector)
                        self.logger.info(f"✅ Clicked Create with: {selector}")
                        time.sleep(8)  # Wait for page transition
                        break
                except:
                    continue
            
            print("\n" + "=" * 80)
            print("🎯 MANUAL SELECTOR DISCOVERY")
            print("=" * 80)
            print("1. You should now be on the Book Details form")
            print("2. Open DevTools (F12 or Cmd+Option+I)")
            print("3. Use the Elements tab to inspect form fields")
            print("4. Right-click on each input field → Inspect")
            print("5. Copy the CSS selector for each field")
            print()
            print("📋 FIELDS TO FIND:")
            print("   - Book Title input field")
            print("   - Subtitle input field") 
            print("   - Author input field")
            print("   - Description textarea field")
            print("   - Keyword input fields (if visible)")
            print("=" * 80)
            
            # Keep browser open for manual inspection
            input("\n🔍 Press Enter when you've found the selectors (keep browser open)...")
            
            # Collect selectors
            selectors = self._collect_selectors()
            
            if selectors:
                # Save selectors
                selectors_file = Path("kdp_exact_selectors.json")
                with open(selectors_file, 'w') as f:
                    json.dump(selectors, f, indent=2)
                
                print(f"\n✅ Selectors saved to: {selectors_file}")
                print("🚀 Ready to update the publisher script!")
                return selectors_file
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Selector inspection failed: {e}")
            return None
        
        finally:
            input("\n📋 Press Enter to close browser...")
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
    
    def _collect_selectors(self):
        """Collect CSS selectors from user input."""
        print("\n📝 ENTER THE EXACT CSS SELECTORS:")
        print("(Copy from DevTools, or type 'skip' to skip a field)")
        
        selectors = {}
        
        fields = [
            ("title", "Book Title"),
            ("subtitle", "Subtitle"),
            ("author", "Author"),
            ("description", "Description")
        ]
        
        for field_key, field_name in fields:
            while True:
                try:
                    selector = input(f"\n{field_name} CSS selector: ").strip()
                    if selector.lower() == 'skip':
                        break
                    if selector:
                        selectors[field_key] = selector
                        print(f"✅ Saved {field_name}: {selector}")
                        break
                    else:
                        print("⚠️ Please enter a valid selector or 'skip'")
                except (EOFError, KeyboardInterrupt):
                    print("\n⚠️ Input cancelled")
                    break
        
        return selectors

def main():
    """Main execution function."""
    print("=" * 80)
    print("🔍 KDP SELECTOR INSPECTOR")
    print("=" * 80)
    print("📋 This will help you find the exact CSS selectors")
    print("    for Amazon KDP form fields using manual inspection")
    print("=" * 80)
    
    inspector = SimpleKDPInspector()
    
    if not inspector.setup_browser():
        print("❌ Browser setup failed")
        return False
    
    selectors_file = inspector.inspect_kdp_selectors()
    
    if selectors_file:
        print(f"\n🎉 Success! Selectors saved to: {selectors_file}")
        return True
    else:
        print("\n❌ No selectors were collected")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)