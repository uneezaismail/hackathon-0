#!/usr/bin/env python3
"""
Watchdog Component Health Monitor

Monitors AI Employee components (orchestrator, watchers, MCP servers) for crashes
and automatically restarts them. Detects crash loops and sends alerts.

Components monitored:
- Orchestrator (run_watcher.py)
- Gmail watcher
- WhatsApp watcher
- LinkedIn watcher
- MCP servers (Odoo, Facebook, Instagram, Twitter)

Usage:
    python watchdog.py
    python watchdog.py --check-interval 60
"""

import os
import sys
import time
import json
import psutil
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/watchdog.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

# Check interval (seconds)
CHECK_INTERVAL = int(os.getenv('WATCHDOG_CHECK_INTERVAL', '60'))

# Crash loop detection (3 restarts within 5 minutes)
CRASH_LOOP_THRESHOLD = 3
CRASH_LOOP_WINDOW = 300  # seconds

# Component definitions
COMPONENTS = {
    'orchestrator': {
        'name': 'Orchestrator',
        'command': ['python3', 'My_AI_Employee/run_watcher.py'],
        'cwd': str(Path(__file__).parent),
        'enabled': True
    },
    'gmail_watcher': {
        'name': 'Gmail Watcher',
        'command': ['python3', 'My_AI_Employee/watchers/gmail_watcher.py'],
        'cwd': str(Path(__file__).parent),
        'enabled': False  # Disabled by default (Silver tier)
    },
    'whatsapp_watcher': {
        'name': 'WhatsApp Watcher',
        'command': ['python3', 'My_AI_Employee/watchers/whatsapp_watcher.py'],
        'cwd': str(Path(__file__).parent),
        'enabled': False  # Disabled by default (Silver tier)
    },
    'linkedin_watcher': {
        'name': 'LinkedIn Watcher',
        'command': ['python3', 'My_AI_Employee/watchers/linkedin_watcher.py'],
        'cwd': str(Path(__file__).parent),
        'enabled': False  # Disabled by default (Silver tier)
    }
}

# State file
STATE_FILE = os.path.join(Path(__file__).parent, '.watchdog_state.json')


# ============================================================================
# STATE MANAGEMENT
# ============================================================================

def load_state() -> Dict[str, Any]:
    """
    Load watchdog state from file.

    Returns:
        State dict
    """
    if not os.path.exists(STATE_FILE):
        return {
            'components': {},
            'started_at': datetime.now().isoformat()
        }

    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to load state: {e}")
        return {
            'components': {},
            'started_at': datetime.now().isoformat()
        }


def save_state(state: Dict[str, Any]) -> bool:
    """
    Save watchdog state to file.

    Args:
        state: State dict

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        return True
    except IOError as e:
        logger.error(f"Failed to save state: {e}")
        return False


# ============================================================================
# COMPONENT DETECTION
# ============================================================================

def detect_components() -> Dict[str, Dict[str, Any]]:
    """
    Detect running components by process name.

    Returns:
        Dict of component_id -> process info
    """
    running = {}

    for component_id, config in COMPONENTS.items():
        if not config['enabled']:
            continue

        # Find process by command
        command_str = ' '.join(config['command'])

        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and command_str in ' '.join(cmdline):
                    running[component_id] = {
                        'pid': proc.info['pid'],
                        'name': config['name'],
                        'started_at': datetime.fromtimestamp(proc.info['create_time']).isoformat(),
                        'status': 'running'
                    }
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    return running


def is_component_running(component_id: str) -> bool:
    """
    Check if component is running.

    Args:
        component_id: Component ID

    Returns:
        True if running, False otherwise
    """
    running = detect_components()
    return component_id in running


# ============================================================================
# COMPONENT MANAGEMENT
# ============================================================================

def start_component(component_id: str) -> Optional[int]:
    """
    Start a component.

    Args:
        component_id: Component ID

    Returns:
        Process PID or None if failed
    """
    config = COMPONENTS.get(component_id)
    if not config:
        logger.error(f"Unknown component: {component_id}")
        return None

    if not config['enabled']:
        logger.warning(f"Component disabled: {component_id}")
        return None

    logger.info(f"Starting {config['name']}...")

    try:
        proc = subprocess.Popen(
            config['command'],
            cwd=config['cwd'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )

        # Wait a moment to ensure it started
        time.sleep(2)

        if proc.poll() is None:
            logger.info(f"✓ {config['name']} started (PID: {proc.pid})")
            return proc.pid
        else:
            logger.error(f"✗ {config['name']} failed to start")
            return None

    except Exception as e:
        logger.error(f"Failed to start {config['name']}: {e}")
        return None


def stop_component(component_id: str) -> bool:
    """
    Stop a component.

    Args:
        component_id: Component ID

    Returns:
        True if stopped, False otherwise
    """
    running = detect_components()
    component_info = running.get(component_id)

    if not component_info:
        logger.warning(f"Component not running: {component_id}")
        return True

    pid = component_info['pid']
    logger.info(f"Stopping {component_info['name']} (PID: {pid})...")

    try:
        proc = psutil.Process(pid)
        proc.terminate()

        # Wait for graceful shutdown
        proc.wait(timeout=10)

        logger.info(f"✓ {component_info['name']} stopped")
        return True

    except psutil.TimeoutExpired:
        # Force kill
        logger.warning(f"Force killing {component_info['name']}...")
        proc.kill()
        return True

    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        logger.error(f"Failed to stop {component_info['name']}: {e}")
        return False


def restart_component(component_id: str) -> bool:
    """
    Restart a component.

    Args:
        component_id: Component ID

    Returns:
        True if restarted, False otherwise
    """
    logger.info(f"Restarting component: {component_id}")

    # Stop if running
    if is_component_running(component_id):
        stop_component(component_id)
        time.sleep(2)

    # Start
    pid = start_component(component_id)
    return pid is not None


# ============================================================================
# CRASH LOOP DETECTION
# ============================================================================

def detect_crash_loop(component_id: str, state: Dict[str, Any]) -> bool:
    """
    Detect crash loop (3 restarts within 5 minutes).

    Args:
        component_id: Component ID
        state: Watchdog state

    Returns:
        True if crash loop detected, False otherwise
    """
    component_state = state['components'].get(component_id, {})
    restart_history = component_state.get('restart_history', [])

    # Filter recent restarts (within window)
    cutoff_time = datetime.now() - timedelta(seconds=CRASH_LOOP_WINDOW)
    recent_restarts = [
        r for r in restart_history
        if datetime.fromisoformat(r) > cutoff_time
    ]

    return len(recent_restarts) >= CRASH_LOOP_THRESHOLD


def record_restart(component_id: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Record component restart in state.

    Args:
        component_id: Component ID
        state: Watchdog state

    Returns:
        Updated state
    """
    if component_id not in state['components']:
        state['components'][component_id] = {
            'restart_count': 0,
            'restart_history': [],
            'last_restart': None
        }

    component_state = state['components'][component_id]
    component_state['restart_count'] += 1
    component_state['restart_history'].append(datetime.now().isoformat())
    component_state['last_restart'] = datetime.now().isoformat()

    # Keep only recent history (last 10 restarts)
    component_state['restart_history'] = component_state['restart_history'][-10:]

    return state


