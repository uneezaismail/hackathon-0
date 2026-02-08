"""Credential manager wrapper for secure credential storage.

Uses the system keyring (OS credential manager) to securely store and retrieve
API keys, tokens, and passwords. Credentials are never stored in plain text.
"""

import keyring
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CredentialManager:
    """Secure credential storage using OS keyring."""

    def __init__(self, service_name: str = "ai_employee"):
        """Initialize credential manager.

        Args:
            service_name: Service name for keyring storage (default: "ai_employee")
        """
        self.service_name = service_name

    def store(self, key: str, value: str) -> bool:
        """Store a credential securely.

        Args:
            key: Credential identifier (e.g., "odoo_api_key")
            value: Credential value to store

        Returns:
            True if successful, False otherwise
        """
        try:
            keyring.set_password(self.service_name, key, value)
            logger.info(f"Stored credential: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to store credential {key}: {e}")
            return False

    def retrieve(self, key: str) -> Optional[str]:
        """Retrieve a credential securely.

        Args:
            key: Credential identifier

        Returns:
            Credential value if found, None otherwise
        """
        try:
            value = keyring.get_password(self.service_name, key)
            if value:
                logger.debug(f"Retrieved credential: {key}")
            else:
                logger.warning(f"Credential not found: {key}")
            return value
        except Exception as e:
            logger.error(f"Failed to retrieve credential {key}: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete a credential.

        Args:
            key: Credential identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            keyring.delete_password(self.service_name, key)
            logger.info(f"Deleted credential: {key}")
            return True
        except keyring.errors.PasswordDeleteError:
            logger.warning(f"Credential not found for deletion: {key}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete credential {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if a credential exists.

        Args:
            key: Credential identifier

        Returns:
            True if credential exists, False otherwise
        """
        return self.retrieve(key) is not None


# Convenience functions for common credential operations
def store_credential(key: str, value: str, service: str = "ai_employee") -> bool:
    """Store a credential (convenience function)."""
    manager = CredentialManager(service)
    return manager.store(key, value)


def get_credential(key: str, service: str = "ai_employee") -> Optional[str]:
    """Retrieve a credential (convenience function)."""
    manager = CredentialManager(service)
    return manager.retrieve(key)


def delete_credential(key: str, service: str = "ai_employee") -> bool:
    """Delete a credential (convenience function)."""
    manager = CredentialManager(service)
    return manager.delete(key)
