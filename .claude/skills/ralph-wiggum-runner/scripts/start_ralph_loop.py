#!/usr/bin/env python3
"""
Start Ralph Wiggum Loop - Autonomous Task Startup Workflow

Initializes Ralph state, validates task, and starts autonomous processing.
The stop hook will intercept Claude's exit and continue until task complete.

Usage:
    python start_ralph_loop.py --task "Process all items in /Needs_Action" --max-iterations 10
    python start_ralph_loop.py --task-file /path/to/task.md --max-iterations 5
"""

import os
import sys
import json
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

# Default max iterations
DEFAULT_MAX_ITERATIONS = int(os.getenv('RALPH_MAX_ITERATIONS', '10'))

# Default check interval (seconds)
DEFAULT_CHECK_INTERVAL = int(os.getenv('RALPH_CHECK_INTERVAL', '5'))


# ============================================================================
# VALIDATION
# ============================================================================

def validate_vault_structure() -> bool:
    """
    Validate that vault has required folder structure.

    Returns:
        True if valid, False otherwise
    """
    required_folders = ['Needs_Action', 'Done', 'Pending_Approval', 'Approved']

    for folder in required_folders:
        folder_path = os.path.join(VAULT_PATH, folder)
        if not os.path.exists(folder_path):
            print(f"❌ Missing required folder: {folder_path}")
            return False

    return True


def validate_stop_hook() -> bool:
    """
    Validate that stop hook is installed and executable.

    Returns:
        True if valid, False otherwise
    """
    stop_hook_path = os.path.join(
        Path(__file__).parent.parent.parent.parent,
        '.claude', 'hooks', 'stop', 'ralph_wiggum_check.py'
    )

    if not os.path.exists(stop_hook_path):
        print(f"❌ Stop hook not found: {stop_hook_path}")
        print("   Run: python scripts/install_stop_hook.py")
        return False

    if not os.access(stop_hook_path, os.X_OK):
        print(f"⚠️  Stop hook not executable: {stop_hook_path}")
        print("   Run: chmod +x .claude/hooks/stop/ralph_wiggum_check.py")
        return False

    return True


def check_existing_loop() -> bool:
    """
    Check if a Ralph loop is already running.

    Returns:
        True if loop running, False otherwise
    """
    if os.path.exists(RALPH_STATE_FILE):
        with open(RALPH_STATE_FILE, 'r') as f:
            state = json.load(f)

        print(f"⚠️  Ralph loop already running:")
        print(f"   Task: {state.get('task_file', 'N/A')}")
        print(f"   Iteration: {state.get('iteration', 0)}/{state.get('max_iterations', 0)}")
        print(f"   Started: {state.get('started_at', 'N/A')}")
        print()
        print("   To stop: python scripts/stop_ralph_loop.py")
        return True

    return False


# ============================================================================
# STATE MANAGEMENT
# ============================================================================

def create_ralph_state(task_file: str, task_description: str, max_iterations: int) -> dict:
    """
    Create initial Ralph state.

    Args:
        task_file: Path to task file (or empty if task description)
        task_description: Task description
        max_iterations: Max iterations

    Returns:
        State dict
    """
    state = {
        "task_file": task_file,
        "task_description": task_description,
        "iteration": 0,
        "max_iterations": max_iterations,
        "started_at": datetime.now().isoformat(),
        "last_iteration_at": None,
        "check_interval": DEFAULT_CHECK_INTERVAL
    }

    return state


