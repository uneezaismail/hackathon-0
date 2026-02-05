#!/usr/bin/env python3
"""
Generate CEO Briefing - Main Workflow

Generates comprehensive weekly business briefing by aggregating data from:
- Completed tasks (/Done/ folder)
- Financial data (Odoo)
- Social media metrics (Facebook, Instagram, Twitter)
- Business goals (Business_Goals.md)
- Proactive suggestions (subscriptions, revenue opportunities)

Usage:
    python generate_briefing.py --days 7
    python generate_briefing.py --start 2026-01-01 --end 2026-01-31
    python generate_briefing.py --weekly  # Generate for last week
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List
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

# Briefings output directory
BRIEFINGS_DIR = os.path.join(VAULT_PATH, 'Briefings')


# ============================================================================
# DATA COLLECTION
# ============================================================================

def collect_odoo_data(start_date: datetime, end_date: datetime, dry_run: bool = True) -> Dict[str, Any]:
    """
    Collect financial data from Odoo.

    Args:
        start_date: Start date
        end_date: End date
        dry_run: Use simulated data

    Returns:
        Odoo data dict
    """
    if dry_run:
        return {
            'revenue': {
                'this_week': 2500.00,
                'mtd': 4500.00,
                'target': 10000.00,
                'progress': 45.0,
                'trend': 'on_track'
            },
            'expenses': {
                'this_week': 850.00,
                'mtd': 1200.00,
                'by_category': {
                    'Software': 400.00,
                    'Office': 250.00,
                    'Marketing': 200.00
                }
            },
            'invoices': {
                'paid': [
                    {'client': 'Client A', 'amount': 1500.00, 'number': 'INV/2026/001'},
                    {'client': 'Client B', 'amount': 1000.00, 'number': 'INV/2026/002'}
                ],
                'unpaid': [
                    {'client': 'Client C', 'amount': 2500.00, 'number': 'INV/2026/003', 'days_overdue': 45}
                ]
            },
            'aged_receivables': {
                '0-30': 1500.00,
                '31-60': 2500.00,
                '61-90': 500.00,
                '90+': 0.00
            }
        }
    else:
        # In production, call Odoo MCP server
        raise NotImplementedError("Production Odoo integration pending")


def collect_social_media_data(start_date: datetime, end_date: datetime, dry_run: bool = True) -> Dict[str, Any]:
    """
    Collect social media metrics.

    Args:
        start_date: Start date
        end_date: End date
        dry_run: Use simulated data

    Returns:
        Social media data dict
    """
    if dry_run:
        return {
            'facebook': {
                'posts': 5,
                'reach': 1234,
                'engagement': 89
            },
            'instagram': {
                'posts': 7,
                'reach': 2456,
                'engagement': 234
            },
            'twitter': {
                'tweets': 12,
                'impressions': 3456,
                'engagement': 145
            },
            'top_posts': [
                {'platform': 'Instagram', 'content': 'Behind-the-scenes reel', 'reach': 1234},
                {'platform': 'Facebook', 'content': 'Product launch announcement', 'reach': 456},
                {'platform': 'Twitter', 'content': 'Feature highlight thread', 'reach': 2345}
            ]
        }
    else:
        # In production, call social media MCP servers
        raise NotImplementedError("Production social media integration pending")


def parse_business_goals() -> Dict[str, Any]:
    """
    Parse Business_Goals.md file.

    Returns:
        Business goals dict
    """
    goals_file = os.path.join(VAULT_PATH, 'Business_Goals.md')

    if not os.path.exists(goals_file):
        return {
            'revenue_target': 10000.00,
            'expense_budget': 3000.00,
            'kpis': {}
        }

    try:
        with open(goals_file, 'r') as f:
            post = frontmatter.load(f)

        metadata = post.metadata

        return {
            'revenue_target': metadata.get('revenue_target', 10000.00),
            'expense_budget': metadata.get('expense_budget', 3000.00),
            'kpis': metadata.get('kpis', {})
        }
    except Exception as e:
        print(f"⚠️  Failed to parse Business_Goals.md: {e}")
        return {
            'revenue_target': 10000.00,
            'expense_budget': 3000.00,
            'kpis': {}
        }


def detect_upcoming_deadlines(days_ahead: int = 14) -> List[Dict[str, Any]]:
    """
    Detect upcoming deadlines from /Needs_Action/ and /Pending_Approval/.

    Args:
        days_ahead: Number of days to look ahead

    Returns:
        List of deadline dicts
    """
    deadlines = []
    cutoff_date = datetime.now() + timedelta(days=days_ahead)

    # Check /Needs_Action/ and /Pending_Approval/
    for folder in ['Needs_Action', 'Pending_Approval']:
        folder_path = os.path.join(VAULT_PATH, folder)

        if not os.path.exists(folder_path):
            continue

        for file_path in Path(folder_path).glob('*.md'):
            try:
                with open(file_path, 'r') as f:
                    post = frontmatter.load(f)

                metadata = post.metadata
                deadline = metadata.get('deadline') or metadata.get('due_date')

                if deadline:
                    deadline_date = datetime.fromisoformat(deadline)
                    if deadline_date <= cutoff_date:
                        days_until = (deadline_date - datetime.now()).days

                        deadlines.append({
                            'title': metadata.get('title', post.content.split('\n')[0].strip('# ')),
                            'deadline': deadline_date.strftime('%b %d'),
                            'days_until': days_until,
                            'status': metadata.get('status', 'pending'),
                            'priority': metadata.get('priority', 'medium')
                        })
            except Exception:
                continue

    # Sort by days until deadline
    deadlines.sort(key=lambda x: x['days_until'])

    return deadlines


# ============================================================================
# BRIEFING GENERATION
# ============================================================================

def generate_executive_summary(odoo_data: Dict[str, Any], task_metrics: Dict[str, Any],
                               bottlenecks: List[Dict[str, Any]]) -> str:
    """
    Generate executive summary section.

    Args:
        odoo_data: Odoo financial data
        task_metrics: Task completion metrics
        bottlenecks: List of bottlenecks

    Returns:
        Executive summary markdown
    """
    # Determine overall performance
    revenue_progress = odoo_data['revenue']['progress']
    if revenue_progress >= 90:
        performance = "Strong"
    elif revenue_progress >= 70:
        performance = "On Track"
    else:
        performance = "Behind Target"

    summary = f"""# Weekly Business Briefing

