# Technology Research: Gold Tier AI Employee

**Date**: 2026-01-27
**Feature**: Gold Tier AI Employee
**Research Method**: Library documentation analysis + Silver tier patterns + HACKATHON-ZERO.md requirements

## Overview

This document consolidates technology research for Gold Tier implementation, covering Odoo Community integration, Facebook/Instagram/Twitter APIs, Ralph Wiggum Loop autonomous operation, weekly CEO briefing generation, and enhanced error recovery.

---

## 1. Odoo Community Integration (Self-Hosted, Local)

### Decision: Use OdooRPC for JSON-RPC API integration

**Library**: `OdooRPC` (Python library for Odoo JSON-RPC)
**Version**: Latest stable (compatible with Odoo 19+)
**Alternative**: Direct `xmlrpc.client` or `requests` with JSON-RPC

### Rationale

1. **Self-Hosted Requirement**: Odoo Community can be installed locally without cloud dependencies
2. **JSON-RPC API**: Odoo provides XML-RPC and JSON-RPC APIs for external integration
3. **Python Native**: OdooRPC provides Pythonic interface to Odoo's API
4. **Operations Supported**: All required operations (invoices, payments, expenses, reports)

### Key Operations for Gold Tier

```python
import odoorpc

# Connect to local Odoo instance
odoo = odoorpc.ODOO('localhost', port=8069)
odoo.login('database_name', 'username', 'password')

# Create invoice
Invoice = odoo.env['account.move']
invoice_id = Invoice.create({
    'partner_id': customer_id,
    'move_type': 'out_invoice',
    'invoice_date': '2026-01-27',
    'invoice_line_ids': [(0, 0, {
        'product_id': product_id,
        'quantity': 1,
        'price_unit': 1500.00,
        'name': 'Consulting services'
    })]
})

# Send invoice via email
invoice = Invoice.browse(invoice_id)
invoice.action_post()  # Validate invoice
invoice.action_invoice_sent()  # Send via email

# Record payment
Payment = odoo.env['account.payment']
payment_id = Payment.create({
    'payment_type': 'inbound',
    'partner_id': customer_id,
    'amount': 1500.00,
    'date': '2026-01-27',
    'journal_id': bank_journal_id
})
payment = Payment.browse(payment_id)
payment.action_post()

# Create expense
Expense = odoo.env['hr.expense']
expense_id = Expense.create({
    'name': 'Office supplies',
    'product_id': expense_product_id,
    'unit_amount': 150.00,
    'date': '2026-01-27',
    'employee_id': employee_id
})

# Generate financial report
# Use Odoo's reporting engine or query account.move records
moves = Invoice.search_read(
    [('move_type', '=', 'out_invoice'), ('state', '=', 'posted')],
    ['name', 'partner_id', 'amount_total', 'invoice_date']
)
```

### Authentication Options

1. **API Key** (Recommended for local): Store in .env, use for all API calls
2. **Username/Password**: Store in OS credential manager (keyring library)
3. **OAuth 2.0**: Not typically used for self-hosted Odoo

### MCP Server Design (odoo_mcp.py)

```python
from fastmcp import FastMCP
import odoorpc

mcp = FastMCP(name="odoo-mcp")

@mcp.tool
async def create_invoice(
    customer_name: str,
    amount: float,
    description: str,
    due_date: str
) -> dict:
    """Create draft invoice in Odoo."""
    # Connect to Odoo
    # Create invoice
    # Return invoice ID and status
    return {"invoice_id": "INV/2026/0001", "status": "draft"}

@mcp.tool
async def send_invoice(invoice_id: str) -> dict:
    """Validate and send invoice via email."""
    # Post invoice (validate)
    # Send via email
    return {"status": "sent", "email_sent": True}

@mcp.tool
async def record_payment(
    invoice_id: str,
    amount: float,
    payment_date: str,
    payment_method: str
) -> dict:
    """Record payment against invoice."""
    # Create payment record
    # Reconcile with invoice
    return {"payment_id": "PAY/2026/0001", "status": "posted"}

@mcp.tool
async def create_expense(
    description: str,
    amount: float,
    category: str,
    receipt_path: str = None
) -> dict:
    """Create expense record."""
    # Create expense
    # Attach receipt if provided
    return {"expense_id": "EXP/2026/0001", "status": "draft"}

@mcp.tool
async def generate_report(
    report_type: str,  # "profit_loss", "balance_sheet", "cash_flow"
    start_date: str,
    end_date: str
) -> dict:
    """Generate financial report."""
    # Query Odoo accounting data
    # Format report
    return {"report_data": {...}, "format": "json"}
```

