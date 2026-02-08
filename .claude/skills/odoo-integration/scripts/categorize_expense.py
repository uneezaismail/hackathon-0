#!/usr/bin/env python3
"""
Expense Categorization Workflow

Handles expense categorization requests from /Needs_Action/ folder.
Creates expense record in Odoo with proper categorization.

Usage:
    python categorize_expense.py <action_item_file>
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


def parse_expense_request(action_item_path: str) -> dict:
    """
    Parse expense request from action item markdown file.

    Args:
        action_item_path: Path to action item file

    Returns:
        Expense details dict
    """
    with open(action_item_path, 'r') as f:
        post = frontmatter.load(f)

    content = post.content
    metadata = post.metadata

    # Extract expense details from content
    expense_data = {
        "description": "",
        "amount": 0.0,
        "expense_date": datetime.now().strftime("%Y-%m-%d"),
        "category": "office_supplies",
        "vendor": None,
        "receipt_path": None
    }

    # Parse expense details from content
    lines = content.split('\n')
    for line in lines:
        line_lower = line.lower()

        # Extract amount
        if '$' in line:
            amount_str = line.split('$')[1].split()[0].replace(',', '')
            try:
                expense_data["amount"] = float(amount_str)
            except ValueError:
                pass

        # Extract vendor
        if 'from' in line_lower or 'vendor' in line_lower:
            parts = line.split()
            for i, part in enumerate(parts):
                if part.lower() in ['from', 'vendor:']:
                    if i + 1 < len(parts):
                        expense_data["vendor"] = ' '.join(parts[i+1:]).strip()
                        break

        # Categorize based on keywords
        if 'office' in line_lower or 'supplies' in line_lower or 'staples' in line_lower:
            expense_data["category"] = "office_supplies"
        elif 'travel' in line_lower or 'flight' in line_lower or 'hotel' in line_lower:
            expense_data["category"] = "travel"
        elif 'meal' in line_lower or 'lunch' in line_lower or 'dinner' in line_lower or 'restaurant' in line_lower:
            expense_data["category"] = "meals"
        elif 'software' in line_lower or 'subscription' in line_lower or 'saas' in line_lower:
            expense_data["category"] = "software"
        elif 'marketing' in line_lower or 'advertising' in line_lower:
            expense_data["category"] = "marketing"
        elif 'professional' in line_lower or 'consulting' in line_lower or 'legal' in line_lower:
            expense_data["category"] = "professional_services"

        # Extract description (first non-empty line)
        if not expense_data["description"] and line.strip() and not line.startswith('#'):
            expense_data["description"] = line.strip()

    # Check for receipt attachment
    if metadata.get("receipt_path"):
        expense_data["receipt_path"] = metadata["receipt_path"]

    return expense_data


def create_plan_file(expense_data: dict, expense_result: dict, vault_path: str) -> str:
    """
    Create plan file documenting expense categorization workflow.

    Args:
        expense_data: Original expense request data
        expense_result: Expense creation result
        vault_path: Path to Obsidian vault

    Returns:
        Path to plan file
    """
    plans_dir = os.path.join(vault_path, "Plans")
    os.makedirs(plans_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plan_file = os.path.join(plans_dir, f"Plan_expense_{timestamp}.md")

    content = f"""# Expense Categorization Plan

**Created**: {datetime.now().isoformat()}
**Expense ID**: {expense_result['expense_id']}

## Objective

Categorize and record expense in Odoo accounting system

## Steps

- [x] Parse expense details from action item
- [x] Determine expense category
- [x] Create expense record in Odoo
- [x] Attach receipt (if available)
- [x] Log to audit trail

## Expense Details

**Description**: {expense_data['description']}
**Amount**: ${expense_data['amount']:.2f}
**Category**: {expense_data['category']}
**Vendor**: {expense_data['vendor'] or 'N/A'}
**Date**: {expense_data['expense_date']}
**Receipt**: {'Attached' if expense_data['receipt_path'] else 'Not provided'}

## Result

**Expense ID**: {expense_result['expense_id']}
**Status**: {expense_result['status']}
**Category**: {expense_result['category']}
**Receipt Attached**: {expense_result['receipt_attached']}

## Next Steps

- Expense recorded in accounting system
- Category: {expense_result['category']}
- Available for financial reporting
"""

    with open(plan_file, 'w') as f:
        f.write(content)

    return plan_file


def main():
    parser = argparse.ArgumentParser(description="Categorize expense from action item")
    parser.add_argument("action_item", help="Path to action item file")
    parser.add_argument("--vault", default=None, help="Path to Obsidian vault")
    args = parser.parse_args()

    # Initialize Odoo client
    client = OdooClient(vault_path=args.vault)

    # Parse expense request
    print(f"Parsing expense request from {args.action_item}")
    expense_data = parse_expense_request(args.action_item)

    if not expense_data["description"]:
        print("❌ Error: Could not extract expense description from action item")
        sys.exit(1)

    if expense_data["amount"] <= 0:
        print("❌ Error: Could not extract expense amount from action item")
        sys.exit(1)

    # Create expense in Odoo
    print(f"Creating expense: {expense_data['description']} - ${expense_data['amount']:.2f}")
    print(f"Category: {expense_data['category']}")
    expense_result = client.create_expense(
        description=expense_data["description"],
        amount=expense_data["amount"],
        expense_date=expense_data["expense_date"],
        category=expense_data["category"],
        vendor=expense_data["vendor"],
        receipt_path=expense_data["receipt_path"]
    )

    print(f"✓ Expense created: {expense_result['expense_id']}")
    print(f"  Status: {expense_result['status']}")
    print(f"  Category: {expense_result['category']}")
    print(f"  Receipt: {'Attached' if expense_result['receipt_attached'] else 'Not attached'}")

    # Create plan file
    plan_file = create_plan_file(expense_data, expense_result, client.vault_path)
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
    post.metadata["expense_id"] = expense_result["expense_id"]
    post.metadata["category"] = expense_result["category"]
    post.metadata["result"] = "expense_categorized"

    with open(done_file, 'w') as f:
        f.write(frontmatter.dumps(post))

    # Remove from Needs_Action
    os.remove(args.action_item)

    print(f"✓ Action item moved to Done: {done_file}")
    print("\n✅ Expense categorization workflow complete!")


if __name__ == "__main__":
    main()
