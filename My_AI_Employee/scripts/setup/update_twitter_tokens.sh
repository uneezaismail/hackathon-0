#!/bin/bash
# Twitter Token Update Script

echo "Twitter Token Update Helper"
echo "============================"
echo ""
echo "This script will help you update your Twitter tokens in .env"
echo ""

# Backup .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backed up .env file"
echo ""

echo "Please paste your NEW Access Token (from Twitter Developer Portal):"
read -r NEW_ACCESS_TOKEN

echo ""
echo "Please paste your NEW Access Token Secret:"
read -r NEW_ACCESS_TOKEN_SECRET

echo ""
echo "Updating .env file..."

# Update tokens
sed -i "s|TWITTER_ACCESS_TOKEN=.*|TWITTER_ACCESS_TOKEN=$NEW_ACCESS_TOKEN|" .env
sed -i "s|TWITTER_ACCESS_TOKEN_SECRET=.*|TWITTER_ACCESS_TOKEN_SECRET=$NEW_ACCESS_TOKEN_SECRET|" .env

echo "✅ Updated .env file"
echo ""
echo "Current Twitter credentials:"
grep "TWITTER_" .env | grep -v "SECRET\|TOKEN" | head -3
echo "TWITTER_ACCESS_TOKEN=${NEW_ACCESS_TOKEN:0:30}..."
echo "TWITTER_ACCESS_TOKEN_SECRET=${NEW_ACCESS_TOKEN_SECRET:0:30}..."
echo ""
echo "✅ Done! Now test with: uv run python test_twitter.py"