### Testing Strategy

- Unit tests with mock Odoo connection
- Integration tests with local Odoo instance (Docker container)
- Dry-run mode (DRY_RUN=true) returns mock data

### Alternatives Considered

- **Xero**: Cloud-based, rejected per requirements (must be self-hosted, local)
- **Direct XML-RPC**: More verbose, OdooRPC provides better abstraction
- **Custom accounting**: Reinventing the wheel, not recommended

**Decision**: OdooRPC with local Odoo Community installation meets all requirements.

---

## 2. Facebook Graph API Integration

### Decision: Use facebook-sdk (Python library)

**Library**: `facebook-sdk` (Python Facebook Graph API wrapper)
**Version**: Latest stable
**Alternative**: Direct `requests` with Graph API endpoints

### Rationale

1. **Official Support**: Well-maintained Python SDK for Facebook Graph API
2. **Page Posting**: Supports posting to Facebook Pages (business use case)
3. **Engagement Metrics**: Retrieve post insights (reach, engagement, reactions)
4. **OAuth 2.0**: Handles Page Access Token authentication

### Key Operations for Gold Tier

```python
import facebook

# Initialize with Page Access Token
graph = facebook.GraphAPI(access_token=PAGE_ACCESS_TOKEN, version='3.0')

# Post to Facebook Page
post = graph.put_object(
    parent_object='me',  # Page ID
    connection_name='feed',
    message='Big announcement tomorrow!',
    link='https://example.com'
)
# Returns: {'id': '123456789_987654321'}

# Upload photo
photo = graph.put_photo(
    image=open('product.jpg', 'rb'),
    message='Check out our new product!'
)

# Get post insights (engagement metrics)
insights = graph.get_object(
    id=f"{post['id']}/insights",
    metric='post_impressions,post_engaged_users'
)

# Get page posts
posts = graph.get_connections(
    id='me',
    connection_name='posts',
    fields='message,created_time,likes.summary(true),comments.summary(true)'
)
```

### Authentication

- **Page Access Token**: Long-lived token (never expires) for posting to Pages
- **OAuth 2.0 Flow**: User grants permissions, app receives token
- **Token Storage**: OS credential manager (keyring library)

### Rate Limits

- **200 requests per hour** per user
- **Respect rate limit headers**: `X-App-Usage`, `X-Business-Use-Case-Usage`
- **Exponential backoff**: 1s, 2s, 4s, 8s on rate limit errors

### MCP Server Design (facebook_mcp.py)

```python
from fastmcp import FastMCP
import facebook

mcp = FastMCP(name="facebook-mcp")

@mcp.tool
async def create_post(
    message: str,
    link: str = None,
    image_path: str = None
) -> dict:
    """Post message to Facebook Page."""
    # Post to page
    return {"post_id": "123456789_987654321", "status": "published"}

@mcp.tool
async def upload_photo(
    image_path: str,
    caption: str
) -> dict:
    """Upload photo to Facebook Page."""
    # Upload photo
    return {"photo_id": "123456789", "status": "published"}

@mcp.tool
async def get_post_insights(
    post_id: str,
    metrics: list = None
) -> dict:
    """Get engagement metrics for post."""
    # Fetch insights
    return {"impressions": 1234, "engaged_users": 89, "reactions": 34}
```

