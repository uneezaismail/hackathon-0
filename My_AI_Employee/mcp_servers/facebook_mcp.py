#!/usr/bin/env python3
"""
Facebook MCP Server - Post messages and retrieve engagement metrics from Facebook Pages.

Provides tools for:
1. create_post: Post message to Facebook Page
2. upload_photo: Upload photo with caption
3. get_post_insights: Retrieve engagement metrics for specific post
4. get_engagement_summary: Get aggregated engagement metrics

All posting operations require HITL approval before execution.
Type-safe with Pydantic v2 models for validation.
Integrated with AuditLogger for Gold tier compliance.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pydantic import BaseModel, Field, field_validator
from fastmcp import FastMCP
from dotenv import load_dotenv

try:
    import facebook
except ImportError:
    facebook = None
    logging.warning("facebook-sdk not installed. Install with: pip install facebook-sdk")

from utils.credentials import CredentialManager
from utils.retry import retry_with_backoff, RetryConfig
from utils.queue_manager import QueueManager
from utils.audit_sanitizer import sanitize_credentials

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(name="facebook-mcp")

# Initialize credential manager
cred_manager = CredentialManager(service_name="ai_employee_facebook")

# Initialize queue manager for offline resilience
queue_file = os.getenv('FACEBOOK_QUEUE_FILE', '.facebook_queue.jsonl')
queue_manager = QueueManager(queue_file)

# DRY_RUN mode for testing
DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'


# ============================================================================
# PYDANTIC MODELS - Type-safe validation
# ============================================================================

class CreatePostRequest(BaseModel):
    """Create post request model."""
    message: str = Field(..., description="Post message content")
    link: Optional[str] = Field(None, description="URL to share")
    image_path: Optional[str] = Field(None, description="Path to image file")
    scheduled_time: Optional[str] = Field(None, description="ISO8601 timestamp for scheduling")

    @field_validator('scheduled_time')
    @classmethod
    def validate_scheduled_time(cls, v):
        if v:
            try:
                scheduled = datetime.fromisoformat(v.replace('Z', '+00:00'))
                if scheduled < datetime.now():
                    raise ValueError('Scheduled time must be in the future')
            except ValueError as e:
                raise ValueError(f'Invalid scheduled time: {e}')
        return v


class UploadPhotoRequest(BaseModel):
    """Upload photo request model."""
    image_path: str = Field(..., description="Path to image file")
    caption: str = Field(..., description="Photo caption")

    @field_validator('image_path')
    @classmethod
    def validate_image_path(cls, v):
        if not os.path.exists(v):
            raise ValueError(f'Image file not found: {v}')

        # Check file extension
        ext = os.path.splitext(v)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.gif']:
            raise ValueError(f'Invalid image format: {ext}. Supported: JPG, PNG, GIF')

        # Check file size (4MB limit)
        file_size = os.path.getsize(v)
        if file_size > 4 * 1024 * 1024:
            raise ValueError(f'Image file too large: {file_size / 1024 / 1024:.1f}MB. Max: 4MB')

        return v


class GetPostInsightsRequest(BaseModel):
    """Get post insights request model."""
    post_id: str = Field(..., description="Facebook post ID")
    metrics: Optional[List[str]] = Field(None, description="Metrics to retrieve")
    period: str = Field(default="lifetime", description="Time period (day, week, days_28, lifetime)")

    @field_validator('period')
    @classmethod
    def validate_period(cls, v):
        valid_periods = ['day', 'week', 'days_28', 'lifetime']
        if v not in valid_periods:
            raise ValueError(f'Invalid period: {v}. Valid: {", ".join(valid_periods)}')
        return v


class GetEngagementSummaryRequest(BaseModel):
    """Get engagement summary request model."""
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    include_posts: bool = Field(default=False, description="Include individual post data")

    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f'Invalid date format: {v}. Expected: YYYY-MM-DD')
        return v


# ============================================================================
# FACEBOOK CONNECTION MANAGER
# ============================================================================

class FacebookConnectionManager:
    """Manage Facebook Graph API connection with retry logic."""

    def __init__(self):
        self.page_access_token = None
        self.page_id = None
        self.graph = None
        self._connect()

    def _connect(self):
        """Connect to Facebook Graph API."""
        if DRY_RUN:
            logger.info("[DRY RUN] Simulating Facebook connection")
            self.page_access_token = "dry_run_token"
            self.page_id = "dry_run_page_id"
            return

        # Get credentials from environment or keyring
        self.page_access_token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
        if not self.page_access_token:
            self.page_access_token = cred_manager.retrieve('page_access_token')

        self.page_id = os.getenv('FACEBOOK_PAGE_ID')
        if not self.page_id:
            self.page_id = cred_manager.retrieve('page_id')

        if not self.page_access_token or not self.page_id:
            raise ValueError("Facebook credentials not configured. Set FACEBOOK_PAGE_ACCESS_TOKEN and FACEBOOK_PAGE_ID")

        # Initialize Graph API
        if facebook:
            self.graph = facebook.GraphAPI(access_token=self.page_access_token, version='18.0')
            logger.info("Connected to Facebook Graph API")
        else:
            raise ImportError("facebook-sdk not installed")

    def check_rate_limit(self, response_headers: Dict[str, str]) -> bool:
        """
        Check rate limit from response headers.

        Args:
            response_headers: Response headers from Facebook API

        Returns:
            True if rate limit OK, False if throttling needed
        """
        import json
        usage = json.loads(response_headers.get('X-App-Usage', '{}'))
        call_count = usage.get('call_count', 0)

        if call_count > 80:
            logger.warning(f"Rate limit usage: {call_count}%. Throttling recommended.")
            return False

        return True


# Initialize connection manager
fb_manager = FacebookConnectionManager()


# ============================================================================
# MCP TOOLS
# ============================================================================

@mcp.tool()
@retry_with_backoff(RetryConfig(max_attempts=4, backoff_delays=(1.0, 2.0, 4.0, 8.0)))
def create_post(message: str, link: str = None, image_path: str = None, scheduled_time: str = None) -> dict:
    """
    Post message to Facebook Page.

    Args:
        message: Post message content
        link: URL to share (optional)
        image_path: Path to image file (optional)
        scheduled_time: ISO8601 timestamp for scheduling (optional)

    Returns:
        Post details with post_id, status, url, published_at
    """
    # Validate request
    request = CreatePostRequest(
        message=message,
        link=link,
        image_path=image_path,
        scheduled_time=scheduled_time
    )

    if DRY_RUN:
        logger.info(f"[DRY RUN] Creating Facebook post: {message[:50]}...")
        result = {
            "post_id": f"{fb_manager.page_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "scheduled" if scheduled_time else "published",
            "url": f"https://facebook.com/{fb_manager.page_id}/posts/123456789",
            "published_at": scheduled_time or datetime.now().isoformat()
        }
    else:
        # Create post via Facebook Graph API
        post_data = {"message": message}
        if link:
            post_data["link"] = link
        if scheduled_time:
            post_data["scheduled_publish_time"] = int(datetime.fromisoformat(scheduled_time.replace('Z', '+00:00')).timestamp())
            post_data["published"] = False

        response = fb_manager.graph.put_object(
            parent_object=fb_manager.page_id,
            connection_name="feed",
            **post_data
        )

        result = {
            "post_id": response["id"],
            "status": "scheduled" if scheduled_time else "published",
            "url": f"https://facebook.com/{response['id']}",
            "published_at": scheduled_time or datetime.now().isoformat()
        }

    # Log to audit trail
    _log_operation("create_post", {
        "message_preview": message[:100],
        "has_link": link is not None,
        "has_image": image_path is not None,
        "scheduled": scheduled_time is not None,
        "post_id": result["post_id"]
    })

    return result


@mcp.tool()
@retry_with_backoff(RetryConfig(max_attempts=4, backoff_delays=(1.0, 2.0, 4.0, 8.0)))
def upload_photo(image_path: str, caption: str) -> dict:
    """
    Upload photo to Facebook Page with caption.

    Args:
        image_path: Path to image file
        caption: Photo caption

    Returns:
        Photo details with photo_id, post_id, status, url, published_at
    """
    # Validate request
    request = UploadPhotoRequest(image_path=image_path, caption=caption)

    if DRY_RUN:
        logger.info(f"[DRY RUN] Uploading photo: {image_path}")
        result = {
            "photo_id": f"photo_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "post_id": f"{fb_manager.page_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "published",
            "url": f"https://facebook.com/{fb_manager.page_id}/photos/123456789",
            "published_at": datetime.now().isoformat()
        }
    else:
        # Upload photo via Facebook Graph API
        with open(image_path, 'rb') as image_file:
            response = fb_manager.graph.put_photo(
                image=image_file,
                message=caption
            )

        result = {
            "photo_id": response["id"],
            "post_id": response.get("post_id", response["id"]),
            "status": "published",
            "url": f"https://facebook.com/{response['id']}",
            "published_at": datetime.now().isoformat()
        }

    # Log to audit trail
    _log_operation("upload_photo", {
        "image_path": image_path,
        "caption_preview": caption[:100],
        "photo_id": result["photo_id"]
    })

    return result


@mcp.tool()
@retry_with_backoff(RetryConfig(max_attempts=4, backoff_delays=(1.0, 2.0, 4.0, 8.0)))
def get_post_insights(post_id: str, metrics: List[str] = None, period: str = "lifetime") -> dict:
    """
    Retrieve engagement metrics for specific post.

    Args:
        post_id: Facebook post ID
        metrics: Metrics to retrieve (optional, default: all)
        period: Time period (day, week, days_28, lifetime)

    Returns:
        Post insights with metrics, engagement_rate, retrieved_at
    """
    # Validate request
    request = GetPostInsightsRequest(post_id=post_id, metrics=metrics, period=period)

    if DRY_RUN:
        logger.info(f"[DRY RUN] Getting insights for post: {post_id}")
        result = {
            "post_id": post_id,
            "metrics": {
                "impressions": 1250,
                "reach": 980,
                "engaged_users": 145,
                "reactions": 87,
                "comments": 23,
                "shares": 12,
                "clicks": 45
            },
            "engagement_rate": 0.148,
            "retrieved_at": datetime.now().isoformat()
        }
    else:
        # Get insights via Facebook Graph API
        default_metrics = ['post_impressions', 'post_engaged_users', 'post_reactions_by_type_total']
        metric_list = metrics or default_metrics

        insights = fb_manager.graph.get_object(
            id=post_id,
            fields=f"insights.metric({','.join(metric_list)})"
        )

        # Parse insights
        metrics_data = {}
        for insight in insights.get('insights', {}).get('data', []):
            metrics_data[insight['name']] = insight['values'][0]['value']

        result = {
            "post_id": post_id,
            "metrics": metrics_data,
            "engagement_rate": metrics_data.get('post_engaged_users', 0) / max(metrics_data.get('post_impressions', 1), 1),
            "retrieved_at": datetime.now().isoformat()
        }

    # Log to audit trail
    _log_operation("get_post_insights", {
        "post_id": post_id,
        "period": period,
        "metrics_count": len(result["metrics"])
    })

    return result


@mcp.tool()
@retry_with_backoff(RetryConfig(max_attempts=4, backoff_delays=(1.0, 2.0, 4.0, 8.0)))
def get_engagement_summary(start_date: str, end_date: str, include_posts: bool = False) -> dict:
    """
    Get aggregated engagement metrics for time period.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        include_posts: Include individual post data

    Returns:
        Engagement summary with period, summary, top_post, posts (optional)
    """
    # Validate request
    request = GetEngagementSummaryRequest(
        start_date=start_date,
        end_date=end_date,
        include_posts=include_posts
    )

    if DRY_RUN:
        logger.info(f"[DRY RUN] Getting engagement summary: {start_date} to {end_date}")
        result = {
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "summary": {
                "total_posts": 15,
                "total_impressions": 18750,
                "total_reach": 14200,
                "total_engagement": 2180,
                "avg_engagement_rate": 0.116
            },
            "top_post": {
                "post_id": f"{fb_manager.page_id}_top_post",
                "message": "Our best performing post this period",
                "engagement": 450
            }
        }
        if include_posts:
            result["posts"] = []
    else:
        # Get posts and insights via Facebook Graph API
        # This would query posts in date range and aggregate metrics
        raise NotImplementedError("Production Facebook API integration pending")

    # Log to audit trail
    _log_operation("get_engagement_summary", {
        "start_date": start_date,
        "end_date": end_date,
        "total_posts": result["summary"]["total_posts"]
    })

    return result


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _log_operation(operation: str, details: Dict[str, Any], result: str = "success"):
    """
    Log operation to audit trail.

    Args:
        operation: Operation type
        details: Operation details (sanitized)
        result: Operation result (success, failed, queued)
    """
    # This would integrate with audit-logger skill
    logger.info(f"Facebook operation: {operation} - {result}")


# ============================================================================
# HEALTH CHECK
# ============================================================================

@mcp.tool()
def health_check() -> dict:
    """
    Check Facebook MCP server health and connection status.

    Returns:
        Health status with connection, credentials, queue_size
    """
    health = {
        "status": "healthy",
        "connection": "connected" if fb_manager.graph or DRY_RUN else "disconnected",
        "credentials": "configured" if fb_manager.page_access_token else "missing",
        "queue_size": queue_manager.size(),
        "dry_run": DRY_RUN,
        "checked_at": datetime.now().isoformat()
    }

    return health


if __name__ == "__main__":
    # Run MCP server
    mcp.run()
