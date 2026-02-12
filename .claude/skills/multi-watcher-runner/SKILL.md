---
name: multi-watcher-runner
description: >
  Orchestrate and manage multiple watchers for Silver tier: Gmail, WhatsApp Web, LinkedIn, and filesystem monitoring.
  Monitors all sources for new emails, messages, and notifications. Creates action items in /Needs_Action/ folder.
  Manages watcher authentication, session persistence, health monitoring, and automatic restart on crash.
  Use when: (1) Setting up Silver tier watcher infrastructure, (2) Starting all watchers simultaneously,
  (3) Checking watcher health and status, (4) Debugging watcher issues, (5) Managing watcher sessions and credentials.
  Trigger phrases: "start Silver watchers", "run all watchers", "monitor Gmail WhatsApp LinkedIn",
  "check watcher status", "setup multi-watcher infrastructure", "orchestrate watchers".
---

# Multi-Watcher Runner (Silver Tier)

Orchestrate multiple watchers (Gmail, WhatsApp Web, LinkedIn, filesystem) running simultaneously using the unified watcher runner with health monitoring and auto-restart.

## Quick Start

### Run All Watchers with Orchestration

```bash
# Start all watchers with health monitoring
uv run python run_watcher.py --watcher all

# This starts:
# - Gmail watcher (monitors inbox)
# - LinkedIn watcher (monitors messages/notifications)
# - WhatsApp watcher (monitors WhatsApp Web)
# - Filesystem watcher (monitors drop folder)
```

### Run Individual Silver Tier Watchers

```bash
# Gmail watcher only
uv run python run_watcher.py --watcher gmail

# LinkedIn watcher only
uv run python run_watcher.py --watcher linkedin

# WhatsApp watcher only
uv run python run_watcher.py --watcher whatsapp
```

## Prerequisites

### 1. Gmail OAuth Setup

```bash
# Run OAuth setup
uv run python scripts/setup/setup_gmail_oauth.py

# Verify connection
uv run python scripts/debug/debug_gmail.py
```

**Required files:**
- `credentials.json` - OAuth client credentials from Google Cloud Console
- `token.json` - Generated after OAuth flow

### 2. LinkedIn Credentials

Configure in `.env`:
```bash
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password
```

### 3. WhatsApp Session

Configure in `.env`:
```bash
WHATSAPP_SESSION_PATH=./whatsapp_session
```

### 4. Playwright Browsers

```bash
# Install Chromium for browser automation
playwright install chromium
```

## Configuration

### Environment Variables (.env)

```bash
# Vault configuration
VAULT_ROOT=AI_Employee_Vault

# Gmail watcher
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json

# LinkedIn watcher
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password

# WhatsApp watcher
WHATSAPP_SESSION_PATH=./whatsapp_session

# Filesystem watcher
WATCH_FOLDER=test_watch_folder
WATCH_MODE=events

# Watcher settings
WATCHER_CHECK_INTERVAL=30  # Health check interval for orchestration

# Logging
LOG_LEVEL=INFO
```

## Orchestration Features

When running with `--watcher all`, you get:

### 1. Health Monitoring
- Checks all watchers every 30 seconds
- Detects crashed watchers
- Logs uptime percentage

### 2. Auto-Restart
- Automatically restarts crashed watchers
- Configurable retry attempts (default: 5)
- Exponential backoff between retries

### 3. Unified Logging
- All watcher logs in one place
- Status updates every 30 seconds
- Easy to monitor all watchers

### 4. Graceful Shutdown
- Ctrl+C stops all watchers cleanly
- Final status report on exit
- No orphaned processes

## Workflow

### Starting All Watchers

```bash
# 1. Verify prerequisites
uv run python scripts/validate/validate_silver_tier.py

# 2. Start all watchers
uv run python run_watcher.py --watcher all

# 3. Monitor logs
# Watch for "✅ {watcher} watcher started successfully"
# Status updates appear every 30 seconds
```

### Monitoring Watcher Health

The orchestrator logs status every 30 seconds:

```
=== Multi-Watcher Orchestrator Status ===
GMAIL        | Status: online   | OK: 120 | Fail: 0   | Items: 5  | Uptime: 100.0%
LINKEDIN     | Status: online   | OK: 120 | Fail: 0   | Items: 2  | Uptime: 100.0%
WHATSAPP     | Status: online   | OK: 120 | Fail: 0   | Items: 8  | Uptime: 100.0%
FILESYSTEM   | Status: online   | OK: 120 | Fail: 0   | Items: 3  | Uptime: 100.0%
```