---

## 3. Instagram Graph API Integration

### Decision: Use Instagram Graph API via Facebook SDK

**Library**: `facebook-sdk` (Instagram Graph API is part of Facebook Graph API)
**Version**: Latest stable
**Requirement**: Instagram Business Account linked to Facebook Page

### Rationale

1. **Unified API**: Instagram Graph API uses same authentication as Facebook
2. **Business Features**: Posting, insights, media management
3. **Two-Step Media Creation**: Container → Publish pattern

### Key Operations for Gold Tier

```python
import facebook

graph = facebook.GraphAPI(access_token=PAGE_ACCESS_TOKEN, version='3.0')

# Create media container (step 1)
container = graph.post(
    path=f'{INSTAGRAM_ACCOUNT_ID}/media',
    image_url='https://example.com/image.jpg',
    caption='New product launch! #innovation'
)
# Returns: {'id': 'container_id'}

# Publish media (step 2)
media = graph.post(
    path=f'{INSTAGRAM_ACCOUNT_ID}/media_publish',
    creation_id=container['id']
)
# Returns: {'id': 'media_id'}

# Get media insights
insights = graph.get(
    path=f'{media_id}/insights',
    metric='impressions,reach,engagement'
)

# Create story
story_container = graph.post(
    path=f'{INSTAGRAM_ACCOUNT_ID}/media',
    image_url='https://example.com/story.jpg',
    media_type='STORIES'
)
story = graph.post(
    path=f'{INSTAGRAM_ACCOUNT_ID}/media_publish',
    creation_id=story_container['id']
)
```

### Authentication

- **Same as Facebook**: Page Access Token with Instagram permissions
- **Required Permissions**: `instagram_basic`, `instagram_content_publish`, `pages_read_engagement`

### Rate Limits

- **200 requests per hour** (shared with Facebook)
- **25 media posts per day** per Instagram account

### MCP Server Design (instagram_mcp.py)

```python
from fastmcp import FastMCP
import facebook

mcp = FastMCP(name="instagram-mcp")

@mcp.tool
async def create_media_post(
    image_url: str,
    caption: str,
    hashtags: list = None
) -> dict:
    """Post photo to Instagram Business."""
    # Create container
    # Publish media
    return {"media_id": "123456789", "status": "published"}

@mcp.tool
async def create_story(
    image_url: str
) -> dict:
    """Post story to Instagram."""
    # Create story container
    # Publish story
    return {"story_id": "987654321", "status": "published"}

@mcp.tool
async def get_media_insights(
    media_id: str
) -> dict:
    """Get engagement metrics for media."""
    # Fetch insights
    return {"impressions": 2456, "reach": 1234, "engagement": 234}
```

---

## 4. Twitter API v2 Integration

### Decision: Use tweepy (Python Twitter API library)

**Library**: `tweepy` (Official Python library for Twitter API v2)
**Version**: Latest stable (v4.0+)
**Authentication**: OAuth 2.0 PKCE (no client secret required)

### Rationale

1. **Official Library**: Maintained by Twitter/X
2. **API v2 Support**: Latest Twitter API features
3. **OAuth 2.0 PKCE**: Secure authentication without client secret
4. **Rate Limit Handling**: Built-in rate limit awareness

### Key Operations for Gold Tier

