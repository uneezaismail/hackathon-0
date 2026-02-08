---
name: social-media-poster
description: >
  Post messages and generate summaries for Facebook, Instagram, Twitter, and LinkedIn via MCP servers.
  Handles social media posting with approval workflow, content scheduling, and engagement tracking.
  Use when: (1) Posting to Facebook, Instagram, Twitter, or LinkedIn, (2) Scheduling social media content,
  (3) Generating social media summaries, (4) Cross-posting to multiple platforms, (5) Tracking
  social media engagement. Trigger phrases: "post to facebook", "post to instagram", "post to twitter",
  "post to linkedin", "share on social media", "schedule social post", "generate social media summary", "cross-post".
---

# Social Media Poster

Post messages and generate summaries for Facebook, Instagram, Twitter, and LinkedIn using MCP servers with approval workflow.

## Overview

Gold tier requires integration with Facebook, Instagram, Twitter, and LinkedIn for posting messages and generating summaries. This skill manages social media posting through MCP servers with HITL approval for sensitive content.

**Supported Platforms:**
- **Facebook**: Posts, photos, videos via Graph API
- **Instagram**: Posts, stories, reels via Graph API
- **Twitter/X**: Tweets, threads, media via API v2
- **LinkedIn**: Professional posts, articles, link sharing via REST API v2

## Quick Start

### Post to Single Platform

```bash
# Post to Facebook
/social-media-poster "Post to Facebook: Check out our new product launch!"

# Post to Instagram
/social-media-poster "Post to Instagram with image: product_launch.jpg"

# Post to Twitter
/social-media-poster "Tweet: Excited to announce our new feature! #innovation"

# Post to LinkedIn
/social-media-poster "Post to LinkedIn: Sharing insights on industry trends"
```

### Cross-Post to Multiple Platforms

```bash
/social-media-poster "Cross-post to all platforms: Big announcement coming tomorrow!"
```

### Generate Social Media Summary

```bash
/social-media-poster "Generate weekly social media summary"
```

## Configuration

### In Company_Handbook.md

```markdown
## Social Media Posting Rules

### Auto-Approve Thresholds
- Scheduled posts: Auto-approve if pre-approved in content calendar
- Replies to comments: Auto-approve if polite and on-brand
- Engagement posts: Auto-approve if < 280 characters
- LinkedIn posts: Auto-approve if professional and industry-relevant

### Always Require Approval
- Posts mentioning competitors
- Posts with pricing information
- Posts with legal/compliance implications
- Posts during crisis/sensitive events
- Posts with external links to non-company domains
- LinkedIn posts with company announcements

### Content Guidelines
- Tone: Professional but friendly (LinkedIn: strictly professional)
- Hashtags: Max 3 per post (LinkedIn: 3-5 professional hashtags)
- Emojis: Use sparingly, brand-appropriate only (LinkedIn: minimal/none)
- Links: Always use branded short links
```

### In .env

```bash
# Facebook MCP
FACEBOOK_ACCESS_TOKEN=your_token
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_MCP_PORT=3004

# Instagram MCP
INSTAGRAM_ACCESS_TOKEN=your_token
INSTAGRAM_ACCOUNT_ID=your_account_id
INSTAGRAM_MCP_PORT=3005

# Twitter MCP
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
TWITTER_MCP_PORT=3006

# LinkedIn MCP
LINKEDIN_ACCESS_TOKEN=your_token
LINKEDIN_PERSON_URN=urn:li:person:your_id
LINKEDIN_MCP_PORT=3007
```

## MCP Server Integration

### Facebook MCP Server

**Capabilities:**
- Post text, photos, videos to Facebook Page
- Schedule posts for later
- Get post engagement metrics
- Reply to comments

**Actions:**
- `create_post` - Post to Facebook timeline
- `upload_photo` - Post photo with caption
- `schedule_post` - Schedule post for future
- `get_post_insights` - Get engagement metrics

### Instagram MCP Server

