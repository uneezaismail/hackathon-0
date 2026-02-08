#!/usr/bin/env python3
"""
Initialize Social Media Sessions - Gold Tier Setup

This script helps you log into Twitter, Facebook, and Instagram once
to establish persistent browser sessions. After running this script,
the MCPs will be able to use these sessions without requiring login.

Usage:
    python scripts/setup/initialize_social_sessions.py [twitter|facebook|instagram|all]
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from playwright.async_api import async_playwright
from dotenv import load_dotenv
import os

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def initialize_twitter_session():
    """Initialize Twitter session by logging in manually."""
    logger.info("=" * 60)
    logger.info("Initializing Twitter Session")
    logger.info("=" * 60)

    # Use project directory (not home directory)
    session_dir = Path(os.getenv('TWITTER_SESSION_DIR', '.twitter_session'))
    session_dir.mkdir(parents=True, exist_ok=True)

    playwright = await async_playwright().start()

    try:
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(session_dir),
            headless=False,
            args=['--disable-blink-features=AutomationControlled'],
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            locale='en-US',
            timezone_id='America/New_York'
        )

        page = context.pages[0] if context.pages else await context.new_page()

        # Navigate to Twitter
        await page.goto('https://twitter.com/i/flow/login')

        logger.info("")
        logger.info("🔐 Please log into Twitter in the browser window")
        logger.info("   Username: %s", os.getenv('TWITTER_USERNAME', 'NOT SET'))
        logger.info("")
        logger.info("⏳ Waiting for you to complete login...")
        logger.info("   (Press Ctrl+C when done)")

        # Wait for user to log in manually
        try:
            await page.wait_for_selector('[data-testid="SideNav_NewTweet_Button"]', timeout=300000)
            logger.info("✅ Twitter login successful! Session saved.")
        except:
            logger.warning("⚠️  Could not detect successful login. Session may not be saved.")

        await context.close()

    finally:
        await playwright.stop()

    logger.info("Twitter session saved to: %s", session_dir)


async def initialize_facebook_session():
    """Initialize Facebook session by logging in manually."""
    logger.info("=" * 60)
    logger.info("Initializing Facebook Session")
    logger.info("=" * 60)

    # Use project directory (not home directory)
    session_dir = Path(os.getenv('FACEBOOK_SESSION_DIR', '.facebook_session'))
    session_dir.mkdir(parents=True, exist_ok=True)

    playwright = await async_playwright().start()

    try:
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(session_dir),
            headless=False,
            args=['--disable-blink-features=AutomationControlled'],
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            locale='en-US',
            timezone_id='America/New_York'
        )

        page = context.pages[0] if context.pages else await context.new_page()

        # Navigate to Facebook
        await page.goto('https://www.facebook.com')

        logger.info("")
        logger.info("🔐 Please log into Facebook in the browser window")
        logger.info("   Email: %s", os.getenv('FACEBOOK_EMAIL', 'NOT SET'))
        logger.info("")
        logger.info("⏳ Waiting for you to complete login...")
        logger.info("   (Press Ctrl+C when done)")

        # Wait for user to log in manually
        try:
            await page.wait_for_selector('[aria-label="Create a post"]', timeout=300000)
            logger.info("✅ Facebook login successful! Session saved.")
        except:
            logger.warning("⚠️  Could not detect successful login. Session may not be saved.")

        await context.close()

    finally:
        await playwright.stop()

    logger.info("Facebook session saved to: %s", session_dir)


async def initialize_instagram_session():
    """Initialize Instagram session by logging in manually."""
    logger.info("=" * 60)
    logger.info("Initializing Instagram Session")
    logger.info("=" * 60)

    # Use project directory (not home directory)
    session_dir = Path(os.getenv('INSTAGRAM_SESSION_DIR', '.instagram_session'))
    session_dir.mkdir(parents=True, exist_ok=True)

    playwright = await async_playwright().start()

    try:
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(session_dir),
            headless=False,
            args=['--disable-blink-features=AutomationControlled'],
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            locale='en-US',
            timezone_id='America/New_York'
        )

        page = context.pages[0] if context.pages else await context.new_page()

        # Navigate to Instagram
        await page.goto('https://www.instagram.com')

        logger.info("")
        logger.info("🔐 Please log into Instagram in the browser window")
        logger.info("   Username: %s", os.getenv('INSTAGRAM_USERNAME', 'NOT SET'))
        logger.info("")
        logger.info("⏳ Waiting for you to complete login...")
        logger.info("   (Press Ctrl+C when done)")

        # Wait for user to log in manually
        try:
            await page.wait_for_selector('[aria-label="New post"]', timeout=300000)
            logger.info("✅ Instagram login successful! Session saved.")
        except:
            logger.warning("⚠️  Could not detect successful login. Session may not be saved.")

        await context.close()

    finally:
        await playwright.stop()

    logger.info("Instagram session saved to: %s", session_dir)


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python initialize_social_sessions.py [twitter|facebook|instagram|all]")
        sys.exit(1)

    platform = sys.argv[1].lower()

    if platform == "twitter":
        await initialize_twitter_session()
    elif platform == "facebook":
        await initialize_facebook_session()
    elif platform == "instagram":
        await initialize_instagram_session()
    elif platform == "all":
        await initialize_twitter_session()
        await initialize_facebook_session()
        await initialize_instagram_session()
    else:
        print(f"Unknown platform: {platform}")
        print("Valid options: twitter, facebook, instagram, all")
        sys.exit(1)

    logger.info("")
    logger.info("=" * 60)
    logger.info("✅ Session initialization complete!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Test the MCP health checks:")
    logger.info("   ccr mcp call %s-web-mcp health_check", platform)
    logger.info("")
    logger.info("2. If healthy, the MCPs are ready to use!")


if __name__ == "__main__":
    asyncio.run(main())
