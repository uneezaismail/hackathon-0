---
name: ceo-briefing-generator
description: >
  Generate weekly business and accounting audit with CEO briefing. Analyzes completed tasks from
  /Done/, financial data from Odoo, social media metrics, and business goals to create comprehensive
  Monday morning CEO briefing with revenue summary, bottlenecks, proactive suggestions, and upcoming
  deadlines. Use when: (1) Generating weekly CEO briefing, (2) Creating business audit reports,
  (3) Analyzing weekly performance, (4) Identifying bottlenecks and opportunities, (5) Scheduled
  Sunday night briefing generation. Trigger phrases: "generate ceo briefing", "weekly business audit",
  "monday morning briefing", "business performance summary", "weekly report".
---

# CEO Briefing Generator

Generate weekly business and accounting audit with comprehensive CEO briefing for Monday morning review.

## Overview

Gold tier requires **Weekly Business and Accounting Audit with CEO Briefing generation**. This skill analyzes completed tasks, financial data from Odoo, social media metrics, and business goals to create actionable insights and proactive suggestions.

**Key Features:**
- Revenue and expense analysis
- Task completion tracking
- Bottleneck identification
- Proactive cost optimization suggestions
- Upcoming deadline alerts
- Social media performance summary

**Scheduled Execution:**
- Runs every Sunday night (8:00 PM)
- Generates briefing for Monday morning
- Uses Ralph Wiggum Loop for autonomous execution

## Quick Start

### Generate Weekly Briefing

```bash
# Manual generation
/ceo-briefing-generator "Generate weekly CEO briefing"

# Scheduled (cron job)
0 20 * * 0 python scripts/start_ralph_loop.py \
  --task "Generate weekly CEO briefing using @ceo-briefing-generator" \
  --max-iterations 5
```

### View Generated Briefing

```bash
# Latest briefing
cat AI_Employee_Vault/Briefings/$(ls -t AI_Employee_Vault/Briefings/ | head -1)

# Open in Obsidian
# Navigate to Briefings/ folder
```

## Configuration

### In Company_Handbook.md

```markdown
## CEO Briefing Configuration

### Data Sources
- Completed tasks: /Done/ folder (last 7 days)
- Financial data: Odoo (revenue, expenses, cash flow)
- Social media: Facebook, Instagram, Twitter metrics
- Business goals: Business_Goals.md

### Metrics to Track
- Revenue: Weekly total, MTD, vs target
- Task completion: Count, average time, bottlenecks
- Expenses: Weekly total, by category, anomalies
- Social media: Posts, engagement, reach
- Subscriptions: Usage, cost, optimization opportunities

### Alert Thresholds
- Revenue < 80% of weekly target: Alert
- Task delay > 3 days: Flag as bottleneck
- Expense > 20% increase: Investigate
- Subscription unused > 30 days: Suggest cancellation
- Upcoming deadline < 7 days: Highlight
```

### In .env

```bash
# CEO Briefing
BRIEFING_SCHEDULE="0 20 * * 0"  # Sunday 8:00 PM
BRIEFING_LOOKBACK_DAYS=7        # Analyze last 7 days
BRIEFING_OUTPUT_DIR=Briefings   # Output directory
```

## Briefing Structure

### Executive Summary

High-level overview of the week:
- Overall performance (strong/weak/on-track)
- Key highlights
- Critical issues requiring attention

### Revenue Analysis

```markdown
## Revenue

- **This Week**: $2,500
- **MTD**: $4,500 (45% of $10,000 target)
- **Trend**: On track / Behind / Ahead
- **Top Revenue Sources**:
  - Client A: $1,500 (Invoice #INV/2026/001)
  - Client B: $1,000 (Invoice #INV/2026/002)
```

### Completed Tasks

```markdown
## Completed Tasks

- [x] Client A invoice sent and paid ($1,500)
- [x] Project Alpha milestone 2 delivered
- [x] Weekly social media posts scheduled (7 posts)
- [x] Expense categorization completed (12 expenses)

**Total Completed**: 15 tasks
**Average Completion Time**: 2.3 days
```

### Bottlenecks

```markdown
## Bottlenecks

| Task | Expected | Actual | Delay | Impact |
|------|----------|--------|-------|--------|
| Client B proposal | 2 days | 5 days | +3 days | High |
| Invoice follow-up | 1 day | 4 days | +3 days | Medium |

**Action Items**:
- Review Client B proposal workflow
- Automate invoice follow-up reminders
```

### Expense Analysis

```markdown
## Expenses

- **This Week**: $850
- **MTD**: $1,200
- **By Category**:
  - Software: $400 (47%)
  - Office: $250 (29%)
  - Marketing: $200 (24%)

**Anomalies**:
- Software expenses up 30% vs last month
- New subscription: Adobe Creative Cloud ($99/month)
```

### Proactive Suggestions

```markdown
## Proactive Suggestions

### Cost Optimization
- **Notion**: No team activity in 45 days. Cost: $15/month.
  - [ACTION] Cancel subscription? Move to /Pending_Approval

- **Duplicate Tools**: Slack + Microsoft Teams both active
  - [ACTION] Consolidate to single platform?

### Revenue Opportunities
- **Client C**: No invoice sent in 60 days
  - [ACTION] Follow up on outstanding work?

- **Recurring Revenue**: 3 clients on monthly retainer
  - [ACTION] Propose annual contracts for discount?
```

### Social Media Performance

```markdown
## Social Media Performance

- **Facebook**: 5 posts, 1,234 total reach, 89 engagements
- **Instagram**: 7 posts, 2,456 total reach, 234 engagements
- **Twitter**: 12 tweets, 3,456 impressions, 145 engagements

**Top Performing**:
1. Product launch announcement (Facebook) - 456 reach
2. Behind-the-scenes reel (Instagram) - 1,234 reach
3. Feature highlight thread (Twitter) - 2,345 impressions
```

