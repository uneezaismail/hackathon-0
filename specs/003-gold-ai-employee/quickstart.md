# Quick Start Guide: Gold Tier AI Employee

**Date**: 2026-01-27
**Feature**: Gold Tier AI Employee
**Purpose**: Setup and deployment guide for Gold tier implementation

---

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or WSL2 (Windows)
- **Python**: 3.13+ installed
- **Node.js**: 18+ (for PM2 process management)
- **Git**: For version control
- **Docker**: Optional, for Odoo Community installation

### Bronze & Silver Tier Operational

Gold tier is ADDITIVE to Silver tier. Verify Bronze and Silver are working:

```bash
# Check Bronze tier
ls -la My_AI_Employee/AI_Employee_Vault/
# Should see: Inbox/, Needs_Action/, Done/, Dashboard.md, Company_Handbook.md

# Check Silver tier
ls -la My_AI_Employee/AI_Employee_Vault/
# Should see: Pending_Approval/, Approved/, Rejected/, Failed/, Logs/

# Verify Silver tier watchers
ps aux | grep watcher
# Should see: gmail_watcher.py, whatsapp_watcher.py, linkedin_watcher.py

# Verify Silver tier MCP servers
ps aux | grep mcp
# Should see: email_mcp.py, linkedin_mcp.py, browser_mcp.py
```

### API Accounts Required

- **Odoo Community**: Self-hosted instance (see Odoo Installation below)
- **Facebook**: Developer account with Page Access Token
- **Instagram**: Business account linked to Facebook Page
- **Twitter**: Developer account with API v2 access

---

## Installation

### 1. Install Dependencies

```bash
# Navigate to project root
cd /path/to/hackathon-0

# Install Python dependencies
uv pip install odoorpc facebook-sdk tweepy keyring

# Install PM2 globally
npm install -g pm2

# Verify installations
python -c "import odoorpc; print('OdooRPC installed')"
python -c "import facebook; print('facebook-sdk installed')"
python -c "import tweepy; print('tweepy installed')"
pm2 --version
```

### 2. Install Odoo Community (Self-Hosted, Local)

#### Option A: Docker Installation (Recommended)

```bash
# Create Odoo directory
mkdir -p ~/odoo-data

# Run Odoo Community in Docker
docker run -d \
  --name odoo \
  -p 8069:8069 \
  -v ~/odoo-data:/var/lib/odoo \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo \
  -e POSTGRES_DB=postgres \
  odoo:19

# Wait for Odoo to start (30-60 seconds)
sleep 60

# Access Odoo web interface
# Open browser: http://localhost:8069
# Create database: odoo_db
# Set master password: (choose secure password)
# Create admin user
```

#### Option B: Native Installation

```bash
# Install PostgreSQL
sudo apt-get install postgresql

# Install Odoo dependencies
sudo apt-get install python3-pip python3-dev libxml2-dev libxslt1-dev \
  zlib1g-dev libsasl2-dev libldap2-dev build-essential libssl-dev \
  libffi-dev libmysqlclient-dev libjpeg-dev libpq-dev libjpeg8-dev \
  liblcms2-dev libblas-dev libatlas-base-dev

# Download Odoo Community 19
wget https://nightly.odoo.com/19.0/nightly/src/odoo_19.0.latest.tar.gz
tar xvf odoo_19.0.latest.tar.gz
cd odoo-19.0

# Install Python dependencies
pip3 install -r requirements.txt

# Create Odoo user and database
sudo -u postgres createuser -s odoo
sudo -u postgres createdb odoo_db

# Start Odoo
./odoo-bin --addons-path=addons --db-filter=odoo_db
```

#### Verify Odoo Installation

```bash
# Test Odoo connection
python3 << EOF
import odoorpc
odoo = odoorpc.ODOO('localhost', port=8069)
odoo.login('odoo_db', 'admin', 'admin_password')
print(f"Connected to Odoo: {odoo.env.uid}")
EOF
```

### 3. Configure Social Media APIs

