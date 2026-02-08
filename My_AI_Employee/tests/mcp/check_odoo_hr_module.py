#!/usr/bin/env python3
"""
Check if Odoo HR/Expense module is installed.
"""
import os
from dotenv import load_dotenv

try:
    import odoorpc
except ImportError:
    print("❌ odoorpc not installed. Install with: pip install odoorpc")
    exit(1)

load_dotenv()

# Odoo connection details
ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
ODOO_DB = os.getenv('ODOO_DB', 'odoo')
ODOO_USERNAME = os.getenv('ODOO_USERNAME', 'admin')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'admin')

def check_hr_expense_module():
    """Check if HR/Expense module is installed."""
    try:
        # Parse URL
        url_parts = ODOO_URL.replace('http://', '').replace('https://', '').split(':')
        host = url_parts[0]
        port = int(url_parts[1]) if len(url_parts) > 1 else 8069

        print(f"🔌 Connecting to Odoo at {host}:{port}...")
        odoo = odoorpc.ODOO(host, port=port, timeout=30)

        print(f"🔐 Logging in as {ODOO_USERNAME}...")
        odoo.login(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)

        print("✅ Connected to Odoo successfully\n")

        # Check if hr.expense model exists
        print("🔍 Checking for hr.expense model...")
        try:
            Expense = odoo.env['hr.expense']
            print("✅ HR/Expense module is INSTALLED")

            # Try to count expenses
            expense_count = Expense.search_count([])
            print(f"📊 Found {expense_count} expense records in database")

            return True

        except Exception as e:
            print(f"❌ HR/Expense module is NOT INSTALLED")
            print(f"   Error: {e}")
            print("\n📋 To install:")
            print("   1. Go to http://localhost:8069")
            print("   2. Click 'Apps' in top menu")
            print("   3. Remove 'Apps' filter")
            print("   4. Search for 'Expenses'")
            print("   5. Click 'Install'")
            return False

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Odoo HR/Expense Module Checker")
    print("=" * 60 + "\n")

    installed = check_hr_expense_module()

    print("\n" + "=" * 60)
    if installed:
        print("✅ Status: READY - You can create expenses")
    else:
        print("⚠️  Status: NOT READY - Install HR/Expense module first")
    print("=" * 60)
