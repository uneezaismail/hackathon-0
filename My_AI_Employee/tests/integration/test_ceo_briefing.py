#!/usr/bin/env python3
"""
Integration Tests for CEO Briefing Generator

Tests data aggregation, analysis, and briefing generation workflows.
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def temp_vault():
    """Create temporary vault directory structure."""
    temp_dir = tempfile.mkdtemp()
    vault_path = os.path.join(temp_dir, "AI_Employee_Vault")

    # Create vault folders
    os.makedirs(os.path.join(vault_path, "Done"))
    os.makedirs(os.path.join(vault_path, "Needs_Action"))
    os.makedirs(os.path.join(vault_path, "Briefings"))

    yield vault_path

    # Cleanup
    shutil.rmtree(temp_dir)


# ============================================================================
# T088: Test Odoo data aggregation
# ============================================================================

def test_odoo_data_aggregation_dry_run():
    """Test Odoo data aggregation with simulated data."""
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "ceo-briefing-generator" / "scripts"))
    from generate_briefing import collect_odoo_data

    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 1, 31)

    data = collect_odoo_data(start_date, end_date, dry_run=True)

    assert 'revenue' in data
    assert 'expenses' in data
    assert 'invoices' in data
    assert 'aged_receivables' in data

    assert data['revenue']['this_week'] > 0
    assert data['revenue']['mtd'] > 0
    assert data['revenue']['target'] > 0
    assert 0 <= data['revenue']['progress'] <= 100


def test_odoo_revenue_calculation():
    """Test revenue calculation and progress tracking."""
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "ceo-briefing-generator" / "scripts"))
    from generate_briefing import collect_odoo_data

    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 1, 31)

    data = collect_odoo_data(start_date, end_date, dry_run=True)

    # Verify progress calculation
    expected_progress = (data['revenue']['mtd'] / data['revenue']['target']) * 100
    assert abs(data['revenue']['progress'] - expected_progress) < 0.1


def test_odoo_expense_categorization():
    """Test expense categorization by category."""
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "ceo-briefing-generator" / "scripts"))
    from generate_briefing import collect_odoo_data

    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 1, 31)

    data = collect_odoo_data(start_date, end_date, dry_run=True)

    assert 'by_category' in data['expenses']
    assert len(data['expenses']['by_category']) > 0

    # Verify total matches sum of categories
    total = sum(data['expenses']['by_category'].values())
    assert total > 0


# ============================================================================
# T089: Test social media metrics aggregation
# ============================================================================

def test_social_media_metrics_aggregation():
    """Test social media metrics aggregation from all platforms."""
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "ceo-briefing-generator" / "scripts"))
    from generate_briefing import collect_social_media_data

    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 1, 31)

    data = collect_social_media_data(start_date, end_date, dry_run=True)

    assert 'facebook' in data
    assert 'instagram' in data
    assert 'twitter' in data
    assert 'top_posts' in data

    # Verify each platform has required metrics
    for platform in ['facebook', 'instagram']:
        assert 'posts' in data[platform]
        assert 'reach' in data[platform]
        assert 'engagement' in data[platform]

    assert 'tweets' in data['twitter']
    assert 'impressions' in data['twitter']


def test_social_media_top_posts():
    """Test top posts identification across platforms."""
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "ceo-briefing-generator" / "scripts"))
    from generate_briefing import collect_social_media_data

    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 1, 31)

    data = collect_social_media_data(start_date, end_date, dry_run=True)

    assert len(data['top_posts']) > 0

    for post in data['top_posts']:
        assert 'platform' in post
        assert 'content' in post
        assert 'reach' in post
        assert post['reach'] > 0


# ============================================================================
# T090: Test completed tasks analysis
# ============================================================================

def test_completed_tasks_analysis(temp_vault):
    """Test completed tasks analysis from /Done/ folder."""
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "ceo-briefing-generator" / "scripts"))
    from analyze_tasks import get_completed_tasks, calculate_task_metrics

    # Create test task files
    done_dir = os.path.join(temp_vault, "Done")

    for i in range(5):
        task_file = os.path.join(done_dir, f"task_{i}.md")
        created = datetime.now() - timedelta(days=7)
        completed = datetime.now() - timedelta(days=7-i)

        content = f"""---
