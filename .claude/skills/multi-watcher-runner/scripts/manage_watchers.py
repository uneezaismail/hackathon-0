#!/usr/bin/env python3
"""
Multi-Watcher Management - PM2 Process Control & Health Monitoring

Provides PM2-based process management for production deployments with
health monitoring, performance metrics, and dashboard integration.

Use this for production (PM2-managed processes).
Use run_watcher.py for development (thread-based).
"""
import argparse
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================

VAULT_ROOT = Path("My_AI_Employee/AI_Employee_Vault")
LOGS_DIR = VAULT_ROOT / "Logs"
DASHBOARD_FILE = VAULT_ROOT / "Dashboard.md"

# Watcher configurations for PM2
WATCHER_CONFIGS = {
    "gmail": {
        "script": "My_AI_Employee/run_watcher.py",
        "args": "--watcher gmail",
        "memory_limit": "100M"
    },
    "whatsapp": {
        "script": "My_AI_Employee/run_watcher.py",
        "args": "--watcher whatsapp",
        "memory_limit": "150M"
    },
    "linkedin": {
        "script": "My_AI_Employee/run_watcher.py",
        "args": "--watcher linkedin",
        "memory_limit": "100M"
    },
    "filesystem": {
        "script": "My_AI_Employee/run_watcher.py",
        "args": "--watcher filesystem",
        "memory_limit": "50M"
    }
}

MEMORY_WARNING_THRESHOLD = 0.8  # 80% of limit


# ============================================================================
# PM2 OPERATIONS
# ============================================================================

