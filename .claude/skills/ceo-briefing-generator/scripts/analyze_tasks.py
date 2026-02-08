#!/usr/bin/env python3
"""
Task Analysis and Bottleneck Detection

Analyzes completed tasks from /Done/ folder to identify:
- Task completion metrics
- Average completion time
- Bottlenecks (tasks taking longer than expected)
- Task type distribution

Usage:
    python analyze_tasks.py --days 7
    python analyze_tasks.py --start 2026-01-01 --end 2026-01-31
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import frontmatter

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

# Expected task durations (in days) by type
EXPECTED_DURATIONS = {
    'email': 0.5,
    'social_media_post': 1.0,
    'invoice': 1.0,
    'payment': 0.5,
    'expense': 0.5,
    'report': 2.0,
    'approval_request': 1.0,
    'general': 2.0
}

# Bottleneck threshold (multiplier of expected duration)
BOTTLENECK_THRESHOLD = 1.5


# ============================================================================
# TASK PARSING
# ============================================================================

def parse_task_file(file_path: str) -> Dict[str, Any]:
    """
    Parse task file and extract metadata.

    Args:
        file_path: Path to task file

    Returns:
        Task data dict
    """
    try:
        with open(file_path, 'r') as f:
            post = frontmatter.load(f)

        metadata = post.metadata
        content = post.content

        # Extract key fields
        task_data = {
            'file': os.path.basename(file_path),
            'title': metadata.get('title', content.split('\n')[0].strip('# ')),
            'type': metadata.get('type', 'general'),
            'created_at': metadata.get('created_at'),
            'completed_at': metadata.get('completed_at') or metadata.get('processed_at'),
            'status': metadata.get('status', 'completed'),
            'priority': metadata.get('priority', 'medium'),
            'result': metadata.get('result', 'success')
        }

        # Calculate duration
        if task_data['created_at'] and task_data['completed_at']:
            created = datetime.fromisoformat(task_data['created_at'])
            completed = datetime.fromisoformat(task_data['completed_at'])
            duration = (completed - created).total_seconds() / 86400  # days
            task_data['duration'] = round(duration, 2)
        else:
            task_data['duration'] = None

        return task_data

    except Exception as e:
        print(f"⚠️  Failed to parse {file_path}: {e}")
        return None


def get_completed_tasks(start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """
    Get all completed tasks within date range.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        List of task data dicts
    """
    done_dir = os.path.join(VAULT_PATH, 'Done')

    if not os.path.exists(done_dir):
        print(f"⚠️  /Done/ directory not found: {done_dir}")
        return []

    tasks = []

    for file_path in Path(done_dir).glob('*.md'):
        task_data = parse_task_file(str(file_path))

        if not task_data:
            continue

        # Check if within date range
        if task_data['completed_at']:
            completed = datetime.fromisoformat(task_data['completed_at'])
            if start_date <= completed <= end_date:
                tasks.append(task_data)

    return tasks


# ============================================================================
# METRICS CALCULATION
# ============================================================================

def calculate_task_metrics(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate task completion metrics.

    Args:
        tasks: List of task data dicts

    Returns:
        Metrics dict
    """
    if not tasks:
        return {
            'total_tasks': 0,
            'avg_duration': 0,
            'by_type': {},
            'by_priority': {},
            'success_rate': 0
        }

    # Count by type
    by_type = {}
    for task in tasks:
        task_type = task['type']
        by_type[task_type] = by_type.get(task_type, 0) + 1

    # Count by priority
    by_priority = {}
    for task in tasks:
        priority = task['priority']
        by_priority[priority] = by_priority.get(priority, 0) + 1

    # Calculate average duration
    durations = [t['duration'] for t in tasks if t['duration'] is not None]
    avg_duration = sum(durations) / len(durations) if durations else 0

    # Calculate success rate
    successful = sum(1 for t in tasks if t['result'] in ['success', 'completed', 'approved'])
    success_rate = (successful / len(tasks) * 100) if tasks else 0

    return {
        'total_tasks': len(tasks),
        'avg_duration': round(avg_duration, 2),
        'by_type': by_type,
        'by_priority': by_priority,
        'success_rate': round(success_rate, 1)
    }


# ============================================================================
# BOTTLENECK DETECTION
# ============================================================================

