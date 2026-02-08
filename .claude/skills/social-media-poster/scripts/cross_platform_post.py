#!/usr/bin/env python3
"""
Cross-Platform Posting Workflow

Handles posting to multiple social media platforms (Facebook, Instagram, Twitter, LinkedIn)
with platform-specific content adaptation and approval workflow.

Usage:
    python cross_platform_post.py <action_item_file>
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
import frontmatter

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent))
from content_adapter import ContentAdapter


def parse_social_media_request(action_item_path: str) -> dict:
    """
    Parse social media posting request from action item.

    Args:
        action_item_path: Path to action item file

    Returns:
        Posting details dict
    """
    with open(action_item_path, 'r') as f:
        post = frontmatter.load(f)

    content = post.content
    metadata = post.metadata

    # Extract posting details
    posting_data = {
        "content": content,
        "platforms": metadata.get("platforms", ["facebook", "instagram", "twitter", "linkedin"]),
        "image_path": metadata.get("image_path"),
        "hashtags": metadata.get("hashtags", []),
        "scheduled_time": metadata.get("scheduled_time")
    }

    # Extract hashtags from content if not in metadata
    if not posting_data["hashtags"] and '#' in content:
        content_clean, hashtags = ContentAdapter.extract_hashtags(content)
        posting_data["content"] = content_clean
        posting_data["hashtags"] = hashtags

    return posting_data


def create_approval_requests(posting_data: dict, adapted_content: dict, vault_path: str) -> list:
    """
    Create approval requests for each platform.

    Args:
        posting_data: Original posting request data
        adapted_content: Platform-adapted content
        vault_path: Path to Obsidian vault

    Returns:
        List of approval request file paths
    """
    approval_dir = os.path.join(vault_path, "Pending_Approval")
    os.makedirs(approval_dir, exist_ok=True)

    approval_files = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for platform in posting_data["platforms"]:
        platform_content = adapted_content[platform]

        # Create approval request file
        approval_file = os.path.join(
            approval_dir,
            f"APPROVAL_{timestamp}_social_post_{platform}.md"
        )

        # Prepare metadata
        metadata = {
            "type": "approval_request",
            "action_type": "social_media_post",
            "platform": platform,
            "status": "pending",
            "priority": "medium",
            "created_at": datetime.now().isoformat(),
            "approved_by": None,
            "approved_at": None
        }

        # Prepare content based on platform
        if platform == "facebook":
            preview = platform_content["message"]
            char_info = f"Character count: {platform_content['char_count']} (no limit)"
        elif platform == "instagram":
            preview = platform_content["caption"]
            char_info = f"Character count: {platform_content['char_count']}/2200"
            if platform_content["truncated"]:
                char_info += " (TRUNCATED)"
        elif platform == "twitter":
            if platform_content["is_thread"]:
                preview = "\n".join(f"  {i+1}. {tweet}" for i, tweet in enumerate(platform_content["thread"]))
                char_info = f"Thread: {platform_content['tweet_count']} tweets"
            else:
                preview = platform_content["text"]
                char_info = f"Character count: {platform_content['char_count']}/280"
        elif platform == "linkedin":
            preview = platform_content["text"]
            char_info = f"Character count: {platform_content['char_count']}/3000"
            if platform_content["truncated"]:
                char_info += " (TRUNCATED)"

        content = f"""# Social Media Post Approval - {platform.title()}

## Platform Details

**Platform**: {platform.title()}
**{char_info}**
**Hashtags**: {platform_content['hashtags_used']}
**Has Image**: {'Yes' if posting_data['image_path'] else 'No'}
**Scheduled**: {'Yes' if posting_data['scheduled_time'] else 'No (immediate)'}

## Content Preview

```
{preview}
```

## Original Content

```
{posting_data['content']}
```

## Action Required

Review the adapted content for {platform.title()} and approve or reject.

### To Approve
Move this file to: `My_AI_Employee/AI_Employee_Vault/Approved/`

### To Reject
Move this file to: `My_AI_Employee/AI_Employee_Vault/Rejected/` and add rejection reason below.

---

**Rejection Reason** (if applicable):
[Add reason here]
"""

        # Write approval request
        post_obj = frontmatter.Post(content, **metadata)
        with open(approval_file, 'w') as f:
            f.write(frontmatter.dumps(post_obj))

        approval_files.append(approval_file)

    return approval_files


def create_plan_file(posting_data: dict, adapted_content: dict, approval_files: list, vault_path: str) -> str:
    """
    Create plan file documenting cross-platform posting workflow.

    Args:
        posting_data: Original posting request data
        adapted_content: Platform-adapted content
        approval_files: List of approval request files
        vault_path: Path to Obsidian vault

    Returns:
        Path to plan file
    """
    plans_dir = os.path.join(vault_path, "Plans")
    os.makedirs(plans_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plan_file = os.path.join(plans_dir, f"Plan_social_post_{timestamp}.md")

    platforms_str = ", ".join(p.title() for p in posting_data["platforms"])

    content = f"""# Cross-Platform Social Media Posting Plan

