"""Handlers module."""
from handlers.commands import register_command_handlers
from handlers.messages import register_message_handlers
from handlers.keyboard import register_keyboard_handlers

__all__ = ['register_command_handlers', 'register_message_handlers', 'register_keyboard_handlers']

