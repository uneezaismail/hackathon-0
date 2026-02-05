#!/usr/bin/env python3
"""
Twitter Web MCP Server - Browser Automation (Gold Tier)

Uses Playwright for browser automation to:
1. Authenticate with Twitter (persistent session)
2. Post tweets with optional images
3. Handle session management and health checks

Type-safe with Pydantic v2 models for validation.
Integrated with AuditLogger for Gold tier compliance.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pydantic import BaseModel, Field, field_validator
from fastmcp import FastMCP
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError
import asyncio

from utils.audit_logger import AuditLogger

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(name="twitter-web-mcp")

# Initialize audit logger
vault_root = os.getenv('VAULT_ROOT', 'AI_Employee_Vault')
audit_logger = AuditLogger(vault_root)

# Session storage - use project directory (not home directory)
SESSION_DIR = os.getenv('TWITTER_SESSION_DIR', '.twitter_session')


# ============================================================================
# PYDANTIC MODELS - Type-safe Twitter message validation
# ============================================================================

class TwitterPostRequest(BaseModel):
    """Twitter post request model with validation."""

    text: str = Field(..., description="Tweet text (max 280 characters)")
    image_path: Optional[str] = Field(None, description="Optional path to image to attach")

    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        """Tweet text validation."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Tweet text cannot be empty')
        if len(v) > 280:
            raise ValueError(f'Tweet text exceeds 280 characters ({len(v)} chars)')
        return v

    @field_validator('image_path')
    @classmethod
    def validate_image_path(cls, v):
        """Image path validation."""
        if v and not Path(v).exists():
            raise ValueError(f'Image file not found: {v}')
        return v


class TwitterPostResponse(BaseModel):
    """Twitter post response model."""

    success: bool = Field(..., description="Whether tweet was posted successfully")
    tweet_id: str = Field(default="", description="Tweet ID (timestamp-based)")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    error: Optional[str] = Field(default=None, description="Error message if failed")


# ============================================================================
# TWITTER BROWSER AUTOMATION
# ============================================================================

