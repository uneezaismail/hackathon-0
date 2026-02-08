#!/usr/bin/env python3
"""
Standalone Twitter Session Initializer
Does not require FastMCP - only uses Playwright directly
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Session directory
SESSION_DIR = os.getenv('TWITTER_SESSION_DIR', '.twitter_session')

async def initialize_twitter_session():
    """Initialize Twitter session by opening browser and waiting for login."""

    logger.info("=" * 60)
    logger.info("Twitter Session Initializer")
    logger.info("=" * 60)
    logger.info("")

    # Create session directory
    Path(SESSION_DIR).mkdir(parents=True, exist_ok=True)
    logger.info(f"Session directory: {SESSION_DIR}")
    logger.info("")

    playwright = await async_playwright().start()

    try:
        # Launch persistent context
        logger.info("Starting browser...")
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,
            args=['--disable-blink-features=AutomationControlled'],
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York'
        )

        # Get or create page
        if len(context.pages) > 0:
            page = context.pages[0]
        else:
            page = await context.new_page()

        logger.info("Browser opened successfully!")
        logger.info("")

        # Navigate to Twitter login
        logger.info("Navigating to Twitter login page...")
        await page.goto('https://twitter.com/i/flow/login', timeout=30000)
        logger.info("")

        logger.info("🔐 Please log into Twitter in the browser window")
        logger.info(f"   Username: {os.getenv('TWITTER_USERNAME', 'NOT SET')}")
        logger.info("")
        logger.info("⏳ Waiting for you to complete login...")
        logger.info("   Press Ctrl+C when you see your Twitter home feed")
        logger.info("")

        # Wait for user to log in (or timeout after 10 minutes)
        try:
            await asyncio.sleep(600)
        except KeyboardInterrupt:
            logger.info("")
            logger.info("Checking login status...")

            # Check if logged in by looking for the tweet button
            try:
                await page.goto('https://twitter.com', timeout=30000)
                await page.wait_for_selector('[data-testid="SideNav_NewTweet_Button"]', timeout=10000)
                logger.info("✅ Successfully logged in! Session saved.")
            except PlaywrightTimeoutError:
                logger.warning("⚠️  Could not verify login. Session may not be saved.")

        # Close browser
        await context.close()

    finally:
        await playwright.stop()

    logger.info("")
    logger.info("=" * 60)
    logger.info(f"Session saved to: {SESSION_DIR}")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Verify session directory exists:")
    logger.info(f"   ls -la {SESSION_DIR}/")
    logger.info("")
    logger.info("2. Test the MCP health check:")
    logger.info("   uv run mcp dev mcp_servers/twitter_web_mcp.py")
    logger.info("   Then call: health_check")
    logger.info("")

if __name__ == "__main__":
    try:
        asyncio.run(initialize_twitter_session())
    except KeyboardInterrupt:
        print("\n\nSession initialization cancelled.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
