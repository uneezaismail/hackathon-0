#!/usr/bin/env python3
"""
Instagram Web MCP Server - Browser Automation (Gold Tier)

Uses Playwright for browser automation to:
1. Authenticate with Instagram (persistent session)
2. Post images with captions
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
mcp = FastMCP(name="instagram-web-mcp")

# Initialize audit logger
vault_root = os.getenv('VAULT_ROOT', 'AI_Employee_Vault')
audit_logger = AuditLogger(vault_root)

# Session storage - use project directory (not home directory)
SESSION_DIR = os.getenv('INSTAGRAM_SESSION_DIR', '.instagram_session')


# ============================================================================
# PYDANTIC MODELS - Type-safe Instagram message validation
# ============================================================================

class InstagramPostRequest(BaseModel):
    """Instagram post request model with validation."""

    caption: str = Field(..., description="The caption for the Instagram post")
    image_path: str = Field(..., description="Path to image to post (required for Instagram)")

    @field_validator('caption')
    @classmethod
    def validate_caption(cls, v):
        """Caption validation."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Caption cannot be empty')
        if len(v) > 2200:  # Instagram's caption limit
            raise ValueError(f'Caption exceeds Instagram character limit ({len(v)} chars)')
        return v

    @field_validator('image_path')
    @classmethod
    def validate_image_path(cls, v):
        """Image path validation."""
        if not v or not Path(v).exists():
            raise ValueError(f'Image file not found: {v}')
        return v


class InstagramPostResponse(BaseModel):
    """Instagram post response model."""

    success: bool = Field(..., description="Whether post was published successfully")
    post_id: str = Field(default="", description="Post ID (timestamp-based)")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    error: Optional[str] = Field(default=None, description="Error message if failed")


# ============================================================================
# INSTAGRAM BROWSER AUTOMATION
# ============================================================================

class InstagramBrowser:
    """Instagram Web browser automation using Playwright."""

    def __init__(self):
        """Initialize Instagram browser."""
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

            logger.info("Instagram browser started successfully")

        except Exception as e:
            logger.error(f"Error starting Instagram browser: {e}")
            await self.close()
            raise

    async def close(self):
        """Close browser and save session."""
        try:
            if self.context:
                await self.context.close()
                logger.info("Instagram browser closed (session saved)")

            if self.playwright:
                await self.playwright.stop()

        except Exception as e:
            logger.error(f"Error closing Instagram browser: {e}")

    async def is_logged_in(self) -> bool:
        """Check if user is logged into Instagram."""
        try:
            await self.page.goto('https://www.instagram.com', timeout=30000)

            # Wait for either login form or home feed
            try:
                # If we see "New post" button, we're logged in
                await self.page.wait_for_selector('[aria-label*="New post"]', timeout=5000)
                logger.info("Instagram session is valid")
                return True
            except PlaywrightTimeoutError:
                # Check for login form
                try:
                    await self.page.wait_for_selector('input[name="username"]', timeout=3000)
                    logger.warning("Instagram session expired - login required")
                    return False
                except PlaywrightTimeoutError:
                    logger.warning("Instagram page state unclear")
                    return False

        except Exception as e:
            logger.error(f"Error checking Instagram login status: {e}")
            return False

    async def login(self) -> bool:
        """Log into Instagram using credentials from environment."""
        try:
            # Get credentials
            username = os.getenv("INSTAGRAM_USERNAME")
            password = os.getenv("INSTAGRAM_PASSWORD")

            if not username or not password:
                logger.error("Instagram credentials not found in environment")
                return False

            # Navigate to Instagram
            await self.page.goto('https://www.instagram.com', timeout=30000)
            await asyncio.sleep(2)

            # Fill login form
            try:
                await self.page.fill('input[name="username"]', username)
                await self.page.fill('input[name="password"]', password)
                logger.info(f"Entered credentials for: {username}")

                # Click login button
                await self.page.click('button[type="submit"]')
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Error filling login form: {e}")
                return False

            # Check if logged in
            try:
                await self.page.wait_for_selector('[aria-label*="New post"]', timeout=30000)
                logger.info("Successfully logged into Instagram")

                # Handle "Save Your Login Info?" dialog
                try:
                    not_now_button = await self.page.query_selector('button:has-text("Not Now")')
                    if not_now_button:
                        await not_now_button.click()
                        await asyncio.sleep(1)
                except:
                    pass

                # Handle "Turn on Notifications?" dialog
                try:
                    not_now_button = await self.page.query_selector('button:has-text("Not Now")')
                    if not_now_button:
                        await not_now_button.click()
                        await asyncio.sleep(1)
                except:
                    pass

                return True
            except PlaywrightTimeoutError:
                logger.error("Login failed - could not find home feed")
                return False

        except Exception as e:
            logger.error(f"Error during Instagram login: {e}")
            return False

    async def post_to_instagram(self, caption: str, image_path: str) -> tuple[bool, str, str]:
        """
        Post an image with caption to Instagram.

        Args:
            caption: The caption for the post
            image_path: Path to image to post

        Returns:
            (success, post_id, error_message) tuple
        """
        try:
            # Check if logged in
            if not await self.is_logged_in():
                # Try to log in
                if not await self.login():
                    return False, "", "Not logged into Instagram. Please check credentials."

            # Navigate to home page
            await self.page.goto('https://www.instagram.com', timeout=30000)
            await asyncio.sleep(2)

            # Click "New post" button
            try:
                new_post_selectors = [
                    '[aria-label*="New post"]',
                    'svg[aria-label*="New post"]',
                    'a[href="#"]'
                ]

                clicked = False
                for selector in new_post_selectors:
                    try:
                        await self.page.click(selector, timeout=3000)
                        clicked = True
                        logger.info(f"Clicked new post button: {selector}")
                        break
                    except PlaywrightTimeoutError:
                        continue

                if not clicked:
                    return False, "", "Could not find 'New post' button"

                # Wait for file upload dialog
                await asyncio.sleep(2)

                # Upload image
                file_input = await self.page.query_selector('input[type="file"]')
                if not file_input:
                    return False, "", "Could not find file upload input"

                await file_input.set_input_files(image_path)
                logger.info(f"Uploaded image: {image_path}")
                await asyncio.sleep(2)

                # Click "Next" button (multiple times for crop, filter, etc.)
                for i in range(3):
                    try:
                        next_button = await self.page.query_selector('button:has-text("Next")')
                        if next_button:
                            await next_button.click()
                            logger.info(f"Clicked Next button ({i+1}/3)")
                            await asyncio.sleep(2)
                    except:
                        break

                # Add caption
                try:
                    caption_selectors = [
                        'textarea[aria-label*="Write a caption"]',
                        'textarea[placeholder*="Write a caption"]',
                        'textarea'
                    ]

                    typed = False
                    for selector in caption_selectors:
                        try:
                            await self.page.fill(selector, caption)
                            typed = True
                            logger.info(f"Added caption: {caption[:50]}...")
                            break
                        except:
                            continue

                    if not typed:
                        logger.warning("Could not add caption")

                except Exception as e:
                    logger.warning(f"Could not add caption: {e}")

                await asyncio.sleep(1)

                # Click "Share" button
                share_selectors = [
                    'button:has-text("Share")',
                    '[aria-label="Share"]',
                    'button[type="button"]'
                ]

                shared = False
                for selector in share_selectors:
                    try:
                        await self.page.click(selector, timeout=3000)
                        shared = True
                        logger.info(f"Clicked share button: {selector}")
                        break
                    except PlaywrightTimeoutError:
                        continue

                if not shared:
                    return False, "", "Could not find Share button"

                # Wait for post to complete
                await asyncio.sleep(5)

                # Generate post ID
                post_id = f"instagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                logger.info(f"Post published successfully: {post_id}")

                return True, post_id, ""

            except Exception as e:
                error_msg = f"Error posting to Instagram: {str(e)}"
                logger.error(error_msg)
                return False, "", error_msg

        except Exception as e:
            error_msg = f"Error in post_to_instagram: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg


