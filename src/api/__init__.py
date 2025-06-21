"""
API package for GenAI Desktop Client.

This package contains API clients for communicating with external services,
primarily the LM Studio REST API.
"""

from .lm_studio_client import LMStudioClient, LMStudioAPIError

__all__ = [
    'LMStudioClient',
    'LMStudioAPIError'
]
