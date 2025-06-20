#!/usr/bin/env python3
"""
KDP Source Code Extractor - Extract HTML source from KDP pages
"""
import sys
import os
import json
import time
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kindlemint.utils.logger import get_logger

class KDPSourceExtractor:
    """Extract HTML source code from KDP pages."""
    
    def __init__(self):
        self.logger = get_logger('kdp_source_extractor')
        self.page = None
        self.browser = None
        self.context = None
        self.playwright = None
        
    def setup_browser(self):
        """Setup browser with session cookies."""
        try:
            from playwright.sync_api import sync_playwright
            
            self.logger.info("🔧 Setting up source extraction browser...")
            
            self.playwright = sync_playwright().start()
            
            self.browser = self.playwright.chromium.launch(
                headless=True,  # Run headless for source extraction
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
    
    def extract_kdp_sources(self):
        """Extract HTML source from KDP pages."""
        try:
            self.logger.info("🌐 Navigating to KDP...")
            self.page.goto("https://kdp.amazon.com", wait_until='domcontentloaded')
            time.sleep(3)
            
            # Save KDP dashboard source
            dashboard_html = self.page.content()
            dashboard_file = Path("kdp_dashboard_source.html")
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                f.write(dashboard_html)
            self.logger.info(f"💾 Saved dashboard source: {dashboard_file}")
            
            # Try to navigate to book creation form
            self.logger.info("📚 Navigating to book creation form...")
            
            create_selectors = [
                'text="Create New Title"',
                'button:has-text("Create New Title")',
                'button:has-text("Create") >> nth=0'
            ]
            
            clicked_create = False
            for selector in create_selectors:
                try:
                    if self.page.wait_for_selector(selector, timeout=5000):
                        self.page.click(selector)
                        self.logger.info(f"✅ Clicked Create with: {selector}")
                        time.sleep(8)  # Wait for page transition
                        clicked_create = True
                        break
                except:
                    continue
            
            if clicked_create:
                # Save book creation form source
                form_html = self.page.content()
                form_file = Path("kdp_book_form_source_AFTER_CREATE.html")
                with open(form_file, 'w', encoding='utf-8') as f:
                    f.write(form_html)
                self.logger.info(f"💾 Saved ACTUAL book form source: {form_file}")
                
                # Extract current page URL for debugging
                current_url = self.page.url
                self.logger.info(f"🌐 Current URL after Create click: {current_url}")
                
                # Take screenshot for visual debugging
                screenshot_file = Path("kdp_after_create_screenshot.png")
                self.page.screenshot(path=str(screenshot_file))
                self.logger.info(f"📸 Screenshot saved: {screenshot_file}")
                
                # Extract all input and textarea elements from ACTUAL page
                self._extract_form_elements()
                
                return [dashboard_file, form_file, screenshot_file]
            else:
                self.logger.warning("⚠️ Could not navigate to book creation form")
                return [dashboard_file]
            
        except Exception as e:
            self.logger.error(f"❌ Source extraction failed: {e}")
            return []
        
        finally:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
    
    def _extract_form_elements(self):
        """Extract and analyze form elements."""
        try:
            self.logger.info("🔍 Extracting form elements...")
            
            # Get all input elements
            inputs = self.page.evaluate("""
                () => {
                    const inputs = Array.from(document.querySelectorAll('input, textarea'));
                    return inputs.map(input => ({
                        tagName: input.tagName,
                        type: input.type,
                        name: input.name,
                        id: input.id,
                        className: input.className,
                        placeholder: input.placeholder,
                        ariaLabel: input.getAttribute('aria-label'),
                        value: input.value,
                        outerHTML: input.outerHTML
                    }));
                }
            """)
            
            # Save form elements analysis
            elements_file = Path("kdp_form_elements.json")
            with open(elements_file, 'w', encoding='utf-8') as f:
                json.dump(inputs, f, indent=2)
            
            self.logger.info(f"📋 Found {len(inputs)} form elements")
            self.logger.info(f"💾 Saved elements analysis: {elements_file}")
            
            # Print summary
            print("\n" + "=" * 80)
            print("📋 FORM ELEMENTS FOUND:")
            print("=" * 80)
            
            for i, elem in enumerate(inputs[:10]):  # Show first 10
                print(f"{i+1:2d}. {elem['tagName']} - name:'{elem['name']}' id:'{elem['id']}' placeholder:'{elem['placeholder']}'")
            
            if len(inputs) > 10:
                print(f"    ... and {len(inputs) - 10} more elements")
            
            print("=" * 80)
            
        except Exception as e:
            self.logger.error(f"❌ Form element extraction failed: {e}")

def main():
    """Main execution function."""
    print("=" * 80)
    print("🔍 KDP SOURCE CODE EXTRACTOR")
    print("=" * 80)
    print("📋 This will extract HTML source code from:")
    print("    1. KDP Dashboard")
    print("    2. Book Creation Form")
    print("    3. All form elements analysis")
    print("=" * 80)
    
    extractor = KDPSourceExtractor()
    
    if not extractor.setup_browser():
        print("❌ Browser setup failed")
        return False
    
    source_files = extractor.extract_kdp_sources()
    
    if source_files:
        print(f"\n🎉 Success! Extracted {len(source_files)} source files:")
        for file in source_files:
            print(f"   📄 {file}")
        
        print("\n📋 Files to analyze:")
        print("   📄 kdp_dashboard_source.html")
        print("   📄 kdp_book_form_source.html")
        print("   📄 kdp_form_elements.json")
        
        print("\n🔍 Next: Analyze these files to find exact selectors!")
        return True
    else:
        print("\n❌ Source extraction failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)