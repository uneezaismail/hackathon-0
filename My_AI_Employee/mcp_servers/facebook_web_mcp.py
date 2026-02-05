#!/usr/bin/env python3
"""
Facebook Web MCP Server - Browser Automation (Gold Tier)

Uses Playwright for browser automation to:
1. Authenticate with Facebook (persistent session)
2. Post messages with optional images
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
mcp = FastMCP(name="facebook-web-mcp")

# Initialize audit logger
vault_root = os.getenv('VAULT_ROOT', 'AI_Employee_Vault')
audit_logger = AuditLogger(vault_root)

# Session storage - use project directory (not home directory)
SESSION_DIR = os.getenv('FACEBOOK_SESSION_DIR', '.facebook_session')


# ============================================================================
# PYDANTIC MODELS - Type-safe Facebook message validation
# ============================================================================

class FacebookPostRequest(BaseModel):
    """Facebook post request model with validation."""

    message: str = Field(..., description="The message to post on Facebook")
    image_path: Optional[str] = Field(None, description="Optional path to image to attach")

    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        """Message validation."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')
        if len(v) > 63206:  # Facebook's character limit
            raise ValueError(f'Message exceeds Facebook character limit ({len(v)} chars)')
        return v

    @field_validator('image_path')
    @classmethod
    def validate_image_path(cls, v):
        """Image path validation."""
        if v and not Path(v).exists():
            raise ValueError(f'Image file not found: {v}')
        return v


class FacebookPostResponse(BaseModel):
    """Facebook post response model."""

    success: bool = Field(..., description="Whether post was published successfully")
    post_id: str = Field(default="", description="Post ID (timestamp-based)")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    error: Optional[str] = Field(default=None, description="Error message if failed")


# ============================================================================
# FACEBOOK BROWSER AUTOMATION
# ============================================================================

class FacebookBrowser:
    """Facebook Web browser automation using Playwright."""

    def __init__(self):
        """Initialize Facebook browser."""
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
            self.session_dir.mkdir(parents=True, exist_ok=True)

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

            logger.info("Facebook browser started successfully")

        except Exception as e:
            logger.error(f"Error starting Facebook browser: {e}")
            await self.close()
            raise

    async def close(self):
        """Close browser and save session."""
        try:
            if self.context:
                await self.context.close()
                logger.info("Facebook browser closed (session saved)")

            if self.playwright:
                await self.playwright.stop()

        except Exception as e:
            logger.error(f"Error closing Facebook browser: {e}")

    async def is_logged_in(self) -> bool:
        """Check if user is logged into Facebook."""
        try:
            await self.page.goto('https://www.facebook.com', timeout=30000)

            # Wait for either login form or home feed
            try:
                # If we see "What's on your mind", we're logged in
                await self.page.wait_for_selector('[aria-label*="What\'s on your mind"]', timeout=5000)
                logger.info("Facebook session is valid")
                return True
            except PlaywrightTimeoutError:
                # Check for login form
                try:
                    await self.page.wait_for_selector('input[name="email"]', timeout=3000)
                    logger.warning("Facebook session expired - login required")
                    return False
                except PlaywrightTimeoutError:
                    logger.warning("Facebook page state unclear")
                    return False

        except Exception as e:
            logger.error(f"Error checking Facebook login status: {e}")
            return False

    async def login(self) -> bool:
        """Log into Facebook using credentials from environment."""
        try:
            # Get credentials
            email = os.getenv("FACEBOOK_EMAIL")
            password = os.getenv("FACEBOOK_PASSWORD")

            if not email or not password:
                logger.error("Facebook credentials not found in environment")
                return False

            # Navigate to Facebook
            await self.page.goto('https://www.facebook.com', timeout=30000)
            await asyncio.sleep(2)

            # Fill login form
            try:
                await self.page.fill('input[name="email"]', email)
                await self.page.fill('input[name="pass"]', password)
                logger.info(f"Entered credentials for: {email}")

                # Click login button
                await self.page.click('button[name="login"]')
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Error filling login form: {e}")
                return False

            # Check if logged in
            try:
                await self.page.wait_for_selector('[aria-label*="What\'s on your mind"]', timeout=30000)
                logger.info("Successfully logged into Facebook")
                return True
            except PlaywrightTimeoutError:
                logger.error("Login failed - could not find home feed")
                return False

        except Exception as e:
            logger.error(f"Error during Facebook login: {e}")
            return False

    async def post_to_facebook(self, message: str, image_path: Optional[str] = None) -> tuple[bool, str, str]:
        """
        Post a message to Facebook.

        Args:
            message: The message to post
            image_path: Optional path to image to attach

        Returns:
            (success, post_id, error_message) tuple
        """
        try:
            # Check if logged in
            if not await self.is_logged_in():
                # Try to log in
                if not await self.login():
                    return False, "", "Not logged into Facebook. Please check credentials."

            # Navigate to home page
            await self.page.goto('https://www.facebook.com', timeout=30000)
            await asyncio.sleep(2)

            # Click "What's on your mind" to open post composer
            try:
                post_box_selectors = [
                    '[aria-label*="What\'s on your mind"]',
                    '[placeholder*="What\'s on your mind"]',
                    'div[role="button"][tabindex="0"]'
                ]

                clicked = False
                for selector in post_box_selectors:
                    try:
                        await self.page.click(selector, timeout=3000)
                        clicked = True
                        logger.info(f"Clicked post composer: {selector}")
                        break
                    except PlaywrightTimeoutError:
                        continue

                if not clicked:
                    return False, "", "Could not find post composer"

                # Wait for post dialog to open
                await asyncio.sleep(2)

                # Find the text input in the dialog
                text_selectors = [
                    '[aria-label*="What\'s on your mind"]',
                    '[contenteditable="true"]',
                    'div[role="textbox"]'
                ]

                typed = False
                for selector in text_selectors:
                    try:
                        element = await self.page.wait_for_selector(selector, timeout=3000)
                        await element.click()
                        await self.page.keyboard.type(message)
                        typed = True
                        logger.info(f"Typed message: {message[:50]}...")
                        break
                    except PlaywrightTimeoutError:
                        continue

                if not typed:
                    return False, "", "Could not type message into post composer"

                await asyncio.sleep(1)

                # Handle image upload if provided
                if image_path and Path(image_path).exists():
                    try:
                        # Look for photo/video button
                        photo_button = await self.page.query_selector('[aria-label*="Photo"]')
                        if photo_button:
                            await photo_button.click()
                            await asyncio.sleep(1)

                            # Upload file
                            file_input = await self.page.query_selector('input[type="file"]')
                            if file_input:
                                await file_input.set_input_files(image_path)
                                await asyncio.sleep(3)
                                logger.info(f"Uploaded image: {image_path}")
                    except Exception as e:
                        logger.warning(f"Could not upload image: {e}")

                # Click Post button
                post_selectors = [
                    '[aria-label="Post"]',
                    'div[aria-label="Post"][role="button"]',
                    'button:has-text("Post")'
                ]

                posted = False
                for selector in post_selectors:
                    try:
                        await self.page.click(selector, timeout=3000)
                        posted = True
                        logger.info(f"Clicked post button: {selector}")
                        break
                    except PlaywrightTimeoutError:
                        continue

                if not posted:
                    return False, "", "Could not find Post button"

                # Wait for post to complete
                await asyncio.sleep(3)

                # Generate post ID
                post_id = f"facebook_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                logger.info(f"Post published successfully: {post_id}")

                return True, post_id, ""

            except Exception as e:
                error_msg = f"Error posting to Facebook: {str(e)}"
                logger.error(error_msg)
                return False, "", error_msg

        except Exception as e:
            error_msg = f"Error in post_to_facebook: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg


