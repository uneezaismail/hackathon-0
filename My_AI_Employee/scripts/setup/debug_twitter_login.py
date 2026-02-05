#!/usr/bin/env python3
"""
Debug Twitter login - take screenshots to see what's happening
"""

import asyncio
import sys
from pathlib import Path
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

SESSION_DIR = os.getenv('TWITTER_SESSION_DIR', '.twitter_session')

async def debug_twitter_login():
    """Debug Twitter login by taking screenshots"""

    print("=" * 60)
    print("Debugging Twitter Login")
    print("=" * 60)
    print()

    playwright = await async_playwright().start()

    try:
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=True,  # Run headless since display isn't working
            args=['--disable-blink-features=AutomationControlled'],
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            locale='en-US',
            timezone_id='America/New_York'
        )

        page = context.pages[0] if context.pages else await context.new_page()

        # Check if already logged in
        print("Step 1: Checking if already logged in...")
        await page.goto('https://twitter.com', timeout=30000)
        await page.screenshot(path='twitter_step1_home.png')
        print("   Screenshot saved: twitter_step1_home.png")

        try:
            await page.wait_for_selector('[data-testid="SideNav_NewTweet_Button"]', timeout=5000)
            print("✅ Already logged in!")
            await context.close()
            await playwright.stop()
            return True
        except:
            print("   Not logged in yet")

        # Navigate to login
        print("\nStep 2: Navigating to login page...")
        await page.goto('https://twitter.com/i/flow/login', timeout=30000)
        await asyncio.sleep(2)
        await page.screenshot(path='twitter_step2_login.png')
        print("   Screenshot saved: twitter_step2_login.png")

        # Enter username
        print("\nStep 3: Entering username...")
        username = os.getenv("TWITTER_USERNAME")
        try:
            username_input = await page.wait_for_selector('input[autocomplete="username"]', timeout=10000)
            await username_input.fill(username)
            await page.screenshot(path='twitter_step3_username.png')
            print(f"   Entered: {username}")
            print("   Screenshot saved: twitter_step3_username.png")

            # Click Next
            next_button = await page.query_selector('button:has-text("Next")')
            if next_button:
                await next_button.click()
                await asyncio.sleep(3)
                await page.screenshot(path='twitter_step4_after_next.png')
                print("   Clicked Next button")
                print("   Screenshot saved: twitter_step4_after_next.png")
        except Exception as e:
            print(f"   Error: {e}")
            await page.screenshot(path='twitter_error_username.png')
            print("   Screenshot saved: twitter_error_username.png")

        # Check what's on screen now
        print("\nStep 4: Checking what Twitter is showing...")
        await asyncio.sleep(2)
        await page.screenshot(path='twitter_step5_current_screen.png')
        print("   Screenshot saved: twitter_step5_current_screen.png")

        # Try to find password field
        print("\nStep 5: Looking for password field...")
        try:
            password_input = await page.wait_for_selector('input[name="password"]', timeout=5000)
            print("   ✅ Found password field!")

            password = os.getenv("TWITTER_PASSWORD")
            await password_input.fill(password)
            await page.screenshot(path='twitter_step6_password.png')
            print("   Entered password")
            print("   Screenshot saved: twitter_step6_password.png")

            # Click login
            login_button = await page.query_selector('button[data-testid="LoginForm_Login_Button"]')
            if login_button:
                await login_button.click()
                await asyncio.sleep(5)
                await page.screenshot(path='twitter_step7_after_login.png')
                print("   Clicked login button")
                print("   Screenshot saved: twitter_step7_after_login.png")

            # Check if logged in
            await page.goto('https://twitter.com', timeout=30000)
            await page.screenshot(path='twitter_step8_final.png')
            print("   Screenshot saved: twitter_step8_final.png")

            try:
                await page.wait_for_selector('[data-testid="SideNav_NewTweet_Button"]', timeout=10000)
                print("\n✅ Successfully logged in!")
                await context.close()
                await playwright.stop()
                return True
            except:
                print("\n❌ Login failed - not on home feed")
                await context.close()
                await playwright.stop()
                return False

        except Exception as e:
            print(f"   ❌ Password field not found: {e}")
            print("\n   Twitter might be asking for:")
            print("   - Phone number verification")
            print("   - Email verification")
            print("   - CAPTCHA")
            print("   - Unusual activity confirmation")
            print("\n   Check the screenshots to see what Twitter is showing.")
            await context.close()
            await playwright.stop()
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        await playwright.stop()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(debug_twitter_login())
        print("\n" + "=" * 60)
        print("Screenshots saved in current directory:")
        print("- twitter_step1_home.png")
        print("- twitter_step2_login.png")
        print("- twitter_step3_username.png")
        print("- twitter_step4_after_next.png")
        print("- twitter_step5_current_screen.png")
        print("=" * 60)

        if success:
            print("\n✅ Login successful! Test the MCP:")
            print("   uv run mcp dev mcp_servers/twitter_web_mcp.py")
            sys.exit(0)
        else:
            print("\n❌ Login failed. Check screenshots to see what Twitter is showing.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nDebug cancelled.")
        sys.exit(0)
