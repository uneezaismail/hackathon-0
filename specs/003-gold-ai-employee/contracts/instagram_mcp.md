# MCP Server Contract: Instagram Graph API Integration

**Server Name**: `instagram-mcp`
**File**: `My_AI_Employee/mcp_servers/instagram_mcp.py`
**Purpose**: Post media and retrieve engagement metrics from Instagram Business accounts
**Authentication**: OAuth 2.0 Page Access Token (same as Facebook)
**Base URL**: `https://graph.facebook.com/v18.0`

---

## Overview

This MCP server provides tools for posting media to Instagram Business accounts and retrieving engagement metrics via Instagram Graph API. Instagram Graph API is part of Facebook Graph API and requires Instagram Business account linked to Facebook Page. All posting operations require HITL approval.

---

## Tools

### 1. create_media_post

Post photo or video to Instagram Business account (two-step process: container → publish).

**Requires HITL Approval**: YES

#### Input Schema

```json
{
  "image_url": "string (required) - URL to image file (must be publicly accessible)",
  "caption": "string (required) - Post caption (max 2200 characters)",
  "hashtags": "array (optional) - List of hashtags (without # symbol)",
  "location_id": "string (optional) - Instagram location ID"
}
```

#### Output Schema

```json
{
  "media_id": "string - Instagram media ID",
  "status": "string - published",
  "url": "string - URL to view post on Instagram",
  "published_at": "string - ISO8601 timestamp"
}
```

#### Error Codes

- `IMAGE_URL_INVALID`: Image URL not accessible or invalid format
- `CAPTION_TOO_LONG`: Caption exceeds 2200 characters
- `CONTAINER_CREATION_FAILED`: Failed to create media container
- `PUBLISH_FAILED`: Failed to publish media
- `RATE_LIMIT_EXCEEDED`: Daily post limit exceeded (25 posts/day)

---

### 2. create_story

Post story to Instagram Business account.

**Requires HITL Approval**: YES

#### Input Schema

```json
{
  "image_url": "string (required) - URL to image file",
  "link": "string (optional) - Swipe-up link (requires 10k+ followers)"
}
```

#### Output Schema

```json
{
  "story_id": "string - Instagram story ID",
  "status": "string - published",
  "expires_at": "string - ISO8601 timestamp (24 hours from publish)",
  "published_at": "string - ISO8601 timestamp"
}
```

#### Error Codes

- `IMAGE_URL_INVALID`: Image URL not accessible
- `LINK_NOT_ALLOWED`: Account does not have swipe-up link permission
- `STORY_CREATION_FAILED`: Failed to create story

---

### 3. get_media

Retrieve media posts with metadata.

**Requires HITL Approval**: NO (read-only operation)

#### Input Schema

```json
{
  "limit": "number (optional) - Number of posts to retrieve (default: 25, max: 100)",
  "since": "string (optional) - ISO8601 timestamp to retrieve posts after",
  "until": "string (optional) - ISO8601 timestamp to retrieve posts before"
}
```

#### Output Schema

```json
{
  "media": [
    {
      "media_id": "string - Instagram media ID",
      "media_type": "string - IMAGE | VIDEO | CAROUSEL_ALBUM",
      "caption": "string - Post caption",
      "permalink": "string - URL to post",
      "timestamp": "string - ISO8601 timestamp",
      "like_count": "number - Number of likes",
      "comments_count": "number - Number of comments"
    }
  ],
  "paging": {
    "next": "string - URL for next page",
    "previous": "string - URL for previous page"
  }
}
```

#### Error Codes

- `INVALID_LIMIT`: Limit exceeds maximum (100)
- `INVALID_DATE_RANGE`: Since date after until date

---

### 4. get_insights

Get account-level insights (impressions, reach, profile views).

**Requires HITL Approval**: NO (read-only operation)

#### Input Schema

```json
{
  "metrics": "array (required) - Metrics to retrieve",
  "period": "string (required) - day | week | days_28 | lifetime",
  "since": "string (optional) - Start date (YYYY-MM-DD)",
  "until": "string (optional) - End date (YYYY-MM-DD)"
}
```

**Available Metrics**:
- `impressions`: Total impressions
- `reach`: Unique accounts reached
- `profile_views`: Profile views
- `follower_count`: Total followers
- `email_contacts`: Email button taps
- `phone_call_clicks`: Phone button taps
- `text_message_clicks`: Text button taps
- `get_directions_clicks`: Directions button taps
- `website_clicks`: Website link clicks

#### Output Schema

```json
{
  "insights": {
    "impressions": "number - Total impressions",
    "reach": "number - Unique accounts reached",
    "profile_views": "number - Profile views",
    "follower_count": "number - Total followers"
  },
  "period": {
    "start_date": "string - Start date",
    "end_date": "string - End date"
  },
  "retrieved_at": "string - ISO8601 timestamp"
}
```

#### Error Codes

- `INVALID_METRIC`: Requested metric not supported
- `INSIGHTS_NOT_AVAILABLE`: Insights not yet available (wait 24 hours)
- `INVALID_PERIOD`: Period not supported for metric

---

### 5. get_media_insights

Get engagement metrics for specific media post.

**Requires HITL Approval**: NO (read-only operation)

#### Input Schema

