#!/usr/bin/env python3
"""
Definitive Playwright Display Test
Uses the EXACT same configuration as the working WhatsApp MCP
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def test_display():
    print("=" * 70)
    print("DEFINITIVE PLAYWRIGHT DISPLAY TEST")
    print("=" * 70)
    print()
    print("This uses the EXACT same configuration as your WhatsApp MCP")
    print("that worked in Silver tier.")
    print()

    # Use a test session directory
    session_dir = Path(".test_browser_session")
    session_dir.mkdir(parents=True, exist_ok=True)

    print(f"Session directory: {session_dir}")
    print(f"DISPLAY: {os.getenv('DISPLAY', 'NOT SET')}")
    print(f"WAYLAND_DISPLAY: {os.getenv('WAYLAND_DISPLAY', 'NOT SET')}")
    print()

    playwright = await async_playwright().start()

    try:
        print("Launching browser with WhatsApp MCP configuration...")
        print("(headless=False, same args, same viewport)")
        print()

        # EXACT same configuration as WhatsApp MCP
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(session_dir),
            headless=False,  # WhatsApp Web requires visible browser
            args=[
                '--disable-blink-features=AutomationControlled',
                '--remote-debugging-port=9223'  # Different port to avoid conflicts
            ],
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['notifications']
        )

        print("✅ Browser context created!")
        print()

        # Get or create page
        if len(context.pages) > 0:
            page = context.pages[0]
            print("Using existing page")
        else:
            page = await context.new_page()
            print("Created new page")

        print()
        print("Navigating to Google.com...")
        await page.goto('https://www.google.com', timeout=30000)

        print()
        print("=" * 70)
        print("✅ SUCCESS! Browser should be visible now.")
        print("=" * 70)
        print()
        print("LOOK AT YOUR SCREEN:")
        print("- Do you see a Chromium browser window?")
        print("- Is Google.com loaded in it?")
        print()
        print("If YES: WSLg and Playwright are working correctly!")
        print("If NO: There's a WSL display issue we need to fix.")
        print()
        print("=" * 70)
        print("Press Ctrl+C to close the browser and continue...")
        print("=" * 70)

        # Wait for user to see the browser
        try:
            await asyncio.sleep(300)  # Wait up to 5 minutes
        except KeyboardInterrupt:
            print("\n\nClosing browser...")

        await context.close()
        await playwright.stop()

        print("\n✅ Browser closed successfully.")
        print("\nPlease report back:")
        print("1. Did you see a browser window? (YES/NO)")
        print("2. Was Google.com visible in it? (YES/NO)")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nThis error suggests a problem with Playwright or WSLg.")
        await playwright.stop()
        raise

if __name__ == "__main__":
    try:
        asyncio.run(test_display())
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        print("\nThis indicates a fundamental issue with browser automation on your WSL.")