def detect_bottlenecks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect tasks that took longer than expected (bottlenecks).

    Args:
        tasks: List of task data dicts

    Returns:
        List of bottleneck dicts
    """
    bottlenecks = []

    for task in tasks:
        if task['duration'] is None:
            continue

        task_type = task['type']
        expected_duration = EXPECTED_DURATIONS.get(task_type, EXPECTED_DURATIONS['general'])
        actual_duration = task['duration']

        # Check if bottleneck
        if actual_duration > expected_duration * BOTTLENECK_THRESHOLD:
            delay = actual_duration - expected_duration

            bottlenecks.append({
                'task': task['title'],
                'type': task_type,
                'expected': expected_duration,
                'actual': actual_duration,
                'delay': round(delay, 2),
                'impact': 'High' if delay > 3 else 'Medium' if delay > 1 else 'Low'
            })

    # Sort by delay (descending)
    bottlenecks.sort(key=lambda x: x['delay'], reverse=True)

    return bottlenecks


# ============================================================================
# REPORT GENERATION
# ============================================================================

def generate_task_report(tasks: List[Dict[str, Any]], metrics: Dict[str, Any],
                        bottlenecks: List[Dict[str, Any]]) -> str:
    """
    Generate task analysis report markdown.

    Args:
        tasks: List of task data dicts
        metrics: Task metrics
        bottlenecks: List of bottleneck dicts

    Returns:
        Markdown report
    """
    report = f"""## Completed Tasks

**Total Completed**: {metrics['total_tasks']} tasks
**Average Completion Time**: {metrics['avg_duration']} days
**Success Rate**: {metrics['success_rate']}%

### By Type

"""

    for task_type, count in sorted(metrics['by_type'].items(), key=lambda x: x[1], reverse=True):
        report += f"- **{task_type.replace('_', ' ').title()}**: {count} tasks\n"

    report += "\n### By Priority\n\n"

    for priority, count in sorted(metrics['by_priority'].items(), key=lambda x: x[1], reverse=True):
        report += f"- **{priority.title()}**: {count} tasks\n"

    # Recent tasks
    report += "\n### Recent Completions\n\n"
    recent_tasks = sorted(tasks, key=lambda x: x['completed_at'] or '', reverse=True)[:10]

    for task in recent_tasks:
        completed = datetime.fromisoformat(task['completed_at']).strftime('%b %d')
        duration_str = f" ({task['duration']}d)" if task['duration'] else ""
        report += f"- [{completed}] {task['title']}{duration_str}\n"

    # Bottlenecks
    if bottlenecks:
        report += "\n## Bottlenecks\n\n"
        report += "| Task | Expected | Actual | Delay | Impact |\n"
        report += "|------|----------|--------|-------|--------|\n"

        for bottleneck in bottlenecks[:5]:  # Top 5
            report += f"| {bottleneck['task'][:40]} | {bottleneck['expected']}d | {bottleneck['actual']}d | +{bottleneck['delay']}d | {bottleneck['impact']} |\n"

        report += "\n**Action Items**:\n"
        for bottleneck in bottlenecks[:3]:  # Top 3
            report += f"- Review {bottleneck['type'].replace('_', ' ')} workflow (avg delay: {bottleneck['delay']}d)\n"

    return report


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Analyze completed tasks and detect bottlenecks")
    parser.add_argument("--days", type=int, default=7, help="Number of days to analyze (default: 7)")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    parser.add_argument("--output", help="Output file path")
    args = parser.parse_args()

    # Determine date range
    if args.start and args.end:
        start_date = datetime.fromisoformat(args.start)
        end_date = datetime.fromisoformat(args.end)
    else:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days)

    print(f"Analyzing tasks from {start_date.date()} to {end_date.date()}")
    print()

    # Get completed tasks
    tasks = get_completed_tasks(start_date, end_date)
    print(f"Found {len(tasks)} completed tasks")

    if not tasks:
        print("No tasks to analyze")
        return 0

    # Calculate metrics
    metrics = calculate_task_metrics(tasks)
    print(f"Average completion time: {metrics['avg_duration']} days")
    print(f"Success rate: {metrics['success_rate']}%")
    print()

    # Detect bottlenecks
    bottlenecks = detect_bottlenecks(tasks)
    print(f"Detected {len(bottlenecks)} bottlenecks")

    if bottlenecks:
        print("\nTop bottlenecks:")
        for bottleneck in bottlenecks[:3]:
            print(f"  - {bottleneck['task'][:50]}: +{bottleneck['delay']}d delay ({bottleneck['impact']} impact)")

    print()

    # Generate report
    report = generate_task_report(tasks, metrics, bottlenecks)

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"✓ Report saved: {args.output}")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