#### Facebook Page Access Token

1. **Create Facebook App**:
   - Go to https://developers.facebook.com/apps
   - Click "Create App" → "Business" type
   - Enter app name and contact email

2. **Add Facebook Login**:
   - Dashboard → Add Product → Facebook Login
   - Settings → Valid OAuth Redirect URIs: `http://localhost:8080/callback`

3. **Request Permissions**:
   - App Review → Permissions and Features
   - Request: `pages_manage_posts`, `pages_read_engagement`, `pages_read_user_content`

4. **Get Page Access Token**:
   ```bash
   # Use Graph API Explorer: https://developers.facebook.com/tools/explorer
   # Select your app
   # Select your Page
   # Generate Access Token with required permissions
   # Copy Page Access Token
   ```

5. **Store Token**:
   ```bash
   python3 << EOF
   import keyring
   keyring.set_password('facebook_mcp', 'page_access_token', 'YOUR_PAGE_ACCESS_TOKEN')
   print("Facebook token stored")
   EOF
   ```

#### Instagram Business Account

1. **Convert to Business Account**:
   - Instagram app → Settings → Account → Switch to Professional Account
   - Choose "Business"

2. **Link to Facebook Page**:
   - Instagram → Settings → Account → Linked Accounts → Facebook
   - Select your Facebook Page

3. **Get Instagram Account ID**:
   ```bash
   # Use Graph API Explorer
   # GET /me/accounts (with Page Access Token)
   # GET /{page-id}?fields=instagram_business_account
   # Copy Instagram Business Account ID
   ```

4. **Store Configuration**:
   ```bash
   # Add to .env
   echo "INSTAGRAM_ACCOUNT_ID=your_instagram_account_id" >> .env
   ```

#### Twitter API v2 Access

1. **Create Twitter Developer Account**:
   - Go to https://developer.twitter.com/en/portal/dashboard
   - Apply for Elevated access (required for posting)

2. **Create App**:
   - Dashboard → Projects & Apps → Create App
   - Enter app name and description

3. **Generate Keys**:
   - App Settings → Keys and Tokens
   - Generate API Key and Secret
   - Generate Access Token and Secret
   - Generate Bearer Token

4. **Store Credentials**:
   ```bash
   python3 << EOF
   import keyring
   keyring.set_password('twitter_mcp', 'api_key', 'YOUR_API_KEY')
   keyring.set_password('twitter_mcp', 'api_secret', 'YOUR_API_SECRET')
   keyring.set_password('twitter_mcp', 'access_token', 'YOUR_ACCESS_TOKEN')
   keyring.set_password('twitter_mcp', 'access_secret', 'YOUR_ACCESS_SECRET')
   keyring.set_password('twitter_mcp', 'bearer_token', 'YOUR_BEARER_TOKEN')
   print("Twitter credentials stored")
   EOF
   ```

### 4. Create Gold Tier Vault Folders

```bash
# Navigate to vault
cd My_AI_Employee/AI_Employee_Vault

# Create Briefings folder
mkdir -p Briefings

# Verify folder structure
ls -la
# Should see: Inbox/, Needs_Action/, Pending_Approval/, Approved/, Rejected/,
#             Failed/, Done/, Plans/, Logs/, Briefings/, Dashboard.md,
#             Company_Handbook.md, Business_Goals.md
```

### 5. Create Business_Goals.md

```bash
cat > My_AI_Employee/AI_Employee_Vault/Business_Goals.md << 'EOF'
---
type: business_goals
updated: 2026-01-27
---

# Business Goals

## Revenue Targets

- **Monthly Revenue Target**: $50,000
- **Quarterly Revenue Target**: $150,000
- **Annual Revenue Target**: $600,000

## Key Performance Indicators (KPIs)

- **Invoice Payment Time**: < 30 days average
- **Outstanding Receivables**: < $20,000
- **Monthly Expenses**: < $15,000
- **Profit Margin**: > 30%

## Social Media Goals

- **Facebook**: 1,000 followers, 5% engagement rate
- **Instagram**: 2,000 followers, 8% engagement rate
- **Twitter**: 500 followers, 3% engagement rate
- **Weekly Posts**: 3-5 posts per platform

## Operational Goals

- **Task Completion Rate**: > 95%
- **Response Time**: < 24 hours for client emails
- **Approval Processing**: < 4 hours for pending approvals
- **System Uptime**: > 99%

## Growth Initiatives

- Launch new product line (Q2 2026)
- Expand to 2 new markets (Q3 2026)
- Hire 2 additional team members (Q4 2026)
EOF
```

