"""Queue manager for offline operation resilience.

When external services (Odoo, social media APIs) are unavailable, operations
are queued locally in JSONL files and processed when services become available.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class QueueManager:
    """Manages local operation queues for offline resilience."""

    def __init__(self, queue_file: str):
        """Initialize queue manager.

        Args:
            queue_file: Path to JSONL queue file (e.g., ".odoo_queue.jsonl")
        """
        self.queue_file = Path(queue_file)
        self._ensure_queue_file()

    def _ensure_queue_file(self):
        """Ensure queue file exists."""
        if not self.queue_file.exists():
            self.queue_file.touch()
            logger.info(f"Created queue file: {self.queue_file}")

    def enqueue(self, operation: Dict[str, Any]) -> bool:
        """Add an operation to the queue.

        Args:
            operation: Operation data to queue (must be JSON-serializable)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Add timestamp if not present
            if 'queued_at' not in operation:
                operation['queued_at'] = datetime.utcnow().isoformat()

            # Append to JSONL file
            with open(self.queue_file, 'a') as f:
                f.write(json.dumps(operation) + '\n')

            logger.info(f"Queued operation: {operation.get('operation_type', 'unknown')}")
            return True

        except Exception as e:
            logger.error(f"Failed to enqueue operation: {e}")
            return False

    def dequeue_all(self) -> List[Dict[str, Any]]:
        """Retrieve all queued operations and clear the queue.

        Returns:
            List of queued operations
        """
        operations = []

        try:
            if not self.queue_file.exists() or self.queue_file.stat().st_size == 0:
                return operations

            # Read all operations
            with open(self.queue_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            operations.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            logger.error(f"Invalid JSON in queue: {e}")

            # Clear the queue file
            self.queue_file.write_text('')

            logger.info(f"Dequeued {len(operations)} operations")
            return operations

        except Exception as e:
            logger.error(f"Failed to dequeue operations: {e}")
            return operations

    def peek(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """View queued operations without removing them.

        Args:
            limit: Maximum number of operations to return (None = all)

        Returns:
            List of queued operations
        """
        operations = []

        try:
            if not self.queue_file.exists():
                return operations

            with open(self.queue_file, 'r') as f:
                for i, line in enumerate(f):
                    if limit and i >= limit:
                        break

                    line = line.strip()
                    if line:
                        try:
                            operations.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass

            return operations

        except Exception as e:
            logger.error(f"Failed to peek queue: {e}")
            return operations

    def count(self) -> int:
        """Count queued operations.

        Returns:
            Number of operations in queue
        """
        try:
            if not self.queue_file.exists():
                return 0

            with open(self.queue_file, 'r') as f:
                return sum(1 for line in f if line.strip())

        except Exception as e:
            logger.error(f"Failed to count queue: {e}")
            return 0

    def clear(self) -> bool:
        """Clear all queued operations.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.queue_file.write_text('')
            logger.info(f"Cleared queue: {self.queue_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear queue: {e}")
            return False


async def process_queue(
    queue_manager: QueueManager,
    processor_func: callable,
    max_retries: int = 3
) -> Dict[str, int]:
    """Process all queued operations.

    Args:
        queue_manager: QueueManager instance
        processor_func: Async function to process each operation
        max_retries: Maximum retries per operation

    Returns:
        Dict with 'processed', 'failed', 'requeued' counts
    """
    stats = {'processed': 0, 'failed': 0, 'requeued': 0}
    operations = queue_manager.dequeue_all()

    for operation in operations:
        try:
            await processor_func(operation)
            stats['processed'] += 1

        except Exception as e:
            logger.error(f"Failed to process queued operation: {e}")

            # Requeue if under retry limit
            retry_count = operation.get('retry_count', 0)
            if retry_count < max_retries:
                operation['retry_count'] = retry_count + 1
                queue_manager.enqueue(operation)
                stats['requeued'] += 1
            else:
                stats['failed'] += 1

    return stats
