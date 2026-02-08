#!/usr/bin/env python3
"""
Subscription Usage Analysis and Proactive Suggestions

Analyzes expenses to identify:
- Unused subscriptions (no activity in 30+ days)
- Duplicate tools (multiple tools for same purpose)
- Cost optimization opportunities
- Revenue opportunities (unpaid invoices, recurring revenue)

Usage:
    python analyze_subscriptions.py --days 30
    python analyze_subscriptions.py --start 2026-01-01 --end 2026-01-31
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

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

# Subscription categories
SUBSCRIPTION_KEYWORDS = [
    'subscription', 'monthly', 'annual', 'saas', 'software',
    'adobe', 'notion', 'slack', 'zoom', 'dropbox', 'github',
    'aws', 'azure', 'gcp', 'heroku', 'vercel', 'netlify'
]

# Tool categories for duplicate detection
TOOL_CATEGORIES = {
    'communication': ['slack', 'teams', 'discord', 'zoom', 'meet'],
    'storage': ['dropbox', 'google drive', 'onedrive', 'box'],
    'project_management': ['asana', 'trello', 'jira', 'monday', 'notion'],
    'design': ['figma', 'sketch', 'adobe xd', 'canva'],
    'analytics': ['google analytics', 'mixpanel', 'amplitude', 'heap']
}

# Unused threshold (days)
UNUSED_THRESHOLD = 30


# ============================================================================
# SUBSCRIPTION DETECTION
# ============================================================================

def detect_subscriptions(expenses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect subscription expenses from expense list.

    Args:
        expenses: List of expense dicts

    Returns:
        List of subscription dicts
    """
    subscriptions = []

    for expense in expenses:
        description = expense.get('description', '').lower()
        category = expense.get('category', '').lower()

        # Check if subscription
        is_subscription = any(keyword in description or keyword in category
                            for keyword in SUBSCRIPTION_KEYWORDS)

        if is_subscription:
            subscriptions.append({
                'name': expense.get('description', 'Unknown'),
                'amount': expense.get('amount', 0),
                'date': expense.get('date'),
                'category': expense.get('category', 'Software'),
                'vendor': expense.get('vendor', 'Unknown')
            })

    return subscriptions


