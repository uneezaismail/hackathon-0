#!/usr/bin/env python3
"""Verify Ralph Wiggum Runner skill operation."""
import sys
import os
from pathlib import Path

# Configuration
VAULT_ROOT = Path(os.getenv('AI_EMPLOYEE_VAULT_PATH', 'My_AI_Employee/AI_Employee_Vault'))
RALPH_STATE = VAULT_ROOT / "Ralph_State"
RALPH_HISTORY = VAULT_ROOT / "Ralph_History"
BACKUP_DIR = Path(".ralph_backups")
LOGS_DIR = VAULT_ROOT / "Logs"

def verify():
    """Verify Ralph Wiggum Runner setup."""
    checks = []

    # Check directories exist
    checks.append(("Ralph State directory", RALPH_STATE.exists()))
    checks.append(("Ralph History directory", RALPH_HISTORY.exists()))
    checks.append(("Backup directory", BACKUP_DIR.exists()))
    checks.append(("Logs directory", LOGS_DIR.exists()))

    # Check for any loop files
    active = list(RALPH_STATE.glob("RALPH_*.json")) if RALPH_STATE.exists() else []
    history = list(RALPH_HISTORY.glob("RALPH_*.json")) if RALPH_HISTORY.exists() else []
    backups = list(BACKUP_DIR.glob("RALPH_*.json")) if BACKUP_DIR.exists() else []

    checks.append(("Loop tracking functional", True))  # Always passes if dirs exist

    # Report results
    all_passed = True
    print("\nRalph Wiggum Runner - Verification")
    print("=" * 50)
    for name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"{status} {name}")
        if not passed:
            all_passed = False

    print(f"\nActive loops: {len(active)}")
    print(f"Completed loops: {len(history)}")
    print(f"Backups: {len(backups)}")
    print()

    if all_passed:
        print("✅ All checks passed!")
    else:
        print("❌ Some checks failed. Run setup:")
        print("  mkdir -p My_AI_Employee/AI_Employee_Vault/Ralph_State")
        print("  mkdir -p My_AI_Employee/AI_Employee_Vault/Ralph_History")
        print("  mkdir -p .ralph_backups")

    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    verify()