class TwitterBrowser:
    """Twitter Web browser automation using Playwright."""

    def __init__(self):
        """Initialize Twitter browser."""
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.session_dir = SESSION_DIR

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self):
        """Start browser with persistent context."""
        try:
            self.playwright = await async_playwright().start()
            Path(self.session_dir).mkdir(parents=True, exist_ok=True)

            # Launch persistent context for session storage
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_dir),
                headless=False,
                args=['--disable-blink-features=AutomationControlled'],
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York'
            )

            # Get or create page
            if len(self.context.pages) > 0:
                self.page = self.context.pages[0]
            else:
                self.page = await self.context.new_page()

            logger.info("Twitter browser started successfully")

        except Exception as e:
            logger.error(f"Error starting Twitter browser: {e}")
            await self.close()
            raise

    async def close(self):
        """Close browser and save session."""
        try:
            if self.context:
                await self.context.close()
                logger.info("Twitter browser closed (session saved)")

            if self.playwright:
                await self.playwright.stop()

        except Exception as e:
            logger.error(f"Error closing Twitter browser: {e}")

    async def is_logged_in(self) -> bool:
        """Check if user is logged into Twitter."""
        try:
            await self.page.goto('https://twitter.com', timeout=30000)

            # Wait for either login form or home feed
            try:
                # If we see the tweet button, we're logged in
                await self.page.wait_for_selector('[data-testid="SideNav_NewTweet_Button"]', timeout=5000)
                logger.info("Twitter session is valid")
                return True
            except PlaywrightTimeoutError:
                # Check for login form
                try:
                    await self.page.wait_for_selector('input[autocomplete="username"]', timeout=3000)
                    logger.warning("Twitter session expired - login required")
                    return False
                except PlaywrightTimeoutError:
                    logger.warning("Twitter page state unclear")
                    return False

        except Exception as e:
            logger.error(f"Error checking Twitter login status: {e}")
            return False

    async def login(self) -> bool:
        """Log into Twitter using credentials from environment."""
        try:
            # Get credentials
            username = os.getenv("TWITTER_USERNAME")
            password = os.getenv("TWITTER_PASSWORD")

            if not username or not password:
                logger.error("Twitter credentials not found in environment")
                return False

            # Navigate to Twitter
            await self.page.goto('https://twitter.com/i/flow/login', timeout=30000)
            await asyncio.sleep(2)

            # Step 1: Enter username/email/phone
            try:
                username_input = await self.page.wait_for_selector('input[autocomplete="username"]', timeout=10000)
                await username_input.fill(username)
                logger.info(f"Entered username: {username}")

                # Click Next
                next_button = await self.page.query_selector('button:has-text("Next")')
                if next_button:
                    await next_button.click()
                    await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Error entering username: {e}")
                return False

            # Step 2: Enter password
            try:
                password_input = await self.page.wait_for_selector('input[name="password"]', timeout=10000)
                await password_input.fill(password)
                logger.info("Entered password")

                # Click Log in
                login_button = await self.page.query_selector('button[data-testid="LoginForm_Login_Button"]')
                if login_button:
                    await login_button.click()
                    await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Error entering password: {e}")
                return False

            # Check if logged in
            try:
                await self.page.wait_for_selector('[data-testid="SideNav_NewTweet_Button"]', timeout=15000)
                logger.info("Successfully logged into Twitter")
                return True
            except PlaywrightTimeoutError:
                logger.error("Login failed - could not find home feed")
                return False

        except Exception as e:
            logger.error(f"Error during Twitter login: {e}")
            return False

    async def post_tweet(self, text: str, image_path: Optional[str] = None) -> tuple[bool, str, str]:
        """
        Post a tweet to Twitter.

        Args:
            text: Tweet text (max 280 characters)
            image_path: Optional path to image to attach

        Returns:
            (success, tweet_id, error_message) tuple
        """
        try:
            # Check if logged in
            if not await self.is_logged_in():
                # Try to log in
                if not await self.login():
                    return False, "", "Not logged into Twitter. Please check credentials."

            # Navigate to home page
            await self.page.goto('https://twitter.com/home', timeout=30000)
            await asyncio.sleep(2)

            # Find and click tweet composer
            try:
                tweet_box_selectors = [
                    '[data-testid="tweetTextarea_0"]',
                    '[aria-label="Tweet text"]',
                    'div[role="textbox"][contenteditable="true"]'
                ]

                clicked = False
                for selector in tweet_box_selectors:
                    try:
                        tweet_box = await self.page.wait_for_selector(selector, timeout=3000)
                        await tweet_box.click()
                        clicked = True
                        logger.info(f"Clicked tweet composer: {selector}")
                        break
                    except PlaywrightTimeoutError:
                        continue

                if not clicked:
                    return False, "", "Could not find tweet composer"

                await asyncio.sleep(1)

                # Type the tweet text
                await self.page.keyboard.type(text)
                logger.info(f"Typed tweet text: {text[:50]}...")
                await asyncio.sleep(1)

                # Handle image upload if provided
                if image_path and Path(image_path).exists():
                    try:
                        media_button = await self.page.query_selector('[data-testid="fileInput"]')
                        if media_button:
                            await media_button.set_input_files(image_path)
                            await asyncio.sleep(3)
                            logger.info(f"Uploaded image: {image_path}")
                    except Exception as e:
                        logger.warning(f"Could not upload image: {e}")

                # Click Tweet button
                tweet_button_selectors = [
                    '[data-testid="tweetButtonInline"]',
                    '[data-testid="tweetButton"]',
                    'button:has-text("Tweet")',
                    'button:has-text("Post")'
                ]

                posted = False
                for selector in tweet_button_selectors:
                    try:
                        tweet_button = await self.page.wait_for_selector(selector, timeout=3000)
                        await tweet_button.click()
                        posted = True
                        logger.info(f"Clicked tweet button: {selector}")
                        break
                    except PlaywrightTimeoutError:
                        continue

                if not posted:
                    return False, "", "Could not find Tweet button"

                # Wait for tweet to post
                await asyncio.sleep(3)

                # Generate tweet ID
                tweet_id = f"twitter_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                logger.info(f"Tweet posted successfully: {tweet_id}")

                return True, tweet_id, ""

            except Exception as e:
                error_msg = f"Error posting tweet: {str(e)}"
                logger.error(error_msg)
                return False, "", error_msg

        except Exception as e:
            error_msg = f"Error in post_tweet: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg


