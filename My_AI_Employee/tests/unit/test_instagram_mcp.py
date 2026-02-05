#!/usr/bin/env python3
"""
Unit tests for Instagram MCP Server.

Tests all 5 tools:
1. create_media_post
2. create_story
3. get_media
4. get_insights
5. get_media_insights

Uses DRY_RUN=true mode to avoid actual Instagram API calls.
"""

import pytest
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Set DRY_RUN mode for testing
os.environ['DRY_RUN'] = 'true'
os.environ['INSTAGRAM_ACCESS_TOKEN'] = 'test_token'
os.environ['INSTAGRAM_ACCOUNT_ID'] = 'test_account_id'

try:
    from mcp.client import ClientSession, StdioServerParameters
    MCP_CLIENT_AVAILABLE = True
except ImportError:
    MCP_CLIENT_AVAILABLE = False
    pytest.skip("MCP client not available", allow_module_level=True)


@pytest.fixture
async def instagram_mcp_client():
    """Create MCP client session for Instagram server."""
    server_params = StdioServerParameters(
        command="python",
        args=[str(Path(__file__).parent.parent / "My_AI_Employee" / "mcp_servers" / "instagram_mcp.py")],
        env={
            "DRY_RUN": "true",
            "INSTAGRAM_ACCESS_TOKEN": "test_token",
            "INSTAGRAM_ACCOUNT_ID": "test_account_id"
        }
    )
    async with ClientSession(server_params) as session:
        await session.initialize()
        yield session


# ============================================================================
# T033: Unit test for create_media_post tool
# ============================================================================

@pytest.mark.asyncio
async def test_create_media_post_success(instagram_mcp_client):
    """Test creating media post with image and caption."""
    result = await instagram_mcp_client.call_tool(
        "create_media_post",
        arguments={
            "image_url": "https://example.com/image.jpg",
            "caption": "Beautiful sunset from our office! 🌅 #business #innovation"
        }
    )

    response = json.loads(result.content[0].text)
    assert "media_id" in response
    assert response["status"] == "published"
    assert "url" in response
    assert "published_at" in response


@pytest.mark.asyncio
async def test_create_media_post_with_hashtags(instagram_mcp_client):
    """Test creating post with separate hashtags."""
    result = await instagram_mcp_client.call_tool(
        "create_media_post",
        arguments={
            "image_url": "https://example.com/image.jpg",
            "caption": "New product launch!",
            "hashtags": ["business", "innovation", "tech", "startup"]
        }
    )

    response = json.loads(result.content[0].text)
    assert "media_id" in response
    assert response["status"] == "published"


@pytest.mark.asyncio
async def test_create_media_post_with_location(instagram_mcp_client):
    """Test creating post with location."""
    result = await instagram_mcp_client.call_tool(
        "create_media_post",
        arguments={
            "image_url": "https://example.com/image.jpg",
            "caption": "Team lunch at our favorite spot!",
            "location_id": "123456789"
        }
    )

    response = json.loads(result.content[0].text)
    assert "media_id" in response


@pytest.mark.asyncio
async def test_create_media_post_caption_too_long(instagram_mcp_client):
    """Test creating post with caption exceeding 2200 characters."""
    long_caption = "A" * 2201

    with pytest.raises(Exception) as exc_info:
        await instagram_mcp_client.call_tool(
            "create_media_post",
            arguments={
                "image_url": "https://example.com/image.jpg",
                "caption": long_caption
            }
        )
    assert "caption" in str(exc_info.value).lower() or "2200" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_media_post_too_many_hashtags(instagram_mcp_client):
    """Test creating post with more than 30 hashtags."""
    too_many_hashtags = [f"tag{i}" for i in range(31)]

    with pytest.raises(Exception) as exc_info:
        await instagram_mcp_client.call_tool(
            "create_media_post",
            arguments={
                "image_url": "https://example.com/image.jpg",
                "caption": "Test post",
                "hashtags": too_many_hashtags
            }
        )
    assert "hashtag" in str(exc_info.value).lower() or "30" in str(exc_info.value)


# ============================================================================
# T034: Unit test for create_story tool
# ============================================================================

@pytest.mark.asyncio
async def test_create_story_success(instagram_mcp_client):
    """Test creating Instagram story."""
    result = await instagram_mcp_client.call_tool(
        "create_story",
        arguments={
            "image_url": "https://example.com/story.jpg"
        }
    )

    response = json.loads(result.content[0].text)
    assert "story_id" in response
    assert response["status"] == "published"
    assert "expires_at" in response
    assert "published_at" in response

    # Verify story expires in 24 hours
    published = datetime.fromisoformat(response["published_at"].replace('Z', '+00:00'))
    expires = datetime.fromisoformat(response["expires_at"].replace('Z', '+00:00'))
    duration = expires - published
    assert 23 <= duration.total_seconds() / 3600 <= 25  # ~24 hours


@pytest.mark.asyncio
async def test_create_story_with_link(instagram_mcp_client):
    """Test creating story with swipe-up link."""
    result = await instagram_mcp_client.call_tool(
        "create_story",
        arguments={
            "image_url": "https://example.com/story.jpg",
            "link": "https://example.com/promo"
        }
    )

    response = json.loads(result.content[0].text)
    assert "story_id" in response
    assert response["status"] == "published"


