#!/usr/bin/env python3
"""
Engagement Metrics Retrieval Workflow

Retrieves and aggregates engagement metrics from Facebook, Instagram, and Twitter
for weekly CEO briefing integration.

Usage:
    python get_engagement_metrics.py --start 2026-01-01 --end 2026-01-31
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
import frontmatter

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


def get_facebook_metrics(start_date: str, end_date: str, dry_run: bool = True) -> dict:
    """
    Get Facebook engagement metrics.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        dry_run: Use simulated data

    Returns:
        Facebook metrics dict
    """
    if dry_run:
        return {
            "platform": "facebook",
            "period": {"start_date": start_date, "end_date": end_date},
            "summary": {
                "total_posts": 15,
                "total_impressions": 18750,
                "total_reach": 14200,
                "total_engagement": 2180,
                "avg_engagement_rate": 0.116
            },
            "top_post": {
                "post_id": "fb_top_post",
                "message": "Our best performing Facebook post",
                "engagement": 450
            }
        }
    else:
        # In production, call Facebook MCP server
        raise NotImplementedError("Production Facebook MCP integration pending")


def get_instagram_metrics(start_date: str, end_date: str, dry_run: bool = True) -> dict:
    """
    Get Instagram engagement metrics.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        dry_run: Use simulated data

    Returns:
        Instagram metrics dict
    """
    if dry_run:
        return {
            "platform": "instagram",
            "period": {"start_date": start_date, "end_date": end_date},
            "summary": {
                "total_posts": 22,
                "total_impressions": 32500,
                "total_reach": 25800,
                "total_engagement": 4250,
                "avg_engagement_rate": 0.131
            },
            "top_post": {
                "media_id": "ig_top_post",
                "caption": "Our best performing Instagram post",
                "engagement": 680
            }
        }
    else:
        # In production, call Instagram MCP server
        raise NotImplementedError("Production Instagram MCP integration pending")


def get_twitter_metrics(start_date: str, end_date: str, dry_run: bool = True) -> dict:
    """
    Get Twitter engagement metrics.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        dry_run: Use simulated data

    Returns:
        Twitter metrics dict
    """
    if dry_run:
        return {
            "platform": "twitter",
            "period": {"start_date": start_date, "end_date": end_date},
            "summary": {
                "total_tweets": 42,
                "total_impressions": 105000,
                "total_likes": 3654,
                "total_retweets": 892,
                "total_replies": 456,
                "avg_engagement_rate": 0.048
            },
            "top_tweet": {
                "tweet_id": "tw_top_tweet",
                "text": "Our best performing tweet",
                "engagement": 1250
            }
        }
    else:
        # In production, call Twitter MCP server
        raise NotImplementedError("Production Twitter MCP integration pending")


def aggregate_metrics(facebook: dict, instagram: dict, twitter: dict) -> dict:
    """
    Aggregate metrics from all platforms.

    Args:
        facebook: Facebook metrics
        instagram: Instagram metrics
        twitter: Twitter metrics

    Returns:
        Aggregated metrics dict
    """
    total_posts = (
        facebook["summary"]["total_posts"] +
        instagram["summary"]["total_posts"] +
        twitter["summary"]["total_tweets"]
    )

    total_impressions = (
        facebook["summary"]["total_impressions"] +
        instagram["summary"]["total_impressions"] +
        twitter["summary"]["total_impressions"]
    )

    total_engagement = (
        facebook["summary"]["total_engagement"] +
        instagram["summary"]["total_engagement"] +
        (twitter["summary"]["total_likes"] + twitter["summary"]["total_retweets"] + twitter["summary"]["total_replies"])
    )

    avg_engagement_rate = total_engagement / total_impressions if total_impressions > 0 else 0

    return {
        "total_posts": total_posts,
        "total_impressions": total_impressions,
        "total_engagement": total_engagement,
        "avg_engagement_rate": avg_engagement_rate,
        "by_platform": {
            "facebook": facebook["summary"],
            "instagram": instagram["summary"],
            "twitter": twitter["summary"]
        },
        "top_posts": {
            "facebook": facebook["top_post"],
            "instagram": instagram["top_post"],
            "twitter": twitter["top_tweet"]
        }
    }


def generate_metrics_report(aggregated: dict, start_date: str, end_date: str, vault_path: str) -> str:
    """
    Generate metrics report markdown file.

    Args:
        aggregated: Aggregated metrics
        start_date: Start date
        end_date: End date
        vault_path: Path to Obsidian vault

    Returns:
        Path to report file
    """
    briefings_dir = os.path.join(vault_path, "Briefings")
    os.makedirs(briefings_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_file = os.path.join(briefings_dir, f"{timestamp}_social_media_metrics.md")

    content = f"""# Social Media Engagement Report

**Period**: {start_date} to {end_date}
**Generated**: {datetime.now().isoformat()}

## Overall Summary

| Metric | Value |
|--------|-------|
| Total Posts | {aggregated['total_posts']} |
| Total Impressions | {aggregated['total_impressions']:,} |
| Total Engagement | {aggregated['total_engagement']:,} |
| Avg Engagement Rate | {aggregated['avg_engagement_rate']:.1%} |

## Platform Breakdown

### Facebook