def send_alert(component_id: str, message: str):
    """
    Send alert notification.

    Args:
        component_id: Component ID
        message: Alert message
    """
    logger.error(f"🚨 ALERT: {message}")

    # In production, send to notification system (email, Slack, etc.)
    # For now, just log
    alert_file = os.path.join(Path(__file__).parent, 'My_AI_Employee', 'AI_Employee_Vault', 'Alerts', f'ALERT_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{component_id}.md')

    os.makedirs(os.path.dirname(alert_file), exist_ok=True)

    with open(alert_file, 'w') as f:
        f.write(f"""---
type: alert
component: {component_id}
severity: critical
created_at: {datetime.now().isoformat()}
---

# Component Alert: {COMPONENTS[component_id]['name']}

{message}

## Action Required

1. Check component logs
2. Investigate root cause
3. Manual intervention may be required

## Component Details

- Component ID: {component_id}
- Name: {COMPONENTS[component_id]['name']}
- Command: {' '.join(COMPONENTS[component_id]['command'])}
""")

    logger.info(f"Alert saved: {alert_file}")


# ============================================================================
# HEALTH CHECK
# ============================================================================

def health_check(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform health check on all components.

    Args:
        state: Watchdog state

    Returns:
        Updated state
    """
    logger.info("=" * 80)
    logger.info("Watchdog Health Check")
    logger.info("=" * 80)

    running = detect_components()

    for component_id, config in COMPONENTS.items():
        if not config['enabled']:
            continue

        logger.info(f"\nChecking {config['name']}...")

        if component_id in running:
            logger.info(f"  ✓ Running (PID: {running[component_id]['pid']})")
        else:
            logger.warning(f"  ✗ Not running - attempting restart...")

            # Check for crash loop
            if detect_crash_loop(component_id, state):
                message = f"{config['name']} crash loop detected ({CRASH_LOOP_THRESHOLD} restarts in {CRASH_LOOP_WINDOW}s)"
                send_alert(component_id, message)
                logger.error(f"  🚨 Crash loop detected - manual intervention required")
                continue

            # Attempt restart
            if restart_component(component_id):
                state = record_restart(component_id, state)
                logger.info(f"  ✓ Restarted successfully")
            else:
                logger.error(f"  ✗ Restart failed")

    logger.info("\n" + "=" * 80)

    return state


# ============================================================================
# MAIN
# ============================================================================

def main():
    logger.info("=" * 80)
    logger.info("Watchdog Component Monitor - Starting")
    logger.info("=" * 80)
    logger.info(f"Check interval: {CHECK_INTERVAL}s")
    logger.info(f"Crash loop threshold: {CRASH_LOOP_THRESHOLD} restarts in {CRASH_LOOP_WINDOW}s")
    logger.info("")

    # Load state
    state = load_state()

    try:
        while True:
            # Perform health check
            state = health_check(state)

            # Save state
            save_state(state)

            # Wait for next check
            logger.info(f"\nNext check in {CHECK_INTERVAL}s...")
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        logger.info("\n\nWatchdog stopped by user")
        return 0

    except Exception as e:
        logger.error(f"Watchdog error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