### 6. Install Ralph Wiggum Stop Hook

```bash
# Create hooks directory
mkdir -p .claude/hooks/stop

# Create stop hook script
cat > .claude/hooks/stop/ralph_wiggum_check.py << 'EOF'
#!/usr/bin/env python3
"""Ralph Wiggum Loop Stop Hook - File movement detection"""

import os
import sys
import json
from pathlib import Path

def check_task_complete(task_file_path: str) -> bool:
    """Check if task file has moved to /Done/ folder."""
    task_path = Path(task_file_path)
    vault_root = Path("My_AI_Employee/AI_Employee_Vault")
    done_folder = vault_root / "Done"

    # Check if file is in Done folder
    if task_path.parent.name == "Done":
        return True

    # Check if file moved to Done
    if not task_path.exists():
        done_file = done_folder / task_path.name
        if done_file.exists():
            return True

    return False

def get_iteration_count() -> int:
    """Get current iteration count from state file."""
    state_file = Path(".ralph_state.json")
    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)
            return state.get("iteration", 0)
    return 0

def increment_iteration():
    """Increment iteration count in state file."""
    state_file = Path(".ralph_state.json")
    iteration = get_iteration_count() + 1
    with open(state_file, 'w') as f:
        json.dump({"iteration": iteration}, f)
    return iteration

def main():
    task_file = os.getenv("RALPH_TASK_FILE", sys.argv[1] if len(sys.argv) > 1 else None)

    if not task_file:
        print("No task file specified, exiting normally")
        sys.exit(0)

    if check_task_complete(task_file):
        print(f"Task complete: {task_file} moved to /Done/")
        Path(".ralph_state.json").unlink(missing_ok=True)
        sys.exit(0)

    max_iterations = int(os.getenv("RALPH_MAX_ITERATIONS", "10"))
    current_iteration = increment_iteration()

    if current_iteration >= max_iterations:
        print(f"Max iterations ({max_iterations}) reached, exiting")
        sys.exit(0)

    print(f"Task not complete (iteration {current_iteration}/{max_iterations}), continuing...")
    print(f"RALPH_CONTINUE: Continue processing task: {task_file}")
    sys.exit(1)

if __name__ == "__main__":
    main()
EOF

# Make executable
chmod +x .claude/hooks/stop/ralph_wiggum_check.py

# Test stop hook
python3 .claude/hooks/stop/ralph_wiggum_check.py
```

### 7. Configure PM2 for Watchdog Monitoring

```bash
# Create PM2 ecosystem config
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    // Silver tier watchers (already configured)
    {
      name: 'gmail-watcher',
      script: 'My_AI_Employee/watchers/gmail_watcher.py',
      interpreter: 'python3',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'whatsapp-watcher',
      script: 'My_AI_Employee/watchers/whatsapp_watcher.py',
      interpreter: 'python3',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'linkedin-watcher',
      script: 'My_AI_Employee/watchers/linkedin_watcher.py',
      interpreter: 'python3',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    },
    // Silver tier orchestrator
    {
      name: 'orchestrator',
      script: 'My_AI_Employee/orchestrator.py',
      interpreter: 'python3',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    },
    // Gold tier: Watchdog monitoring
    {
      name: 'watchdog',
      script: 'My_AI_Employee/watchdog.py',
      interpreter: 'python3',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    }
  ]
};
EOF

# Start all processes
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
# Follow the command output to complete startup configuration

# Check status
pm2 status
```

