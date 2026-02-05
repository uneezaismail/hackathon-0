#!/usr/bin/env python3
"""
Simple Twitter Session Initializer - Runs MCP server directly
This bypasses the initialization script and just starts the MCP server,
which will open a browser for you to log in.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the Twitter browser class
from mcp_servers.twitter_web_mcp import TwitterBrowser

async def main():
    print("=" * 60)
    print("Twitter Session Initializer")
    print("=" * 60)
    print()
    print("This will open a browser window.")
    print("Please log into Twitter and wait for the home feed to load.")
    print("Then press Ctrl+C to save the session.")
    print()

    async with TwitterBrowser() as browser:
        # Navigate to Twitter
        await browser.page.goto('https://twitter.com/i/flow/login')

        print("Browser opened. Please log in...")
        print("Press Ctrl+C when you see your Twitter home feed.")
        print()

        # Wait indefinitely for user to log in
        try:
            await asyncio.sleep(3600)  # Wait up to 1 hour
        except KeyboardInterrupt:
            print()
            print("Checking if logged in...")

            # Check if logged in
            logged_in = await browser.is_logged_in()

            if logged_in:
                print("✅ Successfully logged in! Session saved.")
            else:
                print("⚠️  Could not verify login. Session may not be saved.")

    print()
    print("Session saved to: .twitter_session/")
    print()
    print("Test with: uv run mcp dev mcp_servers/twitter_web_mcp.py")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nSession initialization cancelled.")
        sys.exit(0)
