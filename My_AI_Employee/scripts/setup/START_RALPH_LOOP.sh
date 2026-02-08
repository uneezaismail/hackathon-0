#!/bin/bash
# Start Ralph Wiggum Loop for Gold Tier AI Employee
# This script starts Claude Code in interactive mode and triggers the Ralph Loop

echo "=========================================="
echo "Starting Gold Tier AI Employee"
echo "Ralph Wiggum Loop - Autonomous Processing"
echo "=========================================="
echo ""

# Check if MCP servers are running
echo "Checking MCP servers..."
if ps aux | grep -E "(odoo_mcp|twitter_web_mcp|facebook_web_mcp|email_mcp)" | grep -v grep > /dev/null; then
    echo "✓ MCP servers are running"
else
    echo "⚠ MCP servers not detected. Claude Code will start them automatically."
fi
echo ""

# Check vault structure
echo "Checking Obsidian vault..."
if [ -d "AI_Employee_Vault/Needs_Action" ]; then
    PENDING_COUNT=$(ls -1 AI_Employee_Vault/Needs_Action/*.md 2>/dev/null | wc -l)
    echo "✓ Vault found: $PENDING_COUNT items in Needs_Action/"
else
    echo "✗ Vault not found at AI_Employee_Vault/"
    exit 1
fi
echo ""

# Start Claude Code with Ralph Loop prompt
echo "Starting Claude Code with Ralph Wiggum Loop..."
echo ""
echo "Claude will:"
echo "  1. Connect to MCP servers (10-20 seconds)"
echo "  2. Process all items in /Needs_Action/"
echo "  3. Route for approval or auto-execute"
echo "  4. Continue autonomously until all done"
echo ""
echo "Press Ctrl+C to stop the loop"
echo ""
echo "=========================================="
echo ""

# Start Claude Code in interactive mode
# The prompt will trigger the Ralph Wiggum Loop
claude << 'EOF'
Start the Ralph Wiggum Loop to autonomously process all tasks in the AI Employee Vault.

Your mission:
1. Process all items in /Needs_Action/ using the /needs-action-triage skill
2. For each item:
   - Analyze according to Company_Handbook.md rules
   - Create execution plan
   - Route to /Pending_Approval/ if human approval needed (financial > $100, social media, external comms)
   - Route to /Approved/ if auto-approved (low-risk, internal, < $100)
3. Monitor /Pending_Approval/ for human approvals (check every 5-10 seconds)
4. Execute approved items using /mcp-executor skill with appropriate MCP tools:
   - Odoo: create_invoice, send_invoice, record_payment, create_expense
   - Social media: post_to_facebook, post_to_instagram, post_tweet
   - Email: send_email
5. Log all actions with /audit-logger skill
6. Move completed items to /Done/
7. Update Dashboard.md with progress
8. Continue until all items are processed

IMPORTANT: The stop hook will prevent you from exiting. Keep processing until explicitly told to stop.

Begin now.
EOF
