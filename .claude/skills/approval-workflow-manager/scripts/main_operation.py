#!/usr/bin/env python3
"""
Approval Workflow Manager - Enhanced HITL Implementation

Manages human-in-the-loop approval workflow for sensitive AI actions.
Unique implementation with fuzzy matching, batch operations, and analytics.

Features:
- Smart file matching (fuzzy search)
- Batch approve/reject operations
- Approval analytics and reporting
- Rejection reason tracking
- Auto-archive expired approvals
"""
import argparse
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re

# ============================================================================
# CONFIGURATION
# ============================================================================

VAULT_ROOT = Path("My_AI_Employee/AI_Employee_Vault")
PENDING_DIR = VAULT_ROOT / "Pending_Approval"
APPROVED_DIR = VAULT_ROOT / "Approved"
REJECTED_DIR = VAULT_ROOT / "Rejected"
LOGS_DIR = VAULT_ROOT / "Logs"
ARCHIVE_DIR = VAULT_ROOT / "Approval_Archive"

# Approval expiration (days)
APPROVAL_EXPIRY_DAYS = 7


# ============================================================================
# DIRECTORY SETUP
# ============================================================================

def ensure_directories():
    """Create required directories if they don't exist."""
    for directory in [PENDING_DIR, APPROVED_DIR, REJECTED_DIR, LOGS_DIR, ARCHIVE_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


# ============================================================================
# AUDIT LOGGING
# ============================================================================

def record_action(action_name: str, target_file: str, outcome: str, metadata: Optional[Dict] = None):
    """Record action in audit log."""
    log_date = datetime.now().strftime("%Y-%m-%d")
    log_path = LOGS_DIR / f"{log_date}.json"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action_type": "approval_management",
        "operation": action_name,
        "target": target_file,
        "result": outcome,
        "actor": "human_via_approval_manager",
        "metadata": metadata or {}
    }

    try:
        existing_logs = json.loads(log_path.read_text()) if log_path.exists() else []
        existing_logs.append(log_entry)
        log_path.write_text(json.dumps(existing_logs, indent=2))
    except Exception as error:
        print(f"Warning: Audit logging failed: {error}", file=sys.stderr)


# ============================================================================
# FILE MATCHING (FUZZY SEARCH)
# ============================================================================

def find_approval_file(file_identifier: str) -> Optional[Path]:
    """
    Find approval file using fuzzy matching.

    Supports:
    - Exact filename match
    - Filename without extension
    - Partial filename match
    - Multiple matches (returns first)
    """
    # Try exact match first
    exact_path = PENDING_DIR / file_identifier
    if exact_path.exists():
        return exact_path

    # Try with .md extension
    if not file_identifier.endswith(".md"):
        with_ext = PENDING_DIR / f"{file_identifier}.md"
        if with_ext.exists():
            return with_ext

    # Fuzzy search - find files containing the identifier
    matching_files = list(PENDING_DIR.glob(f"*{file_identifier}*"))

    if len(matching_files) == 1:
        return matching_files[0]
    elif len(matching_files) > 1:
        print(f"Error: Multiple files match '{file_identifier}':")
        for match in matching_files:
            print(f"  - {match.name}")
        return None

    print(f"Error: No file found matching '{file_identifier}' in {PENDING_DIR}")
    return None


# ============================================================================
# APPROVAL LISTING
# ============================================================================

def parse_frontmatter(file_content: str) -> Dict[str, str]:
    """Extract YAML frontmatter from markdown file."""
    metadata = {}

    if not file_content.startswith('---'):
        return metadata

    parts = file_content.split('---', 2)
    if len(parts) < 3:
        return metadata

    frontmatter_text = parts[1]

    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()

    return metadata


