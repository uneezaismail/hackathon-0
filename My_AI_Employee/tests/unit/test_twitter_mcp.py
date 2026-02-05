#!/usr/bin/env python3
"""
Unit tests for Twitter MCP Server.

Tests all 5 tools:
1. create_tweet
2. create_thread
3. upload_media
4. get_tweet_metrics
5. get_engagement_summary

Uses DRY_RUN=true mode to avoid actual Twitter API calls.
"""

import pytest
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Set DRY_RUN mode for testing
os.environ['DRY_RUN'] = 'true'
os.environ['TWITTER_API_KEY'] = 'test_api_key'
os.environ['TWITTER_API_SECRET'] = 'test_api_secret'
os.environ['TWITTER_ACCESS_TOKEN'] = 'test_access_token'
os.environ['TWITTER_ACCESS_TOKEN_SECRET'] = 'test_access_token_secret'

try:
    from mcp.client import ClientSession, StdioServerParameters
    MCP_CLIENT_AVAILABLE = True
except ImportError:
    MCP_CLIENT_AVAILABLE = False
    pytest.skip("MCP client not available", allow_module_level=True)


@pytest.fixture
async def twitter_mcp_client():
    """Create MCP client session for Twitter server."""
    server_params = StdioServerParameters(
        command="python",
        args=[str(Path(__file__).parent.parent / "My_AI_Employee" / "mcp_servers" / "twitter_mcp.py")],
        env={
            "DRY_RUN": "true",
            "TWITTER_API_KEY": "test_api_key",
            "TWITTER_API_SECRET": "test_api_secret",
            "TWITTER_ACCESS_TOKEN": "test_access_token",
            "TWITTER_ACCESS_TOKEN_SECRET": "test_access_token_secret"
        }
    )
    async with ClientSession(server_params) as session:
        await session.initialize()
        yield session


# ============================================================================
# T036: Unit test for create_tweet tool
# ============================================================================

@pytest.mark.asyncio
async def test_create_tweet_text_only(twitter_mcp_client):
    """Test creating text-only tweet."""
    result = await twitter_mcp_client.call_tool(
        "create_tweet",
        arguments={
            "text": "Excited to announce our new product launch! 🚀 #innovation #tech"
        }
    )

    response = json.loads(result.content[0].text)
    assert "tweet_id" in response
    assert response["text"] == "Excited to announce our new product launch! 🚀 #innovation #tech"
    assert "url" in response
    assert "created_at" in response


@pytest.mark.asyncio
async def test_create_tweet_with_media(twitter_mcp_client):
    """Test creating tweet with media."""
    # Create temporary test image
    import tempfile
    from PIL import Image

    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(tmp.name)
        tmp_path = tmp.name

    try:
        result = await twitter_mcp_client.call_tool(
            "create_tweet",
            arguments={
                "text": "Check out this amazing photo!",
                "media_paths": [tmp_path]
            }
        )

        response = json.loads(result.content[0].text)
        assert "tweet_id" in response
    finally:
        os.unlink(tmp_path)


@pytest.mark.asyncio
async def test_create_tweet_reply(twitter_mcp_client):
    """Test creating reply tweet."""
    result = await twitter_mcp_client.call_tool(
        "create_tweet",
        arguments={
            "text": "Thanks for the feedback!",
            "reply_to_tweet_id": "1234567890"
        }
    )

    response = json.loads(result.content[0].text)
    assert "tweet_id" in response


@pytest.mark.asyncio
async def test_create_tweet_quote(twitter_mcp_client):
    """Test creating quote tweet."""
    result = await twitter_mcp_client.call_tool(
        "create_tweet",
        arguments={
            "text": "Great insights here!",
            "quote_tweet_id": "1234567890"
        }
    )

    response = json.loads(result.content[0].text)
    assert "tweet_id" in response


