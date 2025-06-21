"""
UI package for GenAI Desktop Client.

This package contains all user interface components including the main window,
dialogs, and specialized widgets for the desktop application.
"""

from .main_window import MainWindow
from .session_manager import SessionManager
from .settings_dialog import SettingsDialog

__all__ = [
    'MainWindow',
    'SessionManager',
    'SettingsDialog'
]