### Stopping Watchers

```bash
# Press Ctrl+C
# Orchestrator will:
# 1. Stop all watcher threads
# 2. Print final status report
# 3. Exit cleanly
```

## Troubleshooting

### Gmail Watcher Fails to Start

**Problem**: "OAuth authentication failed"
**Solution**: Re-run OAuth setup
```bash
rm token.json
uv run python scripts/setup/setup_gmail_oauth.py
```

### LinkedIn Watcher Fails to Start

**Problem**: "Login failed"
**Solution**: Check credentials in .env
```bash
# Verify credentials
grep LINKEDIN .env

# Test manually
uv run python run_watcher.py --watcher linkedin --log-level DEBUG
```

### WhatsApp Watcher Fails to Start

**Problem**: "Session not found"
**Solution**: Create new session
```bash
# WhatsApp watcher will prompt for QR code scan on first run
uv run python run_watcher.py --watcher whatsapp
```

### Watcher Keeps Restarting

**Problem**: Watcher crashes repeatedly
**Debugging**:
1. Check logs for error messages
2. Run watcher individually with debug logging
3. Verify credentials and configuration

```bash
# Debug specific watcher
uv run python run_watcher.py --watcher gmail --log-level DEBUG
```

### No Action Items Created

**Problem**: Watchers run but no items in Needs_Action/
**Debugging**:
1. Check if watchers are detecting new items
2. Verify vault structure exists
3. Check watcher logs for errors
4. Test with known new item (send test email)

## Testing

### Test Individual Watchers

```bash
# Test Gmail watcher
uv run python run_watcher.py --watcher gmail --log-level DEBUG
# Send yourself a test email
# Check Needs_Action/ for new item

# Test LinkedIn watcher
uv run python run_watcher.py --watcher linkedin --log-level DEBUG
# Send yourself a LinkedIn message
# Check Needs_Action/ for new item
```

### Test Orchestration

```bash
# Start all watchers
uv run python run_watcher.py --watcher all

# In another terminal, trigger multiple sources:
# - Send email to yourself
# - Send LinkedIn message
# - Drop file in watch folder
# - Send WhatsApp message

# Verify action items created for all sources
ls -lh AI_Employee_Vault/Needs_Action/
```

## Integration with Workflow

After watchers create action items:

```bash
# 1. Watchers create items in Needs_Action/
# 2. Process with needs-action-triage
/needs-action-triage

# 3. Approve actions in Pending_Approval/
# (Manual step - move to Approved/)

# 4. Execute approved actions
/mcp-executor
```

## Production Deployment

### Deployment Approaches

**Thread-Based (Development)**: Use `run_watcher.py` for development and testing
- Simple to start/stop
- All watchers in one process
- Easy debugging with unified logs
- Good for development and testing

**PM2-Based (Production)**: Use `manage_watchers.py` for production deployment
- Individual watcher processes
- Advanced health monitoring
- Memory/CPU metrics tracking
- Automatic restart on crash
- Dashboard integration
- Production-grade reliability

### Option 1: PM2 Process Manager (Recommended for Production)

#### Quick Start with PM2 Management

```bash
# Install PM2
npm install -g pm2

# Start all watchers with PM2 management
python3 .claude/skills/multi-watcher-runner/scripts/manage_watchers.py --action start-all

# Check comprehensive status
python3 .claude/skills/multi-watcher-runner/scripts/manage_watchers.py --action status

# Health check with metrics
python3 .claude/skills/multi-watcher-runner/scripts/manage_watchers.py --action health
```

#### PM2 Management Commands

**Start Individual Watcher:**
```bash
python3 .claude/skills/multi-watcher-runner/scripts/manage_watchers.py \
  --action start \
  --watcher gmail
```

**Stop Individual Watcher:**
```bash
python3 .claude/skills/multi-watcher-runner/scripts/manage_watchers.py \
  --action stop \
  --watcher gmail
```

**Restart Individual Watcher:**
```bash
python3 .claude/skills/multi-watcher-runner/scripts/manage_watchers.py \
  --action restart \
  --watcher whatsapp
```

**Stop All Watchers:**
```bash
python3 .claude/skills/multi-watcher-runner/scripts/manage_watchers.py --action stop-all
```

#### Comprehensive Status Display

```bash
python3 .claude/skills/multi-watcher-runner/scripts/manage_watchers.py --action status
```