- Posts: {aggregated['by_platform']['facebook']['total_posts']}
- Impressions: {aggregated['by_platform']['facebook']['total_impressions']:,}
- Reach: {aggregated['by_platform']['facebook']['total_reach']:,}
- Engagement: {aggregated['by_platform']['facebook']['total_engagement']:,}
- Engagement Rate: {aggregated['by_platform']['facebook']['avg_engagement_rate']:.1%}

**Top Post**: {aggregated['top_posts']['facebook']['message']} ({aggregated['top_posts']['facebook']['engagement']} engagements)

### Instagram

- Posts: {aggregated['by_platform']['instagram']['total_posts']}
- Impressions: {aggregated['by_platform']['instagram']['total_impressions']:,}
- Reach: {aggregated['by_platform']['instagram']['total_reach']:,}
- Engagement: {aggregated['by_platform']['instagram']['total_engagement']:,}
- Engagement Rate: {aggregated['by_platform']['instagram']['avg_engagement_rate']:.1%}

**Top Post**: {aggregated['top_posts']['instagram']['caption']} ({aggregated['top_posts']['instagram']['engagement']} engagements)

### Twitter

- Tweets: {aggregated['by_platform']['twitter']['total_tweets']}
- Impressions: {aggregated['by_platform']['twitter']['total_impressions']:,}
- Likes: {aggregated['by_platform']['twitter']['total_likes']:,}
- Retweets: {aggregated['by_platform']['twitter']['total_retweets']:,}
- Replies: {aggregated['by_platform']['twitter']['total_replies']:,}
- Engagement Rate: {aggregated['by_platform']['twitter']['avg_engagement_rate']:.1%}

**Top Tweet**: {aggregated['top_posts']['twitter']['text']} ({aggregated['top_posts']['twitter']['engagement']} engagements)

## Insights

- **Best Platform**: {'Instagram' if aggregated['by_platform']['instagram']['avg_engagement_rate'] > max(aggregated['by_platform']['facebook']['avg_engagement_rate'], aggregated['by_platform']['twitter']['avg_engagement_rate']) else 'Facebook' if aggregated['by_platform']['facebook']['avg_engagement_rate'] > aggregated['by_platform']['twitter']['avg_engagement_rate'] else 'Twitter'} (highest engagement rate)
- **Total Reach**: {aggregated['by_platform']['facebook']['total_reach'] + aggregated['by_platform']['instagram']['total_reach']:,} unique users
- **Posting Frequency**: {aggregated['total_posts'] / 30:.1f} posts per day (average)

## Recommendations

1. Focus on Instagram content (highest engagement rate)
2. Analyze top-performing posts for content patterns
3. Maintain consistent posting schedule
4. Engage with comments and replies to boost reach
"""

    # Add frontmatter
    metadata = {
        "type": "social_media_report",
        "period_start": start_date,
        "period_end": end_date,
        "generated": datetime.now().isoformat(),
        "total_posts": aggregated["total_posts"],
        "total_engagement": aggregated["total_engagement"]
    }

    post = frontmatter.Post(content, **metadata)

    with open(report_file, 'w') as f:
        f.write(frontmatter.dumps(post))

    return report_file


def main():
    parser = argparse.ArgumentParser(description="Retrieve social media engagement metrics")
    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--vault", default=None, help="Path to Obsidian vault")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Use simulated data")
    args = parser.parse_args()

    # Determine vault path
    vault_path = args.vault or os.path.join(
        Path(__file__).parent.parent.parent.parent,
        "My_AI_Employee",
        "AI_Employee_Vault"
    )

    print(f"Retrieving social media metrics for {args.start} to {args.end}")

    # Get metrics from each platform
    print("\nFetching Facebook metrics...")
    facebook_metrics = get_facebook_metrics(args.start, args.end, args.dry_run)
    print(f"  ✓ {facebook_metrics['summary']['total_posts']} posts, {facebook_metrics['summary']['total_engagement']} engagements")

    print("\nFetching Instagram metrics...")
    instagram_metrics = get_instagram_metrics(args.start, args.end, args.dry_run)
    print(f"  ✓ {instagram_metrics['summary']['total_posts']} posts, {instagram_metrics['summary']['total_engagement']} engagements")

    print("\nFetching Twitter metrics...")
    twitter_metrics = get_twitter_metrics(args.start, args.end, args.dry_run)
    print(f"  ✓ {twitter_metrics['summary']['total_tweets']} tweets, {twitter_metrics['summary']['total_likes'] + twitter_metrics['summary']['total_retweets']} engagements")

    # Aggregate metrics
    print("\nAggregating metrics...")
    aggregated = aggregate_metrics(facebook_metrics, instagram_metrics, twitter_metrics)
    print(f"  Total posts: {aggregated['total_posts']}")
    print(f"  Total impressions: {aggregated['total_impressions']:,}")
    print(f"  Total engagement: {aggregated['total_engagement']:,}")
    print(f"  Avg engagement rate: {aggregated['avg_engagement_rate']:.1%}")

    # Generate report
    print("\nGenerating metrics report...")
    report_file = generate_metrics_report(aggregated, args.start, args.end, vault_path)
    print(f"  ✓ Report saved: {report_file}")

    print("\n✅ Engagement metrics retrieval complete!")
    print(f"\nReport available in /Briefings/ for CEO briefing integration")


if __name__ == "__main__":
    main()
