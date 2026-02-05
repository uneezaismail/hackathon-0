# MCP Server Contract: Facebook Graph API Integration

**Server Name**: `facebook-mcp`
**File**: `My_AI_Employee/mcp_servers/facebook_mcp.py`
**Purpose**: Post messages and retrieve engagement metrics from Facebook Pages
**Authentication**: OAuth 2.0 Page Access Token (long-lived, never expires)
**Base URL**: `https://graph.facebook.com/v18.0`

---

## Overview

This MCP server provides tools for posting to Facebook Pages and retrieving engagement metrics via Facebook Graph API. All posting operations require HITL approval per Company_Handbook.md rules.

---

## Tools

### 1. create_post

Post message to Facebook Page.

**Requires HITL Approval**: YES

#### Input Schema

```json
{
  "message": "string (required) - Post message content",
  "link": "string (optional) - URL to share",
  "image_path": "string (optional) - Path to image file",
  "scheduled_time": "string (optional) - ISO8601 timestamp for scheduling"
}
```

#### Output Schema

```json
{
  "post_id": "string - Facebook post ID (e.g., 123456789_987654321)",
  "status": "string - published | scheduled",
  "url": "string - URL to view post on Facebook",
  "published_at": "string - ISO8601 timestamp"
}
```

#### Error Codes

- `AUTH_ERROR`: Invalid or expired Page Access Token
- `RATE_LIMIT_EXCEEDED`: API rate limit exceeded (200 req/hour)
- `INVALID_IMAGE`: Image file not found or invalid format
- `SCHEDULED_TIME_INVALID`: Scheduled time is in the past

---

### 2. upload_photo

Upload photo to Facebook Page with caption.

**Requires HITL Approval**: YES

#### Input Schema

```json
{
  "image_path": "string (required) - Path to image file",
  "caption": "string (required) - Photo caption"
}
```

#### Output Schema

```json
{
  "photo_id": "string - Facebook photo ID",
  "post_id": "string - Associated post ID",
  "status": "string - published",
  "url": "string - URL to view photo on Facebook",
  "published_at": "string - ISO8601 timestamp"
}
```

#### Error Codes

- `IMAGE_NOT_FOUND`: Image file not found at specified path
- `INVALID_FORMAT`: Image format not supported (supported: JPG, PNG, GIF)
- `FILE_TOO_LARGE`: Image file exceeds 4MB limit
- `UPLOAD_FAILED`: Failed to upload image to Facebook

---

### 3. get_post_insights

Retrieve engagement metrics for specific post.

**Requires HITL Approval**: NO (read-only operation)

#### Input Schema

```json
{
  "post_id": "string (required) - Facebook post ID",
  "metrics": "array (optional) - Metrics to retrieve (default: all)",
  "period": "string (optional) - day | week | days_28 (default: lifetime)"
}
```

#### Output Schema

```json
{
  "post_id": "string - Facebook post ID",
  "metrics": {
    "impressions": "number - Total impressions",
    "reach": "number - Unique users reached",
    "engaged_users": "number - Users who engaged",
    "reactions": "number - Total reactions (likes, love, etc.)",
    "comments": "number - Total comments",
    "shares": "number - Total shares",
    "clicks": "number - Total clicks"
  },
  "engagement_rate": "number - Engagement rate (0-1)",
  "retrieved_at": "string - ISO8601 timestamp"
}
```

#### Error Codes

- `POST_NOT_FOUND`: Post ID does not exist
- `INSIGHTS_NOT_AVAILABLE`: Insights not yet available (wait 24 hours)
- `INVALID_METRIC`: Requested metric not supported

---

### 4. get_engagement_summary

Get aggregated engagement metrics for time period.

**Requires HITL Approval**: NO (read-only operation)

#### Input Schema

```json
{
  "start_date": "string (required) - Start date (YYYY-MM-DD)",
  "end_date": "string (required) - End date (YYYY-MM-DD)",
  "include_posts": "boolean (optional) - Include individual post data (default: false)"
}
```

#### Output Schema

```json
{
  "period": {
    "start_date": "string - Start date",
    "end_date": "string - End date"
  },
  "summary": {
    "total_posts": "number - Total posts published",
    "total_impressions": "number - Total impressions",
    "total_reach": "number - Total unique users reached",
    "total_engagement": "number - Total engagements",
    "avg_engagement_rate": "number - Average engagement rate (0-1)"
  },
  "top_post": {
    "post_id": "string - Best performing post ID",
    "message": "string - Post message",
    "engagement": "number - Total engagement"
  },
  "posts": "array (optional) - Individual post data if include_posts=true"
}
```

