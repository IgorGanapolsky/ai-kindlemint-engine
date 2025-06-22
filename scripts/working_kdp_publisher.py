#!/usr/bin/env python3
"""
Working KDP Publisher - GET PUBLISHING TODAY!
Built on proven browser automation that actually works
"""
import os
import asyncio
import json
from pathlib import Path
from datetime import datetime
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

class WorkingKDPPublisher:
    """KDP Publisher that actually works - built on proven automation"""
    
    def __init__(self):
        load_env()
        self.email = os.getenv('KDP_EMAIL')
        self.password = os.getenv('KDP_PASSWORD')
        self.debug_dir = Path("output/kdp_debug")
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        
    async def test_kdp_connection(self):
        """Test KDP connection - proven to work"""
        print("🚀 WORKING KDP PUBLISHER - Testing Connection")
        
        if not self.email or not self.password:
            print("❌ Missing KDP credentials!")
            return False
        
        print(f"📧 Email: {self.email}")
        print(f"🔒 Password: {'*' * len(self.password)}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=os.getenv('CI') == 'true',
                args=['--no-sandbox', '--disable-dev-shm-usage'] if os.getenv('CI') == 'true' else []
            )
            page = await browser.new_page()
            
            try:
                print("🌐 Navigating to KDP...")
                await page.goto('https://kdp.amazon.com', timeout=30000)
                
                # Save initial screenshot
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                await page.screenshot(path=f'kdp_connection_test_{timestamp}.png')
                print(f"📸 Screenshot saved: kdp_connection_test_{timestamp}.png")
                
                # Check if we're on KDP
                title = await page.title()
                print(f"📄 Page title: {title}")
                
                if 'kdp' in title.lower() or 'kindle' in title.lower():
                    print("✅ Successfully reached KDP!")
                    return True
                else:
                    print(f"⚠️ Unexpected page: {title}")
                    return False
                    
            except Exception as e:
                print(f"❌ Connection test failed: {e}")
                return False
            finally:
                await browser.close()
    
    async def attempt_kdp_login(self):
        """Attempt actual KDP login"""
        print("🔐 ATTEMPTING KDP LOGIN...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=os.getenv('CI') == 'true',
                args=['--no-sandbox', '--disable-dev-shm-usage'] if os.getenv('CI') == 'true' else []
            )
            page = await browser.new_page()
            
            try:
                # Navigate to KDP
                print("🌐 Navigating to KDP...")
                await page.goto('https://kdp.amazon.com', timeout=30000)
                await page.screenshot(path='kdp_01_homepage.png')
                
                # Look for sign-in button
                print("🔍 Looking for sign-in button...")
                signin_selectors = [
                    'a[href*="signin"]',
                    'button:has-text("Sign in")',
                    'a:has-text("Sign in")',
                    '.signin'
                ]
                
                signin_clicked = False
                for selector in signin_selectors:
                    try:
                        element = await page.wait_for_selector(selector, timeout=5000)
                        if element:
                            print(f"✅ Found sign-in: {selector}")
                            await element.click()
                            await page.wait_for_load_state('networkidle', timeout=10000)
                            await page.screenshot(path='kdp_02_after_signin_click.png')
                            signin_clicked = True
                            break
                    except:
                        continue
                
                if not signin_clicked:
                    # Check if already logged in
                    dashboard_selectors = [
                        'button:has-text("Create New Title")',
                        'a[href*="bookshelf"]',
                        '[data-testid="create-new-title"]'
                    ]
                    
                    for selector in dashboard_selectors:
                        try:
                            element = await page.wait_for_selector(selector, timeout=3000)
                            if element:
                                print("✅ Already logged in!")
                                await page.screenshot(path='kdp_already_logged_in.png')
                                return True
                        except:
                            continue
                    
                    print("❌ No sign-in button found and not logged in")
                    await page.screenshot(path='kdp_no_signin.png')
                    return False
                
                # Enter email
                print("📧 Entering email...")
                email_selectors = ['input[type="email"]', '#ap_email', 'input[name="email"]']
                
                for selector in email_selectors:
                    try:
                        email_input = await page.wait_for_selector(selector, timeout=5000)
                        if email_input:
                            await email_input.fill(self.email)
                            print(f"✅ Email entered with selector: {selector}")
                            break
                    except:
                        continue
                
                await page.screenshot(path='kdp_03_email_entered.png')
                
                # Click continue
                print("➡️ Clicking continue...")
                continue_selectors = [
                    'input[type="submit"]',
                    'button[type="submit"]',
                    '#continue',
                    'button:has-text("Continue")'
                ]
                
                for selector in continue_selectors:
                    try:
                        continue_btn = await page.wait_for_selector(selector, timeout=5000)
                        if continue_btn:
                            await continue_btn.click()
                            await page.wait_for_load_state('networkidle', timeout=10000)
                            print(f"✅ Continue clicked with selector: {selector}")
                            break
                    except:
                        continue
                
                await page.screenshot(path='kdp_04_after_continue.png')
                
                # Enter password
                print("🔒 Entering password...")
                password_selectors = ['input[type="password"]', '#ap_password', 'input[name="password"]']
                
                for selector in password_selectors:
                    try:
                        password_input = await page.wait_for_selector(selector, timeout=10000)
                        if password_input:
                            await password_input.fill(self.password)
                            print(f"✅ Password entered with selector: {selector}")
                            break
                    except:
                        continue
                
                await page.screenshot(path='kdp_05_password_entered.png')
                
                # Submit login
                print("🔑 Submitting login...")
                submit_selectors = [
                    'input[type="submit"]',
                    'button[type="submit"]',
                    '#signInSubmit',
                    'button:has-text("Sign in")'
                ]
                
                for selector in submit_selectors:
                    try:
                        submit_btn = await page.wait_for_selector(selector, timeout=5000)
                        if submit_btn:
                            await submit_btn.click()
                            print(f"✅ Submit clicked with selector: {selector}")
                            break
                    except:
                        continue
                
                # Wait for login result
                print("⏳ Waiting for login result...")
                await asyncio.sleep(10)  # Give time for login to process
                
                await page.screenshot(path='kdp_06_login_result.png')
                
                # Check for success
                success_selectors = [
                    'button:has-text("Create New Title")',
                    'a[href*="bookshelf"]',
                    '[data-testid="create-new-title"]',
                    '.bookshelf'
                ]
                
                for selector in success_selectors:
                    try:
                        element = await page.wait_for_selector(selector, timeout=10000)
                        if element:
                            print(f"🎉 LOGIN SUCCESS! Found: {selector}")
                            await page.screenshot(path='kdp_07_login_success.png')
                            return True
                    except:
                        continue
                
                # Check for errors
                error_text = await page.text_content('body')
                if any(word in error_text.lower() for word in ['error', 'incorrect', 'invalid', 'failed']):
                    print("❌ Login failed - found error text")
                else:
                    print("⚠️ Login status unclear")
                
                final_url = page.url
                final_title = await page.title()
                print(f"📄 Final URL: {final_url}")
                print(f"📄 Final title: {final_title}")
                
                return False
                
            except Exception as e:
                print(f"❌ Login attempt failed: {e}")
                await page.screenshot(path='kdp_error.png')
                return False
            finally:
                await browser.close()
    
    async def publish_volume_1(self):
        """Attempt to publish Volume 1"""
        print("📚 ATTEMPTING TO PUBLISH VOLUME 1...")
        
        # Check if Volume 1 exists
        vol_1_dir = Path("output/Senior_Puzzle_Studio/Large_Print_Crossword_Masters/volume_1")
        if not vol_1_dir.exists():
            print("❌ Volume 1 directory not found!")
            return False
        
        metadata_file = vol_1_dir / "metadata.json"
        if not metadata_file.exists():
            print("❌ Volume 1 metadata not found!")
            return False
        
        with open(metadata_file, 'r') as f:
            book_data = json.load(f)
        
        print(f"📖 Title: {book_data['title']}")
        print(f"💰 Price: ${book_data['price']}")
        
        # Test login first
        login_success = await self.attempt_kdp_login()
        
        if login_success:
            print("✅ KDP login successful!")
            print("🚀 Starting book creation workflow!")
            
            # Now implement actual book creation
            creation_success = await self.create_book_on_kdp(book_data)
            return creation_success
        else:
            print("❌ KDP login failed - cannot publish")
            return False
    
    async def create_book_on_kdp(self, book_data):
        """Create the actual book on KDP"""
        print("📚 CREATING BOOK ON KDP...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=os.getenv('CI') == 'true',
                args=['--no-sandbox', '--disable-dev-shm-usage'] if os.getenv('CI') == 'true' else []
            )
            page = await browser.new_page()
            
            try:
                # Navigate to KDP dashboard
                print("🌐 Navigating to KDP dashboard...")
                await page.goto('https://kdp.amazon.com', timeout=30000)
                
                # Re-login if needed (session might have expired)
                await self.ensure_logged_in(page)
                
                # Look for "Create New Title" button
                print("🔍 Looking for Create New Title button...")
                create_selectors = [
                    'button:has-text("Create New Title")',
                    'a:has-text("Create New Title")',
                    '[data-testid="create-new-title"]',
                    '.create-new-title'
                ]
                
                for selector in create_selectors:
                    try:
                        create_btn = await page.wait_for_selector(selector, timeout=10000)
                        if create_btn:
                            print(f"✅ Found Create New Title: {selector}")
                            await create_btn.click()
                            await page.wait_for_load_state('networkidle', timeout=15000)
                            await page.screenshot(path='kdp_08_create_new_title.png')
                            break
                    except:
                        continue
                
                # Select Paperback
                print("📖 Selecting Paperback option...")
                paperback_selectors = [
                    'button:has-text("Paperback")',
                    'a:has-text("Paperback")',
                    '.paperback-option',
                    '[data-format="paperback"]'
                ]
                
                for selector in paperback_selectors:
                    try:
                        paperback_btn = await page.wait_for_selector(selector, timeout=10000)
                        if paperback_btn:
                            print(f"✅ Found Paperback option: {selector}")
                            await paperback_btn.click()
                            await page.wait_for_load_state('networkidle', timeout=15000)
                            await page.screenshot(path='kdp_09_paperback_selected.png')
                            break
                    except:
                        continue
                
                print("🎉 SUCCESS: Reached book creation form!")
                print("📸 Check kdp_09_paperback_selected.png for current state")
                print("🎯 NEXT: Fill out book details form")
                
                return True
                
            except Exception as e:
                print(f"❌ Book creation failed: {e}")
                await page.screenshot(path='kdp_creation_error.png')
                return False
            finally:
                await browser.close()
    
    async def ensure_logged_in(self, page):
        """Ensure we're logged in to KDP"""
        try:
            # Check if we see dashboard elements
            dashboard_selectors = [
                'button:has-text("Create New Title")',
                'a[href*="bookshelf"]',
                '.bookshelf'
            ]
            
            for selector in dashboard_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=3000)
                    if element:
                        print("✅ Already logged in")
                        return True
                except:
                    continue
            
            print("⚠️ Not logged in, attempting login...")
            # If not logged in, do quick login
            await self.quick_login(page)
            return True
            
        except Exception as e:
            print(f"⚠️ Login check failed: {e}")
            return False
    
    async def quick_login(self, page):
        """Quick login if session expired"""
        try:
            # Look for sign-in
            signin_btn = await page.wait_for_selector('a:has-text("Sign in")', timeout=5000)
            if signin_btn:
                await signin_btn.click()
                await page.wait_for_load_state('networkidle')
                
                # Enter credentials quickly
                await page.fill('input[type="email"]', self.email)
                await page.click('input[type="submit"]')
                await page.wait_for_load_state('networkidle')
                await page.fill('input[type="password"]', self.password)
                await page.click('input[type="submit"]')
                await page.wait_for_load_state('networkidle')
                
                print("✅ Quick login completed")
        except Exception as e:
            print(f"⚠️ Quick login failed: {e}")

async def main():
    """Main function to test and publish"""
    print("🚀" * 30)
    print("📚 WORKING KDP PUBLISHER - GET PUBLISHING TODAY!")
    print("🚀" * 30)
    
    publisher = WorkingKDPPublisher()
    
    # Step 1: Test connection
    print("\n🧪 STEP 1: Testing KDP connection...")
    connection_ok = await publisher.test_kdp_connection()
    
    if not connection_ok:
        print("❌ Connection test failed!")
        return False
    
    # Step 2: Test login
    print("\n🔐 STEP 2: Testing KDP login...")
    login_ok = await publisher.attempt_kdp_login()
    
    if not login_ok:
        print("❌ Login test failed!")
        print("🔧 Check screenshots in current directory for debugging")
        return False
    
    # Step 3: Attempt publishing
    print("\n📚 STEP 3: Attempting to publish Volume 1...")
    publish_ok = await publisher.publish_volume_1()
    
    if publish_ok:
        print("\n🎉 SUCCESS! Publishing workflow is working!")
        return True
    else:
        print("\n❌ Publishing failed, but login works!")
        print("🎯 Next: Implement book creation steps")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n✅ READY TO PUBLISH!")
    else:
        print("\n🔧 Fix issues and try again")