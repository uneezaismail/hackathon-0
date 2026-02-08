#!/usr/bin/env python3
"""
Ralph Loop Status - Task Completion Detection Workflow

Monitors Ralph Wiggum Loop progress and detects task completion.
Shows current iteration, task status, and completion criteria.

Usage:
    python ralph_status.py
    python ralph_status.py --watch  # Continuous monitoring
"""

import os
import sys
import json
import time
import argparse
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

# Stop hook log
STOP_HOOK_LOG = os.getenv('RALPH_LOG_FILE', '/tmp/ralph_wiggum_hook.log')


# ============================================================================
# STATE READING
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


def check_task_file_location(task_file: str) -> str:
    """
    Check which folder the task file is in.

    Args:
        task_file: Original task file path

    Returns:
        Folder name or "not_found"
    """
    if not task_file:
        return "unknown"

    task_filename = os.path.basename(task_file)

    # Check each folder
    folders = ['Needs_Action', 'Done', 'Pending_Approval', 'Approved', 'Rejected', 'Failed']

    for folder in folders:
        folder_path = os.path.join(VAULT_PATH, folder)
        check_file = os.path.join(folder_path, task_filename)
        if os.path.exists(check_file):
            return folder

    return "not_found"


def count_needs_action_items() -> int:
    """
    Count items in /Needs_Action/.

    Returns:
        Number of markdown files
    """
    needs_action_dir = os.path.join(VAULT_PATH, 'Needs_Action')

    if not os.path.exists(needs_action_dir):
        return 0

    md_files = list(Path(needs_action_dir).glob('*.md'))
    return len(md_files)


def get_recent_log_entries(num_lines: int = 10) -> list:
    """
    Get recent entries from stop hook log.

    Args:
        num_lines: Number of lines to retrieve

    Returns:
        List of log lines
    """
    if not os.path.exists(STOP_HOOK_LOG):
        return []

    try:
        with open(STOP_HOOK_LOG, 'r') as f:
            lines = f.readlines()
        return lines[-num_lines:]
    except IOError:
        return []


# ============================================================================
# STATUS DISPLAY
# ============================================================================

def display_status(state: dict, verbose: bool = False):
    """
    Display Ralph loop status.

    Args:
        state: Ralph state dict
        verbose: Show detailed information
    """
    print("=" * 80)
    print("Ralph Wiggum Loop - Status")
    print("=" * 80)
    print()

    # Basic info
    print("📊 Loop Status")
    print(f"  Iteration: {state.get('iteration', 0)}/{state.get('max_iterations', 0)}")
    print(f"  Started: {state.get('started_at', 'N/A')}")
    print(f"  Last iteration: {state.get('last_iteration_at', 'N/A')}")
    print()

    # Task info
    task_file = state.get('task_file', '')
    task_description = state.get('task_description', 'N/A')

    print("📝 Task Information")
    print(f"  Description: {task_description}")
    if task_file:
        print(f"  File: {os.path.basename(task_file)}")
        location = check_task_file_location(task_file)
        print(f"  Location: /{location}/")
    print()

    # Completion status
    print("✅ Completion Criteria")

    if task_file:
        location = check_task_file_location(task_file)
        if location == "Done":
            print("  ✓ Task file in /Done/ (COMPLETE)")
        elif location == "Needs_Action":
            print("  ⏳ Task file still in /Needs_Action/ (IN PROGRESS)")
        elif location == "Pending_Approval":
            print("  ⏸️  Task file in /Pending_Approval/ (WAITING FOR APPROVAL)")
        elif location == "not_found":
            print("  ⚠️  Task file not found (may have been deleted)")
        else:
            print(f"  ⏳ Task file in /{location}/ (IN PROGRESS)")
    else:
        # Fallback: check /Needs_Action/ count
        needs_action_count = count_needs_action_items()
        if needs_action_count == 0:
            print("  ✓ All items in /Needs_Action/ processed (COMPLETE)")
        else:
            print(f"  ⏳ {needs_action_count} items remaining in /Needs_Action/ (IN PROGRESS)")

    print()

    # Progress estimate
    current_iteration = state.get('iteration', 0)
    max_iterations = state.get('max_iterations', 10)
    progress_pct = (current_iteration / max_iterations * 100) if max_iterations > 0 else 0

    print("📈 Progress")
    print(f"  Iterations: {current_iteration}/{max_iterations} ({progress_pct:.0f}%)")

    # Progress bar
    bar_length = 40
    filled = int(bar_length * current_iteration / max_iterations) if max_iterations > 0 else 0
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"  [{bar}]")
    print()

    # Verbose info
    if verbose:
        print("🔍 Detailed Information")
        print(f"  State file: {RALPH_STATE_FILE}")
        print(f"  Vault path: {VAULT_PATH}")
        print(f"  Check interval: {state.get('check_interval', 5)}s")
        print()

        print("📋 Recent Log Entries")
        log_entries = get_recent_log_entries(5)
        if log_entries:
            for entry in log_entries:
                print(f"  {entry.rstrip()}")
        else:
            print("  No log entries found")
        print()


def display_no_loop():
    """Display message when no loop is running."""
    print("=" * 80)
    print("Ralph Wiggum Loop - Status")
    print("=" * 80)
    print()
    print("ℹ️  No Ralph loop currently running")
    print()
    print("To start a loop:")
    print("  python scripts/start_ralph_loop.py --task \"Your task description\"")
    print()


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Monitor Ralph Wiggum Loop status")
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring (refresh every 5s)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed information")
    parser.add_argument("--interval", type=int, default=5, help="Watch interval in seconds (default: 5)")
    args = parser.parse_args()

    try:
        while True:
            # Clear screen for watch mode
            if args.watch:
                os.system('clear' if os.name == 'posix' else 'cls')

            # Get state
            state = get_ralph_state()

            if state:
                display_status(state, args.verbose)

                # Check if complete
                task_file = state.get('task_file', '')
                if task_file:
                    location = check_task_file_location(task_file)
                    if location == "Done":
                        print("🎉 Task complete! Loop will exit on next iteration.")
                        print()
                        if args.watch:
                            break
                else:
                    needs_action_count = count_needs_action_items()
                    if needs_action_count == 0:
                        print("🎉 All items processed! Loop will exit on next iteration.")
                        print()
                        if args.watch:
                            break

                # Check if max iterations reached
                current_iteration = state.get('iteration', 0)
                max_iterations = state.get('max_iterations', 10)
                if current_iteration >= max_iterations:
                    print("⚠️  Max iterations reached. Loop will exit on next iteration.")
                    print()
                    if args.watch:
                        break

            else:
                display_no_loop()
                if args.watch:
                    break

            # Exit if not watching
            if not args.watch:
                break

            # Wait for next refresh
            print(f"Refreshing in {args.interval}s... (Ctrl+C to stop)")
            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