**Output:**
```
================================================================================
MULTI-WATCHER STATUS (PM2)
================================================================================

📊 Summary:
  Healthy:  3
  Warning:  1
  Offline:  0
  Total:    4

Watcher         | Status     | Memory       | CPU      | Restarts   | Uptime
--------------------------------------------------------------------------------
filesystem      | ✅ healthy | 45.2MB       | 2.1%     | 0          | 2.5h
gmail           | ✅ healthy | 78.3MB       | 5.4%     | 0          | 2.5h
linkedin        | ✅ healthy | 82.1MB       | 3.2%     | 0          | 2.5h
whatsapp        | ⚠️ warning | 125.8MB      | 8.7%     | 2          | 1.2h

================================================================================
```

#### Health Monitoring

```bash
python3 .claude/skills/multi-watcher-runner/scripts/manage_watchers.py --action health
```

**Health Status Levels:**
- ✅ **Healthy**: Process online, memory < 80% limit, restarts < 5
- ⚠️ **Warning**: Memory > 80% limit OR restarts > 5
- 🔴 **Critical**: Process crashing repeatedly
- ⏸️ **Offline**: Process not running

**Automatic Dashboard Updates:**
The PM2 manager automatically updates `Dashboard.md` with watcher status:

```markdown
## 🔍 Watcher Status

- **Gmail**: ✅ HEALTHY (Memory: 78.3MB, CPU: 5.4%, Restarts: 0)
- **Whatsapp**: ⚠️ WARNING (Memory: 125.8MB, CPU: 8.7%, Restarts: 2)
- **Linkedin**: ✅ HEALTHY (Memory: 82.1MB, CPU: 3.2%, Restarts: 0)
- **Filesystem**: ✅ HEALTHY (Memory: 45.2MB, CPU: 2.1%, Restarts: 0)

*Last updated: 2026-02-12 15:30:45*
```

#### Watcher Configurations

| Watcher | Memory Limit | Restart Policy | Check Interval |
|---------|-------------|----------------|----------------|
| Gmail | 100MB | Always | 60s |
| WhatsApp | 150MB | Always | 60s |
| LinkedIn | 100MB | Always | 300s (5min) |
| Filesystem | 50MB | Always | 30s |

#### Advanced PM2 Features

**Memory-Based Auto-Restart:**
- Watchers automatically restart if memory limit exceeded
- Prevents memory leaks from crashing the system

**Exponential Backoff:**
- First restart: Immediate
- Second restart: 3 seconds delay
- Third restart: 6 seconds delay
- Delay doubles each time

**Crash Loop Detection:**
- Threshold: 3 restarts in 5 minutes
- Action: Alert and stop auto-restart
- Recovery: Manual intervention required

#### Direct PM2 Commands

You can also use PM2 directly:

```bash
# List all watcher processes
pm2 list

# Monitor in real-time
pm2 monit

# View logs
pm2 logs watcher-gmail
pm2 logs watcher-whatsapp

# Restart specific watcher
pm2 restart watcher-gmail

# Stop all watchers
pm2 stop all

# Auto-start on system reboot
pm2 startup
pm2 save
```

### Option 2: systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/ai-employee-watchers.service

# Add:
[Unit]
Description=AI Employee Multi-Watcher
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/My_AI_Employee
ExecStart=/usr/bin/uv run python run_watcher.py --watcher all
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable ai-employee-watchers
sudo systemctl start ai-employee-watchers
sudo systemctl status ai-employee-watchers
```

## Architecture

```
run_watcher.py --watcher all
    ↓
MultiWatcherOrchestrator
    ↓
Starts 4 watcher threads:
    ├── GmailWatcher (thread 1)
    ├── LinkedInWatcher (thread 2)
    ├── WhatsAppWatcher (thread 3)
    └── FilesystemWatcher (thread 4)
    ↓
Health check worker (thread 5)
    ↓
Monitors all threads every 30s
    ↓
Auto-restarts failed watchers
    ↓
Logs status updates
```

## Resources

- **Watcher Runner Guide**: `WATCHER_RUNNER_GUIDE.md`
- **Setup Scripts**: `scripts/setup/`
- **Debug Scripts**: `scripts/debug/`
- **Validation**: `scripts/validate/validate_silver_tier.py`

## See Also

- **Bronze Tier**: Use `/watcher-runner-filesystem` for filesystem only
- **Triage**: Use `/needs-action-triage` to process action items
- **Approval**: Use `/approval-workflow-manager` for HITL workflow
- **Execution**: Use `/mcp-executor` to execute approved actions
