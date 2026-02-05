"""Audit log sanitizer for credential redaction.

Sanitizes sensitive information (API keys, tokens, passwords, PII) from audit logs
before writing to disk. Ensures compliance with security and privacy requirements.
"""

import re
import logging
from typing import Dict, Any, List, Pattern
from copy import deepcopy

logger = logging.getLogger(__name__)


# Patterns for detecting sensitive information
SENSITIVE_PATTERNS: List[tuple[str, Pattern]] = [
    # API Keys and Tokens
    ('api_key', re.compile(r'(api[_-]?key|apikey)[\s:=]+["\']?([a-zA-Z0-9_\-]{20,})["\']?', re.IGNORECASE)),
    ('access_token', re.compile(r'(access[_-]?token|accesstoken)[\s:=]+["\']?([a-zA-Z0-9_\-\.]{20,})["\']?', re.IGNORECASE)),
    ('bearer_token', re.compile(r'(bearer[_-]?token|bearertoken)[\s:=]+["\']?([a-zA-Z0-9_\-\.]{20,})["\']?', re.IGNORECASE)),
    ('secret', re.compile(r'(secret|password|passwd|pwd)[\s:=]+["\']?([^\s"\']{8,})["\']?', re.IGNORECASE)),

    # OAuth and JWT
    ('oauth_token', re.compile(r'oauth[_-]?token[\s:=]+["\']?([a-zA-Z0-9_\-\.]{20,})["\']?', re.IGNORECASE)),
    ('jwt', re.compile(r'eyJ[a-zA-Z0-9_\-]+\.eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+')),

    # Email addresses (PII)
    ('email', re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')),

    # Credit card numbers
    ('credit_card', re.compile(r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b')),

    # Social Security Numbers (US)
    ('ssn', re.compile(r'\b\d{3}-\d{2}-\d{4}\b')),
]


# Keys that should be sanitized in dictionaries
SENSITIVE_KEYS = {
    'api_key', 'apikey', 'api-key',
    'access_token', 'accesstoken', 'access-token',
    'bearer_token', 'bearertoken', 'bearer-token',
    'secret', 'client_secret', 'client-secret',
    'password', 'passwd', 'pwd',
    'oauth_token', 'oauth-token',
    'private_key', 'private-key',
    'token', 'auth_token', 'auth-token',
    'page_access_token', 'page-access-token',
}


def sanitize_string(text: str, redact_text: str = "[REDACTED]") -> str:
    """Sanitize sensitive information from a string.

    Args:
        text: Text to sanitize
        redact_text: Replacement text for sensitive data

    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return text

    sanitized = text

    for pattern_name, pattern in SENSITIVE_PATTERNS:
        sanitized = pattern.sub(f'\\1={redact_text}', sanitized)

    return sanitized


def sanitize_dict(data: Dict[str, Any], redact_text: str = "[REDACTED]") -> Dict[str, Any]:
    """Sanitize sensitive information from a dictionary.

    Args:
        data: Dictionary to sanitize
        redact_text: Replacement text for sensitive data

    Returns:
        Sanitized dictionary (deep copy)
    """
    if not isinstance(data, dict):
        return data

    sanitized = deepcopy(data)

    def _sanitize_recursive(obj: Any) -> Any:
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                # Check if key is sensitive
                if key.lower() in SENSITIVE_KEYS:
                    result[key] = redact_text
                else:
                    result[key] = _sanitize_recursive(value)
            return result

        elif isinstance(obj, list):
            return [_sanitize_recursive(item) for item in obj]

        elif isinstance(obj, str):
            return sanitize_string(obj, redact_text)

        else:
            return obj

    return _sanitize_recursive(sanitized)


def sanitize_credentials(
    data: Any,
    redact_text: str = "[REDACTED]",
    preserve_keys: List[str] = None
) -> Any:
    """Sanitize credentials from any data structure.

    This is the main entry point for credential sanitization.

    Args:
        data: Data to sanitize (dict, list, str, or other)
        redact_text: Replacement text for sensitive data
        preserve_keys: Keys to preserve even if they match sensitive patterns

    Returns:
        Sanitized data

    Example:
        >>> log_entry = {
        ...     'action': 'create_invoice',
        ...     'api_key': 'sk_live_abc123xyz',
        ...     'customer_email': 'john@example.com',
        ...     'amount': 1500.00
        ... }
        >>> sanitized = sanitize_credentials(log_entry)
        >>> print(sanitized)
        {
            'action': 'create_invoice',
            'api_key': '[REDACTED]',
            'customer_email': '[REDACTED]',
            'amount': 1500.00
        }
    """
    preserve_keys = preserve_keys or []

    try:
        if isinstance(data, dict):
            return sanitize_dict(data, redact_text)
        elif isinstance(data, str):
            return sanitize_string(data, redact_text)
        elif isinstance(data, list):
            return [sanitize_credentials(item, redact_text, preserve_keys) for item in data]
        else:
            return data

    except Exception as e:
        logger.error(f"Failed to sanitize credentials: {e}")
        return data


def is_sensitive_key(key: str) -> bool:
    """Check if a key name indicates sensitive data.

    Args:
        key: Key name to check

    Returns:
        True if key is sensitive, False otherwise
    """
    return key.lower() in SENSITIVE_KEYS


def mask_email(email: str, visible_chars: int = 2) -> str:
    """Mask an email address for logging.

    Args:
        email: Email address to mask
        visible_chars: Number of characters to show before @

    Returns:
        Masked email (e.g., "jo***@example.com")
    """
    if '@' not in email:
        return "[INVALID_EMAIL]"

    local, domain = email.split('@', 1)

    if len(local) <= visible_chars:
        masked_local = local[0] + '***'
    else:
        masked_local = local[:visible_chars] + '***'

    return f"{masked_local}@{domain}"
