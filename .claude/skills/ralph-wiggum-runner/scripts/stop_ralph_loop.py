#!/usr/bin/env python3
"""
Stop Ralph Wiggum Loop - State Management and Recovery Workflow

Gracefully stops a running Ralph loop with state cleanup and recovery options.
Supports graceful shutdown (completes current iteration) or force stop (immediate).

Usage:
    python stop_ralph_loop.py              # Graceful stop
    python stop_ralph_loop.py --force      # Force stop
    python stop_ralph_loop.py --recover    # Recover from crash
"""

import os
import sys
import json
import argparse
import shutil
from pathlib import Path
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


# ============================================================================
# CONFIGURATION
# ============================================================================

# Vault path
VAULT_PATH = os.getenv(
    'AI_EMPLOYEE_VAULT_PATH',
    os.path.join(Path(__file__).parent.parent.parent.parent, 'My_AI_Employee', 'AI_Employee_Vault')
)

# Ralph state file
RALPH_STATE_FILE = os.getenv(
    'RALPH_STATE_FILE',
    os.path.join(Path(__file__).parent.parent.parent.parent, '.ralph_state.json')
)

# Backup directory
BACKUP_DIR = os.path.join(Path(__file__).parent.parent.parent.parent, '.ralph_backups')


# ============================================================================
# STATE MANAGEMENT
# ============================================================================

def get_ralph_state() -> dict:
    """
    Read Ralph Wiggum Loop state.

    Returns:
        State dict or None if no active loop
    """
    if not os.path.exists(RALPH_STATE_FILE):
        return None

    try:
        with open(RALPH_STATE_FILE, 'r') as f:
            state = json.load(f)
        return state
    except (json.JSONDecodeError, IOError) as e:
        print(f"❌ Failed to read Ralph state: {e}")
        return None


def backup_ralph_state(state: dict) -> str:
    """
    Backup Ralph state before stopping.

    Args:
        state: State dict to backup

    Returns:
        Path to backup file
    """
    os.makedirs(BACKUP_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"ralph_state_{timestamp}.json")

    try:
        with open(backup_file, 'w') as f:
            json.dump(state, f, indent=2)
        return backup_file
    except IOError as e:
        print(f"⚠️  Failed to backup state: {e}")
        return ""


def clear_ralph_state() -> bool:
    """
    Clear Ralph state file.

    Returns:
        True if successful, False otherwise
    """
    try:
        if os.path.exists(RALPH_STATE_FILE):
            os.remove(RALPH_STATE_FILE)
        return True
    except IOError as e:
        print(f"❌ Failed to clear Ralph state: {e}")
        return False


def list_backups() -> list:
    """
    List available state backups.

    Returns:
        List of backup file paths (sorted newest first)
    """
    if not os.path.exists(BACKUP_DIR):
        return []

    backups = []
    for filename in os.listdir(BACKUP_DIR):
        if filename.startswith('ralph_state_') and filename.endswith('.json'):
            backup_path = os.path.join(BACKUP_DIR, filename)
            backups.append(backup_path)

    # Sort by modification time (newest first)
    backups.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return backups


def restore_ralph_state(backup_file: str) -> bool:
    """
    Restore Ralph state from backup.

    Args:
        backup_file: Path to backup file

    Returns:
        True if successful, False otherwise
    """
    if not os.path.exists(backup_file):
        print(f"❌ Backup file not found: {backup_file}")
        return False

    try:
        shutil.copy2(backup_file, RALPH_STATE_FILE)
        print(f"✓ State restored from: {backup_file}")
        return True
    except IOError as e:
        print(f"❌ Failed to restore state: {e}")
        return False


# ============================================================================
# STOP OPERATIONS
# ============================================================================

def graceful_stop(state: dict) -> bool:
    """
    Gracefully stop Ralph loop (completes current iteration).

    Args:
        state: Current Ralph state

    Returns:
        True if successful, False otherwise
    """
    print("Performing graceful stop...")
    print("  Current iteration will complete")
    print("  Stop hook will allow exit on next check")
    print()

    # Backup state
    backup_file = backup_ralph_state(state)
    if backup_file:
        print(f"✓ State backed up: {backup_file}")

    # Clear state (stop hook will allow exit)
    if clear_ralph_state():
        print("✓ State cleared - loop will exit gracefully")
        return True
    else:
        print("❌ Failed to clear state")
        return False


