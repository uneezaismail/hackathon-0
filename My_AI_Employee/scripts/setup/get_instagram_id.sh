#!/bin/bash
# Get Instagram Business Account ID

echo "=== Instagram Business Account ID Finder ==="
echo ""

# Read Facebook credentials from .env
source .env

if [ -z "$FACEBOOK_ACCESS_TOKEN" ] || [ "$FACEBOOK_ACCESS_TOKEN" = "PASTE_YOUR_FACEBOOK_TOKEN_HERE" ]; then
    echo "❌ Facebook Access Token not configured in .env"
    echo ""
    echo "Please update .env file with your Facebook Access Token first:"
    echo "  nano .env"
    echo "  Find: FACEBOOK_ACCESS_TOKEN=PASTE_YOUR_FACEBOOK_TOKEN_HERE"
    echo "  Replace with your actual token"
    exit 1
fi

if [ -z "$FACEBOOK_PAGE_ID" ] || [ "$FACEBOOK_PAGE_ID" = "PASTE_YOUR_PAGE_ID_HERE" ]; then
    echo "❌ Facebook Page ID not configured in .env"
    echo ""
    echo "Please update .env file with your Facebook Page ID first:"
    echo "  nano .env"
    echo "  Find: FACEBOOK_PAGE_ID=PASTE_YOUR_PAGE_ID_HERE"
    echo "  Replace with your actual page ID"
    exit 1
fi

echo "Using Facebook Page ID: $FACEBOOK_PAGE_ID"
echo "Fetching Instagram Business Account..."
echo ""

# Call Facebook Graph API
RESPONSE=$(curl -s "https://graph.facebook.com/v19.0/$FACEBOOK_PAGE_ID?fields=instagram_business_account&access_token=$FACEBOOK_ACCESS_TOKEN")

# Check if successful
if echo "$RESPONSE" | grep -q "instagram_business_account"; then
    IG_ID=$(echo "$RESPONSE" | grep -o '"id":"[0-9]*"' | head -1 | cut -d'"' -f4)
    
    if [ -n "$IG_ID" ]; then
        echo "✅ Instagram Business Account ID found!"
        echo ""
        echo "Instagram Business Account ID: $IG_ID"
        echo ""
        echo "Add this to your .env file:"
        echo "  INSTAGRAM_BUSINESS_ACCOUNT_ID=$IG_ID"
        echo ""
        
        # Test the Instagram account
        echo "Testing Instagram account..."
        IG_INFO=$(curl -s "https://graph.facebook.com/v19.0/$IG_ID?fields=username,followers_count&access_token=$FACEBOOK_ACCESS_TOKEN")
        
        if echo "$IG_INFO" | grep -q "username"; then
            USERNAME=$(echo "$IG_INFO" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
            FOLLOWERS=$(echo "$IG_INFO" | grep -o '"followers_count":[0-9]*' | cut -d':' -f2)
            echo "✅ Instagram account verified!"
            echo "   Username: @$USERNAME"
            echo "   Followers: $FOLLOWERS"
        fi
    else
        echo "❌ Could not extract Instagram Business Account ID"
        echo "Response: $RESPONSE"
    fi
else
    echo "❌ Instagram Business Account not found"
    echo ""
    echo "Possible reasons:"
    echo "1. Instagram account not converted to Business Account"
    echo "2. Instagram not connected to Facebook Page"
    echo "3. Wrong Facebook Page ID"
    echo ""
    echo "Response from Facebook:"
    echo "$RESPONSE"
    echo ""
    echo "Steps to fix:"
    echo "1. Open Instagram app"
    echo "2. Go to Settings → Account type and tools"
    echo "3. Switch to Professional Account → Business"
    echo "4. Go to Settings → Account Center → Add Facebook Page"
fi
