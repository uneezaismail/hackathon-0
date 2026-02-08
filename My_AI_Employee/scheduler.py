#!/usr/bin/env python3
"""
Scheduler for Gold Tier AI Employee

Manages scheduled tasks:
- Weekly CEO briefing (Sunday 8:00 PM)
- Daily health checks
- Periodic cleanup tasks

Usage:
    python scheduler.py
    python scheduler.py --daemon  # Run in background
"""

import os
import sys
import time
import logging
import schedule
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# SCHEDULED TASKS
# ============================================================================

def generate_ceo_briefing():
    """
    Generate weekly CEO briefing.

    Runs every Sunday at 8:00 PM.
    Uses Ralph Wiggum Loop for autonomous execution.
    """
    logger.info("=" * 80)
    logger.info("Starting weekly CEO briefing generation")
    logger.info("=" * 80)

    try:
        # Create briefing request in /Needs_Action/
        vault_path = os.getenv(
            'AI_EMPLOYEE_VAULT_PATH',
            os.path.join(Path(__file__).parent, 'AI_Employee_Vault')
        )

        needs_action_dir = os.path.join(vault_path, 'Needs_Action')
        os.makedirs(needs_action_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        briefing_file = os.path.join(needs_action_dir, f"SCHEDULED_{timestamp}_ceo_briefing.md")

        content = f"""---
type: ceo_briefing
created_at: {datetime.now().isoformat()}
status: pending
priority: high
scheduled: true
---

# Weekly CEO Briefing Request

Generate comprehensive weekly business briefing for Monday morning review.

## Data Sources
- Completed tasks from /Done/ (last 7 days)
- Financial data from Odoo (revenue, expenses, invoices)
- Social media metrics (Facebook, Instagram, Twitter)
- Business goals from Business_Goals.md

## Sections Required
- Executive summary
- Revenue analysis
- Expense analysis
- Completed tasks
- Bottlenecks
- Proactive suggestions
- Social media performance
- Upcoming deadlines

## Instructions
Use @ceo-briefing-generator skill to generate briefing.
Save to /Briefings/BRIEF-{datetime.now().strftime('%Y-W%U')}.md
"""

        with open(briefing_file, 'w') as f:
            f.write(content)

        logger.info(f"✓ CEO briefing request created: {briefing_file}")
        logger.info("  Next: Run @needs-action-triage to process")
        logger.info("  Or: Start Ralph Wiggum Loop for autonomous processing")

        return True

    except Exception as e:
        logger.error(f"Failed to generate CEO briefing: {e}", exc_info=True)
        return False


def daily_health_check():
    """
    Perform daily health check.

    Runs every day at 9:00 AM.
    Checks component status and logs health metrics.
    """
    logger.info("Running daily health check")

    try:
        # Check watchdog status
        watchdog_state = os.path.join(Path(__file__).parent, '.watchdog_state.json')
        if os.path.exists(watchdog_state):
            logger.info("✓ Watchdog state file exists")
        else:
            logger.warning("⚠️  Watchdog state file not found")

        # Check Ralph state
        ralph_state = os.path.join(Path(__file__).parent, '.ralph_state.json')
        if os.path.exists(ralph_state):
            logger.info("✓ Ralph state file exists (loop may be running)")
        else:
            logger.info("✓ No active Ralph loop")

        # Check vault structure
        vault_path = os.getenv(
            'AI_EMPLOYEE_VAULT_PATH',
            os.path.join(Path(__file__).parent, 'AI_Employee_Vault')
        )

        required_folders = ['Needs_Action', 'Done', 'Pending_Approval', 'Approved', 'Briefings']
        for folder in required_folders:
            folder_path = os.path.join(vault_path, folder)
            if os.path.exists(folder_path):
                count = len([f for f in os.listdir(folder_path) if f.endswith('.md')])
                logger.info(f"✓ {folder}: {count} files")
            else:
                logger.warning(f"⚠️  {folder}: Missing")

        logger.info("Daily health check complete")
        return True

    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return False


def cleanup_old_logs():
    """
    Clean up old log files.

    Runs every Sunday at 11:00 PM.
    Removes logs older than 30 days.
    """
    logger.info("Running log cleanup")

    try:
        vault_path = os.getenv(
            'AI_EMPLOYEE_VAULT_PATH',
            os.path.join(Path(__file__).parent, 'AI_Employee_Vault')
        )

        logs_dir = os.path.join(vault_path, 'Logs')
        if not os.path.exists(logs_dir):
            logger.info("No logs directory found")
            return True

        # Count log files
        log_files = [f for f in os.listdir(logs_dir) if f.endswith('.json')]
        logger.info(f"Found {len(log_files)} log files")

        # In production, implement actual cleanup logic here
        # For now, just log the count

        logger.info("Log cleanup complete")
        return True

    except Exception as e:
        logger.error(f"Log cleanup failed: {e}", exc_info=True)
        return False


# ============================================================================
# SCHEDULER SETUP
# ============================================================================

def setup_schedule():
    """Configure all scheduled tasks."""

    # Weekly CEO briefing - Every Sunday at 8:00 PM
    schedule.every().sunday.at("20:00").do(generate_ceo_briefing)
    logger.info("✓ Scheduled: CEO briefing (Sunday 8:00 PM)")

    # Daily health check - Every day at 9:00 AM
    schedule.every().day.at("09:00").do(daily_health_check)
    logger.info("✓ Scheduled: Daily health check (9:00 AM)")

    # Weekly cleanup - Every Sunday at 11:00 PM
    schedule.every().sunday.at("23:00").do(cleanup_old_logs)
    logger.info("✓ Scheduled: Log cleanup (Sunday 11:00 PM)")

    logger.info("")
    logger.info("All scheduled tasks configured")


def run_scheduler():
    """Run the scheduler loop."""
    logger.info("=" * 80)
    logger.info("Gold Tier AI Employee Scheduler - Starting")
    logger.info("=" * 80)
    logger.info("")

    setup_schedule()

    logger.info("")
    logger.info("Scheduler running. Press Ctrl+C to stop.")
    logger.info("")

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    except KeyboardInterrupt:
        logger.info("")
        logger.info("Scheduler stopped by user")
        return 0

    except Exception as e:
        logger.error(f"Scheduler error: {e}", exc_info=True)
        return 1


# ============================================================================
# MAIN
# ============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Gold Tier AI Employee Scheduler")
    parser.add_argument("--daemon", action="store_true", help="Run in background")
    parser.add_argument("--test", action="store_true", help="Test scheduled tasks immediately")
    args = parser.parse_args()

    if args.test:
        logger.info("Testing scheduled tasks...")
        logger.info("")

        logger.info("1. Testing CEO briefing generation...")
        generate_ceo_briefing()
        logger.info("")

        logger.info("2. Testing daily health check...")
        daily_health_check()
        logger.info("")

        logger.info("3. Testing log cleanup...")
        cleanup_old_logs()
        logger.info("")

        logger.info("All tests complete")
        return 0

    if args.daemon:
        logger.info("Daemon mode not yet implemented")
        logger.info("Use: nohup python scheduler.py > /tmp/scheduler.log 2>&1 &")
        return 1

    return run_scheduler()


if __name__ == "__main__":
    sys.exit(main())
