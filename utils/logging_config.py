"""
Centralized Logging Configuration
==================================
Single source of truth for logging setup across all modules.
Import and call setup_logging() once at application startup.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Track if logging has been configured
_logging_configured = False


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Configure logging for the entire application.
    Should be called once at startup.

    Args:
        level: Logging level (default: INFO)
        log_file: Optional path to log file
        format_string: Optional custom format string

    Returns:
        Root logger instance
    """
    global _logging_configured

    if _logging_configured:
        return logging.getLogger()

    # Default format
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(format_string)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear any existing handlers
    root_logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    _logging_configured = True

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    Use this instead of logging.getLogger() directly.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def reset_logging():
    """Reset logging configuration. Mainly for testing."""
    global _logging_configured
    _logging_configured = False
    logging.getLogger().handlers = []
