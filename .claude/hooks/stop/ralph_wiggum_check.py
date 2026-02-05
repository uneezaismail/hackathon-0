#!/usr/bin/env python3
"""
Ralph Wiggum Stop Hook - Autonomous Task Completion

Intercepts Claude Code exit and re-injects prompt until task is complete.
Uses file movement detection: task file moves to /Done/ signals completion.

This hook is called by Claude Code when it's about to exit.
Return exit code:
- 0: Allow exit (task complete)
- 1: Block exit and continue (task incomplete)
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/ralph_wiggum_hook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


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

# Max iterations
MAX_ITERATIONS = int(os.getenv('RALPH_MAX_ITERATIONS', '10'))

# Check interval (seconds)
CHECK_INTERVAL = int(os.getenv('RALPH_CHECK_INTERVAL', '5'))


# ============================================================================
# STATE MANAGEMENT
# ============================================================================

def get_ralph_state() -> Optional[Dict[str, Any]]:
    """
    Read Ralph Wiggum Loop state from .ralph_state.json.

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
        logger.error(f"Failed to read Ralph state: {e}")
        return None


def update_ralph_state(state: Dict[str, Any]) -> bool:
    """
    Update Ralph Wiggum Loop state in .ralph_state.json.

    Args:
        state: State dict to save

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(RALPH_STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        return True
    except IOError as e:
        logger.error(f"Failed to write Ralph state: {e}")
        return False


def increment_iteration(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Increment iteration counter in state.

    Args:
        state: Current state dict

    Returns:
        Updated state dict
    """
    state['iteration'] = state.get('iteration', 0) + 1
    state['last_iteration_at'] = datetime.now().isoformat()
    return state


def clear_ralph_state() -> bool:
    """
    Clear Ralph Wiggum Loop state (task complete).

    Returns:
        True if successful, False otherwise
    """
    try:
        if os.path.exists(RALPH_STATE_FILE):
            os.remove(RALPH_STATE_FILE)
        logger.info("Ralph state cleared (task complete)")
        return True
    except IOError as e:
        logger.error(f"Failed to clear Ralph state: {e}")
        return False


# ============================================================================
# COMPLETION DETECTION
# ============================================================================

def check_task_complete(task_file: str) -> bool:
    """
    Check if task is complete by detecting file movement to /Done/.

    Args:
        task_file: Original task file path (in /Needs_Action/)

    Returns:
        True if task file moved to /Done/, False otherwise
    """
    # Check if task file still exists in /Needs_Action/
    if os.path.exists(task_file):
        logger.info(f"Task file still in /Needs_Action/: {task_file}")
        return False

    # Check if task file moved to /Done/
    done_dir = os.path.join(VAULT_PATH, 'Done')
    task_filename = os.path.basename(task_file)
    done_file = os.path.join(done_dir, task_filename)

    if os.path.exists(done_file):
        logger.info(f"Task file moved to /Done/: {done_file}")
        return True

    # File not in /Needs_Action/ and not in /Done/ - check other folders
    for folder in ['Pending_Approval', 'Approved', 'Rejected', 'Failed']:
        folder_path = os.path.join(VAULT_PATH, folder)
        check_file = os.path.join(folder_path, task_filename)
        if os.path.exists(check_file):
            logger.info(f"Task file in /{folder}/: {check_file} (not complete)")
            return False

    # File disappeared - assume complete
    logger.warning(f"Task file not found anywhere: {task_file} (assuming complete)")
    return True


def check_all_needs_action_processed() -> bool:
    """
    Check if all items in /Needs_Action/ have been processed.

    Returns:
        True if /Needs_Action/ is empty, False otherwise
    """
    needs_action_dir = os.path.join(VAULT_PATH, 'Needs_Action')

    if not os.path.exists(needs_action_dir):
        logger.warning(f"/Needs_Action/ directory not found: {needs_action_dir}")
        return True

    # Count markdown files in /Needs_Action/
    md_files = list(Path(needs_action_dir).glob('*.md'))
    count = len(md_files)

    logger.info(f"Items in /Needs_Action/: {count}")
    return count == 0


# ============================================================================
# MAIN HOOK LOGIC
# ============================================================================

def main() -> int:
    """
    Main stop hook logic.

    Returns:
        0: Allow exit (task complete)
        1: Block exit and continue (task incomplete)
    """
    logger.info("=" * 80)
    logger.info("Ralph Wiggum Stop Hook - Checking task completion")
    logger.info("=" * 80)

    # Get current Ralph state
    state = get_ralph_state()

    if not state:
        logger.info("No active Ralph loop - allowing exit")
        return 0

    # Get current iteration
    current_iteration = state.get('iteration', 0)
    max_iterations = state.get('max_iterations', MAX_ITERATIONS)
    task_file = state.get('task_file', '')

    logger.info(f"Current iteration: {current_iteration}/{max_iterations}")
    logger.info(f"Task file: {task_file}")

    # Check if max iterations reached
    if current_iteration >= max_iterations:
        logger.warning(f"Max iterations reached ({max_iterations}) - forcing exit")
        clear_ralph_state()
        print(f"\n⚠️  Ralph Wiggum Loop: Max iterations ({max_iterations}) reached. Exiting.")
        return 0

    # Check if task is complete
    task_complete = False

    if task_file:
        # Primary completion signal: task file moved to /Done/
        task_complete = check_task_complete(task_file)
    else:
        # Fallback: check if all /Needs_Action/ items processed
        task_complete = check_all_needs_action_processed()

    if task_complete:
        logger.info("✅ Task complete - allowing exit")
        clear_ralph_state()
        print(f"\n✅ Ralph Wiggum Loop: Task complete after {current_iteration} iterations. Exiting.")
        return 0

    # Task not complete - increment iteration and continue
    state = increment_iteration(state)
    update_ralph_state(state)

    logger.info(f"Task incomplete - continuing to iteration {state['iteration']}")
    print(f"\n🔄 Ralph Wiggum Loop: Task incomplete. Continuing to iteration {state['iteration']}/{max_iterations}...")
    print(f"   Checking for task completion: {task_file or '/Needs_Action/ empty'}")

    # Block exit - Claude will continue working
    return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Stop hook error: {e}", exc_info=True)
        # On error, allow exit to prevent infinite loop
        print(f"\n❌ Ralph Wiggum Loop: Error in stop hook: {e}")
        print("   Allowing exit to prevent infinite loop.")
        sys.exit(0)