def save_ralph_state(state: dict) -> bool:
    """
    Save Ralph state to file.

    Args:
        state: State dict

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(RALPH_STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        return True
    except IOError as e:
        print(f"❌ Failed to save Ralph state: {e}")
        return False


# ============================================================================
# TASK SETUP
# ============================================================================

def find_task_file_in_needs_action() -> str:
    """
    Find first task file in /Needs_Action/.

    Returns:
        Path to task file or empty string
    """
    needs_action_dir = os.path.join(VAULT_PATH, 'Needs_Action')

    if not os.path.exists(needs_action_dir):
        return ""

    # Find first markdown file
    for filename in os.listdir(needs_action_dir):
        if filename.endswith('.md'):
            return os.path.join(needs_action_dir, filename)

    return ""


def create_task_file(task_description: str) -> str:
    """
    Create task file in /Needs_Action/ from description.

    Args:
        task_description: Task description

    Returns:
        Path to created task file
    """
    needs_action_dir = os.path.join(VAULT_PATH, 'Needs_Action')
    os.makedirs(needs_action_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    task_file = os.path.join(needs_action_dir, f"RALPH_{timestamp}_autonomous_task.md")

    content = f"""---
type: autonomous_task
created_at: {datetime.now().isoformat()}
status: pending
priority: high
---

# Autonomous Task - Ralph Wiggum Loop

{task_description}

## Instructions

Process this task autonomously until complete. Move this file to /Done/ when finished.

## Completion Criteria

- All action items processed
- All required files created/updated
- All tests passing (if applicable)
- This file moved to /Done/
"""

    with open(task_file, 'w') as f:
        f.write(content)

    return task_file


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Start Ralph Wiggum Loop for autonomous task processing")
    parser.add_argument("--task", help="Task description")
    parser.add_argument("--task-file", help="Path to existing task file in /Needs_Action/")
    parser.add_argument("--max-iterations", type=int, default=DEFAULT_MAX_ITERATIONS,
                        help=f"Max iterations (default: {DEFAULT_MAX_ITERATIONS})")
    parser.add_argument("--force", action="store_true", help="Force start even if loop running")
    args = parser.parse_args()

    print("=" * 80)
    print("Ralph Wiggum Loop - Autonomous Task Startup")
    print("=" * 80)
    print()

    # Validate environment
    print("Validating environment...")

    if not validate_vault_structure():
        print("\n❌ Vault structure invalid. Cannot start Ralph loop.")
        return 1

    if not validate_stop_hook():
        print("\n❌ Stop hook not ready. Cannot start Ralph loop.")
        return 1

    print("✓ Environment valid")
    print()

    # Check for existing loop
    if not args.force and check_existing_loop():
        print("Use --force to override and start new loop")
        return 1

    # Determine task file
    task_file = ""
    task_description = ""

    if args.task_file:
        # Use provided task file
        if not os.path.exists(args.task_file):
            print(f"❌ Task file not found: {args.task_file}")
            return 1
        task_file = args.task_file
        task_description = f"Process task file: {os.path.basename(args.task_file)}"
        print(f"Using task file: {task_file}")

    elif args.task:
        # Create task file from description
        task_description = args.task
        task_file = create_task_file(task_description)
        print(f"Created task file: {task_file}")

    else:
        # Auto-detect first file in /Needs_Action/
        task_file = find_task_file_in_needs_action()
        if task_file:
            task_description = f"Process task file: {os.path.basename(task_file)}"
            print(f"Auto-detected task file: {task_file}")
        else:
            print("❌ No task specified and no files in /Needs_Action/")
            print("   Use --task or --task-file to specify task")
            return 1

    print()

    # Create Ralph state
    print(f"Initializing Ralph loop...")
    print(f"  Task: {task_description}")
    print(f"  Max iterations: {args.max_iterations}")
    print(f"  Check interval: {DEFAULT_CHECK_INTERVAL}s")
    print()

    state = create_ralph_state(task_file, task_description, args.max_iterations)

    if not save_ralph_state(state):
        print("❌ Failed to save Ralph state")
        return 1

    print("✅ Ralph loop initialized!")
    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("1. Claude Code will now process the task autonomously")
    print("2. Stop hook will intercept exit and continue until complete")
    print("3. Task complete when file moves to /Done/")
    print()
    print("Monitor progress:")
    print("  python scripts/ralph_status.py")
    print()
    print("Stop loop:")
    print("  python scripts/stop_ralph_loop.py")
    print()
    print("View logs:")
    print("  tail -f /tmp/ralph_wiggum_hook.log")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
