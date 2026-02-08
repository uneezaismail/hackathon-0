# Gold Tier AI Employee

A comprehensive AI employee system with autonomous operation, business intelligence, and multi-channel integration. Monitors multiple sources (filesystem, Gmail, WhatsApp, LinkedIn), manages Odoo accounting, automates social media, generates weekly CEO briefings, and operates autonomously with error recovery.

## Overview

The Gold Tier AI Employee is a **production-ready, enterprise-grade** system that:

1. **Perceives** - Monitors filesystem, Gmail, WhatsApp, LinkedIn for new inputs
2. **Reasons** - Triages items, creates plans, routes through approval workflow
3. **Acts** - Executes via MCP servers (Odoo, Facebook, Instagram, Twitter)
4. **Learns** - Generates weekly CEO briefings with business intelligence
5. **Recovers** - Automatic error recovery, component monitoring, graceful degradation

**Tier Progression**:
- **Bronze Tier**: Local filesystem watcher + Obsidian vault (no external actions)
- **Silver Tier**: Multi-channel monitoring (Gmail, WhatsApp, LinkedIn) + MCP execution + HITL approval
- **Gold Tier**: Odoo integration + Social media automation + Autonomous operation + CEO briefing + Error recovery

## Features

### Bronze Tier (Foundation)
- ✅ **Filesystem Watcher**: Monitors drop folder, creates action items
- ✅ **Obsidian Vault Integration**: Memory/GUI for AI employee
- ✅ **Duplicate Prevention**: SHA256-based deduplication
- ✅ **Triage Workflow**: Process items per Company Handbook rules
- ✅ **Dashboard Updates**: Real-time status tracking

### Silver Tier (Multi-Channel)
- ✅ **Gmail Watcher**: Monitor inbox, create email action items
- ✅ **WhatsApp Watcher**: Monitor messages via Playwright
- ✅ **LinkedIn Watcher**: Monitor notifications and messages
- ✅ **MCP Execution**: Execute approved actions via FastMCP servers
- ✅ **HITL Approval**: Human-in-the-loop approval workflow
- ✅ **Audit Logging**: Comprehensive action logging with credential sanitization

### Gold Tier (Enterprise)
- ✅ **Odoo Integration**: Invoice management, payment tracking, expense categorization, financial reporting
- ✅ **Social Media Automation**: Facebook, Instagram, Twitter posting with engagement metrics
- ✅ **Autonomous Operation**: Ralph Wiggum Loop with file movement detection
- ✅ **Business Intelligence**: Weekly CEO briefing with data from all sources
- ✅ **Error Recovery**: Watchdog monitoring, retry logic, graceful degradation
- ✅ **Scheduled Tasks**: Weekly CEO briefing (Sunday 8PM), daily health checks

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a step-by-step guide to get started in 5 minutes.

## Requirements

- **Python**: 3.13+
- **uv**: Modern Python package manager
- **Obsidian**: (Optional) For viewing the vault as a GUI
- **Odoo Community**: (Optional) For accounting integration
- **Social Media Accounts**: (Optional) For Facebook, Instagram, Twitter automation

### Python Dependencies

**Bronze Tier**:
- `watchdog>=6.0.0` - Filesystem monitoring
- `python-frontmatter>=1.1.0` - YAML frontmatter parsing
- `python-dotenv>=1.0.0` - Environment variable management
- `pytest>=9.0.2` - Testing framework

**Silver Tier**:
- `fastmcp>=0.1.0` - MCP server framework
- `playwright>=1.40.0` - Browser automation
- `google-api-python-client>=2.100.0` - Gmail API
- `google-auth-oauthlib>=1.1.0` - OAuth 2.0

**Gold Tier**:
- `odoorpc>=0.9.0` - Odoo Community integration
- `facebook-sdk>=3.1.0` - Facebook Graph API
- `tweepy>=4.14.0` - Twitter API v2
- `psutil>=5.9.0` - Component monitoring
- `keyring>=24.3.0` - Secure credential storage
- `pyyaml>=6.0.1` - YAML parsing
- `python-dateutil>=2.8.2` - Better date handling
- `schedule>=1.2.0` - Job scheduling

## Installation

```bash
# 1. Navigate to project directory
cd My_AI_Employee

# 2. Install all dependencies
uv pip install -e .

# 3. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 4. Set up credentials (secure storage)
python -c "from utils.credentials import store_credential; \
  store_credential('odoo_url', 'https://your-odoo.com'); \
  store_credential('odoo_password', 'your_password')"

# 5. Initialize vault structure
python -c "from vault_ops.vault_manager import ensure_vault_structure; \
  ensure_vault_structure('AI_Employee_Vault')"
```

## Usage

### Complete Gold Tier Workflow

#### Step 1: Start All Components

```bash
# Start filesystem watcher (Bronze tier)
python run_watcher.py &

# Start watchdog (component monitoring)
python watchdog.py &

# Start scheduler (weekly CEO briefing)
python scheduler.py &

# Start orchestrator (approval execution)
python orchestrator.py &
```

#### Step 2: Process Action Items

**Option A: Manual Processing**
```bash
# Use Claude Code with skills
/needs-action-triage "Process all pending items"
```

**Option B: Autonomous Processing (Ralph Wiggum Loop)**
```bash
# Start autonomous processing
python .claude/skills/ralph-wiggum-runner/scripts/start_ralph_loop.py

# Check status
python .claude/skills/ralph-wiggum-runner/scripts/ralph_status.py

# Stop loop
python .claude/skills/ralph-wiggum-runner/scripts/stop_ralph_loop.py
```

#### Step 3: Execute Approved Actions

Actions are automatically executed by orchestrator.py when moved to /Approved/ folder.

#### Step 4: Generate CEO Briefing

**Option A: Scheduled (Automatic)**
- Runs every Sunday at 8:00 PM via scheduler.py

**Option B: Manual**
```bash
# Use Claude Code
/ceo-briefing-generator "Generate weekly CEO briefing"

# Or run directly
python .claude/skills/ceo-briefing-generator/scripts/generate_briefing.py --weekly
```
```
/needs-action-triage
```

**Option B: Natural Language**
```
Process the pending action items
```

Claude will:
1. ✅ Read items from `Needs_Action/`
2. ✅ Apply rules from `Company_Handbook.md`
3. ✅ Create plans in `Plans/` with checkboxes
4. ✅ Update `Dashboard.md` with activity
5. ✅ Archive items to `Done/` with metadata

#### Step 4: View Results

**Check the Plan:**
```bash
cat AI_Employee_Vault/Plans/Plan_*.md
```

**Check the Dashboard:**
```bash
cat AI_Employee_Vault/Dashboard.md
```

**Check Done folder:**
```bash
ls AI_Employee_Vault/Done/
```

**Open in Obsidian (Optional):**
1. Open Obsidian app
2. "Open folder as vault"
3. Select: `My_AI_Employee/AI_Employee_Vault/`

### Testing

```bash
cd /path/to/hackathon-0
PYTHONPATH=. My_AI_Employee/.venv/bin/python -m pytest tests/ -v
```

## Project Structure

```
My_AI_Employee/
├── watchers/          # Filesystem monitoring
├── utils/             # Shared utilities
├── vault_ops/         # Vault operations
├── triage/            # Triage logic
└── AI_Employee_Vault/ # Obsidian vault
```

## Documentation

- [QUICKSTART.md](QUICKSTART.md) - Step-by-step setup guide
- [specs/](../specs/001-bronze-ai-employee/) - Design specifications

## License

MIT License