### Upcoming Deadlines

```markdown
## Upcoming Deadlines

- **Project Alpha final delivery**: Jan 15 (9 days) - On track
- **Quarterly tax prep**: Jan 31 (25 days) - Not started
- **Client D proposal**: Jan 20 (14 days) - In progress
```

## Data Collection Workflow

### 1. Query Completed Tasks

```python
# Read /Done/ folder for last 7 days
done_dir = Path('AI_Employee_Vault/Done')
tasks = []

for file in done_dir.glob('*.md'):
    metadata = parse_frontmatter(file)
    if is_within_last_7_days(metadata['completed']):
        tasks.append({
            'title': metadata['title'],
            'completed': metadata['completed'],
            'duration': calculate_duration(metadata),
            'type': metadata['type']
        })
```

### 2. Query Odoo Financial Data

```python
# Query Odoo via MCP server
revenue = odoo_mcp.get_revenue(start_date, end_date)
expenses = odoo_mcp.get_expenses(start_date, end_date)
invoices = odoo_mcp.get_invoices(status='paid', start_date=start_date)
aged_receivables = odoo_mcp.get_aged_receivables()
```

### 3. Query Social Media Metrics

```python
# Query social media MCPs
facebook_metrics = facebook_mcp.get_post_insights(start_date, end_date)
instagram_metrics = instagram_mcp.get_media_insights(start_date, end_date)
twitter_metrics = twitter_mcp.get_tweet_metrics(start_date, end_date)
```

### 4. Analyze Business Goals

```python
# Read Business_Goals.md
goals = parse_business_goals('AI_Employee_Vault/Business_Goals.md')

# Compare actual vs target
revenue_target = goals['revenue_target']
revenue_actual = sum(revenue)
revenue_progress = (revenue_actual / revenue_target) * 100
```

### 5. Identify Bottlenecks

```python
# Analyze task durations
for task in tasks:
    expected_duration = get_expected_duration(task['type'])
    actual_duration = task['duration']

    if actual_duration > expected_duration * 1.5:
        bottlenecks.append({
            'task': task['title'],
            'expected': expected_duration,
            'actual': actual_duration,
            'delay': actual_duration - expected_duration
        })
```

### 6. Generate Proactive Suggestions

```python
# Subscription usage analysis
subscriptions = analyze_subscriptions(expenses)

for sub in subscriptions:
    if sub['last_used'] > 30:  # days
        suggestions.append({
            'type': 'cost_optimization',
            'item': sub['name'],
            'cost': sub['monthly_cost'],
            'reason': f"No activity in {sub['last_used']} days",
            'action': 'Cancel subscription?'
        })
```

### 7. Generate Briefing

```python
# Compile all data into briefing
briefing = generate_briefing_markdown(
    revenue=revenue_data,
    tasks=tasks,
    bottlenecks=bottlenecks,
    expenses=expense_data,
    suggestions=suggestions,
    social_media=social_metrics,
    deadlines=upcoming_deadlines
)

# Write to /Briefings/
output_path = f'AI_Employee_Vault/Briefings/{date}_Monday_Briefing.md'
write_file(output_path, briefing)
```

## Integration with Other Skills

### With odoo-integration

Queries financial data from Odoo:

```
ceo-briefing-generator invokes odoo-integration
       ↓
Retrieves revenue, expenses, invoices, aged receivables
       ↓
Includes in briefing financial summary
```

### With social-media-poster

Queries social media metrics:

```
ceo-briefing-generator invokes social-media-poster
       ↓
Retrieves post metrics from Facebook, Instagram, Twitter
       ↓
Includes in briefing social media performance
```

### With ralph-wiggum-runner

Autonomous weekly execution:

```bash
# Cron job triggers Ralph loop every Sunday 8:00 PM
0 20 * * 0 python scripts/start_ralph_loop.py \
  --task "Generate weekly CEO briefing using @ceo-briefing-generator" \
  --max-iterations 5
```

Ralph loop ensures:
- Briefing generation completes even if multi-step
- Handles errors gracefully
- Retries if data collection fails
- Moves briefing to /Done/ when complete

## Usage Examples

### Example 1: Manual Weekly Briefing

```bash
/ceo-briefing-generator "Generate weekly CEO briefing for last week"
```

Result:
- Analyzes last 7 days of data
- Generates comprehensive briefing
- Saves to /Briefings/2026-01-27_Monday_Briefing.md
- Moves task to /Done/

### Example 2: Monthly Business Audit

```bash
/ceo-briefing-generator "Generate monthly business audit for January 2026"
```

Result:
- Analyzes entire month of data
- Includes monthly trends and comparisons
- Generates detailed financial report
- Saves to /Briefings/2026-01_Monthly_Audit.md

### Example 3: Custom Date Range

```bash
/ceo-briefing-generator "Generate business summary for Dec 1-31, 2025"
```

Result:
- Analyzes specified date range
- Generates custom report
- Includes all standard sections

## Safety Features

- **Data validation**: Verifies all data sources accessible before generation
- **Error handling**: Graceful degradation if data source unavailable
- **Audit logging**: Logs all data queries and briefing generation
- **Version control**: Keeps historical briefings for comparison

## Resources

- **references/briefing-template.md** - CEO briefing template structure
- **references/business-goals-schema.md** - Business_Goals.md format
- **references/metrics-calculation.md** - How metrics are calculated
- **scripts/generate_briefing.py** - Main briefing generation script
- **scripts/analyze_tasks.py** - Task analysis and bottleneck detection
- **scripts/analyze_subscriptions.py** - Subscription usage analysis
- **assets/briefing_template.md** - Markdown template for briefings
