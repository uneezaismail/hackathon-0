#!/usr/bin/env python3
"""
LinkedIn Web MCP Server - Browser Automation (FREE)

Post to LinkedIn via browser automation using Playwright.
FREE alternative to LinkedIn REST API v2 (no API costs, no app approval needed).

Features:
- Text posts (up to 3000 characters)
- Image uploads (JPG, PNG, GIF)
- Persistent browser session (stay logged in)
- Health checks
- Audit logging integration

Type-safe with Pydantic v2 models for validation.
Integrated with AuditLogger for Gold tier compliance.
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Any

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
mcp = FastMCP(name="linkedin-web-mcp")

# Initialize audit logger
vault_root = os.getenv('VAULT_ROOT', 'AI_Employee_Vault')
audit_logger = AuditLogger(vault_root)

# Browser session configuration
LINKEDIN_SESSION_DIR = os.getenv('LINKEDIN_SESSION_DIR', '.linkedin_session')
LINKEDIN_HEADLESS = os.getenv('LINKEDIN_HEADLESS', 'false').lower() == 'true'


# ============================================================================
# PYDANTIC MODELS - Type-safe LinkedIn post validation
# ============================================================================

class LinkedInPostRequest(BaseModel):
    """LinkedIn post request model with validation."""

    text: str = Field(..., description="Post content (1-3000 characters)")
    image_path: Optional[str] = Field(default=None, description="Path to image file (JPG, PNG, GIF)")

    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        """Post text must be 1-3000 characters."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Post text cannot be empty')
        if len(v) > 3000:
            raise ValueError(f'Post text exceeds 3000 character limit ({len(v)} chars)')
        return v

    @field_validator('image_path')
    @classmethod
    def validate_image_path(cls, v):
        """Validate image file exists and is correct format."""
        if v:
            path = Path(v)
            if not path.exists():
                raise ValueError(f'Image file not found: {v}')
            if not path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                raise ValueError(f'Invalid image format. Supported: JPG, PNG, GIF')
            # Check file size (max 10MB)
            if path.stat().st_size > 10 * 1024 * 1024:
                raise ValueError('Image file too large (max 10MB)')
        return v


class LinkedInPostResponse(BaseModel):
    """LinkedIn post response model."""

    success: bool = Field(..., description="Whether post was published successfully")
    post_id: str = Field(default="", description="Post ID (timestamp-based)")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    error: Optional[str] = Field(default=None, description="Error message if failed")


# ============================================================================
# LINKEDIN BROWSER AUTOMATION
# ============================================================================

