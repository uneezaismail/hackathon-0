#!/bin/bash
# Gold Tier Testing Guide - Facebook, Instagram, Odoo
# Run this to test your complete Gold Tier implementation

cd /mnt/d/hackathon-0/My_AI_Employee

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         GOLD TIER TESTING - COMPLETE GUIDE                   ║"
echo "╔══════════════════════════════════════════════════════════════╗"
echo ""

# Check MCP servers
echo "Checking MCP servers..."
MCP_COUNT=$(ps aux | grep -E "(odoo_mcp|facebook_mcp|instagram_mcp|email_mcp)" | grep -v grep | wc -l)
if [ $MCP_COUNT -ge 4 ]; then
    echo "✅ MCP Servers: $MCP_COUNT processes running"
    ps aux | grep -E "(odoo_mcp|facebook_mcp|instagram_mcp|email_mcp)" | grep -v grep | awk '{print "   -", $NF}' | sed 's|.*/||'
else
    echo "⚠️  MCP Servers: Only $MCP_COUNT running (expected 4+)"
    echo "   Claude will auto-start them when needed"
fi
echo ""

# Check pending items
echo "Checking pending items..."
PENDING=$(ls -1 AI_Employee_Vault/Needs_Action/*.md 2>/dev/null | wc -l)
echo "📋 Pending items in /Needs_Action/: $PENDING"
if [ $PENDING -gt 0 ]; then
    ls -1 AI_Employee_Vault/Needs_Action/*.md | while read file; do
        basename "$file"
    done | nl
fi
echo ""

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    TESTING SETUP                             ║"
echo "╔══════════════════════════════════════════════════════════════╗"
echo ""

cat << 'EOF'
You will test these components:
  ✅ Facebook MCP (post to Facebook Page)
  ✅ Instagram MCP (post to Instagram)
  ✅ Odoo MCP (create invoices, expenses)
  ✅ Email MCP (send emails)
  ✅ Filesystem watcher (monitor drop folder)
  ✅ Gmail watcher (monitor Gmail inbox)

Skipped (Playwright issues):
  ❌ WhatsApp watcher (not needed for testing)
  ❌ LinkedIn watcher (not needed for testing)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TERMINAL 1: Start Watchers
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Command:
  uv run python run_watcher.py --watcher filesystem,gmail

What this does:
  - Monitors drop folder for new files
  - Monitors Gmail for new emails
  - Creates action items in /Needs_Action/

Leave this terminal running.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TERMINAL 2: Start Claude with Ralph Loop
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Command:
  claude

Then type:
  Start the Ralph Wiggum Loop to autonomously process all tasks.

  Process items from /Needs_Action/ using /needs-action-triage skill.
  Create approval requests in /Pending_Approval/.
  Execute approved items from /Approved/ using /mcp-executor skill.

  Use these MCP tools:
  - odoo-mcp: create_invoice, send_invoice, create_expense
  - facebook-mcp: post_to_facebook
  - instagram-mcp: post_to_instagram
  - email-mcp: send_email

  Continue until all items are processed.

What this does:
  - Connects to all MCP servers (10-20 seconds)
  - Processes files automatically
  - Creates approval requests
  - Executes approved actions
  - Runs continuously

Leave this terminal running.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TERMINAL 3: Open Obsidian
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Command:
  obsidian AI_Employee_Vault/

What to do:
  1. Navigate to /Pending_Approval/
  2. Review approval requests
  3. Edit YAML: approval_status: approved
  4. Move approved files to /Approved/
  5. Claude will detect and execute automatically

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEST SCENARIOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Test 1: Facebook Post (READY NOW)
──────────────────────────────────
File: AI_Employee_Vault/Needs_Action/20260205_100100_facebook_service_announcement.md
Status: Approval request already created!

Steps:
  1. Open Obsidian
  2. Go to /Pending_Approval/20260205_100100_facebook_approval.md
  3. Review the post content
  4. Edit YAML:
     approval_status: approved
     approved_by: Your Name
     approved_at: 2026-02-08T05:00:00Z
  5. Move file to /Approved/
  6. Claude will detect (5-10 seconds)
  7. Claude posts to Facebook via facebook-mcp ✅
  8. Check /Done/ for results

Expected Result:
  ✅ Post published to Facebook Page
  ✅ Engagement tracking enabled
  ✅ Audit log created

──────────────────────────────────

Test 2: Instagram Post (READY NOW)
──────────────────────────────────
File: AI_Employee_Vault/Needs_Action/20260205_100200_instagram_behind_scenes.md

Steps:
  1. Ralph Loop will detect this file
  2. Claude creates approval request
  3. You approve in Obsidian
  4. Claude posts to Instagram via instagram-mcp ✅

Expected Result:
  ✅ Post published to Instagram
  ✅ Caption and hashtags included
  ✅ Audit log created

──────────────────────────────────

Test 3: Odoo Invoice (READY NOW)
──────────────────────────────────
File: AI_Employee_Vault/Needs_Action/20260205_100400_odoo_invoice_techstart.md

Steps:
  1. Ralph Loop will detect this file
  2. Claude creates approval request
  3. You approve in Obsidian
  4. Claude creates invoice via odoo-mcp.create_invoice() ✅
  5. Claude sends invoice via odoo-mcp.send_invoice() ✅

Expected Result:
  ✅ Invoice INV/2026/XXXX created in Odoo
  ✅ Invoice emailed to client
  ✅ Audit log created

──────────────────────────────────

Test 4: Filesystem → Odoo Expense
──────────────────────────────────
Create a test file:
  echo "Office supplies receipt - $45" > ~/Desktop/AI_Drop/receipt.txt

Steps:
  1. Filesystem watcher detects file (< 1 second)
  2. Creates FILE_receipt.md in /Needs_Action/
  3. Ralph Loop processes it
  4. Claude creates approval request
  5. You approve in Obsidian
  6. Claude creates expense via odoo-mcp.create_expense() ✅

Expected Result:
  ✅ Expense EXP/2026/XXXX created in Odoo
  ✅ Receipt attached
  ✅ Audit log created

──────────────────────────────────

Test 5: Gmail → Email Reply
──────────────────────────────────
Send yourself an email:
  Subject: "Test: Need project update"
  Body: "Can you send me the latest project status?"

Steps:
  1. Gmail watcher detects email (within 2 minutes)
  2. Creates EMAIL_*.md in /Needs_Action/
  3. Ralph Loop processes it
  4. Claude creates approval request
  5. You approve in Obsidian
  6. Claude sends reply via email-mcp.send_email() ✅

Expected Result:
  ✅ Reply email sent
  ✅ Professional tone
  ✅ Audit log created

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MONITORING PROGRESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Check pending items:
  ls -la AI_Employee_Vault/Needs_Action/

Check approval requests:
  ls -la AI_Employee_Vault/Pending_Approval/

Check approved items:
  ls -la AI_Employee_Vault/Approved/

Check completed items:
  ls -la AI_Employee_Vault/Done/

Check audit logs:
  tail -f AI_Employee_Vault/Logs/$(date +%Y-%m-%d).jsonl

Check Dashboard:
  cat AI_Employee_Vault/Dashboard.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If MCP servers not connecting:
  - Check: ps aux | grep mcp
  - Restart Claude (it will auto-start MCP servers)

If files not being processed:
  - Check Ralph Loop is running in Terminal 2
  - Check files exist in /Needs_Action/
  - Check Claude output for errors

If approvals not being detected:
  - Ensure file is moved to /Approved/ (not just edited)
  - Check YAML frontmatter is correct
  - Wait 5-10 seconds for Ralph Loop to detect

If MCP execution fails:
  - Check MCP server logs
  - Verify credentials are configured
  - Check network connectivity

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What you're testing:
  ✅ Complete Gold Tier autonomous workflow
  ✅ Filesystem watcher (Bronze tier)
  ✅ Gmail watcher (Silver tier)
  ✅ Facebook MCP (Gold tier)
  ✅ Instagram MCP (Gold tier)
  ✅ Odoo MCP (Gold tier)
  ✅ Email MCP (Silver tier)
  ✅ Ralph Wiggum Loop (Gold tier)
  ✅ Human-in-the-loop approval workflow
  ✅ Audit logging

What you're skipping:
  ❌ WhatsApp watcher (Playwright issues)
  ❌ LinkedIn watcher (Playwright issues)
  ❌ Twitter MCP (not needed for demo)

This is a COMPLETE Gold Tier demonstration!

EOF

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    READY TO START                            ║"
echo "╔══════════════════════════════════════════════════════════════╗"
echo ""
echo "Next steps:"
echo "  1. Open Terminal 1: uv run python run_watcher.py --watcher filesystem,gmail"
echo "  2. Open Terminal 2: claude (then start Ralph Loop)"
echo "  3. Open Terminal 3: obsidian AI_Employee_Vault/"
echo "  4. Start testing!"
echo ""