**Week of**: {datetime.now().strftime('%B %d, %Y')}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

**Overall Performance**: {performance}

**Key Highlights**:
- Revenue: ${odoo_data['revenue']['this_week']:,.2f} this week ({revenue_progress:.0f}% of monthly target)
- Tasks Completed: {task_metrics['total_tasks']} tasks (avg {task_metrics['avg_duration']}d completion time)
- Success Rate: {task_metrics['success_rate']}%
"""

    # Critical issues
    critical_issues = []

    if revenue_progress < 80:
        critical_issues.append(f"Revenue below target ({revenue_progress:.0f}% of goal)")

    if bottlenecks:
        critical_issues.append(f"{len(bottlenecks)} task bottlenecks detected")

    if odoo_data['invoices']['unpaid']:
        overdue_amount = sum(inv['amount'] for inv in odoo_data['invoices']['unpaid'])
        critical_issues.append(f"${overdue_amount:,.2f} in overdue invoices")

    if critical_issues:
        summary += "\n**Critical Issues**:\n"
        for issue in critical_issues:
            summary += f"- ⚠️  {issue}\n"

    summary += "\n---\n\n"

    return summary


def generate_revenue_section(odoo_data: Dict[str, Any], business_goals: Dict[str, Any]) -> str:
    """
    Generate revenue analysis section.

    Args:
        odoo_data: Odoo financial data
        business_goals: Business goals

    Returns:
        Revenue section markdown
    """
    revenue = odoo_data['revenue']
    target = business_goals['revenue_target']

    section = f"""## Revenue