class LinkedInBrowser:
    """LinkedIn browser automation using Playwright."""

    def __init__(self):
        """Initialize LinkedIn browser."""
        self.playwright = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.session_dir = Path(LINKEDIN_SESSION_DIR)

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

            # Launch persistent context (saves login session)
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_dir),
                headless=LINKEDIN_HEADLESS,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ],
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

            logger.info("LinkedIn browser started successfully")

        except Exception as e:
            logger.error(f"Error starting LinkedIn browser: {e}")
            await self.close()
            raise

    async def close(self):
        """Close browser (session saved automatically)."""
        try:
            if self.context:
                await self.context.close()
                logger.info("LinkedIn browser closed (session saved)")

            if self.playwright:
                await self.playwright.stop()

        except Exception as e:
            logger.error(f"Error closing LinkedIn browser: {e}")

    async def is_logged_in(self) -> bool:
        """Check if user is logged into LinkedIn."""
        try:
            await self.page.goto('https://www.linkedin.com/feed/', timeout=30000)

            # Wait for either login form or feed
            try:
                # If we see the feed, we're logged in
                await self.page.wait_for_selector('div[data-test-id="feed-container"]', timeout=5000)
                logger.info("LinkedIn session is valid")
                return True
            except PlaywrightTimeoutError:
                # Try alternative selector
                try:
                    await self.page.wait_for_selector('main.scaffold-layout__main', timeout=5000)
                    logger.info("LinkedIn session is valid (alternative selector)")
                    return True
                except PlaywrightTimeoutError:
                    # If we see login form, we're not logged in
                    logger.warning("LinkedIn session expired - login required")
                    return False

        except Exception as e:
            logger.error(f"Error checking LinkedIn login status: {e}")
            return False

    async def post_to_linkedin(self, text: str, image_path: Optional[str] = None) -> tuple[bool, str, str]:
        """
        Post to LinkedIn feed.

        Args:
            text: Post content
            image_path: Optional path to image file

        Returns:
            (success, post_id, error_message) tuple
        """
        try:
            # Navigate to LinkedIn feed
            await self.page.goto('https://www.linkedin.com/feed/', timeout=30000)

            # Check if logged in
            if not await self.is_logged_in():
                return False, "", "Not logged into LinkedIn. Please log in manually."

            # Click "Start a post" button
            try:
                start_post_button = await self.page.wait_for_selector(
                    'button.share-box-feed-entry__trigger',
                    timeout=10000
                )
                await start_post_button.click()
                await asyncio.sleep(1)
                logger.info("Clicked 'Start a post' button")
            except Exception as e:
                logger.error(f"Could not find 'Start a post' button: {e}")
                return False, "", "Could not find 'Start a post' button"

            # Wait for post editor to open
            try:
                editor = await self.page.wait_for_selector(
                    'div.ql-editor[contenteditable="true"]',
                    timeout=10000
                )
                await editor.click()
                await asyncio.sleep(0.5)
                logger.info("Post editor opened")
            except Exception as e:
                logger.error(f"Could not find post editor: {e}")
                return False, "", "Could not find post editor"

            # Type post text
            try:
                await editor.fill(text)
                await asyncio.sleep(1)
                logger.info("Typed post text")
            except Exception as e:
                logger.error(f"Could not type post text: {e}")
                return False, "", "Could not type post text"

            # Upload image if provided
            if image_path:
                try:
                    # Click image upload button
                    image_button = await self.page.wait_for_selector(
                        'button[aria-label*="Add a photo"]',
                        timeout=5000
                    )
                    await image_button.click()
                    await asyncio.sleep(0.5)
                    logger.info("Clicked image upload button")

                    # Upload file
                    file_input = await self.page.wait_for_selector(
                        'input[type="file"][accept*="image"]',
                        timeout=5000
                    )
                    await file_input.set_input_files(image_path)
                    await asyncio.sleep(2)  # Wait for image to upload
                    logger.info(f"Uploaded image: {image_path}")

                except Exception as e:
                    logger.warning(f"Could not upload image: {e}")
                    # Continue without image

            # Click "Post" button
            try:
                post_button = await self.page.wait_for_selector(
                    'button.share-actions__primary-action',
                    timeout=10000
                )

                # Check if button is enabled
                is_disabled = await post_button.get_attribute('disabled')
                if is_disabled:
                    return False, "", "Post button is disabled (text may be too short)"

                await post_button.click()
                await asyncio.sleep(3)  # Wait for post to publish
                logger.info("Clicked 'Post' button")

            except Exception as e:
                logger.error(f"Could not click 'Post' button: {e}")
                return False, "", "Could not click 'Post' button"

            # Generate post ID
            post_id = f"linkedin_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"Post published successfully: {post_id}")

            return True, post_id, ""

        except Exception as e:
            error_msg = f"Error posting to LinkedIn: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg


# ============================================================================
# MCP TOOLS - FastMCP exposed functions
# ============================================================================