@pytest.mark.asyncio
async def test_create_tweet_text_too_long(twitter_mcp_client):
    """Test creating tweet with text exceeding 280 characters."""
    long_text = "A" * 281

    with pytest.raises(Exception) as exc_info:
        await twitter_mcp_client.call_tool(
            "create_tweet",
            arguments={
                "text": long_text
            }
        )
    assert "280" in str(exc_info.value) or "character" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_create_tweet_empty_text(twitter_mcp_client):
    """Test creating tweet with empty text."""
    with pytest.raises(Exception) as exc_info:
        await twitter_mcp_client.call_tool(
            "create_tweet",
            arguments={
                "text": ""
            }
        )
    assert "empty" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_create_tweet_too_many_media(twitter_mcp_client):
    """Test creating tweet with more than 4 media files."""
    import tempfile
    from PIL import Image

    temp_files = []
    try:
        for i in range(5):
            tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            img = Image.new('RGB', (100, 100), color='red')
            img.save(tmp.name)
            temp_files.append(tmp.name)
            tmp.close()

        with pytest.raises(Exception) as exc_info:
            await twitter_mcp_client.call_tool(
                "create_tweet",
                arguments={
                    "text": "Too many images",
                    "media_paths": temp_files
                }
            )
        assert "4" in str(exc_info.value) or "maximum" in str(exc_info.value).lower()
    finally:
        for tmp_path in temp_files:
            os.unlink(tmp_path)


# ============================================================================
# T037: Unit test for create_thread tool
# ============================================================================

@pytest.mark.asyncio
async def test_create_thread_success(twitter_mcp_client):
    """Test creating tweet thread."""
    tweets = [
        "Thread 1/3: Excited to share our journey building this product!",
        "Thread 2/3: We learned so much about user needs and market fit.",
        "Thread 3/3: Thank you to everyone who supported us along the way! 🙏"
    ]

    result = await twitter_mcp_client.call_tool(
        "create_thread",
        arguments={
            "tweets": tweets
        }
    )

    response = json.loads(result.content[0].text)
    assert "thread_ids" in response
    assert len(response["thread_ids"]) == 3
    assert "thread_url" in response
    assert "created_at" in response


@pytest.mark.asyncio
async def test_create_thread_with_media(twitter_mcp_client):
    """Test creating thread with media on first tweet."""
    import tempfile
    from PIL import Image

    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        img = Image.new('RGB', (100, 100), color='green')
        img.save(tmp.name)
        tmp_path = tmp.name

    try:
        tweets = [
            "Check out this image!",
            "More details in this thread..."
        ]

        result = await twitter_mcp_client.call_tool(
            "create_thread",
            arguments={
                "tweets": tweets,
                "media_paths": [tmp_path]
            }
        )

        response = json.loads(result.content[0].text)
        assert len(response["thread_ids"]) == 2
    finally:
        os.unlink(tmp_path)


@pytest.mark.asyncio
async def test_create_thread_empty(twitter_mcp_client):
    """Test creating empty thread."""
    with pytest.raises(Exception) as exc_info:
        await twitter_mcp_client.call_tool(
            "create_thread",
            arguments={
                "tweets": []
            }
        )
    assert "empty" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_create_thread_tweet_too_long(twitter_mcp_client):
    """Test creating thread with one tweet exceeding 280 characters."""
    tweets = [
        "First tweet is fine",
        "A" * 281,  # Second tweet too long
        "Third tweet is fine"
    ]

    with pytest.raises(Exception) as exc_info:
        await twitter_mcp_client.call_tool(
            "create_thread",
            arguments={
                "tweets": tweets
            }
        )
    assert "280" in str(exc_info.value) or "character" in str(exc_info.value).lower()


# ============================================================================
# T038: Unit test for get_tweet_metrics tool
# ============================================================================

@pytest.mark.asyncio
async def test_get_tweet_metrics_success(twitter_mcp_client):
    """Test retrieving tweet metrics."""
    result = await twitter_mcp_client.call_tool(
        "get_tweet_metrics",
        arguments={
            "tweet_id": "1234567890"
        }
    )

    response = json.loads(result.content[0].text)
    assert response["tweet_id"] == "1234567890"
    assert "text" in response
    assert "metrics" in response
    assert "impressions" in response["metrics"]
    assert "likes" in response["metrics"]
    assert "retweets" in response["metrics"]
    assert "replies" in response["metrics"]
    assert "quotes" in response["metrics"]
    assert "bookmarks" in response["metrics"]
    assert "engagement_rate" in response
    assert 0 <= response["engagement_rate"] <= 1