# ============================================================================
# MCP TOOLS - FastMCP exposed functions
# ============================================================================

@mcp.tool()
async def post_tweet(
    text: str,
    image_path: str = "",
    entry_id: str = ""
) -> dict:
    """
    Post a tweet to Twitter via browser automation.

    Args:
        text: Tweet text (max 280 characters)
        image_path: Optional path to image to attach
        entry_id: Audit log entry ID for tracking (optional)

    Returns:
        {
            'success': True/False,
            'tweet_id': 'Unique tweet ID',
            'timestamp': 'ISO 8601 timestamp',
            'error': 'Error message if failed (None if successful)'
        }

    Raises:
        ValueError: If text is invalid
    """
    start_time = datetime.utcnow()

    try:
        # Validate request with Pydantic
        request = TwitterPostRequest(
            text=text,
            image_path=image_path if image_path else None
        )

        # Post tweet using browser automation
        async with TwitterBrowser() as browser:
            success, tweet_id, error = await browser.post_tweet(
                text=request.text,
                image_path=request.image_path
            )

            # Calculate execution time
            execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Log to audit logger
            if entry_id:
                audit_logger.log_action_executed(
                    entry_id=entry_id,
                    action_type='post_tweet',
                    mcp_server='twitter_web_mcp',
                    execution_time_ms=execution_time_ms,
                    success=success,
                    result={
                        'tweet_id': tweet_id,
                        'text_length': len(request.text),
                        'has_image': request.image_path is not None
                    },
                    error=error if not success else None
                )

            return {
                'success': success,
                'tweet_id': tweet_id,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'error': error if not success else None
            }

    except ValueError as e:
        # Validation error
        execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        error_msg = f"Validation error: {str(e)}"

        if entry_id:
            audit_logger.log_action_executed(
                entry_id=entry_id,
                action_type='post_tweet',
                mcp_server='twitter_web_mcp',
                execution_time_ms=execution_time_ms,
                success=False,
                error=error_msg
            )

        return {
            'success': False,
            'tweet_id': '',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'error': error_msg
        }
    except Exception as e:
        # Unexpected error
        execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        error_msg = f"Error: {str(e)}"

        if entry_id:
            audit_logger.log_action_executed(
                entry_id=entry_id,
                action_type='post_tweet',
                mcp_server='twitter_web_mcp',
                execution_time_ms=execution_time_ms,
                success=False,
                error=error_msg
            )

        return {
            'success': False,
            'tweet_id': '',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'error': error_msg
        }


@mcp.tool()
async def health_check() -> dict:
    """
    Check if Twitter session is valid and browser automation is working.

    Returns:
        {
            'status': 'healthy' or 'unhealthy',
            'logged_in': True/False,
            'message': 'Status message',
            'timestamp': 'ISO 8601 timestamp'
        }
    """
    try:
        async with TwitterBrowser() as browser:
            logged_in = await browser.is_logged_in()

            if logged_in:
                return {
                    'status': 'healthy',
                    'logged_in': True,
                    'message': 'Twitter session is active',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'logged_in': False,
                    'message': 'Twitter session expired. Please log in.',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }

    except Exception as e:
        return {
            'status': 'unhealthy',
            'logged_in': False,
            'message': f'Error: {str(e)}',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    logger.info("Starting Twitter Web MCP Server")
    logger.info(f"Vault root: {vault_root}")
    logger.info(f"Session directory: {SESSION_DIR}")
    mcp.run()
