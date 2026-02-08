#!/bin/bash
# Gold Tier AI Employee - Complete Startup Guide
# This shows EXACTLY what runs where and how Claude is invoked

echo "=========================================="
echo "Gold Tier AI Employee - Startup Sequence"
echo "=========================================="
echo ""

# Check current directory
if [ ! -d "AI_Employee_Vault" ]; then
    echo "❌ Error: AI_Employee_Vault not found"
    echo "   Run this script from: /mnt/d/hackathon-0/My_AI_Employee"
    exit 1
fi

echo "✓ Vault found: AI_Employee_Vault/"
echo ""

# Check pending items
PENDING=$(ls -1 AI_Employee_Vault/Needs_Action/*.md 2>/dev/null | wc -l)
echo "📋 Current status:"
echo "   - Pending items in /Needs_Action/: $PENDING"
echo ""

# Check if MCP servers are running
MCP_COUNT=$(ps aux | grep -E "(odoo_mcp|twitter_web_mcp|facebook_web_mcp|email_mcp)" | grep -v grep | wc -l)
if [ $MCP_COUNT -gt 0 ]; then
    echo "✓ MCP servers running: $MCP_COUNT processes"
else
    echo "⚠ MCP servers not running (Claude will start them)"
fi
echo ""

echo "=========================================="
echo "GOLD TIER ARCHITECTURE - HOW IT WORKS"
echo "=========================================="
echo ""

cat << 'EOF'
┌─────────────────────────────────────────────────────────────┐
│ TERMINAL 1: Watchers (Input Sensors)                       │
│ Command: uv run python run_watcher.py --watcher all        │
│                                                             │
│ What runs:                                                  │
│   - gmail_watcher.py (monitors Gmail)                      │
│   - whatsapp_watcher.py (monitors WhatsApp Web)            │
│   - linkedin_watcher.py (monitors LinkedIn)                │
│   - filesystem_watcher.py (monitors drop folder)           │
│                                                             │
│ What they do:                                               │
│   - Detect new emails/messages/files                       │
│   - Create .md files in /Needs_Action/                     │
│   - DO NOT trigger Claude                                  │
│   - Run forever in THIS terminal                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ TERMINAL 2: Claude Code with Ralph Loop (Autonomous)       │
│ Command: claude                                             │
│                                                             │
│ What happens:                                               │
│   1. Claude starts in THIS terminal (interactive)          │
│   2. Connects to MCP servers (10-20 seconds)               │
│   3. You type: "Start Ralph Wiggum Loop"                   │
│   4. Claude begins autonomous processing:                  │
│      - Checks /Needs_Action/ every 5-10 seconds            │
│      - Processes new files with skills                     │
│      - Creates approval requests in /Pending_Approval/     │
│      - Executes approved items from /Approved/             │
│      - Moves completed to /Done/                           │
│   5. Stop hook prevents exit                               │
│   6. Runs forever in THIS terminal                         │
│                                                             │
│ NO NEW TERMINALS OPENED                                     │
│ Claude runs as a process in Terminal 2                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ TERMINAL 3: Obsidian (Human Oversight)                     │
│ Command: obsidian AI_Employee_Vault/                       │
│                                                             │
│ What you do:                                                │
│   1. Open Obsidian vault                                   │
│   2. Navigate to /Pending_Approval/                        │
│   3. Review approval requests                              │
│   4. Edit YAML frontmatter:                                │
│      approval_status: approved                             │
│   5. MOVE file to /Approved/ folder                        │
│   6. Claude detects moved file and executes                │
│                                                             │
│ This is what your instructor meant:                        │
│ "Only move files, Claude will be invoked"                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ BACKGROUND: MCP Servers (Started by Claude)                │
│ No terminal needed - Claude manages these                  │
│                                                             │
│ What runs:                                                  │
│   - odoo_mcp.py (Odoo accounting)                          │
│   - email_mcp.py (Gmail sending)                           │
│   - facebook_mcp.py (Facebook posting)                     │
│   - instagram_mcp.py (Instagram posting)                   │
│   - twitter_web_mcp.py (Twitter posting)                   │
│                                                             │
│ These are PERSISTENT processes                             │
│ Claude connects to them (not subprocess)                   │
└─────────────────────────────────────────────────────────────┘

EOF

echo ""
echo "=========================================="
echo "ANSWERING YOUR QUESTIONS"
echo "=========================================="
echo ""

cat << 'EOF'
Q1: "Does Claude start in a new terminal?"
A1: NO. Claude runs in Terminal 2 where you start it.
    - You type: claude
    - Claude starts in THAT terminal
    - No new terminal windows open
    - Claude stays running in that terminal

Q2: "Or no terminal?"
A2: Claude DOES use a terminal (Terminal 2), but:
    - It's the terminal YOU opened
    - Not a new terminal that pops up
    - It's an interactive session in your terminal

Q3: "Watchers vs Orchestrator - what's the difference?"
A3:
    WATCHERS = Input sensors (create files)
      - gmail_watcher.py → Creates EMAIL_*.md in /Needs_Action/
      - whatsapp_watcher.py → Creates WHATSAPP_*.md
      - linkedin_watcher.py → Creates LINKEDIN_*.md
      - filesystem_watcher.py → Creates FILE_*.md
      - DO NOT trigger Claude
      - Just create files and continue monitoring

    ORCHESTRATOR = Automation glue (triggers Claude)
      - Monitors /Needs_Action/ folder
      - When new file appears → Triggers Claude
      - Two approaches:
        A) Subprocess: New Claude for each file (slow)
        B) Ralph Loop: One Claude, continuous (fast)

    GOLD TIER USES: Ralph Loop (no orchestrator needed)
      - Claude checks /Needs_Action/ itself
      - No separate orchestrator process
      - More efficient

Q4: "What about Facebook/Instagram/Twitter?"
A4: These are OUTPUT (MCP servers), not INPUT (watchers)
    - No Facebook watcher (not monitoring Facebook)
    - No Instagram watcher (not monitoring Instagram)
    - No Twitter watcher (not monitoring Twitter)

    Instead:
    - You create: /Needs_Action/post-to-facebook.md
    - Claude reads it
    - Claude uses facebook-mcp to POST
    - Done

    Gold tier requirement: "POST messages" not "monitor messages"

Q5: "What is watchdog for?"
A5: Watchdog is a Python library for filesystem monitoring
    - Used by: filesystem_watcher.py
    - Purpose: Detect when files are created in drop folder
    - Instead of checking every 10 seconds (polling)
    - Watchdog detects INSTANTLY (event-driven)

    Example:
      You drop file in ~/Desktop/AI_Drop/
      → Watchdog detects immediately
      → Creates FILE_*.md in /Needs_Action/
      → Claude processes it

Q6: "Gmail flow - same pattern?"
A6: YES, exactly the same:
    1. gmail_watcher.py monitors Gmail API
    2. New email arrives
    3. Watcher creates EMAIL_*.md in /Needs_Action/
    4. Claude detects new file (Ralph Loop checks every 5-10s)
    5. Claude processes email
    6. Claude creates approval request
    7. You move file to /Approved/
    8. Claude detects moved file
    9. Claude uses email-mcp to send reply
    10. Done

Q7: "Sir said we only move files, Claude will be invoked?"
A7: YES, this is the key insight:

    YOUR ONLY MANUAL ACTION:
      - Move files from /Pending_Approval/ to /Approved/
      - That's it!

    EVERYTHING ELSE IS AUTOMATIC:
      - Watchers create files (automatic)
      - Claude detects files (automatic)
      - Claude processes files (automatic)
      - Claude creates approval requests (automatic)
      - Claude detects your approval (automatic)
      - Claude executes actions (automatic)
      - Claude logs everything (automatic)

    You just move files in Obsidian. That's the "human-in-the-loop".

EOF

echo ""
echo "=========================================="
echo "READY TO START?"
echo "=========================================="
echo ""
echo "Follow these steps:"
echo ""
echo "1. Open Terminal 1 (Watchers):"
echo "   cd /mnt/d/hackathon-0/My_AI_Employee"
echo "   uv run python run_watcher.py --watcher all"
echo ""
echo "2. Open Terminal 2 (Claude with Ralph Loop):"
echo "   cd /mnt/d/hackathon-0/My_AI_Employee"
echo "   claude"
echo "   # Then type: Start Ralph Wiggum Loop to process all tasks"
echo ""
echo "3. Open Terminal 3 (Obsidian):"
echo "   obsidian AI_Employee_Vault/"
echo "   # Review /Pending_Approval/, move files to /Approved/"
echo ""
echo "4. Test it:"
echo "   # Drop a file in your watch folder"
echo "   # Or send yourself a test email"
echo "   # Watch Claude process it automatically"
echo ""
echo "=========================================="
