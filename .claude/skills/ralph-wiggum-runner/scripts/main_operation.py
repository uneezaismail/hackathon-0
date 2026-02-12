#!/usr/bin/env python3
"""Ralph Wiggum Loop - Official Claude Code Plugin Integration

Creates state file in official format (.claude/ralph-loop.local.md) for the
Ralph Wiggum stop hook plugin.

Usage:
    python3 main_operation.py --action start --task "Your task description"
    python3 main_operation.py --action status
    python3 main_operation.py --action stop
"""
import argparse
import sys
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

STATE_FILE = Path(".claude/ralph-loop.local.md")
VAULT_ROOT = Path("My_AI_Employee/AI_Employee_Vault")
RALPH_HISTORY = VAULT_ROOT / "Ralph_History"
BACKUP_DIR = Path(".ralph_backups")

DEFAULT_MAX_ITERATIONS = 10

# ============================================================================
# SETUP
# ============================================================================

def setup_dirs():
    """Create required directories."""
    RALPH_HISTORY.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

# ============================================================================
# STATE MANAGEMENT
# ============================================================================

def create_state_file(task: str, max_iterations: int = DEFAULT_MAX_ITERATIONS,
                      completion_promise: str = None, watch_file: str = None):
    """Create state file in official Claude Code format."""
    setup_dirs()

    # Build frontmatter
    content = "---\n"
    content += f"iteration: 1\n"
    content += f"max_iterations: {max_iterations}\n"

    if completion_promise:
        content += f'completion_promise: "{completion_promise}"\n'

    if watch_file:
        content += f'watch_file: "{watch_file}"\n'

    content += f'started_at: "{datetime.now().isoformat()}"\n'
    content += f'last_iteration_at: "{datetime.now().isoformat()}"\n'
    content += f'status: "running"\n'
    content += "---\n\n"
    content += task

    STATE_FILE.write_text(content)

    # Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"ralph-loop_{timestamp}.md"
    backup_file.write_text(content)

    print(f"✅ Ralph loop initialized")
    print(f"   State file: {STATE_FILE}")
    print(f"   Max iterations: {max_iterations}")
    print(f"   Backup: {backup_file}")

    return STATE_FILE


def read_state_file():
    """Read current state."""
    if not STATE_FILE.exists():
        return None

    content = STATE_FILE.read_text()

    # Parse frontmatter
    if not content.startswith("---"):
        return None

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None

    frontmatter_text = parts[1].strip()
    task_text = parts[2].strip()

    # Parse YAML frontmatter
    state = {"task": task_text}
    for line in frontmatter_text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"')

            if value.isdigit():
                state[key] = int(value)
            else:
                state[key] = value

    return state


def display_status():
    """Display current loop status."""
    state = read_state_file()

    if not state:
        print("❌ No active Ralph loop")
        return

    print("\n" + "=" * 80)
    print("RALPH WIGGUM LOOP STATUS")
    print("=" * 80 + "\n")

    print(f"📊 Status: {state.get('status', 'unknown').upper()}")
    print(f"🔄 Iteration: {state.get('iteration', 0)}/{state.get('max_iterations', 0)}")
    print(f"⏰ Started: {state.get('started_at', 'unknown')}")
    print(f"🕐 Last iteration: {state.get('last_iteration_at', 'unknown')}")

    if state.get('completion_promise'):
        print(f"🎯 Completion promise: {state['completion_promise']}")

    if state.get('watch_file'):
        print(f"👁️  Watching file: {state['watch_file']}")

    print(f"\n📝 Task:\n{state.get('task', 'No task description')}")
    print("\n" + "=" * 80 + "\n")


def stop_loop():
    """Stop the Ralph loop."""
    if not STATE_FILE.exists():
        print("❌ No active Ralph loop to stop")
        return

    # Archive state
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_file = RALPH_HISTORY / f"ralph-loop_{timestamp}.md"

    STATE_FILE.rename(archive_file)

    print(f"✅ Ralph loop stopped")
    print(f"   State archived to: {archive_file}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Ralph Wiggum Loop Manager")
    parser.add_argument("--action", required=True,
                       choices=["start", "status", "stop"],
                       help="Action to perform")
    parser.add_argument("--task", help="Task description (for start action)")
    parser.add_argument("--max-iterations", type=int, default=DEFAULT_MAX_ITERATIONS,
                       help="Maximum iterations before stopping")
    parser.add_argument("--completion-promise", help="Completion promise text")
    parser.add_argument("--watch-file", help="File to watch for completion")

    args = parser.parse_args()

    if args.action == "start":
        if not args.task:
            print("Error: --task required for start action")
            sys.exit(1)

        if STATE_FILE.exists():
            print("⚠️  Active Ralph loop already exists")
            print("   Run with --action stop first, or check status with --action status")
            sys.exit(1)

        create_state_file(
            task=args.task,
            max_iterations=args.max_iterations,
            completion_promise=args.completion_promise,
            watch_file=args.watch_file
        )

        print("\n🚀 Ralph loop ready!")
        print("   The stop hook will intercept Claude's exit attempts")
        print("   and continue until task completion or max iterations.")
        print("\n   Now run your Claude Code command to start the loop.")

    elif args.action == "status":
        display_status()

    elif args.action == "stop":
        stop_loop()


if __name__ == "__main__":
    main()
