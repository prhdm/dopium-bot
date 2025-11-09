"""Tracking code generator."""
import random
import string


def generate_tracking_code(length: int = 5) -> str:
    """
    Generate a random tracking code.
    
    Args:
        length: Length of the tracking code (default: 5)
        
    Returns:
        Random uppercase alphanumeric code
    """
    # Use uppercase letters and numbers (excluding confusing characters like 0, O, I, 1)
    characters = string.ascii_uppercase.replace('O', '').replace('I', '') + '23456789'
    return ''.join(random.choice(characters) for _ in range(length))




