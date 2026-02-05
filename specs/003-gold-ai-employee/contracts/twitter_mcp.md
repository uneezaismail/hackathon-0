# MCP Server Contract: Twitter API v2 Integration

**Server Name**: `twitter-mcp`
**File**: `My_AI_Employee/mcp_servers/twitter_mcp.py`
**Purpose**: Post tweets and retrieve engagement metrics from Twitter/X
**Authentication**: OAuth 2.0 PKCE (no client secret required)
**Base URL**: `https://api.twitter.com/2`

---

## Overview

This MCP server provides tools for posting tweets and retrieving engagement metrics via Twitter API v2. Uses OAuth 2.0 PKCE authentication for enhanced security. All posting operations require HITL approval.

---

## Tools

### 1. create_tweet

Post tweet to Twitter/X.

**Requires HITL Approval**: YES

#### Input Schema

```json
{
  "text": "string (required) - Tweet text (max 280 characters)",
  "media_paths": "array (optional) - Paths to media files (max 4 images or 1 video)",
  "reply_to_tweet_id": "string (optional) - Tweet ID to reply to",
  "quote_tweet_id": "string (optional) - Tweet ID to quote"
}
```

#### Output Schema

```json
{
  "tweet_id": "string - Twitter tweet ID",
  "text": "string - Tweet text",
  "url": "string - URL to view tweet on Twitter",
  "created_at": "string - ISO8601 timestamp"
}
```

#### Error Codes

- `TEXT_TOO_LONG`: Tweet text exceeds 280 characters
- `MEDIA_UPLOAD_FAILED`: Failed to upload media
- `DUPLICATE_TWEET`: Duplicate tweet detected (same text posted recently)
- `RATE_LIMIT_EXCEEDED`: Tweet rate limit exceeded (100 tweets per 15 min)
- `REPLY_TWEET_NOT_FOUND`: Reply-to tweet ID does not exist

---

### 2. create_thread

Post tweet thread (multiple tweets in sequence).

**Requires HITL Approval**: YES

#### Input Schema

```json
{
  "tweets": "array (required) - List of tweet texts (each max 280 characters)",
  "media_paths": "array (optional) - Media files for first tweet only"
}
```

#### Output Schema

```json
{
  "thread_ids": "array - List of tweet IDs in thread order",
  "thread_url": "string - URL to first tweet in thread",
  "created_at": "string - ISO8601 timestamp"
}
```

#### Error Codes

- `EMPTY_THREAD`: Tweets array is empty
- `TEXT_TOO_LONG`: One or more tweets exceed 280 characters
- `THREAD_CREATION_FAILED`: Failed to create thread

---

### 3. upload_media

Upload media for use in tweets.

**Requires HITL Approval**: NO (utility function)

#### Input Schema

```json
{
  "media_path": "string (required) - Path to media file",
  "media_type": "string (optional) - image | video | gif (auto-detected if not provided)"
}
```

#### Output Schema

```json
{
  "media_id": "string - Twitter media ID",
  "media_type": "string - image | video | gif",
  "size_bytes": "number - File size in bytes",
  "uploaded_at": "string - ISO8601 timestamp"
}
```

#### Error Codes

- `FILE_NOT_FOUND`: Media file not found at specified path
- `INVALID_FORMAT`: Media format not supported
- `FILE_TOO_LARGE`: Media file exceeds size limit (5MB for images, 512MB for videos)

---

### 4. get_tweet_metrics

Get engagement metrics for specific tweet.

**Requires HITL Approval**: NO (read-only operation)

#### Input Schema

```json
{
  "tweet_id": "string (required) - Twitter tweet ID"
}
```

#### Output Schema

```json
{
  "tweet_id": "string - Twitter tweet ID",
  "text": "string - Tweet text",
  "metrics": {
    "impressions": "number - Total impressions",
    "likes": "number - Number of likes",
    "retweets": "number - Number of retweets",
    "replies": "number - Number of replies",
    "quotes": "number - Number of quote tweets",
    "bookmarks": "number - Number of bookmarks",
    "url_clicks": "number - URL clicks"
  },
  "engagement_rate": "number - Engagement rate (0-1)",
  "retrieved_at": "string - ISO8601 timestamp"
}
```

#### Error Codes

- `TWEET_NOT_FOUND`: Tweet ID does not exist
- `METRICS_NOT_AVAILABLE`: Metrics not yet available (wait 24 hours)

---

### 5. get_engagement_summary

Get aggregated engagement metrics for time period.

**Requires HITL Approval**: NO (read-only operation)

#### Input Schema

```json
{
  "start_date": "string (required) - Start date (YYYY-MM-DD)",
  "end_date": "string (required) - End date (YYYY-MM-DD)",
  "include_tweets": "boolean (optional) - Include individual tweet data (default: false)"
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
    "total_tweets": "number - Total tweets posted",
    "total_impressions": "number - Total impressions",
    "total_engagement": "number - Total engagements",
    "avg_engagement_rate": "number - Average engagement rate (0-1)"
  },
  "top_tweet": {
    "tweet_id": "string - Best performing tweet ID",
    "text": "string - Tweet text",
    "engagement": "number - Total engagement"
  },
  "tweets": "array (optional) - Individual tweet data if include_tweets=true"
}
```

#### Error Codes