### 8. Configure Cron for Weekly CEO Briefing

```bash
# Add cron job for Sunday 8:00 PM
crontab -e

# Add this line:
0 20 * * 0 cd /path/to/hackathon-0 && /usr/bin/claude-code "/ceo-briefing-generator" >> /tmp/ceo-briefing.log 2>&1

# Verify cron job
crontab -l
```

### 9. Update .env Configuration

```bash
# Add Gold tier configuration to .env
cat >> .env << 'EOF'

# Gold Tier Configuration

# Odoo Community
ODOO_URL=http://localhost:8069
ODOO_DATABASE=odoo_db
ODOO_USERNAME=admin
ODOO_API_KEY=your_odoo_api_key_here
ODOO_MCP_PORT=3007

# Facebook
FACEBOOK_PAGE_ACCESS_TOKEN=stored_in_keyring
FACEBOOK_PAGE_ID=your_page_id_here
FACEBOOK_MCP_PORT=3004

# Instagram
INSTAGRAM_PAGE_ACCESS_TOKEN=stored_in_keyring
INSTAGRAM_ACCOUNT_ID=your_instagram_account_id_here
INSTAGRAM_MCP_PORT=3005

# Twitter
TWITTER_API_KEY=stored_in_keyring
TWITTER_API_SECRET=stored_in_keyring
TWITTER_ACCESS_TOKEN=stored_in_keyring
TWITTER_ACCESS_SECRET=stored_in_keyring
TWITTER_BEARER_TOKEN=stored_in_keyring
TWITTER_MCP_PORT=3006

# Ralph Wiggum Loop
RALPH_MAX_ITERATIONS=10

# Dry Run Mode (set to false for production)
DRY_RUN=true
EOF
```

---

## Testing

### Test 1: Odoo Integration

```bash
# Test invoice creation
python3 << EOF
from My_AI_Employee.mcp_servers import odoo_mcp
import asyncio

async def test_odoo():
    result = await odoo_mcp.create_invoice(
        customer_name="Test Customer",
        customer_email="test@example.com",
        invoice_date="2026-01-27",
        due_date="2026-02-27",
        line_items=[
            {"description": "Consulting", "quantity": 1, "unit_price": 1500.00}
        ]
    )
    print(f"Invoice created: {result}")

asyncio.run(test_odoo())
EOF
```

### Test 2: Social Media Integration

```bash
# Test Facebook post (dry-run mode)
python3 << EOF
from My_AI_Employee.mcp_servers import facebook_mcp
import asyncio

async def test_facebook():
    result = await facebook_mcp.create_post(
        message="Test post from Gold tier AI Employee",
        link="https://example.com"
    )
    print(f"Post created: {result}")

asyncio.run(test_facebook())
EOF
```

### Test 3: Ralph Wiggum Loop

```bash
# Create test task file
cat > My_AI_Employee/AI_Employee_Vault/Needs_Action/test_task.md << 'EOF'
---
type: test
status: pending
---

# Test Task

This is a test task for Ralph Wiggum Loop.
EOF

# Start autonomous processing
RALPH_TASK_FILE="My_AI_Employee/AI_Employee_Vault/Needs_Action/test_task.md" \
RALPH_MAX_ITERATIONS=3 \
claude-code "Process test task autonomously"

# Verify task moved to Done
ls -la My_AI_Employee/AI_Employee_Vault/Done/test_task.md
```

### Test 4: CEO Briefing Generation

```bash
# Manually trigger briefing generation
claude-code "/ceo-briefing-generator"

# Verify briefing created
ls -la My_AI_Employee/AI_Employee_Vault/Briefings/
cat My_AI_Employee/AI_Employee_Vault/Briefings/BRIEF-2026-W04.md
```

### Test 5: End-to-End Workflow