**Capabilities:**
- Post photos, videos, carousels to Instagram
- Post stories and reels
- Get post engagement metrics
- Reply to comments and DMs

**Actions:**
- `create_media_post` - Post photo/video
- `create_story` - Post to Instagram story
- `create_reel` - Post Instagram reel
- `get_media_insights` - Get engagement metrics

### Twitter MCP Server

**Capabilities:**
- Post tweets, threads, polls
- Upload media (photos, videos, GIFs)
- Get tweet engagement metrics
- Reply to mentions

**Actions:**
- `create_tweet` - Post single tweet
- `create_thread` - Post tweet thread
- `upload_media` - Upload media for tweet
- `get_tweet_metrics` - Get engagement metrics

### LinkedIn MCP Server

**Capabilities:**
- Post professional content to LinkedIn profile
- Share articles with link previews
- Get post engagement metrics (likes, comments, shares)
- Professional networking and B2B outreach

**Actions:**
- `create_post` - Post to LinkedIn feed (text, hashtags, links)
- `health_check` - Verify API connection and token validity

**Note**: LinkedIn API requires OAuth 2.0 authentication. Run `python scripts/linkedin_oauth2_setup.py` to set up credentials.

## Workflow

### 1. Content Creation

Claude analyzes the request and creates appropriate content for each platform:

```markdown
# Social Media Post Request

**Platforms**: Facebook, Instagram, Twitter, LinkedIn
**Content**: Product launch announcement
**Media**: product_launch.jpg
**Scheduled**: 2026-01-28 10:00 AM

## Platform-Specific Content

### Facebook
Exciting news! 🎉 We're launching our new product tomorrow. Check it out at [link]

### Instagram
New product alert! 🚀 Swipe to see what's coming tomorrow. #innovation #productlaunch

### Twitter
Big announcement tomorrow! Stay tuned 👀 #productlaunch

### LinkedIn
Excited to announce our new product launch tomorrow. After months of development, we've built a solution that addresses key industry challenges. Learn more: [link] #Innovation #ProductLaunch #BusinessSolutions
```

### 2. Approval Workflow

If content requires approval (per Company_Handbook.md rules):

```markdown
# /Pending_Approval/SOCIAL_20260127_product_launch.md

---
type: approval_request
action: social_media_post
platforms: [facebook, instagram, twitter, linkedin]
status: pending
created: 2026-01-27T14:30:00Z
---

## Post Content

[Platform-specific content]

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

### 3. Execution

After approval, `@mcp-executor` routes to appropriate MCP servers:

```
/Approved/SOCIAL_20260127_product_launch.md
       ↓
mcp-executor reads file
       ↓
Route to Facebook MCP → create_post()
Route to Instagram MCP → create_media_post()
Route to Twitter MCP → create_tweet()
Route to LinkedIn MCP → create_post()
       ↓
Capture post IDs and URLs
       ↓
Move to /Done/ with execution results
```

### 4. Summary Generation

Weekly social media summary:

```markdown
# Weekly Social Media Summary
**Week of**: Jan 21-27, 2026

## Posts Published
- **Facebook**: 5 posts, 1,234 total reach, 89 engagements
- **Instagram**: 7 posts, 2,456 total reach, 234 engagements
- **Twitter**: 12 tweets, 3,456 impressions, 145 engagements
- **LinkedIn**: 3 posts, 890 views, 67 engagements

## Top Performing Content
1. Product launch announcement (Facebook) - 456 reach, 34 engagements
2. Behind-the-scenes reel (Instagram) - 1,234 reach, 89 engagements
3. Feature highlight thread (Twitter) - 2,345 impressions, 67 engagements
4. Industry insights article (LinkedIn) - 890 views, 45 engagements

