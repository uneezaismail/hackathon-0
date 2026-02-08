#!/bin/bash
# Quick script to update Twitter credentials in .env

echo "=== Twitter Credential Update Helper ==="
echo ""
echo "Current .env status:"
cd /mnt/d/hackathon-0/My_AI_Employee

if grep -q "TWITTER_ACCESS_TOKEN=PASTE_YOUR_ACCESS_TOKEN_HERE" .env; then
    echo "❌ Access Token: Not updated yet"
else
    echo "✅ Access Token: Updated"
fi

if grep -q "TWITTER_ACCESS_TOKEN_SECRET=PASTE_YOUR_ACCESS_TOKEN_SECRET_HERE" .env; then
    echo "❌ Access Token Secret: Not updated yet"
else
    echo "✅ Access Token Secret: Updated"
fi

echo ""
echo "To update:"
echo "1. Open .env file: nano .env"
echo "2. Find the Twitter section at the bottom"
echo "3. Replace PASTE_YOUR_ACCESS_TOKEN_HERE with your actual token"
echo "4. Replace PASTE_YOUR_ACCESS_TOKEN_SECRET_HERE with your actual secret"
echo "5. Save (Ctrl+O, Enter) and exit (Ctrl+X)"
echo ""
echo "After updating, run: ./check_twitter_credentials.sh"
