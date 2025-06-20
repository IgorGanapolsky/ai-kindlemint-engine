#!/usr/bin/env python3
"""
KDP Selector Inspector - Use Playwright's codegen to find exact selectors
"""
import sys
import os
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kindlemint.utils.logger import get_logger

def main():
    """Launch Playwright Inspector to find exact KDP selectors."""
    print("=" * 80)
    print("🔍 KDP SELECTOR INSPECTOR - PLAYWRIGHT CODEGEN")
    print("=" * 80)
    print("📋 This will:")
    print("   1. Launch Playwright Inspector with your session cookies")
    print("   2. Open Amazon KDP in inspector mode")
    print("   3. Allow you to click elements to find exact selectors")
    print("   4. Generate precise CSS selectors for all form fields")
    print("=" * 80)
    print()
    
    # Check if session cookies exist
    cookie_file = Path("kdp_session_cookies.json")
    if not cookie_file.exists():
        print("❌ Error: kdp_session_cookies.json not found")
        print("Please run the local authenticator first:")
        print("python scripts/authentication/local_kdp_authenticator.py")
        return False
    
    # Create a temporary script that loads cookies and navigates to KDP
    temp_script = Path("temp_kdp_inspector.py")
    
    script_content = f'''
import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Launch browser with inspector
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=500
        )
        
        context = await browser.new_context(
            viewport={{'width': 1920, 'height': 1080}},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Load session cookies
        with open("{cookie_file}", 'r') as f:
            cookie_data = json.load(f)
            cookies = cookie_data.get('cookies', [])
            await context.add_cookies(cookies)
            print(f"✅ Loaded {{len(cookies)}} session cookies")
        
        page = await context.new_page()
        
        # Navigate to KDP
        print("🌐 Navigating to KDP...")
        await page.goto("https://kdp.amazon.com")
        await page.wait_for_timeout(3000)
        
        # Try to click Create New Title to get to the form
        print("📚 Attempting to navigate to book creation form...")
        try:
            # Try different selectors for Create button
            create_selectors = [
                'text="Create New Title"',
                'button:has-text("Create")',
                'button:has-text("Create") >> nth=0'
            ]
            
            for selector in create_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.click(selector)
                    print(f"✅ Clicked Create button with: {{selector}}")
                    await page.wait_for_timeout(5000)
                    break
                except:
                    continue
            
            print("✅ Should now be on the book creation form")
            
        except Exception as e:
            print(f"⚠️ Could not auto-navigate to form: {{e}}")
            print("Please manually navigate to the book creation form")
        
        print()
        print("=" * 80)
        print("🎯 INSPECTOR READY - MANUAL STEPS:")
        print("=" * 80)
        print("1. In the browser, navigate to the 'Book Details' form if not there")
        print("2. Open DevTools (F12 or Cmd+Option+I)")
        print("3. In DevTools Console, run these commands to find selectors:")
        print()
        print("   # For Book Title field:")
        print("   document.querySelector('input[placeholder*=\"title\" i]')")
        print("   document.querySelector('input[name*=\"title\" i]')")
        print("   document.querySelector('input[id*=\"title\" i]')")
        print()
        print("   # For Author field:")
        print("   document.querySelector('input[placeholder*=\"author\" i]')")
        print("   document.querySelector('input[name*=\"author\" i]')")
        print()
        print("   # For Description field:")
        print("   document.querySelector('textarea[placeholder*=\"description\" i]')")
        print("   document.querySelector('textarea[name*=\"description\" i]')")
        print()
        print("4. Copy the working selectors and paste them below:")
        print("=" * 80)
        
        # Keep browser open for manual inspection
        input("Press Enter when you have found all the selectors...")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    # Write and execute the temporary script
    with open(temp_script, 'w') as f:
        f.write(script_content)
    
    print(f"🚀 Launching Playwright Inspector...")
    print(f"📝 Temporary script created: {temp_script}")
    
    try:
        os.system(f"python {temp_script}")
        
        # Collect the selectors from user
        print("\n" + "=" * 80)
        print("📝 SELECTOR COLLECTION")
        print("=" * 80)
        
        selectors = {}
        
        # Collect selectors for each field
        fields = [
            ("title", "Book Title"),
            ("subtitle", "Subtitle"),
            ("author", "Author"),
            ("description", "Description"),
            ("keyword1", "Keyword 1"),
            ("keyword2", "Keyword 2"),
            ("keyword3", "Keyword 3"),
            ("keyword4", "Keyword 4"),
            ("keyword5", "Keyword 5"),
            ("keyword6", "Keyword 6"),
            ("keyword7", "Keyword 7")
        ]
        
        for field_key, field_name in fields:
            while True:
                selector = input(f"Enter the working CSS selector for {field_name} (or 'skip' to skip): ").strip()
                if selector.lower() == 'skip':
                    break
                if selector:
                    selectors[field_key] = selector
                    print(f"✅ Saved {field_name}: {selector}")
                    break
                else:
                    print("⚠️ Please enter a valid selector or 'skip'")
        
        # Save selectors to file
        if selectors:
            selectors_file = Path("kdp_exact_selectors.json")
            with open(selectors_file, 'w') as f:
                json.dump(selectors, f, indent=2)
            
            print(f"\n✅ Selectors saved to: {selectors_file}")
            print(f"📊 Found {len(selectors)} working selectors")
            
            # Display what was found
            print("\n📋 DISCOVERED SELECTORS:")
            for field, selector in selectors.items():
                print(f"   {field}: {selector}")
                
            return True
        else:
            print("❌ No selectors were provided")
            return False
            
    finally:
        # Clean up temporary script
        if temp_script.exists():
            temp_script.unlink()
            print(f"🧹 Cleaned up temporary script")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)