#### Error Codes

- `INVALID_DATE_RANGE`: Start date after end date
- `NO_DATA`: No posts published in specified period

---

## Authentication

### Page Access Token

1. **Create Facebook App**: https://developers.facebook.com/apps
2. **Add Facebook Login**: Configure OAuth redirect URI
3. **Request Permissions**: `pages_manage_posts`, `pages_read_engagement`, `pages_read_user_content`
4. **Get Page Access Token**: Exchange user token for Page Access Token
5. **Token Storage**: Store in OS credential manager (keyring library)

**Token Lifetime**: Long-lived Page Access Tokens never expire (unless revoked)

### OAuth 2.0 Flow

```python
import facebook

# Step 1: Get user access token (via OAuth flow)
# Step 2: Exchange for Page Access Token
graph = facebook.GraphAPI(access_token=USER_ACCESS_TOKEN)
pages = graph.get_connections(id='me', connection_name='accounts')
page_access_token = pages['data'][0]['access_token']

# Step 3: Store Page Access Token securely
import keyring
keyring.set_password('facebook_mcp', 'page_access_token', page_access_token)
```

---

## Rate Limits

- **200 requests per hour** per user
- **Rate limit headers**: `X-App-Usage`, `X-Business-Use-Case-Usage`
- **Exponential backoff**: 1s, 2s, 4s, 8s on rate limit errors
- **Respect headers**: Check usage percentage and throttle if > 80%

### Rate Limit Handling

```python
def check_rate_limit(response_headers):
    usage = json.loads(response_headers.get('X-App-Usage', '{}'))
    if usage.get('call_count', 0) > 80:
        # Throttle requests
        await asyncio.sleep(60)
```

---

## Error Handling

### Retry Logic

- **Transient errors** (network timeout, 5xx errors): Retry with exponential backoff
- **Rate limit errors** (429): Wait for rate limit reset, then retry
- **Authentication errors** (401, 403): Do NOT retry, alert user
- **Validation errors** (400): Do NOT retry, return error to user

### Graceful Degradation

- **Facebook API unavailable**: Queue posts locally in `.facebook_queue.jsonl`
- **Process queue**: When API becomes available, process queued posts
- **Alert user**: Notify when Facebook API is unavailable

---

## Audit Logging

All operations MUST be logged to `/Logs/YYYY-MM-DD.json` with:
- Timestamp
- Action type (create_post, upload_photo, get_post_insights, get_engagement_summary)
- Actor (system | user | autonomous_task)
- Target (post_id, page_id)
- Approval status
- Result (success | failed | queued)
- Platform (facebook)

**Credential Sanitization**: Page Access Token MUST be sanitized before logging (show first 4 chars + ***).

---

## Testing

### Unit Tests

```python
import pytest
from mcp.client import ClientSession, StdioServerParameters

@pytest.fixture
async def facebook_mcp_client():
    server_params = StdioServerParameters(
        command="python",
        args=["My_AI_Employee/mcp_servers/facebook_mcp.py"],
        env={"DRY_RUN": "true"}
    )
    async with ClientSession(server_params) as session:
        await session.initialize()
        yield session

@pytest.mark.asyncio
async def test_create_post(facebook_mcp_client):
    result = await facebook_mcp_client.call_tool(
        "create_post",
        arguments={
            "message": "Test post from MCP server",
            "link": "https://example.com"
        }
    )
    assert "post_id" in result.content[0].text
```

### Integration Tests

- Test with Facebook test app and test page
- Verify post creation, photo upload, insights retrieval
- Test error handling and rate limit handling

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
FACEBOOK_PAGE_ACCESS_TOKEN=your_page_access_token_here
FACEBOOK_PAGE_ID=your_page_id_here
FACEBOOK_MCP_PORT=3004
```

---

## Platform-Specific Considerations

### Character Limits

- **No character limit** for Facebook posts
- **Recommended**: Keep posts < 500 characters for better engagement
- **Link preview**: Automatically generated for URLs

### Content Adaptation

```python
def adapt_content_for_facebook(content: str) -> str:
    """Adapt content for Facebook (no character limit)."""
    # No truncation needed
    # Add hashtags at end if not present
    if '#' not in content:
        content += '\n\n#business #innovation'
    return content
```

### Best Practices

- Post during peak engagement times (10 AM - 12 PM, 7 PM - 9 PM)
- Include images for 2.3x higher engagement
- Ask questions to encourage comments
- Use 1-2 hashtags (more than 3 reduces engagement)