```bash
# 1. Drop file to trigger watcher
echo "Create invoice for Client A: $1,500 for consulting" > ~/drop_folder/invoice_request.txt

# 2. Wait for watcher to detect (30-60 seconds)
sleep 60

# 3. Check Needs_Action folder
ls -la My_AI_Employee/AI_Employee_Vault/Needs_Action/

# 4. Process with needs-action-triage skill
claude-code "@needs-action-triage"

# 5. Check Pending_Approval folder
ls -la My_AI_Employee/AI_Employee_Vault/Pending_Approval/

# 6. Approve request (move to Approved)
mv My_AI_Employee/AI_Employee_Vault/Pending_Approval/INVOICE_*.md \
   My_AI_Employee/AI_Employee_Vault/Approved/

# 7. Wait for orchestrator to execute (5-10 seconds)
sleep 10

# 8. Check Done folder and audit logs
ls -la My_AI_Employee/AI_Employee_Vault/Done/
cat My_AI_Employee/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json

# 9. Verify invoice in Odoo
# Open browser: http://localhost:8069
# Navigate to Accounting → Customers → Invoices
```

---

## Monitoring

### Check System Status

```bash
# PM2 process status
pm2 status

# View logs
pm2 logs orchestrator --lines 50
pm2 logs watchdog --lines 50

# Check vault activity
ls -la My_AI_Employee/AI_Employee_Vault/Needs_Action/
ls -la My_AI_Employee/AI_Employee_Vault/Pending_Approval/
ls -la My_AI_Employee/AI_Employee_Vault/Done/

# Check audit logs
tail -f My_AI_Employee/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json
```

### Dashboard Monitoring

```bash
# View Dashboard.md
cat My_AI_Employee/AI_Employee_Vault/Dashboard.md

# Check recent activity
tail -20 My_AI_Employee/AI_Employee_Vault/Dashboard.md
```

---

## Troubleshooting

### Odoo Connection Issues

```bash
# Check Odoo is running
docker ps | grep odoo
# OR
ps aux | grep odoo

# Test connection
curl http://localhost:8069/web/database/selector

# Check logs
docker logs odoo
# OR
tail -f ~/odoo-data/odoo.log
```

### Social Media API Errors

```bash
# Test Facebook token
python3 << EOF
import facebook
graph = facebook.GraphAPI(access_token='YOUR_TOKEN')
print(graph.get_object(id='me'))
EOF

# Test Twitter credentials
python3 << EOF
import tweepy
client = tweepy.Client(bearer_token='YOUR_TOKEN')
print(client.get_me())
EOF
```

### Ralph Wiggum Loop Not Continuing

```bash
# Check stop hook is executable
ls -la .claude/hooks/stop/ralph_wiggum_check.py

# Test stop hook manually
RALPH_TASK_FILE="test.md" python3 .claude/hooks/stop/ralph_wiggum_check.py

# Check state file
cat .ralph_state.json
```

### CEO Briefing Not Generated

```bash
# Check cron job
crontab -l

# Test briefing generation manually
claude-code "/ceo-briefing-generator"

# Check cron logs
tail -f /tmp/ceo-briefing.log
```

---

## Security Checklist

- [ ] All credentials stored in OS credential manager (keyring)
- [ ] .env file is gitignored
- [ ] Audit logs sanitize credentials
- [ ] DRY_RUN=true for testing
- [ ] HITL approval enabled for all financial operations
- [ ] Odoo database password is strong
- [ ] Social media API tokens have minimum required permissions
- [ ] PM2 processes run with appropriate user permissions

---

## Next Steps

1. **Validate Bronze & Silver Tier**: Ensure all Bronze and Silver functionality works
2. **Install Odoo Community**: Set up self-hosted Odoo instance
3. **Configure Social Media APIs**: Get tokens for Facebook, Instagram, Twitter
4. **Install Gold Tier Components**: MCP servers, stop hook, watchdog
5. **Run End-to-End Test**: Verify complete workflow
6. **Monitor System**: Check PM2 status, audit logs, dashboard
7. **Generate First CEO Briefing**: Manually trigger or wait for Sunday 8:00 PM

For implementation details, see `specs/003-gold-ai-employee/plan.md`.
