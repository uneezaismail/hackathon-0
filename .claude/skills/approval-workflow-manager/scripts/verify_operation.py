#!/usr/bin/env python3
"""
Approval Workflow Manager - Verification Script

Tests the approval workflow functionality to ensure everything works correctly.
"""
import sys
import subprocess
from pathlib import Path
import tempfile
import shutil

# Configuration
VAULT_ROOT = Path("My_AI_Employee/AI_Employee_Vault")
PENDING_DIR = VAULT_ROOT / "Pending_Approval"
APPROVED_DIR = VAULT_ROOT / "Approved"
REJECTED_DIR = VAULT_ROOT / "Rejected"
SCRIPT_PATH = Path(__file__).parent / "main_operation.py"

def run_test():
    """Run verification tests."""
    print("\nApproval Workflow Manager - Verification")
    print("=" * 60)

    test_results = []

    # Test 1: Check directories exist
    print("\n[Test 1] Checking directory structure...")
    dirs_exist = all([
        PENDING_DIR.exists(),
        APPROVED_DIR.exists(),
        REJECTED_DIR.exists()
    ])
    test_results.append(("Directory structure", dirs_exist))
    print(f"  {'✓' if dirs_exist else '✗'} Directories exist")

    # Test 2: Create test approval file
    print("\n[Test 2] Creating test approval file...")
    test_file = PENDING_DIR / "TEST_VERIFICATION_APPROVAL.md"
    test_content = """---
type: approval_request
action_type: test_action
priority: medium
created_at: 2026-02-12T10:00:00Z
---

# Test Approval Request

This is a test approval request for verification purposes.
"""

    try:
        test_file.write_text(test_content)
        file_created = test_file.exists()
        test_results.append(("Test file creation", file_created))
        print(f"  {'✓' if file_created else '✗'} Test file created")
    except Exception as e:
        test_results.append(("Test file creation", False))
        print(f"  ✗ Failed to create test file: {e}")
        return False

    # Test 3: List pending approvals
    print("\n[Test 3] Testing list functionality...")
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--action", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        list_works = result.returncode == 0 and "TEST_VERIFICATION_APPROVAL" in result.stdout
        test_results.append(("List functionality", list_works))
        print(f"  {'✓' if list_works else '✗'} List command works")
    except Exception as e:
        test_results.append(("List functionality", False))
        print(f"  ✗ List command failed: {e}")

    # Test 4: Approve action
    print("\n[Test 4] Testing approve functionality...")
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH),
             "--action", "approve",
             "--id", "TEST_VERIFICATION_APPROVAL",
             "--notes", "Automated verification test"],
            capture_output=True,
            text=True,
            timeout=10
        )
        approve_works = result.returncode == 0
        file_moved = (APPROVED_DIR / "TEST_VERIFICATION_APPROVAL.md").exists()
        test_results.append(("Approve functionality", approve_works and file_moved))
        print(f"  {'✓' if approve_works and file_moved else '✗'} Approve command works")
    except Exception as e:
        test_results.append(("Approve functionality", False))
        print(f"  ✗ Approve command failed: {e}")

    # Test 5: Analytics
    print("\n[Test 5] Testing analytics functionality...")
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--action", "analytics"],
            capture_output=True,
            text=True,
            timeout=10
        )
        analytics_works = result.returncode == 0 and "ANALYTICS" in result.stdout
        test_results.append(("Analytics functionality", analytics_works))
        print(f"  {'✓' if analytics_works else '✗'} Analytics command works")
    except Exception as e:
        test_results.append(("Analytics functionality", False))
        print(f"  ✗ Analytics command failed: {e}")

    # Cleanup
    print("\n[Cleanup] Removing test files...")
    try:
        approved_test = APPROVED_DIR / "TEST_VERIFICATION_APPROVAL.md"
        if approved_test.exists():
            approved_test.unlink()
        print("  ✓ Cleanup complete")
    except Exception as e:
        print(f"  ⚠ Cleanup warning: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    for test_name, result in test_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ All verification tests passed!")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return False

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
