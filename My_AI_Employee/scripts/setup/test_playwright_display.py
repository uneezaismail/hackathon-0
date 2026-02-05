#!/usr/bin/env python3
"""
Minimal Playwright test - just open a browser to Google
"""

import asyncio
from playwright.async_api import async_playwright

async def test_browser():
    print("=" * 60)
    print("Testing Playwright Browser Display")
    print("=" * 60)
    print()

    print("Starting Playwright...")
    playwright = await async_playwright().start()

    print("Launching browser (non-headless)...")
    browser = await playwright.chromium.launch(
        headless=False,
        args=['--no-sandbox']
    )

    print("✅ Browser launched!")
    print()
    print("Creating new page...")
    page = await browser.new_page()

    print("Navigating to Google...")
    await page.goto('https://www.google.com')

    print()
    print("=" * 60)
    print("SUCCESS! Browser window should be visible now.")
    print("You should see a Chromium window with Google.com")
    print("=" * 60)
    print()
    print("Press Ctrl+C to close the browser...")

    # Wait for user to see the browser
    try:
        await asyncio.sleep(300)  # Wait 5 minutes
    except KeyboardInterrupt:
        print("\nClosing browser...")

    await browser.close()
    await playwright.stop()
    print("Browser closed.")

if __name__ == "__main__":
    try:
        asyncio.run(test_browser())
    except KeyboardInterrupt:
        print("\nTest cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
