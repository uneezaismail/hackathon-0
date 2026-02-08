#!/usr/bin/env python3
"""
Complete Gold Tier Credentials Checker
Verifies all required credentials for hackathon submission.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


# Load environment variables
load_dotenv()

def check_credentials():
    """Check all Gold tier credentials."""

    print("=" * 70)
    print("GOLD TIER CREDENTIALS CHECK")
    print("=" * 70)
    print()

    results = {}

    # Twitter/X
    print("📱 Twitter/X (API-based)")
    print("-" * 70)
    twitter_creds = {
        "TWITTER_API_KEY": os.getenv("TWITTER_API_KEY"),
        "TWITTER_API_SECRET": os.getenv("TWITTER_API_SECRET"),
        "TWITTER_ACCESS_TOKEN": os.getenv("TWITTER_ACCESS_TOKEN"),
        "TWITTER_ACCESS_TOKEN_SECRET": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        "TWITTER_BEARER_TOKEN": os.getenv("TWITTER_BEARER_TOKEN"),
    }

    twitter_ok = all(v and v != "PASTE_YOUR_TOKEN_HERE" for v in twitter_creds.values())

    for key, value in twitter_creds.items():
        if value and value != "PASTE_YOUR_TOKEN_HERE":
            print(f"  ✅ {key}: {value[:20]}...")
        else:
            print(f"  ❌ {key}: NOT SET")

    results["Twitter"] = twitter_ok
    print()

    # Facebook (Browser Automation)
    print("📘 Facebook (Browser Automation)")
    print("-" * 70)
    fb_email = os.getenv("FACEBOOK_EMAIL")
    fb_password = os.getenv("FACEBOOK_PASSWORD")

    fb_ok = (
        fb_email and fb_email != "your_facebook_email@example.com" and
        fb_password and fb_password != "your_facebook_password"
    )

    if fb_ok:
        print(f"  ✅ FACEBOOK_EMAIL: {fb_email}")
        print(f"  ✅ FACEBOOK_PASSWORD: {'*' * len(fb_password)}")
    else:
        print(f"  ❌ FACEBOOK_EMAIL: {fb_email or 'NOT SET'}")
        print(f"  ❌ FACEBOOK_PASSWORD: {'NOT SET' if not fb_password else 'DEFAULT VALUE'}")

    results["Facebook"] = fb_ok
    print()

    # Instagram (Browser Automation)
    print("📷 Instagram (Browser Automation)")
    print("-" * 70)
    ig_username = os.getenv("INSTAGRAM_USERNAME")
    ig_password = os.getenv("INSTAGRAM_PASSWORD")

    ig_ok = (
        ig_username and ig_username != "your_instagram_username" and
        ig_password and ig_password != "your_instagram_password"
    )

    if ig_ok:
        print(f"  ✅ INSTAGRAM_USERNAME: {ig_username}")
        print(f"  ✅ INSTAGRAM_PASSWORD: {'*' * len(ig_password)}")
    else:
        print(f"  ❌ INSTAGRAM_USERNAME: {ig_username or 'NOT SET'}")
        print(f"  ❌ INSTAGRAM_PASSWORD: {'NOT SET' if not ig_password else 'DEFAULT VALUE'}")

    results["Instagram"] = ig_ok
    print()

    # LinkedIn (Browser Automation - from Silver tier)
    print("💼 LinkedIn (Browser Automation - Silver Tier)")
    print("-" * 70)
    linkedin_email = os.getenv("LINKEDIN_EMAIL")
    linkedin_password = os.getenv("LINKEDIN_PASSWORD")

    linkedin_ok = (
        linkedin_email and linkedin_email != "your_linkedin_email@example.com" and
        linkedin_password and linkedin_password != "your_linkedin_password"
    )

    if linkedin_ok:
        print(f"  ✅ LINKEDIN_EMAIL: {linkedin_email}")
        print(f"  ✅ LINKEDIN_PASSWORD: {'*' * len(linkedin_password)}")
    else:
        print(f"  ⚠️  LINKEDIN_EMAIL: {linkedin_email or 'NOT SET'}")
        print(f"  ⚠️  LINKEDIN_PASSWORD: {'NOT SET' if not linkedin_password else 'DEFAULT VALUE'}")
        print(f"  Note: LinkedIn is optional (Silver tier feature)")

    results["LinkedIn"] = linkedin_ok
    print()

    # Odoo
    print("🏢 Odoo Community (ERP)")
    print("-" * 70)
    odoo_url = os.getenv("ODOO_URL")
    odoo_db = os.getenv("ODOO_DB")
    odoo_username = os.getenv("ODOO_USERNAME")
    odoo_password = os.getenv("ODOO_PASSWORD")

    odoo_ok = all([odoo_url, odoo_db, odoo_username, odoo_password])

    if odoo_ok:
        print(f"  ✅ ODOO_URL: {odoo_url}")
        print(f"  ✅ ODOO_DB: {odoo_db}")
        print(f"  ✅ ODOO_USERNAME: {odoo_username}")
        print(f"  ✅ ODOO_PASSWORD: {'*' * len(odoo_password)}")
    else:
        print(f"  ❌ ODOO_URL: {odoo_url or 'NOT SET'}")
        print(f"  ❌ ODOO_DB: {odoo_db or 'NOT SET'}")
        print(f"  ❌ ODOO_USERNAME: {odoo_username or 'NOT SET'}")
        print(f"  ❌ ODOO_PASSWORD: {'NOT SET' if not odoo_password else 'SET'}")

    results["Odoo"] = odoo_ok
    print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for platform, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {platform}: {'CONFIGURED' if status else 'NOT CONFIGURED'}")

    print()
    print(f"Total: {passed}/{total} platforms configured")
    print()

    # Gold Tier Requirements
    print("=" * 70)
    print("GOLD TIER REQUIREMENTS (from HACKATHON-ZERO.md)")
    print("=" * 70)
    print()
    print("Required:")
    print(f"  {'✅' if results['Odoo'] else '❌'} Odoo Community integration")
    print(f"  {'✅' if any([results['Twitter'], results['Facebook'], results['Instagram']]) else '❌'} At least ONE social media platform")
    print()
    print("Social Media Platforms:")
    print(f"  {'✅' if results['Twitter'] else '❌'} Twitter/X (API-based)")
    print(f"  {'✅' if results['Facebook'] else '❌'} Facebook (Browser automation)")
    print(f"  {'✅' if results['Instagram'] else '❌'} Instagram (Browser automation)")
    print(f"  {'⚠️ ' if results['LinkedIn'] else '❌'} LinkedIn (Optional - Silver tier)")
    print()

    # Check if minimum requirements met
    min_requirements_met = (
        results["Odoo"] and
        any([results["Twitter"], results["Facebook"], results["Instagram"]])
    )

    if min_requirements_met:
        print("🎉 MINIMUM GOLD TIER REQUIREMENTS MET!")
        print()
        print("You have:")
        print("  ✅ Odoo Community (accounting/invoicing)")
        print(f"  ✅ {sum([results['Twitter'], results['Facebook'], results['Instagram']])} social media platform(s)")
        print()
        print("Ready to proceed with testing!")
    else:
        print("⚠️  MINIMUM REQUIREMENTS NOT MET")
        print()
        print("You need:")
        if not results["Odoo"]:
            print("  ❌ Odoo Community credentials")
        if not any([results["Twitter"], results["Facebook"], results["Instagram"]]):
            print("  ❌ At least ONE social media platform (Twitter, Facebook, or Instagram)")

    print("=" * 70)

    return min_requirements_met


if __name__ == "__main__":
    success = check_credentials()
    exit(0 if success else 1)