```json
{
  "media_id": "string (required) - Instagram media ID",
  "metrics": "array (optional) - Metrics to retrieve (default: all)"
}
```

**Available Metrics**:
- `impressions`: Total impressions
- `reach`: Unique accounts reached
- `engagement`: Total engagement (likes + comments + saves + shares)
- `saved`: Number of saves
- `video_views`: Video views (for videos only)

#### Output Schema

```json
{
  "media_id": "string - Instagram media ID",
  "metrics": {
    "impressions": "number - Total impressions",
    "reach": "number - Unique accounts reached",
    "engagement": "number - Total engagement",
    "saved": "number - Number of saves",
    "likes": "number - Number of likes",
    "comments": "number - Number of comments"
  },
  "engagement_rate": "number - Engagement rate (0-1)",
  "retrieved_at": "string - ISO8601 timestamp"
}
```

#### Error Codes

- `MEDIA_NOT_FOUND`: Media ID does not exist
- `INSIGHTS_NOT_AVAILABLE`: Insights not yet available (wait 24 hours)

---

## Authentication

### Page Access Token (Same as Facebook)

Instagram Graph API uses the same Page Access Token as Facebook Graph API. The Instagram Business account must be linked to a Facebook Page.

**Required Permissions**:
- `instagram_basic`
- `instagram_content_publish`
- `pages_read_engagement`

**Token Storage**: Store in OS credential manager (keyring library)

---

## Rate Limits

- **200 requests per hour** (shared with Facebook)
- **25 media posts per day** per Instagram account
- **Rate limit headers**: `X-App-Usage`, `X-Business-Use-Case-Usage`
- **Exponential backoff**: 1s, 2s, 4s, 8s on rate limit errors

---

## Error Handling

### Retry Logic

- **Transient errors**: Retry with exponential backoff
- **Rate limit errors**: Wait for rate limit reset, then retry
- **Authentication errors**: Do NOT retry, alert user
- **Validation errors**: Do NOT retry, return error to user

### Graceful Degradation

- **Instagram API unavailable**: Queue posts locally in `.instagram_queue.jsonl`
- **Process queue**: When API becomes available, process queued posts
- **Alert user**: Notify when Instagram API is unavailable

---

## Audit Logging

All operations MUST be logged to `/Logs/YYYY-MM-DD.json` with:
- Timestamp
- Action type (create_media_post, create_story, get_media, get_insights, get_media_insights)
- Actor (system | user | autonomous_task)
- Target (media_id, account_id)
- Approval status
- Result (success | failed | queued)
- Platform (instagram)

**Credential Sanitization**: Page Access Token MUST be sanitized before logging.

---

## Testing

### Unit Tests

```python
import pytest
from mcp.client import ClientSession, StdioServerParameters

@pytest.fixture
async def instagram_mcp_client():
    server_params = StdioServerParameters(
        command="python",
        args=["My_AI_Employee/mcp_servers/instagram_mcp.py"],
        env={"DRY_RUN": "true"}
    )
    async with ClientSession(server_params) as session:
        await session.initialize()
        yield session

@pytest.mark.asyncio
async def test_create_media_post(instagram_mcp_client):
    result = await instagram_mcp_client.call_tool(
        "create_media_post",
        arguments={
            "image_url": "https://example.com/image.jpg",
            "caption": "Test post from MCP server #test"
        }
    )
    assert "media_id" in result.content[0].text
```

---

## Dependencies

```
facebook-sdk>=3.1.0
fastmcp>=0.1.0
pydantic>=2.0.0
keyring>=24.0.0
requests>=2.31.0
```

---

## Configuration (.env)

```bash
INSTAGRAM_PAGE_ACCESS_TOKEN=your_page_access_token_here
INSTAGRAM_ACCOUNT_ID=your_instagram_business_account_id_here
INSTAGRAM_MCP_PORT=3005
```

---

## Platform-Specific Considerations

### Character Limits

- **Caption**: 2200 characters max
- **Hashtags**: 30 hashtags max per post
- **Recommended**: 3-5 hashtags for optimal engagement

### Content Adaptation

```python
def adapt_content_for_instagram(content: str, hashtags: list = None) -> str:
    """Adapt content for Instagram (2200 char limit)."""
    # Truncate if needed
    if len(content) > 2200:
        content = content[:2197] + "..."

    # Add hashtags at end
    if hashtags:
        hashtag_str = ' '.join([f'#{tag}' for tag in hashtags[:30]])
        content = f"{content}\n\n{hashtag_str}"

    return content
```

### Two-Step Media Creation

Instagram requires two-step process for posting:

1. **Create Container**: Upload media and create container
2. **Publish Container**: Publish container to make post live

```python
# Step 1: Create container
container = graph.post(
    path=f'{INSTAGRAM_ACCOUNT_ID}/media',
    image_url='https://example.com/image.jpg',
    caption='Post caption #hashtag'
)

# Step 2: Publish container
media = graph.post(
    path=f'{INSTAGRAM_ACCOUNT_ID}/media_publish',
    creation_id=container['id']
)
```

### Best Practices

- Post during peak engagement times (11 AM - 1 PM, 7 PM - 9 PM)
- Use high-quality images (1080x1080 for square, 1080x1350 for portrait)
- Include 3-5 relevant hashtags
- Engage with comments within first hour
- Post consistently (1-2 times per day)
