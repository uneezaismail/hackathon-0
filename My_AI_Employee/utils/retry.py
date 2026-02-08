"""Retry utility with exponential backoff for transient errors.

This module provides retry logic for handling transient failures like:
- Network timeouts
- API rate limits
- Temporary service unavailability
"""

import asyncio
import time
from typing import Callable, TypeVar, Optional, Type, Tuple
from functools import wraps
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 4,
        backoff_delays: Tuple[float, ...] = (1.0, 2.0, 4.0, 8.0),
        retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
        non_retryable_exceptions: Tuple[Type[Exception], ...] = (),
    ):
        """Initialize retry configuration.

        Args:
            max_attempts: Maximum number of retry attempts (default: 4)
            backoff_delays: Delay in seconds between retries (default: 1s, 2s, 4s, 8s)
            retryable_exceptions: Exceptions that should trigger retry
            non_retryable_exceptions: Exceptions that should NOT be retried
        """
        self.max_attempts = max_attempts
        self.backoff_delays = backoff_delays
        self.retryable_exceptions = retryable_exceptions
        self.non_retryable_exceptions = non_retryable_exceptions


def retry_with_backoff(
    config: Optional[RetryConfig] = None,
    operation_name: str = "operation"
):
    """Decorator for retrying operations with exponential backoff.

    Args:
        config: RetryConfig instance (uses defaults if None)
        operation_name: Name of operation for logging

    Example:
        @retry_with_backoff(operation_name="create_invoice")
        async def create_invoice(data):
            # API call that might fail transiently
            return await odoo_api.create(data)
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)

                except config.non_retryable_exceptions as e:
                    # Don't retry these exceptions
                    logger.error(
                        f"{operation_name} failed with non-retryable error: {e}"
                    )
                    raise

                except config.retryable_exceptions as e:
                    last_exception = e

                    if attempt < config.max_attempts - 1:
                        delay = config.backoff_delays[min(attempt, len(config.backoff_delays) - 1)]
                        logger.warning(
                            f"{operation_name} attempt {attempt + 1}/{config.max_attempts} "
                            f"failed: {e}. Retrying in {delay}s..."
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"{operation_name} failed after {config.max_attempts} attempts: {e}"
                        )

            # All retries exhausted
            raise last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)

                except config.non_retryable_exceptions as e:
                    logger.error(
                        f"{operation_name} failed with non-retryable error: {e}"
                    )
                    raise

                except config.retryable_exceptions as e:
                    last_exception = e

                    if attempt < config.max_attempts - 1:
                        delay = config.backoff_delays[min(attempt, len(config.backoff_delays) - 1)]
                        logger.warning(
                            f"{operation_name} attempt {attempt + 1}/{config.max_attempts} "
                            f"failed: {e}. Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"{operation_name} failed after {config.max_attempts} attempts: {e}"
                        )

            raise last_exception

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
