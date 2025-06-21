"""
Models package for GenAI Desktop Client.

This package contains data models for chat sessions, messages, and other core data structures.
"""

from .message import Message, MessageRole
from .chat_session import ChatSession

__all__ = [
    'Message',
    'MessageRole',
    'ChatSession'
]
