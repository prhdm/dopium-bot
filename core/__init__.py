"""Core application module."""
from core.bot import create_application
from core.lifecycle import get_post_init_callback

__all__ = ['create_application', 'get_post_init_callback']

