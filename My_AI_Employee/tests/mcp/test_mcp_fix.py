#!/usr/bin/env python3
"""
Test the fixed Odoo MCP create_invoice function.
Run this after restarting Claude Code to verify the fix works.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add My_AI_Employee directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

async def test_mcp_fix():
    """Test that the MCP fix works with frozendict conversion."""
    print("=" * 70)
    print("Testing Fixed Odoo MCP")
    print("=" * 70 + "\n")

    try:
        # Import the MCP tool
        from mcp_servers.odoo_mcp import create_invoice

        print("✅ Successfully imported create_invoice\n")

        # Test with simple data
        print("Test: Creating test invoice...")
        result = await create_invoice(
            customer_name="Test Customer MCP",
            customer_email="test@example.com",
            invoice_date="2026-02-08",
            due_date="2026-02-23",
            line_items=[
                {"description": "Test Service", "quantity": 1, "unit_price": 100.0}
            ],
            tax_rate=0.0,
            notes="Test invoice via fixed MCP"
        )

        if 'error' in result:
            print(f"❌ FAILED: {result['error']}\n")
            return False
        else:
            print(f"✅ SUCCESS!")
            print(f"   Invoice ID: {result['invoice_id']}")
            print(f"   Total: ${result['total_amount']:.2f}")
            print(f"   Status: {result['status']}")
            print(f"   URL: {result['odoo_url']}\n")
            return True

    except Exception as e:
        print(f"❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("NOTE: Make sure Claude Code has been restarted to reload MCP changes!\n")
    success = asyncio.run(test_mcp_fix())

    if success:
        print("=" * 70)
        print("✅ MCP Fix Verified - Ready to use!")
        print("=" * 70)
        sys.exit(0)
    else:
        print("=" * 70)
        print("❌ MCP Fix Failed - Check error above")
        print("=" * 70)
        sys.exit(1)