def analyze_subscription_usage(subscriptions: List[Dict[str, Any]],
                               tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyze subscription usage based on completed tasks.

    Args:
        subscriptions: List of subscription dicts
        tasks: List of completed task dicts

    Returns:
        List of subscription usage dicts
    """
    usage_data = []

    for sub in subscriptions:
        sub_name = sub['name'].lower()

        # Find tasks that mention this subscription
        related_tasks = [
            t for t in tasks
            if sub_name in t.get('title', '').lower() or
               sub_name in t.get('content', '').lower()
        ]

        # Calculate last used date
        if related_tasks:
            last_used = max(datetime.fromisoformat(t['completed_at'])
                          for t in related_tasks if t.get('completed_at'))
            days_since_used = (datetime.now() - last_used).days
        else:
            last_used = None
            days_since_used = 999  # Assume never used

        usage_data.append({
            'name': sub['name'],
            'amount': sub['amount'],
            'last_used': last_used.isoformat() if last_used else None,
            'days_since_used': days_since_used,
            'usage_count': len(related_tasks),
            'category': sub['category']
        })

    return usage_data


# ============================================================================
# DUPLICATE DETECTION
# ============================================================================

def detect_duplicate_tools(subscriptions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect duplicate tools (multiple tools for same purpose).

    Args:
        subscriptions: List of subscription dicts

    Returns:
        List of duplicate tool groups
    """
    duplicates = []

    for category, tools in TOOL_CATEGORIES.items():
        # Find subscriptions in this category
        category_subs = []
        for sub in subscriptions:
            sub_name = sub['name'].lower()
            if any(tool in sub_name for tool in tools):
                category_subs.append(sub)

        # If multiple tools in same category, flag as duplicate
        if len(category_subs) > 1:
            total_cost = sum(s['amount'] for s in category_subs)
            duplicates.append({
                'category': category.replace('_', ' ').title(),
                'tools': [s['name'] for s in category_subs],
                'total_cost': total_cost,
                'suggestion': f"Consolidate to single {category.replace('_', ' ')} tool?"
            })

    return duplicates


# ============================================================================
# REVENUE OPPORTUNITIES
# ============================================================================

def detect_revenue_opportunities(invoices: List[Dict[str, Any]],
                                clients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect revenue opportunities (unpaid invoices, recurring revenue).

    Args:
        invoices: List of invoice dicts
        clients: List of client dicts

    Returns:
        List of revenue opportunity dicts
    """
    opportunities = []

    # Unpaid invoices
    unpaid = [inv for inv in invoices if inv.get('status') == 'unpaid']
    for invoice in unpaid:
        days_overdue = (datetime.now() - datetime.fromisoformat(invoice['date'])).days
        if days_overdue > 30:
            opportunities.append({
                'type': 'unpaid_invoice',
                'client': invoice.get('client', 'Unknown'),
                'amount': invoice.get('amount', 0),
                'days_overdue': days_overdue,
                'action': 'Follow up on outstanding invoice'
            })

    # Clients with no recent invoices
    for client in clients:
        client_invoices = [inv for inv in invoices if inv.get('client') == client['name']]
        if client_invoices:
            last_invoice = max(datetime.fromisoformat(inv['date']) for inv in client_invoices)
            days_since_invoice = (datetime.now() - last_invoice).days

            if days_since_invoice > 60:
                opportunities.append({
                    'type': 'inactive_client',
                    'client': client['name'],
                    'days_since_invoice': days_since_invoice,
                    'action': 'Follow up on outstanding work or new projects'
                })

    # Recurring revenue opportunities
    monthly_clients = [c for c in clients if c.get('billing_type') == 'monthly']
    if len(monthly_clients) >= 3:
        opportunities.append({
            'type': 'recurring_revenue',
            'count': len(monthly_clients),
            'action': 'Propose annual contracts for discount (increase predictability)'
        })

    return opportunities


# ============================================================================
# REPORT GENERATION
# ============================================================================

def generate_suggestions_report(usage_data: List[Dict[str, Any]],
                                duplicates: List[Dict[str, Any]],
                                revenue_opps: List[Dict[str, Any]]) -> str:
    """
    Generate proactive suggestions report markdown.

    Args:
        usage_data: Subscription usage data
        duplicates: Duplicate tool groups
        revenue_opps: Revenue opportunities

    Returns:
        Markdown report
    """
    report = "## Proactive Suggestions\n\n"

    # Cost optimization
    unused = [u for u in usage_data if u['days_since_used'] > UNUSED_THRESHOLD]

    if unused or duplicates:
        report += "### Cost Optimization\n\n"

        # Unused subscriptions
        for sub in unused:
            report += f"- **{sub['name']}**: No activity in {sub['days_since_used']} days. Cost: ${sub['amount']:.2f}/month.\n"
            report += f"  - [ACTION] Cancel subscription? Move to /Pending_Approval\n\n"

        # Duplicate tools
        for dup in duplicates:
            tools_str = " + ".join(dup['tools'])
            report += f"- **Duplicate Tools**: {tools_str} both active\n"
            report += f"  - Total cost: ${dup['total_cost']:.2f}/month\n"
            report += f"  - [ACTION] {dup['suggestion']}\n\n"

    # Revenue opportunities
    if revenue_opps:
        report += "### Revenue Opportunities\n\n"

        for opp in revenue_opps:
            if opp['type'] == 'unpaid_invoice':
                report += f"- **{opp['client']}**: Invoice overdue by {opp['days_overdue']} days (${opp['amount']:.2f})\n"
                report += f"  - [ACTION] {opp['action']}\n\n"

            elif opp['type'] == 'inactive_client':
                report += f"- **{opp['client']}**: No invoice sent in {opp['days_since_invoice']} days\n"
                report += f"  - [ACTION] {opp['action']}\n\n"

            elif opp['type'] == 'recurring_revenue':
                report += f"- **Recurring Revenue**: {opp['count']} clients on monthly retainer\n"
                report += f"  - [ACTION] {opp['action']}\n\n"

    if not unused and not duplicates and not revenue_opps:
        report += "No optimization opportunities detected at this time.\n\n"

    return report


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Analyze subscriptions and generate proactive suggestions")
    parser.add_argument("--days", type=int, default=30, help="Number of days to analyze (default: 30)")
    parser.add_argument("--expenses-file", help="Path to expenses JSON file")
    parser.add_argument("--tasks-file", help="Path to tasks JSON file")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Use simulated data")
    args = parser.parse_args()

    print("Analyzing subscriptions and generating proactive suggestions")
    print()

    # Load data (simulated for now)
    if args.dry_run:
        expenses = [
            {'description': 'Adobe Creative Cloud', 'amount': 99.99, 'date': '2026-01-15', 'category': 'Software'},
            {'description': 'Notion Team Plan', 'amount': 15.00, 'date': '2026-01-01', 'category': 'Software'},
            {'description': 'Slack Pro', 'amount': 12.50, 'date': '2026-01-10', 'category': 'Software'},
            {'description': 'Microsoft Teams', 'amount': 20.00, 'date': '2026-01-05', 'category': 'Software'},
            {'description': 'Dropbox Business', 'amount': 25.00, 'date': '2026-01-12', 'category': 'Storage'},
        ]

        tasks = [
            {'title': 'Design social media graphics in Adobe', 'completed_at': '2026-01-20T10:00:00'},
            {'title': 'Send message via Slack', 'completed_at': '2026-01-25T14:00:00'},
            {'title': 'Upload files to Dropbox', 'completed_at': '2026-01-28T09:00:00'},
        ]

        invoices = [
            {'client': 'Client A', 'amount': 2500, 'date': '2025-12-01', 'status': 'unpaid'},
            {'client': 'Client B', 'amount': 1500, 'date': '2026-01-15', 'status': 'paid'},
        ]

        clients = [
            {'name': 'Client A', 'billing_type': 'monthly'},
            {'name': 'Client B', 'billing_type': 'monthly'},
            {'name': 'Client C', 'billing_type': 'monthly'},
        ]
    else:
        # Load from files
        print("Production mode not yet implemented")
        return 1

    # Detect subscriptions
    subscriptions = detect_subscriptions(expenses)
    print(f"Detected {len(subscriptions)} subscriptions")

    # Analyze usage
    usage_data = analyze_subscription_usage(subscriptions, tasks)
    unused = [u for u in usage_data if u['days_since_used'] > UNUSED_THRESHOLD]
    print(f"Found {len(unused)} unused subscriptions (>{UNUSED_THRESHOLD} days)")

    # Detect duplicates
    duplicates = detect_duplicate_tools(subscriptions)
    print(f"Found {len(duplicates)} duplicate tool categories")

    # Detect revenue opportunities
    revenue_opps = detect_revenue_opportunities(invoices, clients)
    print(f"Found {len(revenue_opps)} revenue opportunities")

    print()

    # Generate report
    report = generate_suggestions_report(usage_data, duplicates, revenue_opps)

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
