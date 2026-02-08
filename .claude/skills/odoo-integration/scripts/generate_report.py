#!/usr/bin/env python3
"""
Financial Report Generation Workflow

Generates financial reports from Odoo accounting data.
Creates reports in /Briefings/ folder for CEO briefing integration.

Usage:
    python generate_report.py --type profit_loss --start 2026-01-01 --end 2026-01-31
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import frontmatter

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent))
from odoo_client import OdooClient


def format_currency(amount: float) -> str:
    """Format amount as currency string."""
    return f"${amount:,.2f}"


def generate_report_markdown(report_data: dict, report_type: str) -> str:
    """
    Generate markdown report from Odoo data.

    Args:
        report_data: Report data from Odoo
        report_type: Type of report

    Returns:
        Markdown formatted report
    """
    period_start = report_data["period"]["start_date"]
    period_end = report_data["period"]["end_date"]
    data = report_data["data"]

    if report_type == "profit_loss":
        content = f"""# Profit & Loss Statement

**Period**: {period_start} to {period_end}
**Generated**: {report_data['generated_at']}

## Summary

| Metric | Amount |
|--------|--------|
| Revenue | {format_currency(data['revenue'])} |
| Expenses | {format_currency(data['expenses'])} |
| **Net Income** | **{format_currency(data['net_income'])}** |

## Revenue Breakdown

{_format_details(data.get('details', {}).get('revenue', {}))}

## Expense Breakdown

{_format_details(data.get('details', {}).get('expenses', {}))}

## Analysis

- **Profit Margin**: {(data['net_income'] / data['revenue'] * 100) if data['revenue'] > 0 else 0:.1f}%
- **Revenue Growth**: Compare with previous period for trend analysis
- **Top Expense Categories**: Review for cost optimization opportunities
"""

    elif report_type == "balance_sheet":
        content = f"""# Balance Sheet

**As of**: {period_end}
**Generated**: {report_data['generated_at']}

## Assets

{_format_details(data.get('details', {}).get('assets', {}))}

**Total Assets**: {format_currency(data.get('total_assets', 0))}

## Liabilities

{_format_details(data.get('details', {}).get('liabilities', {}))}

**Total Liabilities**: {format_currency(data.get('total_liabilities', 0))}

## Equity

**Total Equity**: {format_currency(data.get('total_equity', 0))}

---

**Assets = Liabilities + Equity**
"""

    elif report_type == "cash_flow":
        content = f"""# Cash Flow Statement

**Period**: {period_start} to {period_end}
**Generated**: {report_data['generated_at']}

## Operating Activities

{_format_details(data.get('details', {}).get('operating', {}))}

**Net Cash from Operating**: {format_currency(data.get('operating_cash', 0))}

## Investing Activities

{_format_details(data.get('details', {}).get('investing', {}))}

**Net Cash from Investing**: {format_currency(data.get('investing_cash', 0))}

## Financing Activities

{_format_details(data.get('details', {}).get('financing', {}))}

**Net Cash from Financing**: {format_currency(data.get('financing_cash', 0))}

---

**Net Change in Cash**: {format_currency(data.get('net_cash_change', 0))}
"""

    elif report_type == "aged_receivables":
        content = f"""# Aged Receivables Report

**As of**: {period_end}
**Generated**: {report_data['generated_at']}

## Summary

| Age Bucket | Amount | Count |
|------------|--------|-------|
| Current (0-30 days) | {format_currency(data.get('current', 0))} | {data.get('current_count', 0)} |
| 31-60 days | {format_currency(data.get('days_31_60', 0))} | {data.get('days_31_60_count', 0)} |
| 61-90 days | {format_currency(data.get('days_61_90', 0))} | {data.get('days_61_90_count', 0)} |
| Over 90 days | {format_currency(data.get('over_90', 0))} | {data.get('over_90_count', 0)} |
| **Total** | **{format_currency(data.get('total', 0))}** | **{data.get('total_count', 0)}** |

## Action Items

- Follow up on invoices over 60 days
- Review payment terms for slow-paying customers
- Consider late payment fees for overdue invoices
"""

    else:
        content = f"""# Financial Report

**Type**: {report_type}
**Period**: {period_start} to {period_end}
**Generated**: {report_data['generated_at']}

{json.dumps(data, indent=2)}
"""

    return content


def _format_details(details: dict) -> str:
    """Format details dictionary as markdown list."""
    if not details:
        return "No detailed breakdown available."

    lines = []
    for key, value in details.items():
        if isinstance(value, (int, float)):
            lines.append(f"- {key.replace('_', ' ').title()}: {format_currency(value)}")
        else:
            lines.append(f"- {key.replace('_', ' ').title()}: {value}")

    return '\n'.join(lines) if lines else "No detailed breakdown available."


def save_report(report_content: str, report_type: str, vault_path: str) -> str:
    """
    Save report to /Briefings/ folder.

    Args:
        report_content: Markdown report content
        report_type: Type of report
        vault_path: Path to Obsidian vault

    Returns:
        Path to saved report file
    """
    briefings_dir = os.path.join(vault_path, "Briefings")
    os.makedirs(briefings_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_file = os.path.join(briefings_dir, f"{timestamp}_{report_type}_report.md")

    # Add frontmatter
    metadata = {
        "type": "financial_report",
        "report_type": report_type,
        "generated": datetime.now().isoformat(),
        "source": "odoo"
    }

    post = frontmatter.Post(report_content, **metadata)

    with open(report_file, 'w') as f:
        f.write(frontmatter.dumps(post))

    return report_file


def main():
    parser = argparse.ArgumentParser(description="Generate financial report from Odoo")
    parser.add_argument("--type", required=True,
                        choices=["profit_loss", "balance_sheet", "cash_flow", "aged_receivables"],
                        help="Report type")
    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--format", default="json", choices=["json", "pdf"], help="Output format")
    parser.add_argument("--vault", default=None, help="Path to Obsidian vault")
    args = parser.parse_args()

    # Initialize Odoo client
    client = OdooClient(vault_path=args.vault)

    # Generate report
    print(f"Generating {args.type} report for {args.start} to {args.end}")
    report_data = client.generate_report(
        report_type=args.type,
        start_date=args.start,
        end_date=args.end,
        format=args.format
    )

    print(f"✓ Report generated")
    print(f"  Type: {report_data['report_type']}")
    print(f"  Period: {report_data['period']['start_date']} to {report_data['period']['end_date']}")

    # Format as markdown
    report_content = generate_report_markdown(report_data, args.type)

    # Save to /Briefings/
    report_file = save_report(report_content, args.type, client.vault_path)
    print(f"✓ Report saved: {report_file}")

    # Display summary
    if args.type == "profit_loss":
        data = report_data["data"]
        print(f"\n📊 Summary:")
        print(f"  Revenue: {format_currency(data['revenue'])}")
        print(f"  Expenses: {format_currency(data['expenses'])}")
        print(f"  Net Income: {format_currency(data['net_income'])}")
        print(f"  Profit Margin: {(data['net_income'] / data['revenue'] * 100) if data['revenue'] > 0 else 0:.1f}%")

    print("\n✅ Financial report generation complete!")


if __name__ == "__main__":
    main()