# ============================================================================
# MCP TOOLS - FastMCP exposed functions
# ============================================================================

@mcp.tool()
async def post_to_instagram(
    caption: str,
    image_path: str,
    entry_id: str = ""
) -> dict:
    """
    Post an image with caption to Instagram via browser automation.

    Args:
        caption: The caption for the Instagram post
        image_path: Path to image to post (required)
        entry_id: Audit log entry ID for tracking (optional)

    Returns:
        {
            'success': True/False,
            'post_id': 'Unique post ID',
            'timestamp': 'ISO 8601 timestamp',
            'error': 'Error message if failed (None if successful)'
        }

    Raises:
        ValueError: If caption or image_path is invalid
    """
    start_time = datetime.utcnow()

    try:
        # Validate request with Pydantic
        request = InstagramPostRequest(
            caption=caption,
            image_path=image_path
        )

        # Post to Instagram using browser automation
        async with InstagramBrowser() as browser:
            success, post_id, error = await browser.post_to_instagram(
                caption=request.caption,
                image_path=request.image_path
            )

            # Calculate execution time
            execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Log to audit logger
            if entry_id:
                audit_logger.log_action_executed(
                    entry_id=entry_id,
                    action_type='post_to_instagram',
                    mcp_server='instagram_web_mcp',
                    execution_time_ms=execution_time_ms,
                    success=success,
                    result={
                        'post_id': post_id,
                        'caption_length': len(request.caption),
                        'image_path': request.image_path
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
                action_type='post_to_instagram',
                mcp_server='instagram_web_mcp',
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
                action_type='post_to_instagram',
                mcp_server='instagram_web_mcp',
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
    Check if Instagram session is valid and browser automation is working.

    Returns:
        {
            'status': 'healthy' or 'unhealthy',
            'logged_in': True/False,
            'message': 'Status message',
            'timestamp': 'ISO 8601 timestamp'
        }
    """
    try:
        async with InstagramBrowser() as browser:
            logged_in = await browser.is_logged_in()

            if logged_in:
                return {
                    'status': 'healthy',
                    'logged_in': True,
                    'message': 'Instagram session is active',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'logged_in': False,
                    'message': 'Instagram session expired. Please log in.',
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
    logger.info("Starting Instagram Web MCP Server")
    logger.info(f"Vault root: {vault_root}")
    logger.info(f"Session directory: {SESSION_DIR}")
    mcp.run()
