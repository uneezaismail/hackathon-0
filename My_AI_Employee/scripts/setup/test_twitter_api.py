#!/usr/bin/env python3
"""
Test Twitter API credentials
"""

import os
from dotenv import load_dotenv
import tweepy

load_dotenv()

print("=" * 60)
print("Testing Twitter API Credentials")
print("=" * 60)
print()

# Get credentials
api_key = os.getenv("TWITTER_API_KEY")
api_secret = os.getenv("TWITTER_API_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

print("Checking credentials...")
print(f"API Key: {api_key[:10]}..." if api_key else "API Key: NOT SET")
print(f"Bearer Token: {bearer_token[:20]}..." if bearer_token else "Bearer Token: NOT SET")
print()

if not all([api_key, api_secret, access_token, access_token_secret]):
    print("❌ Missing Twitter API credentials in .env")
    exit(1)

try:
    # Test API v2 client
    print("Testing Twitter API v2 connection...")
    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    # Get authenticated user info
    me = client.get_me()

    if me.data:
        print(f"✅ Successfully authenticated!")
        print(f"   Username: @{me.data.username}")
        print(f"   Name: {me.data.name}")
        print(f"   User ID: {me.data.id}")
        print()
        print("=" * 60)
        print("Twitter API is working! You can use twitter_mcp.py")
        print("=" * 60)
    else:
        print("❌ Authentication failed - no user data returned")
        exit(1)

except tweepy.errors.Unauthorized as e:
    print(f"❌ Unauthorized: {e}")
    print("   Your API credentials may be invalid or expired")
    exit(1)
except tweepy.errors.Forbidden as e:
    print(f"❌ Forbidden: {e}")
    print("   Your app may not have the required permissions")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
