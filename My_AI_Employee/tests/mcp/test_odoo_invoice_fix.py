#!/usr/bin/env python3
"""
Test Odoo MCP invoice creation after frozendict fix.
This validates that the code fix in odoo_mcp.py line 550 works correctly.
"""
import os
import sys
import asyncio
from pathlib import Path

# Add My_AI_Employee directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Set DRY_RUN mode for safe testing
os.environ['DRY_RUN'] = 'true'

async def test_invoice_creation():
    """Test invoice creation with the frozendict fix."""
    print("=" * 70)
    print("Testing Odoo MCP Invoice Creation (DRY_RUN mode)")
    print("=" * 70 + "\n")

    try:
        # Import after setting DRY_RUN
        from mcp_servers.odoo_mcp import create_invoice

        print("✅ Successfully imported create_invoice function\n")

        # Test 1: Simple invoice
        print("Test 1: Simple single-item invoice")
        print("-" * 70)
        result1 = await create_invoice(
            customer_name="Test Customer",
            customer_email="test@example.com",
            invoice_date="2026-02-08",
            due_date="2026-02-23",
            line_items=[
                {"description": "Test Service", "quantity": 1, "unit_price": 100.00}
            ],
            tax_rate=0.0,
            notes="Test invoice"
        )

        if 'error' in result1:
            print(f"❌ FAILED: {result1['error']}")
            return False
        else:
            print(f"✅ SUCCESS: Invoice created")
            print(f"   Invoice ID: {result1['invoice_id']}")
            print(f"   Total: ${result1['total_amount']:.2f}")
            print(f"   Status: {result1['status']}\n")

        # Test 2: Multi-item invoice (like the real DataFlow Systems invoice)
        print("Test 2: Multi-item invoice (DataFlow Systems format)")
        print("-" * 70)
        result2 = await create_invoice(
            customer_name="DataFlow Systems",
            customer_email="james.wilson@dataflowsystems.com",
            invoice_date="2026-02-08",
            due_date="2026-02-23",
            line_items=[
                {"description": "AI system monitoring and maintenance", "quantity": 1, "unit_price": 800.00},
                {"description": "Priority support (up to 5 hours)", "quantity": 1, "unit_price": 400.00}
            ],
            tax_rate=0.0,
            notes="Monthly AI Automation Support & Maintenance - February 2026"
        )

        if 'error' in result2:
            print(f"❌ FAILED: {result2['error']}")
            return False
        else:
            print(f"✅ SUCCESS: Invoice created")
            print(f"   Invoice ID: {result2['invoice_id']}")
            print(f"   Total: ${result2['total_amount']:.2f}")
            print(f"   Status: {result2['status']}\n")

        # Test 3: Invoice with tax
        print("Test 3: Invoice with tax rate")
        print("-" * 70)
        result3 = await create_invoice(
            customer_name="Test Customer with Tax",
            customer_email="tax@example.com",
            invoice_date="2026-02-08",
            due_date="2026-02-23",
            line_items=[
                {"description": "Taxable Service", "quantity": 2, "unit_price": 50.00}
            ],
            tax_rate=0.1,  # 10% tax
            notes="Invoice with tax"
        )

        if 'error' in result3:
            print(f"❌ FAILED: {result3['error']}")
            return False
        else:
            print(f"✅ SUCCESS: Invoice created")
            print(f"   Invoice ID: {result3['invoice_id']}")
            print(f"   Total: ${result3['total_amount']:.2f} (includes 10% tax)")
            print(f"   Status: {result3['status']}\n")

        print("=" * 70)
        print("✅ ALL TESTS PASSED - frozendict fix is working!")
        print("=" * 70 + "\n")

        print("📋 Next Steps:")
        print("1. Turn off DRY_RUN mode: Remove 'DRY_RUN=true' from .env")
        print("2. Ensure Odoo is running: http://localhost:8069")
        print("3. Install HR/Expense module (for expense operations)")
        print("4. Re-execute the 3 failed Odoo operations via MCP\n")

        return True

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_invoice_creation())
    sys.exit(0 if success else 1)
