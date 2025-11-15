"""
Logger Module
Centralized logging system for the entire application
"""

from loguru import logger
import sys
from src.config import LOG_FILE, LOG_LEVEL, LOG_FORMAT

# Remove default handler
logger.remove()

# Add console handler (colorful output)
logger.add(
    sys.stdout,
    format=LOG_FORMAT,
    level=LOG_LEVEL,
    colorize=True
)

# Add file handler (persistent logs)
logger.add(
    LOG_FILE,
    format=LOG_FORMAT,
    level=LOG_LEVEL,
    rotation="500 MB",  # Rotate when file reaches 500MB
    retention="7 days"   # Keep logs for 7 days
)

# Export logger for use in other modules
__all__ = ['logger']