## Engagement Trends
- Best posting time: 10:00 AM - 12:00 PM
- Most engaging content type: Video/Reels (Instagram), Professional insights (LinkedIn)
- Top hashtags: #innovation, #productlaunch, #tech
```

## Usage Examples

### Example 1: Simple Text Post

```bash
/social-media-poster "Post to Twitter: Just shipped a major update! Check it out."
```

Result:
- Creates tweet via Twitter MCP
- Logs to audit trail
- Moves to /Done/ with tweet URL

### Example 2: Multi-Platform Post with Media

```bash
/social-media-poster "Cross-post with image product.jpg: Introducing our latest innovation!"
```

Result:
- Creates approval request in /Pending_Approval/
- After approval, posts to all platforms
- Adapts content for each platform's character limits
- Logs all posts to audit trail

### Example 3: Scheduled Post

```bash
/social-media-poster "Schedule for tomorrow 10am: Big announcement coming!"
```

Result:
- Creates scheduled post in platform schedulers
- Logs scheduled post details
- Sends confirmation to /Done/

### Example 4: Weekly Summary

```bash
/social-media-poster "Generate social media summary for last week"
```

Result:
- Queries all MCP servers for post metrics
- Aggregates engagement data
- Generates summary report in /Briefings/
- Identifies top-performing content

## Integration with Other Skills

### With approval-workflow-manager

Social media posts requiring approval flow through HITL workflow:

```
needs-action-triage detects social post request
       ↓
social-media-poster creates content
       ↓
approval-workflow-manager creates approval request
       ↓
Human approves → moves to /Approved/
       ↓
mcp-executor posts via MCP servers
```

### With ceo-briefing-generator

Social media metrics included in weekly CEO briefing:

```
ceo-briefing-generator queries social-media-poster
       ↓
Retrieves weekly post metrics
       ↓
Includes in CEO briefing under "Marketing & Outreach"
```

### With ralph-wiggum-runner

Autonomous social media management:

```bash
/ralph-loop "Process all social media requests in /Needs_Action using @social-media-poster"
```

## Safety Features

- **Approval workflow**: Sensitive content requires human approval
- **Content validation**: Checks for prohibited content (profanity, competitors, legal issues)
- **Rate limiting**: Respects platform API rate limits
- **Audit logging**: All posts logged with timestamps and content
- **Rollback capability**: Can delete posts if needed (within platform limits)

## Resources

- **references/best-practices.md** - Comprehensive social media best practices guide with image specs, hashtag strategies, optimal posting times, and content formatting for Facebook, Instagram, Twitter, and LinkedIn
- **scripts/content_adapter.py** - Adapts content for platform-specific requirements
- **scripts/cross_platform_post.py** - Cross-platform posting orchestration
- **scripts/get_engagement_metrics.py** - Retrieves engagement metrics from all platforms

## Best Practices

Claude Code automatically reads `references/best-practices.md` when using this skill. The guide includes:

- **Image Specifications**: Optimal dimensions and file sizes for each platform
  - Facebook: 1200x630px (feed), 1080x1080px (square)
  - Instagram: 1080x1080px (square), 1080x1350px (portrait)
  - Twitter: 1200x675px (16:9)
  - LinkedIn: 1200x627px (feed), 1080x1080px (square)

- **Hashtag Strategies**: Platform-specific optimal counts
  - Facebook: 1-2 hashtags
  - Instagram: 20-30 hashtags (mix popular and niche)
  - Twitter: 1-2 hashtags
  - LinkedIn: 3-5 professional hashtags

- **Optimal Posting Times**:
  - Facebook: 1-3 PM weekdays, 12-1 PM weekends
  - Instagram: 11 AM - 1 PM weekdays, 10-11 AM weekends
  - Twitter: 8-10 AM and 6-9 PM weekdays
  - LinkedIn: 7-9 AM and 12-2 PM weekdays (avoid weekends)

- **Content Formatting**: Character limits, emoji usage, call-to-action guidelines
  - Facebook: 40-80 chars optimal (casual tone)
  - Instagram: First 125 chars critical (casual tone, emojis)
  - Twitter: 240 chars optimal (concise)
  - LinkedIn: 150-300 chars optimal (professional tone, minimal emojis)

- **Quality Scoring**: Automatic content quality analysis (0-100 scale)

When you use this skill, Claude will automatically optimize your content based on these best practices.