```python
import tweepy

# OAuth 2.0 PKCE authentication
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

# Post tweet
tweet = client.create_tweet(text='Big announcement tomorrow! #innovation')
# Returns: Response(data={'id': '1234567890', 'text': '...'})

# Create thread
tweet1 = client.create_tweet(text='Thread 1/3: Introduction')
tweet2 = client.create_tweet(
    text='Thread 2/3: Details',
    in_reply_to_tweet_id=tweet1.data['id']
)
tweet3 = client.create_tweet(
    text='Thread 3/3: Conclusion',
    in_reply_to_tweet_id=tweet2.data['id']
)

# Upload media
media = api.media_upload('image.jpg')
tweet_with_media = client.create_tweet(
    text='Check out this image!',
    media_ids=[media.media_id]
)

# Get tweet metrics
tweet_data = client.get_tweet(
    id=tweet.data['id'],
    tweet_fields=['public_metrics']
)
# Returns: impressions, likes, retweets, replies
```

### Authentication

- **OAuth 2.0 PKCE**: No client secret, more secure
- **Bearer Token**: For read-only operations
- **Access Token**: For posting and user-specific operations

### Rate Limits

- **100 tweets per 15 minutes** per user
- **300 tweets per 3 hours** per user
- **Respect rate limit headers**: `x-rate-limit-remaining`, `x-rate-limit-reset`

### MCP Server Design (twitter_mcp.py)

```python
from fastmcp import FastMCP
import tweepy

mcp = FastMCP(name="twitter-mcp")

@mcp.tool
async def create_tweet(
    text: str,
    media_paths: list = None
) -> dict:
    """Post tweet to Twitter/X."""
    # Upload media if provided
    # Create tweet
    return {"tweet_id": "1234567890", "status": "published"}

@mcp.tool
async def create_thread(
    tweets: list  # List of tweet texts
) -> dict:
    """Post tweet thread."""
    # Create tweets in sequence
    return {"thread_ids": ["123", "456", "789"], "status": "published"}

@mcp.tool
async def get_tweet_metrics(
    tweet_id: str
) -> dict:
    """Get engagement metrics for tweet."""
    # Fetch tweet with metrics
    return {"impressions": 3456, "likes": 145, "retweets": 23, "replies": 12}
```

---

## 5. Ralph Wiggum Loop (Autonomous Operation)

### Decision: Stop hook with file movement detection

**Implementation**: `.claude/hooks/stop/ralph_wiggum_check.py`
**Pattern**: File movement detection (NOT promise-based)
**Safety**: Max iterations limit (default: 10)

### Rationale

1. **Autonomous Operation**: Continue processing until all tasks complete
2. **File Movement Detection**: Task file moves to /Done/ signals completion
3. **Safety Limits**: Max iterations prevents infinite loops
4. **State Persistence**: Save state after each iteration for crash recovery

### Stop Hook Implementation

```python
#!/usr/bin/env python3
"""
Ralph Wiggum Loop Stop Hook

Checks if autonomous task is complete by detecting if task file
has moved to /Done/ folder. If not complete, re-inject prompt
to continue processing.

Max iterations: 10 (configurable via RALPH_MAX_ITERATIONS env var)
"""

import os
import sys
from pathlib import Path

def check_task_complete(task_file_path: str) -> bool:
    """Check if task file has moved to /Done/ folder."""
    task_path = Path(task_file_path)

    # Check if file exists in /Done/ folder
    vault_root = Path("My_AI_Employee/AI_Employee_Vault")
    done_folder = vault_root / "Done"

    # Check if task file is in Done folder
    if task_path.parent.name == "Done":
        return True

    # Check if file no longer exists in original location
    if not task_path.exists():
        # Check if it moved to Done
        done_file = done_folder / task_path.name
        if done_file.exists():
            return True

    return False

def get_iteration_count() -> int:
    """Get current iteration count from state file."""
    state_file = Path(".ralph_state.json")
    if state_file.exists():
        import json
        with open(state_file) as f:
            state = json.load(f)
            return state.get("iteration", 0)
    return 0

def increment_iteration():
    """Increment iteration count in state file."""
    import json
    state_file = Path(".ralph_state.json")
    iteration = get_iteration_count() + 1
    with open(state_file, 'w') as f:
        json.dump({"iteration": iteration}, f)
    return iteration

def main():
    # Get task file path from environment or args
    task_file = os.getenv("RALPH_TASK_FILE", sys.argv[1] if len(sys.argv) > 1 else None)

    if not task_file:
        print("No task file specified, exiting normally")
        sys.exit(0)

    # Check if task is complete
    if check_task_complete(task_file):
        print(f"Task complete: {task_file} moved to /Done/")
        # Clean up state file
        Path(".ralph_state.json").unlink(missing_ok=True)
        sys.exit(0)

    # Check iteration limit
    max_iterations = int(os.getenv("RALPH_MAX_ITERATIONS", "10"))
    current_iteration = increment_iteration()

    if current_iteration >= max_iterations:
        print(f"Max iterations ({max_iterations}) reached, exiting")
        sys.exit(0)

    # Task not complete, re-inject prompt
    print(f"Task not complete (iteration {current_iteration}/{max_iterations}), continuing...")

    # Re-inject prompt to continue processing
    prompt = f"Continue processing task: {task_file}"
    print(f"RALPH_CONTINUE: {prompt}")
    sys.exit(1)  # Non-zero exit triggers re-injection

if __name__ == "__main__":
    main()
```