def display_pending_approvals():
    """Display all pending approval requests."""
    approval_files = sorted(PENDING_DIR.glob("*.md"))

    if not approval_files:
        print("✅ No pending approvals!")
        return

    print(f"\n{'=' * 80}")
    print(f"PENDING APPROVALS ({len(approval_files)} items)")
    print(f"{'=' * 80}\n")

    # Table header
    print(f"{'ID':<35} | {'Type':<18} | {'Priority':<10} | {'Age'}")
    print("-" * 80)

    for file_path in approval_files:
        content = file_path.read_text()
        metadata = parse_frontmatter(content)

        # Extract key fields
        action_type = metadata.get('action_type', 'unknown')
        priority = metadata.get('priority', 'medium')
        created_str = metadata.get('created_at', 'unknown')

        # Calculate age
        try:
            created_time = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
            age_delta = datetime.now(created_time.tzinfo) - created_time

            if age_delta.days > 0:
                age_display = f"{age_delta.days}d {age_delta.seconds // 3600}h"
            elif age_delta.seconds >= 3600:
                age_display = f"{age_delta.seconds // 3600}h {(age_delta.seconds % 3600) // 60}m"
            else:
                age_display = f"{age_delta.seconds // 60}m"
        except:
            age_display = 'unknown'

        # Priority indicator
        priority_icons = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
        priority_icon = priority_icons.get(priority.lower(), '⚪')

        print(f"{file_path.name:<35} | {action_type:<18} | {priority_icon} {priority:<8} | {age_display}")

    print(f"\n{'=' * 80}")
    print(f"Total: {len(approval_files)} pending approvals")
    print(f"{'=' * 80}\n")


# ============================================================================
# APPROVAL OPERATIONS
# ============================================================================

def approve_action(file_identifier: str, approval_notes: Optional[str] = None) -> bool:
    """Approve an action and move to Approved folder."""
    file_path = find_approval_file(file_identifier)
    if not file_path:
        return False

    destination = APPROVED_DIR / file_path.name

    try:
        # Add approval metadata to file
        content = file_path.read_text()

        approval_annotation = f"""

## ✅ APPROVAL GRANTED
- **Approved At**: {datetime.now().isoformat()}
- **Approved By**: Human Operator
- **Notes**: {approval_notes or 'No additional notes'}
"""

        updated_content = content + approval_annotation
        destination.write_text(updated_content)

        # Remove original
        file_path.unlink()

        print(f"✓ Approved: {file_path.name}")
        print(f"  Moved to: {destination}")

        record_action("approve", file_path.name, "success", {"notes": approval_notes})
        return True

    except Exception as error:
        print(f"✗ Approval failed for {file_path.name}: {error}")
        record_action("approve", file_path.name, "failure", {"error": str(error)})
        return False


def reject_action(file_identifier: str, rejection_reason: str) -> bool:
    """Reject an action with reason and move to Rejected folder."""
    if not rejection_reason:
        print("Error: Rejection reason is required")
        return False

    file_path = find_approval_file(file_identifier)
    if not file_path:
        return False

    destination = REJECTED_DIR / file_path.name

    try:
        # Add rejection metadata to file
        content = file_path.read_text()

        rejection_annotation = f"""

## ❌ REJECTION NOTICE
- **Rejected At**: {datetime.now().isoformat()}
- **Rejected By**: Human Operator
- **Reason**: {rejection_reason}

### Next Steps
This action has been rejected and will not be executed. Review the rejection reason above and take appropriate corrective action if needed.
"""

        updated_content = content + rejection_annotation
        destination.write_text(updated_content)

        # Remove original
        file_path.unlink()

        print(f"✓ Rejected: {file_path.name}")
        print(f"  Reason: {rejection_reason}")
        print(f"  Moved to: {destination}")

        record_action("reject", file_path.name, "success", {"reason": rejection_reason})
        return True

    except Exception as error:
        print(f"✗ Rejection failed for {file_path.name}: {error}")
        record_action("reject", file_path.name, "failure", {"error": str(error)})
        return False


# ============================================================================
# BATCH OPERATIONS
# ============================================================================

def batch_approve(pattern: str, approval_notes: Optional[str] = None) -> int:
    """Approve multiple files matching pattern."""
    matching_files = list(PENDING_DIR.glob(f"*{pattern}*"))

    if not matching_files:
        print(f"No files match pattern: {pattern}")
        return 0

    print(f"Found {len(matching_files)} files matching '{pattern}'")
    print("Files to approve:")
    for f in matching_files:
        print(f"  - {f.name}")

    confirm = input(f"\nApprove all {len(matching_files)} files? (yes/no): ")
    if confirm.lower() not in ['yes', 'y']:
        print("Batch approval cancelled")
        return 0

    approved_count = 0
    for file_path in matching_files:
        if approve_action(file_path.name, approval_notes):
            approved_count += 1

    print(f"\n✓ Batch approved: {approved_count}/{len(matching_files)} files")
    return approved_count