# ============================================================================
# MCP TOOLS - FastMCP exposed functions
# ============================================================================

@mcp.tool()
async def post_to_facebook(
    message: str,
    image_path: str = "",
    entry_id: str = ""
) -> dict:
    """
    Post a message to Facebook via browser automation.

    Args:
        message: The message to post on Facebook
        image_path: Optional path to image to attach
        entry_id: Audit log entry ID for tracking (optional)

    Returns:
        {
            'success': True/False,
            'post_id': 'Unique post ID',
            'timestamp': 'ISO 8601 timestamp',
            'error': 'Error message if failed (None if successful)'
        }

    Raises:
        ValueError: If message is invalid
    """
    start_time = datetime.utcnow()

    try:
        # Validate request with Pydantic
        request = FacebookPostRequest(
            message=message,
            image_path=image_path if image_path else None
        )

        # Post to Facebook using browser automation
        async with FacebookBrowser() as browser:
            success, post_id, error = await browser.post_to_facebook(
                message=request.message,
                image_path=request.image_path
            )

            # Calculate execution time
            execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Log to audit logger
            if entry_id:
                audit_logger.log_action_executed(
                    entry_id=entry_id,
                    action_type='post_to_facebook',
                    mcp_server='facebook_web_mcp',
                    execution_time_ms=execution_time_ms,
                    success=success,
                    result={
                        'post_id': post_id,
                        'message_length': len(request.message),
                        'has_image': request.image_path is not None
                    },
                    error=error if not success else None
                )

            return {
                'success': success,
                'post_id': post_id,
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
                action_type='post_to_facebook',
                mcp_server='facebook_web_mcp',
                execution_time_ms=execution_time_ms,
                success=False,
                error=error_msg
            )

        return {
            'success': False,
            'post_id': '',
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
                action_type='post_to_facebook',
                mcp_server='facebook_web_mcp',
                execution_time_ms=execution_time_ms,
                success=False,
                error=error_msg
            )

        return {
            'success': False,
            'post_id': '',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'error': error_msg
        }


@mcp.tool()
async def health_check() -> dict:
    """
    Check if Facebook session is valid and browser automation is working.

    Returns:
        {
            'status': 'healthy' or 'unhealthy',
            'logged_in': True/False,
            'message': 'Status message',
            'timestamp': 'ISO 8601 timestamp'
        }
    """
    try:
        async with FacebookBrowser() as browser:
            logged_in = await browser.is_logged_in()

            if logged_in:
                return {
                    'status': 'healthy',
                    'logged_in': True,
                    'message': 'Facebook session is active',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'logged_in': False,
                    'message': 'Facebook session expired. Please log in.',
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
    logger.info("Starting Facebook Web MCP Server")
    logger.info(f"Vault root: {vault_root}")
    logger.info(f"Session directory: {SESSION_DIR}")
    mcp.run()
