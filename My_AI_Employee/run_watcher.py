#!/usr/bin/env python3
"""
Entrypoint script for running the filesystem watcher.

Usage:
    python -m My_AI_Employee.run_watcher --vault-path <path> --watch-folder <path>
    python -m My_AI_Employee.run_watcher  # Uses .env configuration

Environment variables (from .env):
    VAULT_PATH: Path to Obsidian vault root
    WATCH_FOLDER: Path to folder to watch for new files
    WATCH_MODE: "events" or "polling" (default: events)
    LOG_LEVEL: Logging level (default: INFO)
"""

import argparse
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

from watchers.filesystem_watcher import FilesystemWatcher


def setup_logging(level: str = "INFO") -> None:
    """
    Configure logging for the watcher.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Run the filesystem watcher for Bronze Tier AI Employee",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use .env configuration
  python -m My_AI_Employee.run_watcher

  # Override with command-line arguments
  python -m My_AI_Employee.run_watcher \\
    --vault-path My_AI_Employee/AI_Employee_Vault \\
    --watch-folder /path/to/watch

  # Use polling mode (for WSL/network drives)
  python -m My_AI_Employee.run_watcher --watch-mode polling
        """
    )

    parser.add_argument(
        '--vault-path',
        type=str,
        help='Path to Obsidian vault root (overrides VAULT_PATH env var)'
    )

    parser.add_argument(
        '--watch-folder',
        type=str,
        help='Path to folder to watch for new files (overrides WATCH_FOLDER env var)'
    )

    parser.add_argument(
        '--watch-mode',
        type=str,
        choices=['events', 'polling'],
        help='Watch mode: "events" for native events, "polling" for polling (overrides WATCH_MODE env var)'
    )

    parser.add_argument(
        '--check-interval',
        type=int,
        default=60,
        help='Seconds between checks in polling mode (default: 60)'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (overrides LOG_LEVEL env var)'
    )

    return parser.parse_args()


def load_config(args: argparse.Namespace) -> dict:
    """
    Load configuration from .env and command-line arguments.

    Command-line arguments take precedence over environment variables.

    Args:
        args: Parsed command-line arguments

    Returns:
        Configuration dictionary

    Raises:
        ValueError: If required configuration is missing
    """
    # Load .env file if it exists
    load_dotenv()

    # Get configuration with precedence: CLI args > env vars > defaults
    config = {
        'vault_path': args.vault_path or os.getenv('VAULT_PATH'),
        'watch_folder': args.watch_folder or os.getenv('WATCH_FOLDER'),
        'watch_mode': args.watch_mode or os.getenv('WATCH_MODE', 'events'),
        'check_interval': args.check_interval,
        'log_level': args.log_level or os.getenv('LOG_LEVEL', 'INFO')
    }

    # Validate required configuration
    if not config['vault_path']:
        raise ValueError(
            "VAULT_PATH must be set in .env or provided via --vault-path"
        )

    if not config['watch_folder']:
        raise ValueError(
            "WATCH_FOLDER must be set in .env or provided via --watch-folder"
        )

    # Convert paths to absolute paths
    config['vault_path'] = Path(config['vault_path']).resolve()
    config['watch_folder'] = Path(config['watch_folder']).resolve()

    return config


def main() -> int:
    """
    Main entrypoint for the watcher.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Parse arguments
        args = parse_args()

        # Load configuration
        config = load_config(args)

        # Setup logging
        setup_logging(config['log_level'])
        logger = logging.getLogger(__name__)

        # Log configuration
        logger.info("=" * 60)
        logger.info("Bronze Tier AI Employee - Filesystem Watcher")
        logger.info("=" * 60)
        logger.info(f"Vault path: {config['vault_path']}")
        logger.info(f"Watch folder: {config['watch_folder']}")
        logger.info(f"Watch mode: {config['watch_mode']}")
        logger.info(f"Check interval: {config['check_interval']}s")
        logger.info(f"Log level: {config['log_level']}")
        logger.info("=" * 60)

        # Validate paths exist
        if not config['vault_path'].exists():
            logger.error(f"Vault path does not exist: {config['vault_path']}")
            logger.error("Please create the vault first or check the path")
            return 1

        if not config['watch_folder'].exists():
            logger.error(f"Watch folder does not exist: {config['watch_folder']}")
            logger.error("Please create the watch folder or check the path")
            return 1

        # Create and run watcher
        watcher = FilesystemWatcher(
            vault_path=config['vault_path'],
            watch_folder=config['watch_folder'],
            watch_mode=config['watch_mode'],
            check_interval=config['check_interval']
        )

        # Run watcher (blocks until Ctrl+C)
        watcher.run()

        return 0

    except KeyboardInterrupt:
        logger = logging.getLogger(__name__)
        logger.info("\nWatcher stopped by user")
        return 0

    except ValueError as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Configuration error: {e}")
        return 1

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
