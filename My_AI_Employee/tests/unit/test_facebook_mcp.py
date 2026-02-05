#!/usr/bin/env python3
"""
Unit tests for Facebook MCP Server.

Tests all 4 tools:
1. create_post
2. upload_photo
3. get_post_insights
4. get_engagement_summary

Uses DRY_RUN=true mode to avoid actual Facebook API calls.
"""

import pytest
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Set DRY_RUN mode for testing
os.environ['DRY_RUN'] = 'true'
os.environ['FACEBOOK_PAGE_ACCESS_TOKEN'] = 'test_token'
os.environ['FACEBOOK_PAGE_ID'] = 'test_page_id'

try:
    from mcp.client import ClientSession, StdioServerParameters
    MCP_CLIENT_AVAILABLE = True
except ImportError:
    MCP_CLIENT_AVAILABLE = False
    pytest.skip("MCP client not available", allow_module_level=True)


@pytest.fixture
async def facebook_mcp_client():
    """Create MCP client session for Facebook server."""
    server_params = StdioServerParameters(
        command="python",
        args=[str(Path(__file__).parent.parent / "My_AI_Employee" / "mcp_servers" / "facebook_mcp.py")],
        env={
            "DRY_RUN": "true",
            "FACEBOOK_PAGE_ACCESS_TOKEN": "test_token",
            "FACEBOOK_PAGE_ID": "test_page_id"
        }
    )
    async with ClientSession(server_params) as session:
        await session.initialize()
        yield session


# ============================================================================
# T030: Unit test for create_post tool
# ============================================================================

@pytest.mark.asyncio
async def test_create_post_text_only(facebook_mcp_client):
    """Test creating text-only post."""
    result = await facebook_mcp_client.call_tool(
        "create_post",
        arguments={
            "message": "Excited to announce our new product launch! 🚀"
        }
    )

    response = json.loads(result.content[0].text)
    assert "post_id" in response
    assert response["status"] == "published"
    assert "url" in response
    assert "published_at" in response


@pytest.mark.asyncio
async def test_create_post_with_link(facebook_mcp_client):
    """Test creating post with link."""
    result = await facebook_mcp_client.call_tool(
        "create_post",
        arguments={
            "message": "Check out our latest blog post!",
            "link": "https://example.com/blog/latest-post"
        }
    )

    response = json.loads(result.content[0].text)
    assert "post_id" in response
    assert response["status"] == "published"


@pytest.mark.asyncio
async def test_create_post_scheduled(facebook_mcp_client):
    """Test creating scheduled post."""
    future_time = (datetime.now() + timedelta(hours=24)).isoformat()

    result = await facebook_mcp_client.call_tool(
        "create_post",
        arguments={
            "message": "This post will be published tomorrow",
            "scheduled_time": future_time
        }
    )

    response = json.loads(result.content[0].text)
    assert response["status"] == "scheduled"
    assert response["published_at"] == future_time


@pytest.mark.asyncio
async def test_create_post_invalid_scheduled_time(facebook_mcp_client):
    """Test creating post with past scheduled time."""
    past_time = (datetime.now() - timedelta(hours=1)).isoformat()

    with pytest.raises(Exception) as exc_info:
        await facebook_mcp_client.call_tool(
            "create_post",
            arguments={
                "message": "This should fail",
                "scheduled_time": past_time
            }
        )
    assert "future" in str(exc_info.value).lower() or "past" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_create_post_empty_message(facebook_mcp_client):
    """Test creating post with empty message."""
    with pytest.raises(Exception) as exc_info:
        await facebook_mcp_client.call_tool(
            "create_post",
            arguments={
                "message": ""
            }
        )
    assert "message" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()


# ============================================================================
# T031: Unit test for upload_photo tool
# ============================================================================

@pytest.mark.asyncio
async def test_upload_photo_success(facebook_mcp_client):
    """Test successful photo upload."""
    # Create temporary test image
    import tempfile
    from PIL import Image

    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        img = Image.new('RGB', (100, 100), color='red')
        img.save(tmp.name)
        tmp_path = tmp.name

    try:
        result = await facebook_mcp_client.call_tool(
            "upload_photo",
            arguments={
                "image_path": tmp_path,
                "caption": "Beautiful sunset from our office! 🌅"
            }
        )

        response = json.loads(result.content[0].text)
        assert "photo_id" in response
        assert "post_id" in response
        assert response["status"] == "published"
        assert "url" in response
    finally:
        os.unlink(tmp_path)


@pytest.mark.asyncio
async def test_upload_photo_file_not_found(facebook_mcp_client):
    """Test photo upload with non-existent file."""
    with pytest.raises(Exception) as exc_info:
        await facebook_mcp_client.call_tool(
            "upload_photo",
            arguments={
                "image_path": "/nonexistent/path/to/image.jpg",
                "caption": "This should fail"
            }
        )
    assert "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_upload_photo_invalid_format(facebook_mcp_client):
    """Test photo upload with invalid format."""
    import tempfile

    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
        tmp.write(b"Not an image")
        tmp_path = tmp.name

    try:
        with pytest.raises(Exception) as exc_info:
            await facebook_mcp_client.call_tool(
                "upload_photo",
                arguments={
                    "image_path": tmp_path,
                    "caption": "This should fail"
                }
            )
        assert "format" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()
    finally:
        os.unlink(tmp_path)


