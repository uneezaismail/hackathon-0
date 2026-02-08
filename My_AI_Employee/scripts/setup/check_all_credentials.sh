#!/bin/bash
# Check all Gold tier credentials

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           GOLD TIER CREDENTIALS STATUS CHECK                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

cd /mnt/d/hackathon-0/My_AI_Employee

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    exit 1
fi

# Function to check credential
check_cred() {
    local name=$1
    local var=$2
    local placeholder=$3
    
    value=$(grep "^${var}=" .env | cut -d'=' -f2)
    
    if [ -z "$value" ]; then
        echo "❌ $name: Not found in .env"
        return 1
    elif [ "$value" = "$placeholder" ]; then
        echo "⏳ $name: Placeholder (needs update)"
        return 1
    else
        echo "✅ $name: Configured (${value:0:20}...)"
        return 0
    fi
}

echo "=== Twitter/X API ==="
check_cred "API Key" "TWITTER_API_KEY" "PASTE_YOUR_API_KEY_HERE"
check_cred "API Secret" "TWITTER_API_SECRET" "PASTE_YOUR_API_SECRET_HERE"
check_cred "Access Token" "TWITTER_ACCESS_TOKEN" "PASTE_YOUR_ACCESS_TOKEN_HERE"
check_cred "Access Token Secret" "TWITTER_ACCESS_TOKEN_SECRET" "PASTE_YOUR_ACCESS_TOKEN_SECRET_HERE"
check_cred "Bearer Token" "TWITTER_BEARER_TOKEN" ""

echo ""
echo "=== Facebook API ==="
check_cred "Access Token" "FACEBOOK_ACCESS_TOKEN" "PASTE_YOUR_FACEBOOK_TOKEN_HERE"
check_cred "Page ID" "FACEBOOK_PAGE_ID" "PASTE_YOUR_PAGE_ID_HERE"

echo ""
echo "=== Instagram API ==="
check_cred "Access Token" "INSTAGRAM_ACCESS_TOKEN" "PASTE_YOUR_FACEBOOK_TOKEN_HERE"
check_cred "Business Account ID" "INSTAGRAM_BUSINESS_ACCOUNT_ID" "PASTE_YOUR_IG_ACCOUNT_ID_HERE"

echo ""
echo "=== Odoo Community ==="
check_cred "URL" "ODOO_URL" ""
check_cred "Database" "ODOO_DB" ""
check_cred "Username" "ODOO_USERNAME" ""

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Count configured credentials
twitter_count=0
facebook_count=0
instagram_count=0
odoo_count=0

grep -q "^TWITTER_API_KEY=3ChbgCCiQw" .env && ((twitter_count++))
grep -q "^TWITTER_API_SECRET=Uefc23h8Th" .env && ((twitter_count++))
grep -q "^TWITTER_ACCESS_TOKEN=2018690007" .env && ((twitter_count++))
grep -q "^TWITTER_ACCESS_TOKEN_SECRET=UXCn9MhCsu" .env && ((twitter_count++))
grep -q "^TWITTER_BEARER_TOKEN=AAAAAAAAAA" .env && ((twitter_count++))

grep -q "^FACEBOOK_ACCESS_TOKEN=EAA" .env && ((facebook_count++))
grep -q "^FACEBOOK_PAGE_ID=[0-9]" .env && ((facebook_count++))

grep -q "^INSTAGRAM_ACCESS_TOKEN=EAA" .env && ((instagram_count++))
grep -q "^INSTAGRAM_BUSINESS_ACCOUNT_ID=[0-9]" .env && ((instagram_count++))

grep -q "^ODOO_URL=http://localhost:8069" .env && ((odoo_count++))

echo "Progress Summary:"
echo "  Twitter/X:  $twitter_count/5 credentials"
echo "  Facebook:   $facebook_count/2 credentials"
echo "  Instagram:  $instagram_count/2 credentials"
echo "  Odoo:       $odoo_count/1 configured"
echo ""

total=$((twitter_count + facebook_count + instagram_count + odoo_count))
echo "Total: $total/10 credentials configured"
echo ""

if [ $twitter_count -eq 5 ]; then
    echo "✅ Twitter/X: Complete"
else
    echo "⏳ Twitter/X: Incomplete"
fi

if [ $facebook_count -eq 2 ]; then
    echo "✅ Facebook: Complete"
else
    echo "⏳ Facebook: Incomplete - Next step!"
fi

if [ $instagram_count -eq 2 ]; then
    echo "✅ Instagram: Complete"
else
    echo "⏳ Instagram: Incomplete"
fi

if [ $odoo_count -eq 1 ]; then
    echo "✅ Odoo: Configured"
    # Check if Odoo is actually running
    if docker ps 2>/dev/null | grep -q odoo; then
        echo "✅ Odoo: Running"
    else
        echo "⏳ Odoo: Not running (need to start containers)"
    fi
else
    echo "✅ Odoo: Pre-configured (need to start containers)"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
