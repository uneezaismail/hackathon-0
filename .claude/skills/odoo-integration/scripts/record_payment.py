#!/usr/bin/env python3
"""
Payment Recording Workflow

Handles payment recording requests from /Needs_Action/ folder.
Records payment in Odoo and reconciles with invoice.

Usage:
    python record_payment.py <action_item_file>
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
import frontmatter

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent))
from odoo_client import OdooClient


def parse_payment_request(action_item_path: str) -> dict:
    """
    Parse payment request from action item markdown file.

    Args:
        action_item_path: Path to action item file

    Returns:
        Payment details dict
    """
    with open(action_item_path, 'r') as f:
        post = frontmatter.load(f)

    content = post.content
    metadata = post.metadata

    # Extract payment details from content
    payment_data = {
        "invoice_id": metadata.get("invoice_id", ""),
        "amount": 0.0,
        "payment_date": datetime.now().strftime("%Y-%m-%d"),
        "payment_method": "bank_transfer",
        "reference": ""
    }

    # Parse payment details from content
    lines = content.split('\n')
    for line in lines:
        line_lower = line.lower()

        # Extract amount
        if '$' in line:
            amount_str = line.split('$')[1].split()[0].replace(',', '')
            try:
                payment_data["amount"] = float(amount_str)
            except ValueError:
                pass

        # Extract invoice ID
        if 'inv/' in line_lower or 'invoice' in line_lower:
            parts = line.split()
            for part in parts:
                if 'INV/' in part.upper():
                    payment_data["invoice_id"] = part.strip()

        # Extract payment method
        if 'wire' in line_lower or 'transfer' in line_lower:
            payment_data["payment_method"] = "bank_transfer"
        elif 'credit card' in line_lower or 'card' in line_lower:
            payment_data["payment_method"] = "credit_card"
        elif 'cash' in line_lower:
            payment_data["payment_method"] = "cash"
        elif 'check' in line_lower or 'cheque' in line_lower:
            payment_data["payment_method"] = "check"

        # Extract reference
        if 'ref' in line_lower or 'reference' in line_lower:
            payment_data["reference"] = line.strip()

    return payment_data


def create_plan_file(payment_data: dict, payment_result: dict, vault_path: str) -> str:
    """
    Create plan file documenting payment recording workflow.

    Args:
        payment_data: Original payment request data
        payment_result: Payment recording result
        vault_path: Path to Obsidian vault

    Returns:
        Path to plan file
    """
    plans_dir = os.path.join(vault_path, "Plans")
    os.makedirs(plans_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plan_file = os.path.join(plans_dir, f"Plan_payment_{timestamp}.md")

    content = f"""# Payment Recording Plan

**Created**: {datetime.now().isoformat()}
**Payment ID**: {payment_result['payment_id']}

## Objective

Record payment received for invoice {payment_data['invoice_id']}

## Steps

- [x] Parse payment notification from action item
- [x] Query Odoo for invoice details
- [x] Record payment in Odoo
- [x] Reconcile payment with invoice
- [x] Update invoice status
- [x] Log to audit trail

## Payment Details

**Invoice**: {payment_data['invoice_id']}
**Amount**: ${payment_data['amount']:.2f}
**Payment Date**: {payment_data['payment_date']}
**Payment Method**: {payment_data['payment_method']}
**Reference**: {payment_data['reference']}

## Result

**Payment ID**: {payment_result['payment_id']}
**Status**: {payment_result['status']}
**Reconciled**: {payment_result['reconciled']}
**Invoice Status**: {payment_result['invoice_status']}

## Next Steps

- Invoice marked as {payment_result['invoice_status']}
- Payment recorded in accounting system
- Audit trail updated
"""

    with open(plan_file, 'w') as f:
        f.write(content)

    return plan_file


def main():
    parser = argparse.ArgumentParser(description="Record payment from action item")
    parser.add_argument("action_item", help="Path to action item file")
    parser.add_argument("--vault", default=None, help="Path to Obsidian vault")
    args = parser.parse_args()

    # Initialize Odoo client
    client = OdooClient(vault_path=args.vault)

    # Parse payment request
    print(f"Parsing payment request from {args.action_item}")
    payment_data = parse_payment_request(args.action_item)

    if not payment_data["invoice_id"]:
        print("❌ Error: Could not extract invoice ID from action item")
        sys.exit(1)

    if payment_data["amount"] <= 0:
        print("❌ Error: Could not extract payment amount from action item")
        sys.exit(1)

    # Record payment in Odoo
    print(f"Recording payment for {payment_data['invoice_id']}: ${payment_data['amount']:.2f}")
    payment_result = client.record_payment(
        invoice_id=payment_data["invoice_id"],
        amount=payment_data["amount"],
        payment_date=payment_data["payment_date"],
        payment_method=payment_data["payment_method"],
        reference=payment_data["reference"]
    )

    print(f"✓ Payment recorded: {payment_result['payment_id']}")
    print(f"  Status: {payment_result['status']}")
    print(f"  Reconciled: {payment_result['reconciled']}")
    print(f"  Invoice Status: {payment_result['invoice_status']}")

    # Create plan file
    plan_file = create_plan_file(payment_data, payment_result, client.vault_path)
    print(f"✓ Plan file created: {plan_file}")

    # Move action item to Done
    done_dir = os.path.join(client.vault_path, "Done")
    os.makedirs(done_dir, exist_ok=True)
    done_file = os.path.join(done_dir, os.path.basename(args.action_item))

    # Update action item with result
    with open(args.action_item, 'r') as f:
        post = frontmatter.load(f)

    post.metadata["status"] = "processed"
    post.metadata["processed_at"] = datetime.now().isoformat()
    post.metadata["payment_id"] = payment_result["payment_id"]
    post.metadata["invoice_status"] = payment_result["invoice_status"]
    post.metadata["result"] = "payment_recorded"

    with open(done_file, 'w') as f:
        f.write(frontmatter.dumps(post))

    # Remove from Needs_Action
    os.remove(args.action_item)

    print(f"✓ Action item moved to Done: {done_file}")
    print("\n✅ Payment recording workflow complete!")


if __name__ == "__main__":
    main()