### Usage Pattern

```bash
# Start autonomous task
RALPH_TASK_FILE="My_AI_Employee/AI_Employee_Vault/Needs_Action/task.md" \
RALPH_MAX_ITERATIONS=10 \
claude-code "Process all pending items in /Needs_Action/"

# Stop hook runs after each Claude Code exit
# If task not complete, re-injects prompt automatically
# Continues until task moves to /Done/ or max iterations reached
```

---

## 6. Weekly CEO Briefing Generation

### Decision: Scheduled task via cron + Claude Code skill

**Schedule**: Sunday 8:00 PM (cron: `0 20 * * 0`)
**Implementation**: `ceo-briefing-generator` skill
**Data Sources**: /Done/ folder, Odoo, social media APIs, Business_Goals.md

### Rationale

1. **Scheduled Execution**: Cron ensures weekly briefing runs automatically
2. **Data Aggregation**: Collect from multiple sources (tasks, accounting, social media)
3. **AI Analysis**: Claude Code generates insights, identifies bottlenecks, suggests optimizations
4. **Output Format**: Markdown file in /Briefings/ folder

### Cron Configuration

```bash
# Add to crontab
0 20 * * 0 cd /path/to/hackathon-0 && claude-code "/ceo-briefing-generator"
```

### Briefing Generation Workflow

```python
# Pseudo-code for ceo-briefing-generator skill

def generate_ceo_briefing():
    # 1. Collect completed tasks from /Done/ (last 7 days)
    tasks = read_done_folder(days=7)

    # 2. Query Odoo for financial data
    revenue = odoo_mcp.generate_report("profit_loss", start_date, end_date)
    expenses = odoo_mcp.generate_report("expenses", start_date, end_date)
    invoices = odoo_mcp.get_invoices(status="overdue")

    # 3. Query social media for metrics
    fb_metrics = facebook_mcp.get_engagement_summary(days=7)
    ig_metrics = instagram_mcp.get_media_insights(days=7)
    tw_metrics = twitter_mcp.get_engagement_summary(days=7)

    # 4. Read business goals
    goals = read_business_goals()

    # 5. Generate briefing with AI analysis
    briefing = create_briefing_markdown(
        tasks=tasks,
        revenue=revenue,
        expenses=expenses,
        invoices=invoices,
        social_media={
            "facebook": fb_metrics,
            "instagram": ig_metrics,
            "twitter": tw_metrics
        },
        goals=goals
    )

    # 6. Save to /Briefings/ folder
    save_briefing(briefing, date="2026-01-27")
```

---

## 7. Enhanced Error Recovery

### Decision: Exponential backoff + watchdog monitoring + graceful degradation