@pytest.mark.asyncio
async def test_upload_photo_empty_caption(facebook_mcp_client):
    """Test photo upload with empty caption."""
    import tempfile
    from PIL import Image

    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(tmp.name)
        tmp_path = tmp.name

    try:
        with pytest.raises(Exception) as exc_info:
            await facebook_mcp_client.call_tool(
                "upload_photo",
                arguments={
                    "image_path": tmp_path,
                    "caption": ""
                }
            )
        assert "caption" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()
    finally:
        os.unlink(tmp_path)


# ============================================================================
# T032: Unit test for get_post_insights tool
# ============================================================================

@pytest.mark.asyncio
async def test_get_post_insights_success(facebook_mcp_client):
    """Test retrieving post insights."""
    result = await facebook_mcp_client.call_tool(
        "get_post_insights",
        arguments={
            "post_id": "test_page_id_123456789",
            "period": "lifetime"
        }
    )

    response = json.loads(result.content[0].text)
    assert response["post_id"] == "test_page_id_123456789"
    assert "metrics" in response
    assert "impressions" in response["metrics"]
    assert "reach" in response["metrics"]
    assert "engaged_users" in response["metrics"]
    assert "reactions" in response["metrics"]
    assert "comments" in response["metrics"]
    assert "shares" in response["metrics"]
    assert "clicks" in response["metrics"]
    assert "engagement_rate" in response
    assert 0 <= response["engagement_rate"] <= 1


@pytest.mark.asyncio
async def test_get_post_insights_specific_metrics(facebook_mcp_client):
    """Test retrieving specific metrics."""
    result = await facebook_mcp_client.call_tool(
        "get_post_insights",
        arguments={
            "post_id": "test_page_id_123456789",
            "metrics": ["impressions", "reach"],
            "period": "day"
        }
    )

    response = json.loads(result.content[0].text)
    assert "metrics" in response


@pytest.mark.asyncio
async def test_get_post_insights_invalid_period(facebook_mcp_client):
    """Test retrieving insights with invalid period."""
    with pytest.raises(Exception) as exc_info:
        await facebook_mcp_client.call_tool(
            "get_post_insights",
            arguments={
                "post_id": "test_page_id_123456789",
                "period": "invalid_period"
            }
        )
    assert "period" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_post_insights_empty_post_id(facebook_mcp_client):
    """Test retrieving insights with empty post ID."""
    with pytest.raises(Exception) as exc_info:
        await facebook_mcp_client.call_tool(
            "get_post_insights",
            arguments={
                "post_id": ""
            }
        )
    assert "post_id" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()


# ============================================================================
# T032 (continued): Unit test for get_engagement_summary tool
# ============================================================================

@pytest.mark.asyncio
async def test_get_engagement_summary_success(facebook_mcp_client):
    """Test retrieving engagement summary."""
    result = await facebook_mcp_client.call_tool(
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
    assert "total_posts" in response["summary"]
    assert "total_impressions" in response["summary"]
    assert "total_reach" in response["summary"]
    assert "total_engagement" in response["summary"]
    assert "avg_engagement_rate" in response["summary"]
    assert "top_post" in response


@pytest.mark.asyncio
async def test_get_engagement_summary_with_posts(facebook_mcp_client):
    """Test retrieving engagement summary with individual posts."""
    result = await facebook_mcp_client.call_tool(
        "get_engagement_summary",
        arguments={
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
            "include_posts": True
        }
    )

    response = json.loads(result.content[0].text)
    assert "posts" in response


@pytest.mark.asyncio
async def test_get_engagement_summary_invalid_date_range(facebook_mcp_client):
    """Test engagement summary with invalid date range (start after end)."""
    with pytest.raises(Exception) as exc_info:
        await facebook_mcp_client.call_tool(
            "get_engagement_summary",
            arguments={
                "start_date": "2026-02-01",
                "end_date": "2026-01-01"
            }
        )
    # Note: This validation might be in the implementation
    # If not caught, the test will pass but should be implemented


@pytest.mark.asyncio
async def test_get_engagement_summary_invalid_date_format(facebook_mcp_client):
    """Test engagement summary with invalid date format."""
    with pytest.raises(Exception) as exc_info:
        await facebook_mcp_client.call_tool(
            "get_engagement_summary",
            arguments={
                "start_date": "01/01/2026",  # Wrong format
                "end_date": "2026-01-31"
            }
        )
    assert "date" in str(exc_info.value).lower() or "format" in str(exc_info.value).lower()


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_full_posting_workflow(facebook_mcp_client):
    """Test complete posting workflow: create post → get insights."""
    # Step 1: Create post
    create_result = await facebook_mcp_client.call_tool(
        "create_post",
        arguments={
            "message": "Integration test post for Facebook MCP"
        }
    )

    create_response = json.loads(create_result.content[0].text)
    post_id = create_response["post_id"]

    # Step 2: Get insights for the post
    insights_result = await facebook_mcp_client.call_tool(
        "get_post_insights",
        arguments={
            "post_id": post_id
        }
    )

    insights_response = json.loads(insights_result.content[0].text)
    assert insights_response["post_id"] == post_id
    assert "metrics" in insights_response


@pytest.mark.asyncio
async def test_health_check(facebook_mcp_client):
    """Test health check endpoint."""
    result = await facebook_mcp_client.call_tool("health_check", arguments={})

    response = json.loads(result.content[0].text)
    assert response["status"] == "healthy"
    assert "connection" in response
    assert "credentials" in response
    assert response["dry_run"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
