#!/usr/bin/env python3
"""
Minimal KDP Test - Get Publishing Today!
Simple, working KDP authentication test without complex dependencies
"""
import os
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

# Load environment variables from .env file
def load_env():
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

async def minimal_kdp_test():
    """Minimal KDP test that actually works"""
    print("🚀 MINIMAL KDP TEST - Getting Publishing Today!")
    
    # Load environment variables
    load_env()
    
    # Check credentials
    email = os.getenv('KDP_EMAIL')
    password = os.getenv('KDP_PASSWORD')
    
    if not email or not password:
        print("❌ Missing KDP credentials!")
        print("Set KDP_EMAIL and KDP_PASSWORD environment variables")
        return False
    
    print(f"📧 Email: {email}")
    print(f"🔒 Password: {'*' * len(password)}")
    
    async with async_playwright() as p:
        # Simple browser launch
        browser = await p.chromium.launch(headless=False)  # Show browser for debugging
        page = await browser.new_page()
        
        try:
            print("🌐 Navigating to KDP...")
            await page.goto('https://kdp.amazon.com')
            
            print("📸 Taking screenshot...")
            await page.screenshot(path='kdp_test.png')
            
            print("✅ Basic navigation successful!")
            print("📸 Screenshot saved as kdp_test.png")
            
            # If we get here, browser automation is working
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
        finally:
            await browser.close()

if __name__ == "__main__":
    success = asyncio.run(minimal_kdp_test())
    if success:
        print("\n🎉 SUCCESS! Browser automation is working!")
        print("Next step: Add actual KDP login")
    else:
        print("\n❌ FAILED! Fix browser setup first")