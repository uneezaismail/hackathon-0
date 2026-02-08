#!/usr/bin/env python3
"""
Quick verification script for Odoo MCP operations.
Shows recent invoices and expenses created today.
"""
import os
import sys

try:
    import odoorpc
except ImportError:
    print("❌ odoorpc not installed")
    sys.exit(1)

ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
ODOO_DB = os.getenv('ODOO_DB', 'odoo_db')
ODOO_USERNAME = os.getenv('ODOO_USERNAME', 'admin')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'admin')

def main():
    print("=" * 70)
    print("Odoo MCP Verification - Recent Operations")
    print("=" * 70 + "\n")

    # Connect
    url_parts = ODOO_URL.replace('http://', '').replace('https://', '').split(':')
    host = url_parts[0]
    port = int(url_parts[1]) if len(url_parts) > 1 else 8069

    print(f"🔌 Connecting to {host}:{port}...")
    odoo = odoorpc.ODOO(host, port=port, timeout=30)
    odoo.login(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)
    print("✅ Connected\n")

    # Check recent invoices (today)
    print("📄 Recent Invoices (Today):")
    print("-" * 70)
    invoice_ids = odoo.execute_kw('account.move', 'search', [[
        ['move_type', '=', 'out_invoice'],
        ['invoice_date', '=', '2026-02-08']
    ]], {'limit': 5, 'order': 'id desc'})

    if invoice_ids:
        invoices = odoo.execute_kw('account.move', 'read', [invoice_ids], {
            'fields': ['id', 'name', 'partner_id', 'amount_total', 'state']
        })

        for inv in invoices:
            print(f"  ✅ ID: {inv['id']}")
            print(f"     Customer: {inv['partner_id'][1]}")
            print(f"     Amount: ${inv['amount_total']:.2f}")
            print(f"     Status: {inv['state']}")
            print(f"     URL: {ODOO_URL}/web#id={inv['id']}&model=account.move")
            print()
    else:
        print("  ⚠️  No invoices found for today\n")

    # Check recent expenses
    print("💳 Recent Expenses:")
    print("-" * 70)
    expense_ids = odoo.execute_kw('hr.expense', 'search', [[]], {
        'limit': 5,
        'order': 'id desc'
    })

    if expense_ids:
        expenses = odoo.execute_kw('hr.expense', 'read', [expense_ids], {
            'fields': ['id', 'name', 'total_amount', 'state', 'date']
        })

        for exp in expenses:
            print(f"  ✅ ID: {exp['id']}")
            print(f"     Description: {exp['name']}")
            print(f"     Amount: ${exp['total_amount']:.2f}")
            print(f"     Status: {exp['state']}")
            print(f"     Date: {exp['date']}")
            print()
    else:
        print("  ⚠️  No expenses found\n")

    print("=" * 70)
    print("✅ Verification Complete")
    print("=" * 70)

if __name__ == "__main__":
    main()