def force_stop(state: dict) -> bool:
    """
    Force stop Ralph loop (immediate).

    Args:
        state: Current Ralph state

    Returns:
        True if successful, False otherwise
    """
    print("⚠️  Performing force stop...")
    print("  Loop will stop immediately")
    print("  Current iteration may be incomplete")
    print()

    # Backup state
    backup_file = backup_ralph_state(state)
    if backup_file:
        print(f"✓ State backed up: {backup_file}")

    # Clear state
    if clear_ralph_state():
        print("✓ State cleared - loop stopped")
        return True
    else:
        print("❌ Failed to clear state")
        return False


# ============================================================================
# RECOVERY OPERATIONS
# ============================================================================

def recover_from_crash() -> bool:
    """
    Recover Ralph loop from crash.

    Returns:
        True if successful, False otherwise
    """
    print("Attempting crash recovery...")
    print()

    # List available backups
    backups = list_backups()

    if not backups:
        print("❌ No backups found. Cannot recover.")
        return False

    print(f"Found {len(backups)} backup(s):")
    for i, backup in enumerate(backups[:5], 1):
        filename = os.path.basename(backup)
        mtime = datetime.fromtimestamp(os.path.getmtime(backup))
        print(f"  {i}. {filename} ({mtime.strftime('%Y-%m-%d %H:%M:%S')})")

    print()

    # Use most recent backup
    latest_backup = backups[0]
    print(f"Using most recent backup: {os.path.basename(latest_backup)}")
    print()

    # Read backup state
    try:
        with open(latest_backup, 'r') as f:
            state = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"❌ Failed to read backup: {e}")
        return False

    # Display state info
    print("Backup state:")
    print(f"  Task: {state.get('task_description', 'N/A')}")
    print(f"  Iteration: {state.get('iteration', 0)}/{state.get('max_iterations', 0)}")
    print(f"  Started: {state.get('started_at', 'N/A')}")
    print()

    # Ask for confirmation
    response = input("Restore this state? (y/n): ")
    if response.lower() != 'y':
        print("Recovery cancelled.")
        return False

    # Restore state
    if restore_ralph_state(latest_backup):
        print()
        print("✅ Recovery complete!")
        print()
        print("To resume loop:")
        print("  Claude Code will automatically continue on next run")
        return True
    else:
        return False


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Stop Ralph Wiggum Loop")
    parser.add_argument("--force", action="store_true", help="Force stop (immediate)")
    parser.add_argument("--recover", action="store_true", help="Recover from crash")
    parser.add_argument("--list-backups", action="store_true", help="List available backups")
    args = parser.parse_args()

    print("=" * 80)
    print("Ralph Wiggum Loop - Stop/Recovery")
    print("=" * 80)
    print()

    # List backups
    if args.list_backups:
        backups = list_backups()
        if not backups:
            print("No backups found.")
        else:
            print(f"Found {len(backups)} backup(s):")
            for backup in backups:
                filename = os.path.basename(backup)
                mtime = datetime.fromtimestamp(os.path.getmtime(backup))
                print(f"  {filename} ({mtime.strftime('%Y-%m-%d %H:%M:%S')})")
        print()
        return 0

    # Recover from crash
    if args.recover:
        if recover_from_crash():
            return 0
        else:
            return 1

    # Stop loop
    state = get_ralph_state()

    if not state:
        print("ℹ️  No Ralph loop currently running")
        print()
        return 0

    # Display current state
    print("Current loop:")
    print(f"  Task: {state.get('task_description', 'N/A')}")
    print(f"  Iteration: {state.get('iteration', 0)}/{state.get('max_iterations', 0)}")
    print(f"  Started: {state.get('started_at', 'N/A')}")
    print()

    # Perform stop
    if args.force:
        success = force_stop(state)
    else:
        success = graceful_stop(state)

    print()

    if success:
        print("✅ Ralph loop stopped successfully")
        print()
        print("To view backups:")
        print("  python scripts/stop_ralph_loop.py --list-backups")
        print()
        print("To recover:")
        print("  python scripts/stop_ralph_loop.py --recover")
        print()
        return 0
    else:
        print("❌ Failed to stop Ralph loop")
        return 1


if __name__ == "__main__":
    sys.exit(main())