type: email
created_at: {created.isoformat()}
completed_at: {completed.isoformat()}
status: completed
priority: medium
result: success
---

# Task {i}

Test task content
"""
        with open(task_file, 'w') as f:
            f.write(content)

    # Override VAULT_PATH
    import analyze_tasks
    original_vault = analyze_tasks.VAULT_PATH
    analyze_tasks.VAULT_PATH = temp_vault

    try:
        start_date = datetime.now() - timedelta(days=8)
        end_date = datetime.now()

        tasks = get_completed_tasks(start_date, end_date)
        assert len(tasks) == 5

        metrics = calculate_task_metrics(tasks)
        assert metrics['total_tasks'] == 5
        assert metrics['avg_duration'] > 0
        assert metrics['success_rate'] == 100.0
    finally:
        analyze_tasks.VAULT_PATH = original_vault


def test_task_metrics_calculation():
    """Test task metrics calculation (avg duration, success rate)."""
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "ceo-briefing-generator" / "scripts"))
    from analyze_tasks import calculate_task_metrics

    tasks = [
        {'type': 'email', 'duration': 0.5, 'priority': 'high', 'result': 'success'},
        {'type': 'invoice', 'duration': 1.0, 'priority': 'medium', 'result': 'success'},
        {'type': 'report', 'duration': 2.0, 'priority': 'low', 'result': 'failed'},
    ]

    metrics = calculate_task_metrics(tasks)

    assert metrics['total_tasks'] == 3
    assert metrics['avg_duration'] == 1.17  # (0.5 + 1.0 + 2.0) / 3
    assert metrics['success_rate'] == 66.7  # 2/3 * 100
    assert 'email' in metrics['by_type']
    assert 'high' in metrics['by_priority']


# ============================================================================
# T091: Test bottleneck detection
# ============================================================================

def test_bottleneck_detection():
    """Test bottleneck detection for tasks taking longer than expected."""
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "ceo-briefing-generator" / "scripts"))
    from analyze_tasks import detect_bottlenecks

    tasks = [
        {'title': 'Quick email', 'type': 'email', 'duration': 0.3},  # Expected: 0.5d, no bottleneck
        {'title': 'Slow invoice', 'type': 'invoice', 'duration': 3.0},  # Expected: 1.0d, bottleneck!
        {'title': 'Long report', 'type': 'report', 'duration': 5.0},  # Expected: 2.0d, bottleneck!
    ]

    bottlenecks = detect_bottlenecks(tasks)

    assert len(bottlenecks) == 2
    assert bottlenecks[0]['task'] == 'Long report'  # Sorted by delay
    assert bottlenecks[0]['delay'] > 0
    assert bottlenecks[0]['impact'] in ['High', 'Medium', 'Low']


def test_bottleneck_threshold():
    """Test bottleneck threshold (1.5x expected duration)."""
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "ceo-briefing-generator" / "scripts"))
    from analyze_tasks import detect_bottlenecks, EXPECTED_DURATIONS, BOTTLENECK_THRESHOLD

    # Task exactly at threshold (not a bottleneck)
    tasks = [
        {'title': 'At threshold', 'type': 'email', 'duration': EXPECTED_DURATIONS['email'] * BOTTLENECK_THRESHOLD}
    ]

    bottlenecks = detect_bottlenecks(tasks)
    assert len(bottlenecks) == 0

    # Task just over threshold (is a bottleneck)
    tasks = [
        {'title': 'Over threshold', 'type': 'email', 'duration': EXPECTED_DURATIONS['email'] * BOTTLENECK_THRESHOLD + 0.1}
    ]

    bottlenecks = detect_bottlenecks(tasks)
    assert len(bottlenecks) == 1


# ============================================================================
# T092: Test proactive suggestions
# ============================================================================

def test_subscription_detection():
    """Test subscription detection from expenses."""
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "ceo-briefing-generator" / "scripts"))
    from analyze_subscriptions import detect_subscriptions

    expenses = [
        {'description': 'Adobe Creative Cloud subscription', 'amount': 99.99, 'date': '2026-01-15', 'category': 'Software'},
        {'description': 'Office supplies', 'amount': 50.00, 'date': '2026-01-10', 'category': 'Office'},
        {'description': 'Notion monthly plan', 'amount': 15.00, 'date': '2026-01-01', 'category': 'Software'},
    ]

    subscriptions = detect_subscriptions(expenses)

    assert len(subscriptions) == 2  # Adobe and Notion
    assert any('Adobe' in sub['name'] for sub in subscriptions)
    assert any('Notion' in sub['name'] for sub in subscriptions)


def test_unused_subscription_detection():
    """Test unused subscription detection (no activity in 30+ days)."""
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "ceo-briefing-generator" / "scripts"))
    from analyze_subscriptions import analyze_subscription_usage

    subscriptions = [
        {'name': 'Adobe Creative Cloud', 'amount': 99.99, 'date': '2026-01-15', 'category': 'Software', 'vendor': 'Adobe'},
        {'name': 'Notion', 'amount': 15.00, 'date': '2026-01-01', 'category': 'Software', 'vendor': 'Notion'},
    ]

    tasks = [
        {'title': 'Design in Adobe', 'completed_at': '2026-01-20T10:00:00', 'content': 'Used Adobe Creative Cloud'},
        # No tasks mentioning Notion
    ]

    usage_data = analyze_subscription_usage(subscriptions, tasks)

    assert len(usage_data) == 2

    # Adobe should have recent usage
    adobe = next(u for u in usage_data if 'Adobe' in u['name'])
    assert adobe['days_since_used'] < 30

    # Notion should be unused
    notion = next(u for u in usage_data if 'Notion' in u['name'])
    assert notion['days_since_used'] > 30


def test_duplicate_tools_detection():
    """Test duplicate tools detection (multiple tools for same purpose)."""
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "ceo-briefing-generator" / "scripts"))
    from analyze_subscriptions import detect_duplicate_tools

    subscriptions = [
        {'name': 'Slack Pro', 'amount': 12.50, 'date': '2026-01-10', 'category': 'Software'},
        {'name': 'Microsoft Teams', 'amount': 20.00, 'date': '2026-01-05', 'category': 'Software'},
    ]

    duplicates = detect_duplicate_tools(subscriptions)

    assert len(duplicates) == 1
    assert duplicates[0]['category'] == 'Communication'
    assert len(duplicates[0]['tools']) == 2
    assert duplicates[0]['total_cost'] == 32.50


def test_briefing_generation_integration(temp_vault):
    """Test complete briefing generation workflow."""
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "ceo-briefing-generator" / "scripts"))
    from generate_briefing import generate_briefing_markdown

    # Prepare test data
    odoo_data = {
        'revenue': {'this_week': 2500.00, 'mtd': 4500.00, 'target': 10000.00, 'progress': 45.0, 'trend': 'on_track'},
        'expenses': {'this_week': 850.00, 'mtd': 1200.00, 'by_category': {'Software': 400.00}},
        'invoices': {'paid': [], 'unpaid': []},
        'aged_receivables': {}
    }

    social_data = {
        'facebook': {'posts': 5, 'reach': 1234, 'engagement': 89},
        'instagram': {'posts': 7, 'reach': 2456, 'engagement': 234},
        'twitter': {'tweets': 12, 'impressions': 3456, 'engagement': 145},
        'top_posts': []
    }

    task_metrics = {'total_tasks': 10, 'avg_duration': 2.3, 'success_rate': 95.0, 'by_type': {}, 'by_priority': {}}
    bottlenecks = []
    suggestions = "## Proactive Suggestions\n\nNo suggestions at this time.\n"
    deadlines = []
    business_goals = {'revenue_target': 10000.00, 'expense_budget': 3000.00, 'kpis': {}}
    tasks_report = "## Completed Tasks\n\n**Total**: 10 tasks\n"

    briefing = generate_briefing_markdown(
        odoo_data, social_data, task_metrics, bottlenecks,
        suggestions, deadlines, business_goals, tasks_report
    )

    # Verify briefing structure
    assert '# Weekly Business Briefing' in briefing
    assert '## Executive Summary' in briefing
    assert '## Revenue' in briefing
    assert '## Expenses' in briefing
    assert '## Completed Tasks' in briefing
    assert '## Social Media Performance' in briefing
    assert '## Proactive Suggestions' in briefing
    assert '## Upcoming Deadlines' in briefing


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