def check_pm2_installed() -> bool:
    """Check if PM2 is installed."""
    try:
        subprocess.run(["pm2", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_pm2_processes() -> List[Dict]:
    """Get list of PM2 processes."""
    try:
        result = subprocess.run(
            ["pm2", "jlist"],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error getting PM2 processes: {e}", file=sys.stderr)
        return []


def start_watcher_pm2(watcher_name: str) -> bool:
    """Start a watcher using PM2."""
    config = WATCHER_CONFIGS.get(watcher_name)
    if not config:
        print(f"✗ Unknown watcher: {watcher_name}")
        return False

    # Check if already running
    processes = get_pm2_processes()
    for proc in processes:
        if proc.get("name") == f"watcher-{watcher_name}" and proc.get("pm2_env", {}).get("status") == "online":
            print(f"⚠️  Watcher '{watcher_name}' already running")
            return True

    # Start with PM2
    try:
        cmd = [
            "pm2", "start", config["script"],
            "--name", f"watcher-{watcher_name}",
            "--interpreter", "uv",
            "--interpreter-args", "run python",
            "--", *config["args"].split(),
            "--max-memory-restart", config["memory_limit"]
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            subprocess.run(["pm2", "save"], capture_output=True)
            print(f"✓ Started watcher: {watcher_name}")
            return True
        else:
            print(f"✗ Failed to start {watcher_name}: {result.stderr}")
            return False

    except Exception as e:
        print(f"✗ Error starting {watcher_name}: {e}")
        return False


def stop_watcher_pm2(watcher_name: str) -> bool:
    """Stop a watcher using PM2."""
    try:
        result = subprocess.run(
            ["pm2", "stop", f"watcher-{watcher_name}"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            subprocess.run(["pm2", "delete", f"watcher-{watcher_name}"], capture_output=True)
            subprocess.run(["pm2", "save"], capture_output=True)
            print(f"✓ Stopped watcher: {watcher_name}")
            return True
        else:
            print(f"⚠️  Watcher '{watcher_name}' not running")
            return True

    except Exception as e:
        print(f"✗ Error stopping {watcher_name}: {e}")
        return False


def restart_watcher_pm2(watcher_name: str) -> bool:
    """Restart a watcher using PM2."""
    try:
        result = subprocess.run(
            ["pm2", "restart", f"watcher-{watcher_name}"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"✓ Restarted watcher: {watcher_name}")
            return True
        else:
            print(f"✗ Failed to restart {watcher_name}")
            return False

    except Exception as e:
        print(f"✗ Error restarting {watcher_name}: {e}")
        return False


# ============================================================================
# HEALTH MONITORING
# ============================================================================

def check_watcher_health(watcher_name: str) -> Tuple[str, Dict]:
    """
    Check health of a watcher.
    Returns: (status, metrics)
    """
    processes = get_pm2_processes()

    for proc in processes:
        if proc.get("name") == f"watcher-{watcher_name}":
            pm2_env = proc.get("pm2_env", {})
            monit = proc.get("monit", {})

            status = pm2_env.get("status", "unknown")
            memory_mb = monit.get("memory", 0) / (1024 * 1024)
            cpu_percent = monit.get("cpu", 0)
            restart_count = pm2_env.get("restart_time", 0)
            uptime_ms = pm2_env.get("pm_uptime", 0)

            metrics = {
                "status": status,
                "memory_mb": round(memory_mb, 2),
                "cpu_percent": cpu_percent,
                "restart_count": restart_count,
                "uptime_seconds": (datetime.now().timestamp() * 1000 - uptime_ms) / 1000 if uptime_ms > 0 else 0
            }

            # Determine health status
            if status != "online":
                return "offline", metrics

            # Check memory usage
            config = WATCHER_CONFIGS.get(watcher_name, {})
            memory_limit_str = config.get("memory_limit", "100M")
            memory_limit_mb = int(memory_limit_str.replace("M", ""))

            if memory_mb > memory_limit_mb * MEMORY_WARNING_THRESHOLD:
                return "warning", metrics

            if restart_count > 5:
                return "warning", metrics

            return "healthy", metrics

    return "offline", {}


def perform_health_check_all() -> Dict[str, Tuple[str, Dict]]:
    """Perform health check on all watchers."""
    results = {}
    for watcher_name in WATCHER_CONFIGS.keys():
        health_status, metrics = check_watcher_health(watcher_name)
        results[watcher_name] = (health_status, metrics)
    return results


# ============================================================================
# DASHBOARD OPERATIONS
# ============================================================================

def update_dashboard_watchers(health_results: Dict[str, Tuple[str, Dict]]):
    """Update watcher status in Dashboard.md."""
    if not DASHBOARD_FILE.exists():
        return

    try:
        content = DASHBOARD_FILE.read_text()
        watcher_section = "\n## 🔍 Watcher Status\n\n"

        for watcher_name, (health_status, metrics) in health_results.items():
            status_emoji = {
                "healthy": "✅",
                "warning": "⚠️",
                "critical": "🔴",
                "offline": "⏸️"
            }.get(health_status, "❓")

            watcher_section += f"- **{watcher_name.title()}**: {status_emoji} {health_status.upper()}"

            if metrics:
                watcher_section += f" (Memory: {metrics.get('memory_mb', 0):.1f}MB, "
                watcher_section += f"CPU: {metrics.get('cpu_percent', 0):.1f}%, "
                watcher_section += f"Restarts: {metrics.get('restart_count', 0)})"

            watcher_section += "\n"

        watcher_section += f"\n*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        # Update or append watcher section
        if "## 🔍 Watcher Status" in content:
            lines = content.split("\n")
            new_lines = []
            skip = False

            for line in lines:
                if line.startswith("## 🔍 Watcher Status"):
                    skip = True
                    new_lines.append(watcher_section.strip())
                    continue

                if skip and line.startswith("##"):
                    skip = False

                if not skip:
                    new_lines.append(line)

            content = "\n".join(new_lines)
        else:
            content += "\n" + watcher_section

        DASHBOARD_FILE.write_text(content)

    except Exception as e:
        print(f"Warning: Dashboard update failed: {e}", file=sys.stderr)


# ============================================================================
# ORCHESTRATION OPERATIONS
# ============================================================================

def start_all_watchers() -> int:
    """Start all configured watchers."""
    started_count = 0

    print("Starting all watchers with PM2...")
    print("-" * 60)

    for watcher_name in WATCHER_CONFIGS.keys():
        if start_watcher_pm2(watcher_name):
            started_count += 1
            time.sleep(1)

    print("-" * 60)
    print(f"✓ Started {started_count}/{len(WATCHER_CONFIGS)} watchers")

    return started_count


def stop_all_watchers() -> int:
    """Stop all watchers."""
    stopped_count = 0

    print("Stopping all watchers...")
    print("-" * 60)

    for watcher_name in WATCHER_CONFIGS.keys():
        if stop_watcher_pm2(watcher_name):
            stopped_count += 1

    print("-" * 60)
    print(f"✓ Stopped {stopped_count}/{len(WATCHER_CONFIGS)} watchers")

    return stopped_count


def display_status():
    """Display comprehensive status of all watchers."""
    print("\n" + "=" * 80)
    print("MULTI-WATCHER STATUS (PM2)")
    print("=" * 80 + "\n")

    health_results = perform_health_check_all()

    # Summary
    healthy_count = sum(1 for status, _ in health_results.values() if status == "healthy")
    warning_count = sum(1 for status, _ in health_results.values() if status == "warning")
    offline_count = sum(1 for status, _ in health_results.values() if status == "offline")

    print(f"📊 Summary:")
    print(f"  Healthy:  {healthy_count}")
    print(f"  Warning:  {warning_count}")
    print(f"  Offline:  {offline_count}")
    print(f"  Total:    {len(WATCHER_CONFIGS)}")
    print()

    # Detailed status
    print(f"{'Watcher':<15} | {'Status':<10} | {'Memory':<12} | {'CPU':<8} | {'Restarts':<10} | {'Uptime'}")
    print("-" * 80)

    for watcher_name, (health_status, metrics) in sorted(health_results.items()):
        status_emoji = {
            "healthy": "✅",
            "warning": "⚠️",
            "critical": "🔴",
            "offline": "⏸️"
        }.get(health_status, "❓")

        memory_str = f"{metrics.get('memory_mb', 0):.1f}MB" if metrics else "N/A"
        cpu_str = f"{metrics.get('cpu_percent', 0):.1f}%" if metrics else "N/A"
        restart_str = str(metrics.get('restart_count', 0)) if metrics else "N/A"

        uptime_seconds = metrics.get('uptime_seconds', 0) if metrics else 0
        if uptime_seconds > 3600:
            uptime_str = f"{uptime_seconds / 3600:.1f}h"
        elif uptime_seconds > 60:
            uptime_str = f"{uptime_seconds / 60:.1f}m"
        else:
            uptime_str = f"{uptime_seconds:.0f}s" if uptime_seconds > 0 else "N/A"

        print(f"{watcher_name:<15} | {status_emoji} {health_status:<8} | {memory_str:<12} | {cpu_str:<8} | {restart_str:<10} | {uptime_str}")

    print("\n" + "=" * 80 + "\n")

    # Update dashboard
    update_dashboard_watchers(health_results)


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Multi-Watcher Management (PM2)")
    parser.add_argument("--action", required=True,
                       choices=["start", "stop", "restart", "status", "start-all", "stop-all", "health"])
    parser.add_argument("--watcher", help="Specific watcher (gmail, whatsapp, linkedin, filesystem)")

    args = parser.parse_args()

    # Check PM2 installation
    if not check_pm2_installed():
        print("✗ PM2 not installed. Install with: npm install -g pm2")
        print("\nAlternatively, use thread-based approach:")
        print("  uv run python run_watcher.py --watcher all")
        sys.exit(1)

    if args.action == "start":
        if not args.watcher:
            print("Error: --watcher required for start action")
            sys.exit(1)
        if not start_watcher_pm2(args.watcher):
            sys.exit(1)

    elif args.action == "stop":
        if not args.watcher:
            print("Error: --watcher required for stop action")
            sys.exit(1)
        if not stop_watcher_pm2(args.watcher):
            sys.exit(1)

    elif args.action == "restart":
        if not args.watcher:
            print("Error: --watcher required for restart action")
            sys.exit(1)
        if not restart_watcher_pm2(args.watcher):
            sys.exit(1)

    elif args.action == "start-all":
        start_all_watchers()

    elif args.action == "stop-all":
        stop_all_watchers()

    elif args.action == "status":
        display_status()

    elif args.action == "health":
        health_results = perform_health_check_all()
        print("\nHealth Check Results:")
        print("-" * 60)
        for watcher_name, (health_status, metrics) in health_results.items():
            status_emoji = {
                "healthy": "✅",
                "warning": "⚠️",
                "offline": "⏸️"
            }.get(health_status, "❓")
            print(f"{status_emoji} {watcher_name}: {health_status.upper()}")
            if metrics:
                print(f"   Memory: {metrics.get('memory_mb', 0):.1f}MB")
                print(f"   CPU: {metrics.get('cpu_percent', 0):.1f}%")
                print(f"   Restarts: {metrics.get('restart_count', 0)}")
        print("-" * 60)
        update_dashboard_watchers(health_results)


if __name__ == "__main__":
    main()