**Retry Logic**: 1s, 2s, 4s, 8s (max 4 attempts)
**Watchdog**: Check every 60 seconds
**Graceful Degradation**: Queue operations when services unavailable

### Rationale

1. **Transient Errors**: Network timeouts, API rate limits recover with retry
2. **Component Monitoring**: Detect crashes and auto-restart
3. **Graceful Degradation**: System continues operating when components fail
4. **Zero Data Loss**: Queue operations locally, process when service restored

### Retry Logic Implementation

```python
import asyncio
from typing import Callable, Any

async def retry_with_backoff(
    func: Callable,
    max_attempts: int = 4,
    backoff_base: float = 1.0,
    *args,
    **kwargs
) -> Any:
    """Retry function with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts - 1:
                raise  # Last attempt, re-raise exception

            # Calculate backoff delay: 1s, 2s, 4s, 8s
            delay = backoff_base * (2 ** attempt)
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
            await asyncio.sleep(delay)
```

### Watchdog Monitoring

```python
# watchdog.py - Monitor critical components

import time
import subprocess
from pathlib import Path

COMPONENTS = [
    {"name": "orchestrator", "command": "python My_AI_Employee/orchestrator.py"},
    {"name": "gmail_watcher", "command": "python My_AI_Employee/watchers/gmail_watcher.py"},
    {"name": "whatsapp_watcher", "command": "python My_AI_Employee/watchers/whatsapp_watcher.py"},
]

def check_component_running(component: dict) -> bool:
    """Check if component process is running."""
    # Check PID file or process list
    pid_file = Path(f".{component['name']}.pid")
    if pid_file.exists():
        pid = int(pid_file.read_text())
        try:
            os.kill(pid, 0)  # Check if process exists
            return True
        except OSError:
            return False
    return False

def restart_component(component: dict):
    """Restart crashed component."""
    print(f"Restarting {component['name']}...")
    subprocess.Popen(component['command'].split())

def main():
    while True:
        for component in COMPONENTS:
            if not check_component_running(component):
                print(f"Component {component['name']} not running!")
                restart_component(component)

        time.sleep(60)  # Check every 60 seconds

if __name__ == "__main__":
    main()
```

### Graceful Degradation

```python
# Queue operations when services unavailable

from pathlib import Path
import json

def queue_operation(operation: dict):
    """Queue operation for later processing."""
    queue_file = Path("My_AI_Employee/.operation_queue.jsonl")
    with open(queue_file, 'a') as f:
        f.write(json.dumps(operation) + '\n')

def process_queue():
    """Process queued operations when service restored."""
    queue_file = Path("My_AI_Employee/.operation_queue.jsonl")
    if not queue_file.exists():
        return

    with open(queue_file) as f:
        operations = [json.loads(line) for line in f]

    for operation in operations:
        try:
            # Execute operation
            execute_operation(operation)
        except Exception as e:
            print(f"Failed to process queued operation: {e}")
            # Re-queue if still failing
            queue_operation(operation)

    # Clear queue file
    queue_file.unlink()
```

---

## Summary of Technology Decisions

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Odoo Integration | OdooRPC | Self-hosted, local, JSON-RPC API, all operations supported |
| Facebook API | facebook-sdk | Official SDK, Page posting, engagement metrics, OAuth 2.0 |
| Instagram API | facebook-sdk | Unified with Facebook, Business account, two-step media creation |
| Twitter API | tweepy | Official library, API v2, OAuth 2.0 PKCE, rate limit handling |
| Autonomous Operation | Stop hook + file detection | File movement signals completion, max iterations safety |
| CEO Briefing | Cron + Claude Code skill | Scheduled execution, multi-source data aggregation, AI analysis |
| Error Recovery | Exponential backoff + watchdog | Retry transient errors, monitor components, graceful degradation |
| MCP Framework | FastMCP | Consistent with Silver tier, Pydantic validation, production-ready |

All technology choices align with constitution principles and build on Silver tier patterns.
