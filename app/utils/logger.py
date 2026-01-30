"""
Project Prism - Enhanced Logger
===============================
Comprehensive logging with DEBUG level for troubleshooting.
Logs to: /app/logs/prism_debug.log
"""

import logging
import os
import sys
import traceback
from logging.handlers import RotatingFileHandler
from datetime import datetime
from functools import wraps

# Log configuration
LOG_DIR = "/app/logs"
LOG_FILE = os.path.join(LOG_DIR, "prism_debug.log")
MAX_BYTES = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Create logger
logger = logging.getLogger("prism")
logger.setLevel(logging.DEBUG)  # Capture everything

# Clear existing handlers
logger.handlers = []

# File handler - captures DEBUG and above
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=MAX_BYTES,
    backupCount=BACKUP_COUNT,
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)

# Detailed format for file
file_format = logging.Formatter(
    fmt='%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_format)
logger.addHandler(file_handler)

# Console handler - INFO and above only
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)


def log_exception(e: Exception, context: str = ""):
    """
    Log an exception with full traceback.
    
    Args:
        e: The exception
        context: Additional context about where/what failed
    """
    tb = traceback.format_exc()
    logger.error(f"{'='*60}")
    logger.error(f"EXCEPTION: {type(e).__name__}: {str(e)}")
    if context:
        logger.error(f"CONTEXT: {context}")
    logger.error(f"TRACEBACK:\n{tb}")
    logger.error(f"{'='*60}")


def log_function_call(func):
    """
    Decorator to log function entry, exit, and any exceptions.
    Use on functions you want to trace.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.debug(f"→ ENTER: {func_name}(args={args[:2] if args else ''}, kwargs={list(kwargs.keys())})")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"← EXIT: {func_name} → success")
            return result
        except Exception as e:
            log_exception(e, f"Function: {func_name}")
            raise
    return wrapper


def log_page_load(page_name: str):
    """Log when a page is loaded."""
    logger.info(f"📄 PAGE LOAD: {page_name}")


def log_user_action(action: str, details: str = ""):
    """Log user actions for debugging."""
    logger.info(f"👤 USER ACTION: {action} | {details}" if details else f"👤 USER ACTION: {action}")


def log_db_operation(operation: str, success: bool, details: str = ""):
    """Log database operations."""
    status = "✓" if success else "✗"
    level = logging.DEBUG if success else logging.ERROR
    logger.log(level, f"🗄️ DB {status}: {operation} | {details}" if details else f"🗄️ DB {status}: {operation}")


# Log startup
logger.info("="*60)
logger.info(f"PRISM LOGGER INITIALIZED | {datetime.now().isoformat()}")
logger.info(f"Log file: {LOG_FILE}")
logger.info("="*60)
