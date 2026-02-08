#!/bin/bash
# Complete Gold Tier Startup Script
# This starts the CORRECT architecture with Ralph Wiggum Loop

set -e

echo "========================================================================"
echo "  Gold Tier AI Employee - Complete Startup"
echo "========================================================================"
echo ""

# Set critical environment variables
export MCP_TIMEOUT=60000
export VAULT_ROOT="AI_Employee_Vault"

echo "✓ Environment variables set:"
echo "  MCP_TIMEOUT=$MCP_TIMEOUT"
echo "  VAULT_ROOT=$VAULT_ROOT"
echo ""

# Check if ccr is available
if command -v ccr &> /dev/null; then
    echo "✓ ccr (Claude Code Router) found"
    USE_CCR=true
else
    echo "⚠️  ccr not found, will use 'claude' command"
    echo "   Install ccr for better performance: npm install -g @anthropic/claude-code-router"
    USE_CCR=false
fi
echo ""

# Check if claude is available
if ! command -v claude &> /dev/null && [ "$USE_CCR" = false ]; then
    echo "❌ ERROR: Neither 'ccr' nor 'claude' command found!"
    echo "   Install Claude Code first"
    exit 1
fi

# Ensure vault directories exist
mkdir -p "$VAULT_ROOT"/{Inbox,Needs_Action,Pending_Approval,Approved,Rejected,Done,Logs,Briefings,Archive}
echo "✓ Vault directories created"
echo ""

# Start unified watcher in background
echo "Starting unified watcher..."
uv run python unified_watcher.py > "$VAULT_ROOT/Logs/watcher.log" 2>&1 &
WATCHER_PID=$!
echo "✓ Unified watcher started (PID: $WATCHER_PID)"
echo ""

# Wait a moment for watcher to initialize
sleep 2

# Start orchestrator with Ralph Wiggum Loop
echo "========================================================================"
echo "  Starting Orchestrator (Ralph Wiggum Loop)"
echo "========================================================================"
echo ""
echo "⏳ This will take ~3 minutes to connect all MCPs (first time only)"
echo "   After that, all tasks process instantly!"
echo ""
echo "Press Ctrl+C to stop everything"
echo ""

# Trap Ctrl+C to clean up
trap "echo ''; echo 'Stopping...'; kill $WATCHER_PID 2>/dev/null; exit 0" INT TERM

# Start orchestrator (this blocks)
uv run python orchestrator_fixed.py --mode ralph

# Cleanup on exit
kill $WATCHER_PID 2>/dev/null || true
echo "Stopped"