@mcp.tool()
async def post_to_linkedin(
    text: str,
    image_path: str = "",
    entry_id: str = ""
) -> dict[str, Any]:
    """
    Post to LinkedIn via browser automation (FREE - no API costs).

    Args:
        text: Post content (1-3000 characters)
        image_path: Optional path to image file (JPG, PNG, GIF, max 10MB)
        entry_id: Audit log entry ID for tracking (optional)

    Returns:
        {
            'success': True/False,
            'post_id': 'Unique post ID',
            'timestamp': 'ISO 8601 timestamp',
            'error': 'Error message if failed (None if successful)'
        }

    Raises:
        ValueError: If text or image_path is invalid
    """
    start_time = datetime.now(timezone.utc)

    try:
        # Validate request with Pydantic
        request = LinkedInPostRequest(
            text=text,
            image_path=image_path if image_path else None
        )

        # Post to LinkedIn using browser automation
        async with LinkedInBrowser() as browser:
            success, post_id, error = await browser.post_to_linkedin(
                text=request.text,
                image_path=request.image_path
            )

            # Calculate execution time
            execution_time_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

            # Log to audit logger
            if entry_id:
                audit_logger.log_action_executed(
                    entry_id=entry_id,
                    action_type='post_to_linkedin',
                    mcp_server='linkedin_web_mcp',
                    execution_time_ms=execution_time_ms,
                    success=success,
                    result={
                        'post_id': post_id,
                        'text_length': len(request.text),
                        'has_image': bool(request.image_path)
                    },
                    error=error if not success else None
                )

            return {
                'success': success,
                'post_id': post_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'error': error if not success else None
            }

    except ValueError as e:
        # Validation error
        execution_time_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        error_msg = f"Validation error: {str(e)}"

        if entry_id:
            audit_logger.log_action_executed(
                entry_id=entry_id,
                action_type='post_to_linkedin',
                mcp_server='linkedin_web_mcp',
                execution_time_ms=execution_time_ms,
                success=False,
                error=error_msg
            )

        return {
            'success': False,
            'post_id': '',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error': error_msg
        }

    except Exception as e:
        # Unexpected error
        execution_time_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        error_msg = f"Error: {str(e)}"

        if entry_id:
            audit_logger.log_action_executed(
                entry_id=entry_id,
                action_type='post_to_linkedin',
                mcp_server='linkedin_web_mcp',
                execution_time_ms=execution_time_ms,
                success=False,
                error=error_msg
            )

        return {
            'success': False,
            'post_id': '',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error': error_msg
        }


@mcp.tool()
async def health_check() -> dict[str, Any]:
    """
    Check if LinkedIn session is valid and browser automation is working.

    Returns:
        {
            'status': 'healthy' or 'unhealthy',
            'logged_in': True/False,
            'message': 'Status message',
            'timestamp': 'ISO 8601 timestamp'
        }
    """
    try:
        async with LinkedInBrowser() as browser:
            logged_in = await browser.is_logged_in()

            if logged_in:
                return {
                    'status': 'healthy',
                    'logged_in': True,
                    'message': 'LinkedIn session is active',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'logged_in': False,
                    'message': 'LinkedIn session expired. Please log in manually by running: python mcp_servers/linkedin_web_mcp.py',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }

    except Exception as e:
        return {
            'status': 'unhealthy',
            'logged_in': False,
            'message': f'Browser automation error: {str(e)}',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("LinkedIn Web MCP Server (Browser Automation - FREE)")
    logger.info("=" * 60)
    logger.info(f"Vault root: {vault_root}")
    logger.info(f"Session directory: {LINKEDIN_SESSION_DIR}")
    logger.info(f"Headless mode: {LINKEDIN_HEADLESS}")
    logger.info("")
    logger.info("First time setup:")
    logger.info("1. Run this script to open LinkedIn login page")
    logger.info("2. Log in manually (session will be saved)")
    logger.info("3. Close browser when done")
    logger.info("4. Add to Claude Desktop config")
    logger.info("")

    # Run health check on startup
    async def startup_check():
        logger.info("Running startup health check...")
        async with LinkedInBrowser() as browser:
            logged_in = await browser.is_logged_in()
            if logged_in:
                logger.info("✅ LinkedIn session is active")
            else:
                logger.warning("⚠️  LinkedIn session expired - please log in")
                logger.info("Browser will stay open for login. Close when done.")
                await asyncio.sleep(60)  # Keep browser open for 60 seconds

    # Run startup check
    asyncio.run(startup_check())

    # Start MCP server
    logger.info("")
    logger.info("Starting MCP server...")
    mcp.run()