# ============================================================================
# ANALYTICS
# ============================================================================

def generate_analytics():
    """Generate approval workflow analytics."""
    pending_count = len(list(PENDING_DIR.glob("*.md")))
    approved_count = len(list(APPROVED_DIR.glob("*.md")))
    rejected_count = len(list(REJECTED_DIR.glob("*.md")))

    total = pending_count + approved_count + rejected_count

    print(f"\n{'=' * 60}")
    print("APPROVAL WORKFLOW ANALYTICS")
    print(f"{'=' * 60}\n")

    print(f"📊 Current Status:")
    print(f"  Pending:  {pending_count:>4} ({pending_count/total*100 if total > 0 else 0:.1f}%)")
    print(f"  Approved: {approved_count:>4} ({approved_count/total*100 if total > 0 else 0:.1f}%)")
    print(f"  Rejected: {rejected_count:>4} ({rejected_count/total*100 if total > 0 else 0:.1f}%)")
    print(f"  Total:    {total:>4}")

    # Check for old pending items
    old_items = []
    for file_path in PENDING_DIR.glob("*.md"):
        age_days = (datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)).days
        if age_days > APPROVAL_EXPIRY_DAYS:
            old_items.append((file_path.name, age_days))

    if old_items:
        print(f"\n⚠️  Old Pending Items (>{APPROVAL_EXPIRY_DAYS} days):")
        for name, age in old_items:
            print(f"  - {name} ({age} days old)")

    print(f"\n{'=' * 60}\n")


# ============================================================================
# ARCHIVE OPERATIONS
# ============================================================================

def archive_old_approvals(days_threshold: int = 30):
    """Archive old approved/rejected items."""
    archived_count = 0
    cutoff_date = datetime.now() - timedelta(days=days_threshold)

    for folder in [APPROVED_DIR, REJECTED_DIR]:
        for file_path in folder.glob("*.md"):
            file_age = datetime.fromtimestamp(file_path.stat().st_mtime)

            if file_age < cutoff_date:
                archive_path = ARCHIVE_DIR / file_path.name
                shutil.move(str(file_path), str(archive_path))
                archived_count += 1

    print(f"✓ Archived {archived_count} old approval records (>{days_threshold} days)")
    return archived_count


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Approval Workflow Manager - Enhanced HITL")
    parser.add_argument("--action", required=True,
                       choices=["list", "approve", "reject", "batch-approve", "analytics", "archive"])
    parser.add_argument("--id", help="File ID or name for approve/reject")
    parser.add_argument("--reason", help="Rejection reason (required for reject)")
    parser.add_argument("--notes", help="Approval notes (optional for approve)")
    parser.add_argument("--pattern", help="Pattern for batch operations")
    parser.add_argument("--days", type=int, default=30, help="Days threshold for archive")

    args = parser.parse_args()
    ensure_directories()

    if args.action == "list":
        display_pending_approvals()

    elif args.action == "approve":
        if not args.id:
            print("Error: --id required for approve action")
            sys.exit(1)
        if not approve_action(args.id, args.notes):
            sys.exit(1)

    elif args.action == "reject":
        if not args.id:
            print("Error: --id required for reject action")
            sys.exit(1)
        if not args.reason:
            print("Error: --reason required for reject action")
            sys.exit(1)
        if not reject_action(args.id, args.reason):
            sys.exit(1)

    elif args.action == "batch-approve":
        if not args.pattern:
            print("Error: --pattern required for batch-approve")
            sys.exit(1)
        batch_approve(args.pattern, args.notes)

    elif args.action == "analytics":
        generate_analytics()

    elif args.action == "archive":
        archive_old_approvals(args.days)


if __name__ == "__main__":
    main()