@pytest.mark.asyncio
async def test_get_tweet_metrics_empty_id(twitter_mcp_client):
    """Test retrieving metrics with empty tweet ID."""
    with pytest.raises(Exception) as exc_info:
        await twitter_mcp_client.call_tool(
            "get_tweet_metrics",
            arguments={
                "tweet_id": ""
            }
        )
    assert "tweet_id" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_upload_media_success(twitter_mcp_client):
    """Test uploading media."""
    import tempfile
    from PIL import Image

    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        img = Image.new('RGB', (100, 100), color='yellow')
        img.save(tmp.name)
        tmp_path = tmp.name

    try:
        result = await twitter_mcp_client.call_tool(
            "upload_media",
            arguments={
                "media_path": tmp_path
            }
        )

        response = json.loads(result.content[0].text)
        assert "media_id" in response
        assert response["media_type"] == "image"
        assert "size_bytes" in response
        assert "uploaded_at" in response
    finally:
        os.unlink(tmp_path)


@pytest.mark.asyncio
async def test_upload_media_file_not_found(twitter_mcp_client):
    """Test uploading non-existent media file."""
    with pytest.raises(Exception) as exc_info:
        await twitter_mcp_client.call_tool(
            "upload_media",
            arguments={
                "media_path": "/nonexistent/path/to/media.jpg"
            }
        )
    assert "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_engagement_summary_success(twitter_mcp_client):
    """Test retrieving engagement summary."""
    result = await twitter_mcp_client.call_tool(
        "get_engagement_summary",
        arguments={
            "start_date": "2026-01-01",
            "end_date": "2026-01-31"
        }
    )

    response = json.loads(result.content[0].text)
    assert "period" in response
    assert response["period"]["start_date"] == "2026-01-01"
    assert response["period"]["end_date"] == "2026-01-31"
    assert "summary" in response
    assert "total_tweets" in response["summary"]
    assert "total_impressions" in response["summary"]
    assert "total_likes" in response["summary"]
    assert "total_retweets" in response["summary"]
    assert "avg_engagement_rate" in response["summary"]
    assert "top_tweet" in response


@pytest.mark.asyncio
async def test_get_engagement_summary_with_tweets(twitter_mcp_client):
    """Test retrieving engagement summary with individual tweets."""
    result = await twitter_mcp_client.call_tool(
        "get_engagement_summary",
        arguments={
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
            "include_tweets": True
        }
    )

    response = json.loads(result.content[0].text)
    assert "tweets" in response


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_full_tweeting_workflow(twitter_mcp_client):
    """Test complete tweeting workflow: create tweet → get metrics."""
    # Step 1: Create tweet
    create_result = await twitter_mcp_client.call_tool(
        "create_tweet",
        arguments={
            "text": "Integration test tweet for Twitter MCP"
        }
    )

    create_response = json.loads(create_result.content[0].text)
    tweet_id = create_response["tweet_id"]

    # Step 2: Get metrics for the tweet
    metrics_result = await twitter_mcp_client.call_tool(
        "get_tweet_metrics",
        arguments={
            "tweet_id": tweet_id
        }
    )

    metrics_response = json.loads(metrics_result.content[0].text)
    assert metrics_response["tweet_id"] == tweet_id
    assert "metrics" in metrics_response


@pytest.mark.asyncio
async def test_health_check(twitter_mcp_client):
    """Test health check endpoint."""
    result = await twitter_mcp_client.call_tool("health_check", arguments={})

    response = json.loads(result.content[0].text)
    assert response["status"] == "healthy"
    assert "connection" in response
    assert "credentials" in response
    assert response["dry_run"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