@pytest.mark.asyncio
async def test_create_story_empty_image_url(instagram_mcp_client):
    """Test creating story with empty image URL."""
    with pytest.raises(Exception) as exc_info:
        await instagram_mcp_client.call_tool(
            "create_story",
            arguments={
                "image_url": ""
            }
        )
    assert "image_url" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()


# ============================================================================
# T035: Unit test for get_media_insights tool
# ============================================================================

@pytest.mark.asyncio
async def test_get_media_success(instagram_mcp_client):
    """Test retrieving media posts."""
    result = await instagram_mcp_client.call_tool(
        "get_media",
        arguments={
            "limit": 10
        }
    )

    response = json.loads(result.content[0].text)
    assert "media" in response
    assert isinstance(response["media"], list)
    assert len(response["media"]) <= 10
    assert "paging" in response

    # Check media structure
    if response["media"]:
        media = response["media"][0]
        assert "media_id" in media
        assert "media_type" in media
        assert "caption" in media
        assert "permalink" in media
        assert "timestamp" in media
        assert "like_count" in media
        assert "comments_count" in media


@pytest.mark.asyncio
async def test_get_media_with_date_range(instagram_mcp_client):
    """Test retrieving media with date range."""
    since = (datetime.now() - timedelta(days=7)).isoformat()
    until = datetime.now().isoformat()

    result = await instagram_mcp_client.call_tool(
        "get_media",
        arguments={
            "limit": 25,
            "since": since,
            "until": until
        }
    )

    response = json.loads(result.content[0].text)
    assert "media" in response


@pytest.mark.asyncio
async def test_get_media_invalid_limit(instagram_mcp_client):
    """Test retrieving media with invalid limit."""
    with pytest.raises(Exception) as exc_info:
        await instagram_mcp_client.call_tool(
            "get_media",
            arguments={
                "limit": 150  # Exceeds max of 100
            }
        )
    assert "limit" in str(exc_info.value).lower() or "100" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_insights_success(instagram_mcp_client):
    """Test retrieving account insights."""
    result = await instagram_mcp_client.call_tool(
        "get_insights",
        arguments={
            "metrics": ["impressions", "reach", "profile_views"],
            "period": "day"
        }
    )

    response = json.loads(result.content[0].text)
    assert "metrics" in response
    assert "impressions" in response["metrics"]
    assert "reach" in response["metrics"]
    assert "profile_views" in response["metrics"]
    assert response["period"] == "day"
    assert "retrieved_at" in response


@pytest.mark.asyncio
async def test_get_insights_invalid_period(instagram_mcp_client):
    """Test retrieving insights with invalid period."""
    with pytest.raises(Exception) as exc_info:
        await instagram_mcp_client.call_tool(
            "get_insights",
            arguments={
                "metrics": ["impressions"],
                "period": "invalid_period"
            }
        )
    assert "period" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_media_insights_success(instagram_mcp_client):
    """Test retrieving media-specific insights."""
    result = await instagram_mcp_client.call_tool(
        "get_media_insights",
        arguments={
            "media_id": "ig_media_123456789"
        }
    )

    response = json.loads(result.content[0].text)
    assert response["media_id"] == "ig_media_123456789"
    assert "metrics" in response
    assert "impressions" in response["metrics"]
    assert "reach" in response["metrics"]
    assert "engagement" in response["metrics"]
    assert "engagement_rate" in response
    assert 0 <= response["engagement_rate"] <= 1


@pytest.mark.asyncio
async def test_get_media_insights_specific_metrics(instagram_mcp_client):
    """Test retrieving specific media metrics."""
    result = await instagram_mcp_client.call_tool(
        "get_media_insights",
        arguments={
            "media_id": "ig_media_123456789",
            "metrics": ["impressions", "saved"]
        }
    )

    response = json.loads(result.content[0].text)
    assert "metrics" in response


@pytest.mark.asyncio
async def test_get_media_insights_empty_media_id(instagram_mcp_client):
    """Test retrieving insights with empty media ID."""
    with pytest.raises(Exception) as exc_info:
        await instagram_mcp_client.call_tool(
            "get_media_insights",
            arguments={
                "media_id": ""
            }
        )
    assert "media_id" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_full_posting_workflow(instagram_mcp_client):
    """Test complete posting workflow: create post → get media → get insights."""
    # Step 1: Create media post
    create_result = await instagram_mcp_client.call_tool(
        "create_media_post",
        arguments={
            "image_url": "https://example.com/test.jpg",
            "caption": "Integration test post",
            "hashtags": ["test", "integration"]
        }
    )

    create_response = json.loads(create_result.content[0].text)
    media_id = create_response["media_id"]

    # Step 2: Get media insights
    insights_result = await instagram_mcp_client.call_tool(
        "get_media_insights",
        arguments={
            "media_id": media_id
        }
    )

    insights_response = json.loads(insights_result.content[0].text)
    assert insights_response["media_id"] == media_id
    assert "metrics" in insights_response


@pytest.mark.asyncio
async def test_health_check(instagram_mcp_client):
    """Test health check endpoint."""
    result = await instagram_mcp_client.call_tool("health_check", arguments={})

    response = json.loads(result.content[0].text)
    assert response["status"] == "healthy"
    assert "connection" in response
    assert "credentials" in response
    assert response["dry_run"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
