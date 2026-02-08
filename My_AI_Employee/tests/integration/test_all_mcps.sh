#!/bin/bash
# Test All MCPs - Quick validation script (Updated with LinkedIn Web MCP)

echo "========================================================================"
echo "                    TESTING ALL GOLD TIER MCPs"
echo "========================================================================"
echo ""

cd /mnt/d/hackathon-0/My_AI_Employee

PASSED=0
FAILED=0

# Test 1: Twitter Web MCP
echo "1. Testing Twitter Web MCP..."
if uv run python tests/integration/test_mcp_twitter.py > /tmp/twitter_test.log 2>&1; then
    echo "   ✅ Twitter Web MCP: PASSED"
    ((PASSED++))
else
    echo "   ❌ Twitter Web MCP: FAILED (see /tmp/twitter_test.log)"
    ((FAILED++))
fi
echo ""

# Test 2: Facebook Web MCP
echo "2. Testing Facebook Web MCP..."
if uv run python tests/integration/test_mcp_facebook.py > /tmp/facebook_test.log 2>&1; then
    echo "   ✅ Facebook Web MCP: PASSED"
    ((PASSED++))
else
    echo "   ❌ Facebook Web MCP: FAILED (see /tmp/facebook_test.log)"
    ((FAILED++))
fi
echo ""

# Test 3: Instagram Web MCP
echo "3. Testing Instagram Web MCP..."
if uv run python tests/integration/test_mcp_instagram.py > /tmp/instagram_test.log 2>&1; then
    echo "   ✅ Instagram Web MCP: PASSED"
    ((PASSED++))
else
    echo "   ❌ Instagram Web MCP: FAILED (see /tmp/instagram_test.log)"
    ((FAILED++))
fi
echo ""

# Test 4: LinkedIn Web MCP (NEW - FREE browser automation)
echo "4. Testing LinkedIn Web MCP..."
if uv run python tests/integration/test_mcp_linkedin_web.py > /tmp/linkedin_test.log 2>&1; then
    echo "   ✅ LinkedIn Web MCP: PASSED"
    ((PASSED++))
else
    echo "   ❌ LinkedIn Web MCP: FAILED (see /tmp/linkedin_test.log)"
    ((FAILED++))
fi
echo ""

# Test 5: Odoo MCP
echo "5. Testing Odoo MCP..."
if uv run python tests/integration/test_mcp_odoo.py > /tmp/odoo_test.log 2>&1; then
    echo "   ✅ Odoo MCP: PASSED"
    ((PASSED++))
else
    echo "   ❌ Odoo MCP: FAILED (see /tmp/odoo_test.log)"
    ((FAILED++))
fi
echo ""

# Summary
echo "========================================================================"
echo "                           TEST SUMMARY"
echo "========================================================================"
echo ""
echo "Passed: $PASSED/5"
echo "Failed: $FAILED/5"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 ALL MCPs PASSED!"
    echo ""
    echo "Next steps:"
    echo "1. Add MCPs to Claude Desktop config"
    echo "2. Restart Claude Desktop"
    echo "3. Test in Claude Desktop chat"
    echo ""
else
    echo "⚠️  Some MCPs failed. Check logs in /tmp/"
    echo ""
    echo "Common issues:"
    echo "- Browser MCPs: Expected to fail in WSL (no GUI)"
    echo "- Odoo MCP: Check if Docker is running"
    echo "- LinkedIn Web MCP: Session may need login"
    echo ""
fi

echo "========================================================================"
