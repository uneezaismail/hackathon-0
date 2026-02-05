#!/usr/bin/env python3
"""
Ralph Wiggum Stop Hook - Keep Claude working until task complete.

This stop hook intercepts Claude's exit and checks if the task is complete.
If not, it re-injects the prompt to continue the loop.

Gold Tier Strategy: File movement detection
- Checks if task file has moved to /Done/ folder
- More reliable than promise-based completion
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime


def check_completion():
    """Check if Ralph loop task is complete."""
    state_dir = Path(os.getenv('RALPH_STATE_DIR', 'Active_Tasks'))

    # Find active state file
    state_files = list(state_dir.glob('ralph_state_*.json'))
    if not state_files:
        return True  # No active loop, allow exit

    state_file = state_files[0]

    try:
        with open(state_file) as f:
            state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading state file: {e}", file=sys.stderr)
        return True  # Allow exit on error

    # Check completion criteria
    task_file = state.get('task_file')
    vault_root = Path(os.getenv('VAULT_ROOT', 'AI_Employee_Vault'))
    done_dir = vault_root / 'Done'

    # Primary completion: Task file in /Done/
    if task_file and (done_dir / task_file).exists():
        print(f"✅ Task complete: {task_file} found in /Done/", file=sys.stderr)
        state_file.unlink()  # Cleanup state file
        return True

    # Secondary completion: Max iterations reached
    if state['iteration'] >= state['max_iterations']:
        print(f"⚠️  Max iterations ({state['max_iterations']}) reached", file=sys.stderr)
        state_file.unlink()  # Cleanup state file
        return True

    # Task incomplete - update state and continue loop
    state['iteration'] += 1
    state['last_iteration'] = datetime.now().isoformat()

    try:
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
    except IOError as e:
        print(f"Error updating state file: {e}", file=sys.stderr)
        return True  # Allow exit on error

    print(f"🔄 Continuing loop (iteration {state['iteration']}/{state['max_iterations']})", file=sys.stderr)
    return False  # Block exit, continue loop


if __name__ == '__main__':
    should_exit = check_completion()
    sys.exit(0 if should_exit else 1)
