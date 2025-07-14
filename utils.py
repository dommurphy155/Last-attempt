import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def log_action(action, details=None):
    msg = f"ACTION: {action}"
    if details:
        msg += f" | Details: {details}"
    logger.info(msg)

def log_error(error, details=None):
    msg = f"ERROR: {error}"
    if details:
        msg += f" | Details: {details}"
    logger.error(msg)

def get_recent_logs(n=5):
    # Placeholder: In production, this should read from a log file or buffer
    return []

def format_currency(value):
    return f"${value:,.2f}"

def format_percentage(value):
    return f"{value:.2f}%"