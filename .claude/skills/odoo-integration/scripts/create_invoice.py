#!/usr/bin/env python3
"""
Invoice Creation Workflow

Handles invoice creation requests from /Needs_Action/ folder.
Creates draft invoice in Odoo and generates approval request for sending.

Usage:
    python create_invoice.py <action_item_file>
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import frontmatter

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent))
from odoo_client import OdooClient


def parse_invoice_request(action_item_path: str) -> dict:
    """
    Parse invoice request from action item markdown file.

    Args:
        action_item_path: Path to action item file

    Returns:
        Invoice details dict
    """
    with open(action_item_path, 'r') as f:
        post = frontmatter.load(f)

    content = post.content
    metadata = post.metadata

    # Extract invoice details from content
    # This is a simplified parser - production would use NLP/LLM
    invoice_data = {
        "customer_name": metadata.get("customer_name", "Unknown Customer"),
        "customer_email": metadata.get("customer_email", "customer@example.com"),
        "invoice_date": datetime.now().strftime("%Y-%m-%d"),
        "due_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "line_items": [],
        "tax_rate": 0.10,
        "notes": "Payment terms: Net 30"
    }

    # Parse line items from content
    # Example: "Consulting Services - January 2026: $1,500"
    lines = content.split('\n')
    for line in lines:
        if '$' in line and ':' in line:
            parts = line.split(':')
            if len(parts) == 2:
                description = parts[0].strip()
                amount_str = parts[1].strip().replace('$', '').replace(',', '')
                try:
                    amount = float(amount_str)
                    invoice_data["line_items"].append({
                        "description": description,
                        "quantity": 1,
                        "unit_price": amount
                    })
                except ValueError:
                    pass

    return invoice_data


def create_approval_request(invoice_result: dict, vault_path: str) -> str:
    """
    Create approval request for sending invoice.

    Args:
        invoice_result: Invoice creation result from Odoo
        vault_path: Path to Obsidian vault

    Returns:
        Path to approval request file
    """
    approval_dir = os.path.join(vault_path, "Pending_Approval")
    os.makedirs(approval_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    approval_file = os.path.join(
        approval_dir,
        f"APPROVAL_{timestamp}_send_invoice_{invoice_result['invoice_id'].replace('/', '_')}.md"
    )

    # Create approval request content
    metadata = {
        "type": "approval_request",
        "action_type": "send_invoice",
        "invoice_id": invoice_result["invoice_id"],
        "amount": invoice_result["total_amount"],
        "status": "pending",
        "priority": "medium",
        "created_at": datetime.now().isoformat(),
        "approved_by": None,
        "approved_at": None
    }

    content = f"""# Invoice Approval Request

## Invoice Details

**Invoice #**: {invoice_result['invoice_id']}
**Status**: {invoice_result['status']}
**Total Amount**: ${invoice_result['total_amount']:.2f}
**Created**: {invoice_result['created_at']}

**Odoo URL**: {invoice_result['odoo_url']}

## Action Required

This invoice has been created in draft status. To send it to the customer:

1. Review the invoice details in Odoo
2. Verify customer information and line items
3. If approved, move this file to `/Approved/` folder
4. If rejected, move to `/Rejected/` folder with reason

## Approval Decision

Status: **PENDING**

### To Approve
Move this file to: `My_AI_Employee/AI_Employee_Vault/Approved/`

### To Reject
Move this file to: `My_AI_Employee/AI_Employee_Vault/Rejected/` and add rejection reason below.

---

**Rejection Reason** (if applicable):
[Add reason here]
"""

    # Write approval request
    post = frontmatter.Post(content, **metadata)
    with open(approval_file, 'w') as f:
        f.write(frontmatter.dumps(post))

    return approval_file


def create_plan_file(invoice_data: dict, invoice_result: dict, vault_path: str) -> str:
    """
    Create plan file documenting invoice creation workflow.

    Args:
        invoice_data: Original invoice request data
        invoice_result: Invoice creation result
        vault_path: Path to Obsidian vault

    Returns:
        Path to plan file
    """
    plans_dir = os.path.join(vault_path, "Plans")
    os.makedirs(plans_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plan_file = os.path.join(plans_dir, f"Plan_invoice_{timestamp}.md")

    content = f"""# Invoice Creation Plan

**Created**: {datetime.now().isoformat()}
**Invoice ID**: {invoice_result['invoice_id']}

## Objective

Create and send invoice to {invoice_data['customer_name']}

## Steps

- [x] Parse invoice request from action item
- [x] Create draft invoice in Odoo
- [x] Generate invoice PDF
- [ ] Send invoice via email (requires approval)

## Invoice Details

**Customer**: {invoice_data['customer_name']} ({invoice_data['customer_email']})
**Invoice Date**: {invoice_data['invoice_date']}
**Due Date**: {invoice_data['due_date']}
**Total Amount**: ${invoice_result['total_amount']:.2f}

**Line Items**:
{chr(10).join(f"- {item['description']}: ${item['quantity'] * item['unit_price']:.2f}" for item in invoice_data['line_items'])}

## Approval Required

Invoice must be approved before sending to customer.

**Approval Request**: Created in `/Pending_Approval/`

## Next Steps

1. Human reviews invoice in Odoo
2. Human approves/rejects via approval request
3. If approved, orchestrator sends invoice via email
4. Payment tracking begins
"""

    with open(plan_file, 'w') as f:
        f.write(content)

    return plan_file


def main():
    parser = argparse.ArgumentParser(description="Create invoice from action item")
    parser.add_argument("action_item", help="Path to action item file")
    parser.add_argument("--vault", default=None, help="Path to Obsidian vault")
    args = parser.parse_args()

    # Initialize Odoo client
    client = OdooClient(vault_path=args.vault)

    # Parse invoice request
    print(f"Parsing invoice request from {args.action_item}")
    invoice_data = parse_invoice_request(args.action_item)

    # Create invoice in Odoo
    print(f"Creating invoice for {invoice_data['customer_name']}")
    invoice_result = client.create_invoice(
        customer_name=invoice_data["customer_name"],
        customer_email=invoice_data["customer_email"],
        line_items=invoice_data["line_items"],
        invoice_date=invoice_data["invoice_date"],
        due_date=invoice_data["due_date"],
        tax_rate=invoice_data["tax_rate"],
        notes=invoice_data["notes"]
    )

    print(f"✓ Invoice created: {invoice_result['invoice_id']}")
    print(f"  Total: ${invoice_result['total_amount']:.2f}")
    print(f"  Status: {invoice_result['status']}")

    # Create approval request
    approval_file = create_approval_request(invoice_result, client.vault_path)
    print(f"✓ Approval request created: {approval_file}")

    # Create plan file
    plan_file = create_plan_file(invoice_data, invoice_result, client.vault_path)
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
    post.metadata["invoice_id"] = invoice_result["invoice_id"]
    post.metadata["result"] = "invoice_created"

    with open(done_file, 'w') as f:
        f.write(frontmatter.dumps(post))

    # Remove from Needs_Action
    os.remove(args.action_item)

    print(f"✓ Action item moved to Done: {done_file}")
    print("\n✅ Invoice creation workflow complete!")
    print(f"\nNext: Human reviews and approves invoice in /Pending_Approval/")


if __name__ == "__main__":
    main()