- **This Week**: ${revenue['this_week']:,.2f}
- **MTD**: ${revenue['mtd']:,.2f} ({revenue['progress']:.0f}% of ${target:,.2f} target)
- **Trend**: {revenue['trend'].replace('_', ' ').title()}

**Top Revenue Sources**:
"""

    for invoice in odoo_data['invoices']['paid'][:3]:
        section += f"- {invoice['client']}: ${invoice['amount']:,.2f} ({invoice['number']})\n"

    section += "\n"

    return section


def generate_expense_section(odoo_data: Dict[str, Any]) -> str:
    """
    Generate expense analysis section.

    Args:
        odoo_data: Odoo financial data

    Returns:
        Expense section markdown
    """
    expenses = odoo_data['expenses']

    section = f"""## Expenses

- **This Week**: ${expenses['this_week']:,.2f}
- **MTD**: ${expenses['mtd']:,.2f}

**By Category**:
"""

    total = sum(expenses['by_category'].values())
    for category, amount in sorted(expenses['by_category'].items(), key=lambda x: x[1], reverse=True):
        pct = (amount / total * 100) if total > 0 else 0
        section += f"- {category}: ${amount:,.2f} ({pct:.0f}%)\n"

    section += "\n"

    return section


def generate_social_media_section(social_data: Dict[str, Any]) -> str:
    """
    Generate social media performance section.

    Args:
        social_data: Social media metrics

    Returns:
        Social media section markdown
    """
    section = """## Social Media Performance

