#!/usr/bin/env python3
"""
Test Odoo MCP - FastMCP Implementation
Tests the Odoo Community integration MCP server.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "mcp_servers"))

from odoo_mcp import mcp
import odoorpc


def test_odoo_mcp():
    """Test Odoo MCP."""
    print("=" * 70)
    print("ODOO MCP TEST (FastMCP)")
    print("=" * 70)
    print()

    # Test 1: Check MCP initialization
    print("1. Testing MCP initialization...")
    print(f"   MCP Name: {mcp.name}")
    print(f"   ✅ FastMCP initialized")
    print()

    # Test 2: Check Odoo connection
    print("2. Testing Odoo connection...")
    try:
        odoo = odoorpc.ODOO('localhost', port=8069)
        odoo.login('odoo_db', 'admin', 'admin')
        print(f"   ✅ Connected to Odoo")
        print(f"   Database: {odoo.env.db}")
        print(f"   User: {odoo.env.user}")
        print()

        # Test 3: Query accounting journals
        print("3. Testing Odoo queries...")
        journals = odoo.env['account.journal']
        journal_ids = journals.search([])
        journal_count = len(journal_ids)

        print(f"   ✅ Found {journal_count} accounting journals")

        if journal_count > 0:
            # Show first 3 journals
            for journal_id in journal_ids[:3]:
                journal = journals.browse(journal_id)
                print(f"      - {journal.name} ({journal.type})")

        print()
        print("=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print("✅ MCP initialization: PASSED")
        print("✅ Odoo connection: PASSED")
        print(f"✅ Database queries: PASSED ({journal_count} journals)")
        print()
        print("Odoo MCP is ready to use!")
        print("Add to Claude Desktop with:")
        print("  claude mcp add odoo-mcp -s local \\")
        print("    -e VAULT_ROOT=AI_Employee_Vault \\")
        print("    -- uv run --directory /mnt/d/hackathon-0/My_AI_Employee \\")
        print("    python /mnt/d/hackathon-0/My_AI_Employee/mcp_servers/odoo_mcp.py")
        print()

        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print()
        print("Troubleshooting:")
        print("1. Check if Odoo is running: docker ps | grep odoo")
        print("2. Start Odoo if needed: docker-compose up -d")
        print("3. Verify credentials in .env file")
        print()
        return False


if __name__ == "__main__":
    print()
    success = test_odoo_mcp()
    sys.exit(0 if success else 1)
