#!/usr/bin/env python3
"""
Test LinkedIn Web MCP - Browser Automation

Tests the FREE LinkedIn browser automation MCP.
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "mcp_servers"))

from linkedin_web_mcp import mcp, LinkedInBrowser


async def test_linkedin_web_mcp():
    """Test LinkedIn Web MCP initialization and health check."""
    print("=" * 70)
    print("Testing LinkedIn Web MCP (Browser Automation - FREE)")
    print("=" * 70)
    print()

    # Test 1: MCP initialization
    print("Test 1: MCP Server Initialization")
    try:
        assert mcp.name == "linkedin-web-mcp"
        print("  ✅ MCP server initialized")
        print(f"     Name: {mcp.name}")
    except Exception as e:
        print(f"  ❌ MCP initialization failed: {e}")
        return False

    # Test 2: Browser startup
    print()
    print("Test 2: Browser Startup")
    try:
        async with LinkedInBrowser() as browser:
            print("  ✅ Browser started successfully")
            print(f"     Session dir: {browser.session_dir}")

            # Test 3: Login status check
            print()
            print("Test 3: Login Status Check")
            logged_in = await browser.is_logged_in()
            if logged_in:
                print("  ✅ LinkedIn session is active")
            else:
                print("  ⚠️  LinkedIn session expired (login required)")
                print("     Run: python mcp_servers/linkedin_web_mcp.py")
                print("     Then log in manually to save session")
    except Exception as e:
        print(f"  ❌ Browser test failed: {e}")
        return False

    print()
    print("=" * 70)
    print("LinkedIn Web MCP: PASSED")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. If not logged in, run: python mcp_servers/linkedin_web_mcp.py")
    print("2. Log in to LinkedIn manually (session will be saved)")
    print("3. Add to Claude Desktop config")
    print("4. Test posting: Use /social-media-poster skill")
    print()
    return True


if __name__ == "__main__":
    result = asyncio.run(test_linkedin_web_mcp())
    sys.exit(0 if result else 1)
