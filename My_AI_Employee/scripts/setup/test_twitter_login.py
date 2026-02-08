#!/usr/bin/env python3
"""
Test Twitter MCP authentication
Uses the existing .twitter_session and attempts to log in programmatically
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the Twitter browser class
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

load_dotenv()

SESSION_DIR = os.getenv('TWITTER_SESSION_DIR', '.twitter_session')

async def test_twitter_login():
    """Test Twitter login using credentials from .env"""

    print("=" * 60)
    print("Testing Twitter Authentication")
    print("=" * 60)
    print()

    playwright = await async_playwright().start()

    try:
        # Launch persistent context (reuse existing session)
        print(f"Using session directory: {SESSION_DIR}")
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,  # Keep visible for debugging
            args=['--disable-blink-features=AutomationControlled'],
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            locale='en-US',
            timezone_id='America/New_York'
        )

        page = context.pages[0] if context.pages else await context.new_page()

        # Check if already logged in
        print("Checking if already logged in...")
        await page.goto('https://twitter.com', timeout=30000)

        try:
            await page.wait_for_selector('[data-testid="SideNav_NewTweet_Button"]', timeout=5000)
            print("✅ Already logged in! Session is valid.")
            await context.close()
            await playwright.stop()
            return True
        except PlaywrightTimeoutError:
            print("Not logged in yet. Attempting to log in...")

        # Get credentials
        username = os.getenv("TWITTER_USERNAME")
        password = os.getenv("TWITTER_PASSWORD")

        if not username or not password:
            print("❌ Twitter credentials not found in .env")
            await context.close()
            await playwright.stop()
            return False

        # Navigate to login page
        print("Navigating to login page...")
        await page.goto('https://twitter.com/i/flow/login', timeout=30000)
        await asyncio.sleep(2)

        # Step 1: Enter username
        print(f"Entering username: {username}")
        try:
            username_input = await page.wait_for_selector('input[autocomplete="username"]', timeout=10000)
            await username_input.fill(username)

            next_button = await page.query_selector('button:has-text("Next")')
            if next_button:
                await next_button.click()
                await asyncio.sleep(2)
        except Exception as e:
            print(f"❌ Error entering username: {e}")
            await context.close()
            await playwright.stop()
            return False

        # Step 2: Enter password
        print("Entering password...")
        try:
            password_input = await page.wait_for_selector('input[name="password"]', timeout=10000)
            await password_input.fill(password)

            login_button = await page.query_selector('button[data-testid="LoginForm_Login_Button"]')
            if login_button:
                await login_button.click()
                await asyncio.sleep(5)
        except Exception as e:
            print(f"❌ Error entering password: {e}")
            await context.close()
            await playwright.stop()
            return False

        # Check if logged in
        print("Verifying login...")
        try:
            await page.wait_for_selector('[data-testid="SideNav_NewTweet_Button"]', timeout=15000)
            print("✅ Successfully logged in! Session saved.")
            await context.close()
            await playwright.stop()
            return True
        except PlaywrightTimeoutError:
            print("❌ Login failed - could not find home feed")
            await context.close()
            await playwright.stop()
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        await playwright.stop()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_twitter_login())
        if success:
            print()
            print("=" * 60)
            print("Next steps:")
            print("1. Test the MCP health check:")
            print("   uv run mcp dev mcp_servers/twitter_web_mcp.py")
            print("   Then call: health_check")
            print("=" * 60)
            sys.exit(0)
        else:
            print()
            print("Login failed. Please check your credentials in .env")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        sys.exit(0)
