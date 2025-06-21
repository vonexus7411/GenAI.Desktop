"""
Utils package for GenAI Desktop Client.

This package contains utility modules for configuration management,
logging, file operations, and other helper functions.
"""

from .config import ConfigManager, config_manager, PERSONAS

__all__ = [
    'ConfigManager',
    'config_manager',
    'PERSONAS'
]