- `INVALID_DATE_RANGE`: Start date after end date
- `NO_DATA`: No tweets posted in specified period

---

## Authentication

### OAuth 2.0 PKCE Flow

Twitter API v2 uses OAuth 2.0 PKCE (Proof Key for Code Exchange) for enhanced security without requiring client secret.

**Required Scopes**:
- `tweet.read`
- `tweet.write`
- `users.read`
- `offline.access` (for refresh token)

### Authentication Flow

```python
import tweepy

# OAuth 2.0 PKCE
oauth2_user_handler = tweepy.OAuth2UserHandler(
    client_id=CLIENT_ID,
    redirect_uri=REDIRECT_URI,
    scope=["tweet.read", "tweet.write", "users.read", "offline.access"],
    client_secret=None  # Not required for PKCE
)

# Get authorization URL
auth_url = oauth2_user_handler.get_authorization_url()

# After user authorizes, exchange code for token
access_token = oauth2_user_handler.fetch_token(authorization_response)

# Create client
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    access_token=access_token
)
```

**Token Storage**: Store access token and refresh token in OS credential manager (keyring library)

---

## Rate Limits

### Tweet Creation

- **100 tweets per 15 minutes** per user
- **300 tweets per 3 hours** per user

### Read Operations

- **900 requests per 15 minutes** for most endpoints
- **Rate limit headers**: `x-rate-limit-remaining`, `x-rate-limit-reset`

### Rate Limit Handling

```python
def check_rate_limit(response):
    remaining = int(response.headers.get('x-rate-limit-remaining', 0))
    if remaining < 10:
        reset_time = int(response.headers.get('x-rate-limit-reset', 0))
        wait_seconds = reset_time - time.time()
        await asyncio.sleep(wait_seconds)
```

---

## Error Handling

### Retry Logic

- **Transient errors**: Retry with exponential backoff (1s, 2s, 4s, 8s)
- **Rate limit errors**: Wait for rate limit reset, then retry
- **Authentication errors**: Do NOT retry, alert user
- **Validation errors**: Do NOT retry, return error to user

### Graceful Degradation

- **Twitter API unavailable**: Queue tweets locally in `.twitter_queue.jsonl`
- **Process queue**: When API becomes available, process queued tweets
- **Alert user**: Notify when Twitter API is unavailable

---

## Audit Logging

All operations MUST be logged to `/Logs/YYYY-MM-DD.json` with:
- Timestamp
- Action type (create_tweet, create_thread, upload_media, get_tweet_metrics, get_engagement_summary)
- Actor (system | user | autonomous_task)
- Target (tweet_id)
- Approval status
- Result (success | failed | queued)
- Platform (twitter)

**Credential Sanitization**: Access tokens MUST be sanitized before logging.

---

## Testing

### Unit Tests

```python
import pytest
from mcp.client import ClientSession, StdioServerParameters

@pytest.fixture
async def twitter_mcp_client():
    server_params = StdioServerParameters(
        command="python",
        args=["My_AI_Employee/mcp_servers/twitter_mcp.py"],
        env={"DRY_RUN": "true"}
    )
    async with ClientSession(server_params) as session:
        await session.initialize()
        yield session

@pytest.mark.asyncio
async def test_create_tweet(twitter_mcp_client):
    result = await twitter_mcp_client.call_tool(
        "create_tweet",
        arguments={
            "text": "Test tweet from MCP server #test"
        }
    )
    assert "tweet_id" in result.content[0].text
```

---

## Dependencies

```
tweepy>=4.14.0
fastmcp>=0.1.0
pydantic>=2.0.0
keyring>=24.0.0
requests>=2.31.0
```

---

## Configuration (.env)

```bash
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_SECRET=your_access_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_MCP_PORT=3006
```

---

## Platform-Specific Considerations

### Character Limits

- **Tweet text**: 280 characters max
- **URLs**: Count as 23 characters (t.co shortening)
- **Media**: Does not count toward character limit
- **Mentions**: Count toward character limit

### Content Adaptation

```python
def adapt_content_for_twitter(content: str) -> str:
    """Adapt content for Twitter (280 char limit)."""
    # Truncate if needed
    if len(content) > 280:
        # Account for ellipsis
        content = content[:277] + "..."

    # Add hashtags if space available
    if len(content) < 260:
        content += " #innovation #tech"

    return content
```

### Thread Creation

For content longer than 280 characters, automatically split into thread:

```python
def create_thread_from_content(content: str) -> list:
    """Split long content into tweet thread."""
    max_length = 270  # Leave room for "1/N" numbering

    # Split into sentences
    sentences = content.split('. ')

    tweets = []
    current_tweet = ""

    for sentence in sentences:
        if len(current_tweet) + len(sentence) + 2 <= max_length:
            current_tweet += sentence + ". "
        else:
            tweets.append(current_tweet.strip())
            current_tweet = sentence + ". "

    if current_tweet:
        tweets.append(current_tweet.strip())

    # Add numbering
    total = len(tweets)
    numbered_tweets = [f"{i+1}/{total} {tweet}" for i, tweet in enumerate(tweets)]

    return numbered_tweets
```

### Best Practices

- Post during peak engagement times (12 PM - 1 PM, 5 PM - 6 PM)
- Use 1-2 hashtags (more reduces engagement)
- Include media for 2x higher engagement
- Engage with replies within first hour
- Retweet and quote relevant content
