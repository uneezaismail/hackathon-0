#!/usr/bin/env python3
"""
Multi-Watcher Runner - Verification Script

Tests the PM2 management functionality.
"""
import sys
import subprocess
from pathlib import Path

SCRIPT_PATH = Path(__file__).parent / "manage_watchers.py"

def verify():
    """Run verification tests."""
    print("\nMulti-Watcher Runner - Verification")
    print("=" * 60)

    test_results = []

    # Test 1: Check PM2 installation
    print("\n[Test 1] Checking PM2 installation...")
    try:
        result = subprocess.run(
            ["pm2", "--version"],
            capture_output=True,
            timeout=5
        )
        pm2_installed = result.returncode == 0
        test_results.append(("PM2 installed", pm2_installed))
        print(f"  {'✓' if pm2_installed else '✗'} PM2 available")
        if pm2_installed:
            version = result.stdout.decode().strip()
            print(f"    Version: {version}")
    except Exception:
        test_results.append(("PM2 installed", False))
        print("  ✗ PM2 not found")

    # Test 2: Check manage_watchers.py exists
    print("\n[Test 2] Checking manage_watchers.py exists...")
    script_exists = SCRIPT_PATH.exists()
    test_results.append(("Script exists", script_exists))
    print(f"  {'✓' if script_exists else '✗'} manage_watchers.py found")

    # Test 3: Check script is executable
    print("\n[Test 3] Checking script permissions...")
    if script_exists:
        is_executable = SCRIPT_PATH.stat().st_mode & 0o111 != 0
        test_results.append(("Script executable", is_executable))
        print(f"  {'✓' if is_executable else '✗'} Script has execute permissions")
    else:
        test_results.append(("Script executable", False))
        print("  ✗ Cannot check permissions (script not found)")

    # Test 4: Test status command
    print("\n[Test 4] Testing status command...")
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--action", "status"],
            capture_output=True,
            text=True,
            timeout=10
        )
        status_works = result.returncode == 0
        test_results.append(("Status command", status_works))
        print(f"  {'✓' if status_works else '✗'} Status command works")
        if not status_works and result.stderr:
            print(f"    Error: {result.stderr[:100]}")
    except Exception as e:
        test_results.append(("Status command", False))
        print(f"  ✗ Status command failed: {e}")

    # Test 5: Test health check command
    print("\n[Test 5] Testing health check command...")
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--action", "health"],
            capture_output=True,
            text=True,
            timeout=10
        )
        health_works = result.returncode == 0
        test_results.append(("Health check command", health_works))
        print(f"  {'✓' if health_works else '✗'} Health check works")
    except Exception as e:
        test_results.append(("Health check command", False))
        print(f"  ✗ Health check failed: {e}")

    # Test 6: Check vault structure
    print("\n[Test 6] Checking vault structure...")
    vault_root = Path("My_AI_Employee/AI_Employee_Vault")
    required_dirs = [
        vault_root / "Logs",
        vault_root / "Needs_Action",
        vault_root / "Plans",
        vault_root / "Approved",
        vault_root / "Done"
    ]

    vault_ok = all(d.exists() for d in required_dirs)
    test_results.append(("Vault structure", vault_ok))
    print(f"  {'✓' if vault_ok else '✗'} Vault directories exist")

    if not vault_ok:
        for d in required_dirs:
            if not d.exists():
                print(f"    Missing: {d}")

    # Test 7: Check Dashboard.md exists
    print("\n[Test 7] Checking Dashboard.md...")
    dashboard_file = vault_root / "Dashboard.md"
    dashboard_exists = dashboard_file.exists()
    test_results.append(("Dashboard.md exists", dashboard_exists))
    print(f"  {'✓' if dashboard_exists else '✗'} Dashboard.md found")

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
        print("\nYou can now use PM2 management:")
        print("  python3 .claude/skills/multi-watcher-runner/scripts/manage_watchers.py --action start-all")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

        if not test_results[0][1]:  # PM2 not installed
            print("\nTo install PM2:")
            print("  npm install -g pm2")

        if not test_results[5][1]:  # Vault structure missing
            print("\nTo create vault structure:")
            print("  /setup-vault")

        return False

if __name__ == "__main__":
    success = verify()
    sys.exit(0 if success else 1)
