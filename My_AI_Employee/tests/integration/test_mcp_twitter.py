#!/usr/bin/env python3
"""
Test Twitter Web MCP - FastMCP Implementation
Tests the Twitter browser automation MCP server.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "mcp_servers"))

from twitter_web_mcp import mcp, TwitterBrowser


async def test_twitter_mcp():
    """Test Twitter Web MCP."""
    print("=" * 70)
    print("TWITTER WEB MCP TEST (FastMCP)")
    print("=" * 70)
    print()

    # Test 1: Check MCP initialization
    print("1. Testing MCP initialization...")
    print(f"   MCP Name: {mcp.name}")
    print(f"   ✅ FastMCP initialized")
    print()

    # Test 2: Check browser initialization
    print("2. Testing browser initialization...")
    try:
        async with TwitterBrowser() as browser:
            print(f"   ✅ Browser started successfully")
            print(f"   Session directory: {browser.session_dir}")

            # Test 3: Check login status
            print()
            print("3. Testing login status check...")
            logged_in = await browser.is_logged_in()

            if logged_in:
                print(f"   ✅ Logged in to Twitter")
            else:
                print(f"   ⚠️  Not logged in (expected in WSL)")
                print(f"   Note: Browser automation requires GUI environment")

            print()
            print("=" * 70)
            print("TEST SUMMARY")
            print("=" * 70)
            print("✅ MCP initialization: PASSED")
            print("✅ Browser initialization: PASSED")
            print(f"{'✅' if logged_in else '⚠️ '} Login status: {'LOGGED IN' if logged_in else 'NOT LOGGED IN (GUI required)'}")
            print()
            print("Twitter Web MCP is ready to use!")
            print("Add to Claude Desktop with:")
            print("  claude mcp add twitter-web-mcp -s local \\")
            print("    -e VAULT_ROOT=AI_Employee_Vault \\")
            print("    -- uv run --directory /mnt/d/hackathon-0/My_AI_Employee \\")
            print("    python /mnt/d/hackathon-0/My_AI_Employee/mcp_servers/twitter_web_mcp.py")
            print()

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    print()
    success = asyncio.run(test_twitter_mcp())
    sys.exit(0 if success else 1)
