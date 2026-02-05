#!/bin/bash
# Check if Twitter credentials are properly configured

echo "=== Twitter Credentials Check ==="
echo ""

cd /mnt/d/hackathon-0/My_AI_Employee

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    exit 1
fi

# Source .env
export $(grep -v '^#' .env | xargs)

# Check each credential
echo "Checking credentials..."
echo ""

if [ -n "$TWITTER_API_KEY" ] && [ "$TWITTER_API_KEY" != "PASTE_YOUR_API_KEY_HERE" ]; then
    echo "✅ API Key: ${TWITTER_API_KEY:0:10}..."
else
    echo "❌ API Key: Missing or not updated"
fi

if [ -n "$TWITTER_API_SECRET" ] && [ "$TWITTER_API_SECRET" != "PASTE_YOUR_API_SECRET_HERE" ]; then
    echo "✅ API Secret: ${TWITTER_API_SECRET:0:10}..."
else
    echo "❌ API Secret: Missing or not updated"
fi

if [ -n "$TWITTER_ACCESS_TOKEN" ] && [ "$TWITTER_ACCESS_TOKEN" != "PASTE_YOUR_ACCESS_TOKEN_HERE" ]; then
    echo "✅ Access Token: ${TWITTER_ACCESS_TOKEN:0:10}..."
else
    echo "❌ Access Token: Missing or not updated"
    echo "   → Generate at: https://console.x.com/ → Keys and tokens → Access Token and Secret"
fi

if [ -n "$TWITTER_ACCESS_TOKEN_SECRET" ] && [ "$TWITTER_ACCESS_TOKEN_SECRET" != "PASTE_YOUR_ACCESS_TOKEN_SECRET_HERE" ]; then
    echo "✅ Access Token Secret: ${TWITTER_ACCESS_TOKEN_SECRET:0:10}..."
else
    echo "❌ Access Token Secret: Missing or not updated"
    echo "   → Generate at: https://console.x.com/ → Keys and tokens → Access Token and Secret"
fi

if [ -n "$TWITTER_BEARER_TOKEN" ]; then
    echo "✅ Bearer Token: ${TWITTER_BEARER_TOKEN:0:10}..."
else
    echo "❌ Bearer Token: Missing"
fi

echo ""

# Test Bearer Token
if [ -n "$TWITTER_BEARER_TOKEN" ]; then
    echo "Testing Bearer Token..."
    RESPONSE=$(curl -s -X GET "https://api.twitter.com/2/users/me" \
        -H "Authorization: Bearer $TWITTER_BEARER_TOKEN")

    if echo "$RESPONSE" | grep -q '"id"'; then
        USERNAME=$(echo "$RESPONSE" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
        echo "✅ Bearer Token works! Logged in as: @$USERNAME"
    else
        echo "❌ Bearer Token test failed"
        echo "Response: $RESPONSE"
    fi
fi

echo ""
echo "=== Summary ==="

# Count how many credentials are set
COUNT=0
[ -n "$TWITTER_API_KEY" ] && [ "$TWITTER_API_KEY" != "PASTE_YOUR_API_KEY_HERE" ] && ((COUNT++))
[ -n "$TWITTER_API_SECRET" ] && [ "$TWITTER_API_SECRET" != "PASTE_YOUR_API_SECRET_HERE" ] && ((COUNT++))
[ -n "$TWITTER_ACCESS_TOKEN" ] && [ "$TWITTER_ACCESS_TOKEN" != "PASTE_YOUR_ACCESS_TOKEN_HERE" ] && ((COUNT++))
[ -n "$TWITTER_ACCESS_TOKEN_SECRET" ] && [ "$TWITTER_ACCESS_TOKEN_SECRET" != "PASTE_YOUR_ACCESS_TOKEN_SECRET_HERE" ] && ((COUNT++))
[ -n "$TWITTER_BEARER_TOKEN" ] && ((COUNT++))

echo "Twitter credentials: $COUNT/5 configured"

if [ $COUNT -eq 5 ]; then
    echo "✅ All Twitter credentials configured!"
    echo "Next: Set up Odoo, Facebook, and Instagram"
else
    echo "⏳ Still need to configure $((5-COUNT)) credential(s)"
    echo "Follow instructions in TWITTER_SETUP_INSTRUCTIONS.md"
fi