**Created**: {datetime.now().isoformat()}
**Platforms**: {platforms_str}

## Objective

Post content to {platforms_str} with platform-appropriate formatting

## Steps

- [x] Parse social media request from action item
- [x] Extract hashtags from content
- [x] Adapt content for each platform
- [x] Create approval requests for each platform
- [ ] Human approves posts (move to /Approved/)
- [ ] Orchestrator executes posts via MCP servers
- [ ] Track engagement metrics

## Original Content

```
{posting_data['content']}
```

**Hashtags**: {', '.join(f'#{tag}' for tag in posting_data['hashtags'])}
**Image**: {posting_data['image_path'] or 'None'}

## Platform Adaptations

### Facebook
- Character count: {adapted_content['facebook']['char_count']}
- Hashtags used: {adapted_content['facebook']['hashtags_used']}
- Truncated: {adapted_content['facebook']['truncated']}

### Instagram
- Character count: {adapted_content['instagram']['char_count']}/2200
- Hashtags used: {adapted_content['instagram']['hashtags_used']}
- Truncated: {adapted_content['instagram']['truncated']}

### Twitter
- {'Thread' if adapted_content['twitter']['is_thread'] else 'Single tweet'}
- {'Tweets: ' + str(adapted_content['twitter']['tweet_count']) if adapted_content['twitter']['is_thread'] else 'Character count: ' + str(adapted_content['twitter']['char_count']) + '/280'}
- Hashtags used: {adapted_content['twitter']['hashtags_used']}

### LinkedIn
- Character count: {adapted_content['linkedin']['char_count']}/3000
- Hashtags used: {adapted_content['linkedin']['hashtags_used']}
- Truncated: {adapted_content['linkedin']['truncated']}

## Approval Requests

{chr(10).join(f'- {os.path.basename(f)}' for f in approval_files)}

## Next Steps

1. Human reviews approval requests in /Pending_Approval/
2. Approved posts moved to /Approved/
3. Orchestrator executes via MCP servers:
   - Facebook: facebook_mcp.create_post
   - Instagram: instagram_mcp.create_media_post
   - Twitter: twitter_mcp.create_tweet or create_thread
   - LinkedIn: linkedin_mcp.create_post
4. Engagement tracking begins
"""

    with open(plan_file, 'w') as f:
        f.write(content)

    return plan_file


def main():
    parser = argparse.ArgumentParser(description="Cross-platform social media posting")
    parser.add_argument("action_item", help="Path to action item file")
    parser.add_argument("--vault", default=None, help="Path to Obsidian vault")
    args = parser.parse_args()

    # Determine vault path
    vault_path = args.vault or os.path.join(
        Path(__file__).parent.parent.parent.parent,
        "My_AI_Employee",
        "AI_Employee_Vault"
    )

    # Parse social media request
    print(f"Parsing social media request from {args.action_item}")
    posting_data = parse_social_media_request(args.action_item)

    print(f"Platforms: {', '.join(posting_data['platforms'])}")
    print(f"Hashtags: {len(posting_data['hashtags'])}")

    # Adapt content for all platforms
    print("\nAdapting content for each platform...")
    adapter = ContentAdapter()
    adapted_content = adapter.adapt_for_all_platforms(
        posting_data["content"],
        posting_data["hashtags"]
    )

    # Display adaptations
    for platform in posting_data["platforms"]:
        platform_content = adapted_content[platform]
        print(f"\n{platform.title()}:")
        if platform == "twitter" and platform_content["is_thread"]:
            print(f"  Thread: {platform_content['tweet_count']} tweets")
        else:
            print(f"  Char count: {platform_content['char_count']}")
        print(f"  Hashtags: {platform_content['hashtags_used']}")

    # Create approval requests
    print("\nCreating approval requests...")
    approval_files = create_approval_requests(posting_data, adapted_content, vault_path)
    for approval_file in approval_files:
        print(f"  ✓ {os.path.basename(approval_file)}")

    # Create plan file
    plan_file = create_plan_file(posting_data, adapted_content, approval_files, vault_path)
    print(f"\n✓ Plan file created: {plan_file}")

    # Move action item to Done
    done_dir = os.path.join(vault_path, "Done")
    os.makedirs(done_dir, exist_ok=True)
    done_file = os.path.join(done_dir, os.path.basename(args.action_item))

    # Update action item with result
    with open(args.action_item, 'r') as f:
        post = frontmatter.load(f)

    post.metadata["status"] = "processed"
    post.metadata["processed_at"] = datetime.now().isoformat()
    post.metadata["result"] = "approval_requests_created"
    post.metadata["platforms"] = posting_data["platforms"]

    with open(done_file, 'w') as f:
        f.write(frontmatter.dumps(post))

    # Remove from Needs_Action
    os.remove(args.action_item)

    print(f"✓ Action item moved to Done: {done_file}")
    print("\n✅ Cross-platform posting workflow complete!")
    print(f"\nNext: Human reviews and approves posts in /Pending_Approval/")


if __name__ == "__main__":
    main()
