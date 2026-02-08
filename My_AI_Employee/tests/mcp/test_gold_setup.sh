#!/bin/bash
# Quick Test Script - Verify Gold Tier Setup

echo "========================================================================"
echo "  Gold Tier AI Employee - Quick Test"
echo "========================================================================"
echo ""

cd /mnt/d/hackathon-0/My_AI_Employee

# Check files exist
echo "Checking files..."
files=(
    "orchestrator_fixed.py"
    "unified_watcher.py"
    "start_gold_tier.sh"
    "mcp_servers/twitter_web_mcp.py"
    "mcp_servers/facebook_web_mcp.py"
    "mcp_servers/instagram_web_mcp.py"
    "mcp_servers/odoo_mcp.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (MISSING)"
    fi
done
echo ""

# Check commands
echo "Checking commands..."
if command -v claude &> /dev/null; then
    echo "  ✅ claude command found"
else
    echo "  ❌ claude command not found"
fi

if command -v ccr &> /dev/null; then
    echo "  ✅ ccr command found"
else
    echo "  ⚠️  ccr command not found (will use claude)"
fi

if command -v uv &> /dev/null; then
    echo "  ✅ uv command found"
else
    echo "  ❌ uv command not found"
fi
echo ""

# Check vault structure
echo "Checking vault structure..."
vault_dirs=(
    "AI_Employee_Vault/Inbox"
    "AI_Employee_Vault/Needs_Action"
    "AI_Employee_Vault/Pending_Approval"
    "AI_Employee_Vault/Approved"
    "AI_Employee_Vault/Done"
    "AI_Employee_Vault/Logs"
)

for dir in "${vault_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir"
    else
        echo "  ⚠️  $dir (will be created)"
        mkdir -p "$dir"
    fi
done
echo ""

# Check MCP tests
echo "Checking MCP tests..."
if [ -f "tests/integration/test_all_mcps.sh" ]; then
    echo "  ✅ MCP test script exists"
    echo "  Running MCP tests..."
    echo ""
    ./tests/integration/test_all_mcps.sh
else
    echo "  ❌ MCP test script not found"
fi
echo ""

# Summary
echo "========================================================================"
echo "  Test Complete"
echo "========================================================================"
echo ""
echo "Next steps:"
echo "  1. Set environment: export MCP_TIMEOUT=60000"
echo "  2. Start system: ./start_gold_tier.sh"
echo "  3. Wait 3 minutes for MCPs to connect"
echo "  4. Create test file in AI_Employee_Vault/Inbox/"
echo "  5. Watch it work!"
echo ""
