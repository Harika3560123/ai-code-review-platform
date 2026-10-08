from typing import Optional
import logging

logger = logging.getLogger(__name__)

def calculate_ratio(numerator: float, denominator: float) -> Optional[float]:
    """Calculate ratio between two numbers safely."""
    if denominator == 0:
        logger.warning("Attempted division by zero; returning None.")
        return None
    return numerator / denominator

def greet_user(name: str) -> str:
    """Format a clean greeting message for the user."""
    safe_name = name.strip()
    return f"Hello, {safe_name}!"