"""

    section += f"- **Facebook**: {social_data['facebook']['posts']} posts, {social_data['facebook']['reach']:,} reach, {social_data['facebook']['engagement']} engagements\n"
    section += f"- **Instagram**: {social_data['instagram']['posts']} posts, {social_data['instagram']['reach']:,} reach, {social_data['instagram']['engagement']} engagements\n"
    section += f"- **Twitter**: {social_data['twitter']['tweets']} tweets, {social_data['twitter']['impressions']:,} impressions, {social_data['twitter']['engagement']} engagements\n"

    section += "\n**Top Performing**:\n"
    for i, post in enumerate(social_data['top_posts'][:3], 1):
        section += f"{i}. {post['content']} ({post['platform']}) - {post['reach']:,} reach\n"

    section += "\n"

    return section


def generate_deadlines_section(deadlines: List[Dict[str, Any]]) -> str:
    """
    Generate upcoming deadlines section.

    Args:
        deadlines: List of deadline dicts

    Returns:
        Deadlines section markdown
    """
    if not deadlines:
        return "## Upcoming Deadlines\n\nNo upcoming deadlines in the next 14 days.\n\n"

    section = "## Upcoming Deadlines\n\n"

    for deadline in deadlines[:5]:
        status_emoji = "✅" if deadline['status'] == 'completed' else "⏳" if deadline['status'] == 'in_progress' else "❌"
        section += f"- **{deadline['title']}**: {deadline['deadline']} ({deadline['days_until']} days) {status_emoji} {deadline['status'].title()}\n"

    section += "\n"

    return section


def generate_briefing_markdown(odoo_data: Dict[str, Any], social_data: Dict[str, Any],
                               task_metrics: Dict[str, Any], bottlenecks: List[Dict[str, Any]],
                               suggestions: str, deadlines: List[Dict[str, Any]],
                               business_goals: Dict[str, Any], tasks_report: str) -> str:
    """
    Generate complete briefing markdown.

    Args:
        odoo_data: Odoo financial data
        social_data: Social media metrics
        task_metrics: Task completion metrics
        bottlenecks: List of bottlenecks
        suggestions: Proactive suggestions markdown
        deadlines: List of upcoming deadlines
        business_goals: Business goals
        tasks_report: Task analysis report

    Returns:
        Complete briefing markdown
    """
    briefing = ""

    # Executive summary
    briefing += generate_executive_summary(odoo_data, task_metrics, bottlenecks)

    # Revenue
    briefing += generate_revenue_section(odoo_data, business_goals)

    # Expenses
    briefing += generate_expense_section(odoo_data)

    # Tasks
    briefing += tasks_report

    # Social media
    briefing += generate_social_media_section(social_data)

    # Proactive suggestions
    briefing += suggestions

    # Upcoming deadlines
    briefing += generate_deadlines_section(deadlines)

    # Footer
    briefing += "---\n\n"
    briefing += "🤖 Generated with [Claude Code](https://claude.com/claude-code) - Gold Tier AI Employee\n"

    return briefing


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Generate CEO briefing")
    parser.add_argument("--days", type=int, default=7, help="Number of days to analyze (default: 7)")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    parser.add_argument("--weekly", action="store_true", help="Generate for last week (Mon-Sun)")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Use simulated data")
    args = parser.parse_args()

    print("=" * 80)
    print("CEO Briefing Generator")
    print("=" * 80)
    print()

    # Determine date range
    if args.weekly:
        # Last Monday to Sunday
        today = datetime.now()
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        last_sunday = last_monday + timedelta(days=6)
        start_date = last_monday
        end_date = last_sunday
    elif args.start and args.end:
        start_date = datetime.fromisoformat(args.start)
        end_date = datetime.fromisoformat(args.end)
    else:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days)

    print(f"Generating briefing for {start_date.date()} to {end_date.date()}")
    print()

    # Collect data
    print("Collecting data from all sources...")

    print("  - Odoo financial data...")
    odoo_data = collect_odoo_data(start_date, end_date, args.dry_run)

    print("  - Social media metrics...")
    social_data = collect_social_media_data(start_date, end_date, args.dry_run)

    print("  - Business goals...")
    business_goals = parse_business_goals()

    print("  - Upcoming deadlines...")
    deadlines = detect_upcoming_deadlines()

    print("  - Task analysis...")
    # Import and run task analysis
    sys.path.insert(0, str(Path(__file__).parent))
    from analyze_tasks import get_completed_tasks, calculate_task_metrics, detect_bottlenecks, generate_task_report

    tasks = get_completed_tasks(start_date, end_date)
    task_metrics = calculate_task_metrics(tasks)
    bottlenecks = detect_bottlenecks(tasks)
    tasks_report = generate_task_report(tasks, task_metrics, bottlenecks)

    print("  - Subscription analysis...")
    from analyze_subscriptions import generate_suggestions_report

    # Simulated data for suggestions
    usage_data = []
    duplicates = []
    revenue_opps = []
    suggestions = generate_suggestions_report(usage_data, duplicates, revenue_opps)

    print()
    print("Generating briefing...")

    # Generate briefing
    briefing = generate_briefing_markdown(
        odoo_data, social_data, task_metrics, bottlenecks,
        suggestions, deadlines, business_goals, tasks_report
    )

    # Save briefing
    os.makedirs(BRIEFINGS_DIR, exist_ok=True)

    # Determine filename
    if args.weekly:
        week_num = start_date.isocalendar()[1]
        filename = f"BRIEF-{start_date.year}-W{week_num:02d}.md"
    else:
        filename = f"BRIEF-{datetime.now().strftime('%Y-%m-%d')}.md"

    output_path = os.path.join(BRIEFINGS_DIR, filename)

    # Add frontmatter
    metadata = {
        'type': 'ceo_briefing',
        'period_start': start_date.isoformat(),
        'period_end': end_date.isoformat(),
        'generated': datetime.now().isoformat(),
        'revenue': odoo_data['revenue']['this_week'],
        'tasks_completed': task_metrics['total_tasks']
    }

    post = frontmatter.Post(briefing, **metadata)

    with open(output_path, 'w') as f:
        f.write(frontmatter.dumps(post))

    print(f"✓ Briefing saved: {output_path}")
    print()
    print("=" * 80)
    print("Briefing Generation Complete")
    print("=" * 80)
    print()
    print(f"Revenue: ${odoo_data['revenue']['this_week']:,.2f}")
    print(f"Tasks: {task_metrics['total_tasks']} completed")
    print(f"Bottlenecks: {len(bottlenecks)}")
    print(f"Deadlines: {len(deadlines)} upcoming")
    print()
    print(f"View briefing: {output_path}")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
