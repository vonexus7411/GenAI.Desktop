#!/usr/bin/env python3
"""
Main application entry point for GenAI Desktop Client.

This module initializes and runs the desktop application for interfacing with LM Studio's REST API.
"""

import sys
import os
import asyncio
import logging
from pathlib import Path
from typing import Optional

# Add src directory to Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

try:
    from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QIcon, QPixmap, QFont
except ImportError as e:
    print(f"Error: PyQt5 not found. Please install PyQt5: pip install PyQt5")
    print(f"Import error: {e}")
    sys.exit(1)

from ui.main_window import MainWindow
from utils.config import config_manager


def setup_logging():
    """Setup application logging."""
    log_dir = config_manager.get_config_directory() / 'logs'
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / 'genai_client.log'

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Create logger
    logger = logging.getLogger(__name__)
    logger.info("GenAI Desktop starting...")

    return logger


def check_dependencies():
    """Check if all required dependencies are available."""
    required_modules = [
        'PyQt5',
        'requests',
        'aiohttp',
        'json',
        'pathlib',
        'datetime'
    ]

    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        return False, missing_modules

    return True, []


def create_splash_screen():
    """Create and display splash screen."""
    # Create a simple splash screen
    splash_pix = QPixmap(400, 300)
    splash_pix.fill(Qt.white)

    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())

    # Add some text to splash screen
    splash.showMessage(
        "GenAI Desktop\nLoading...",
        Qt.AlignCenter | Qt.AlignBottom,
        Qt.black
    )

    splash.show()
    return splash


def setup_application_style(app: QApplication):
    """Setup application-wide styling and theme."""
    # Set application properties
    app.setApplicationName("GenAI Desktop")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("GenAI")
    app.setOrganizationDomain("genai.desktop")

    # Set default font
    ui_config = config_manager.ui_config
    font = QFont(ui_config.font_family, ui_config.font_size)
    app.setFont(font)

    # Apply theme if specified
    if ui_config.theme == "dark":
        apply_dark_theme(app)
    elif ui_config.theme == "light":
        apply_light_theme(app)


def apply_dark_theme(app: QApplication):
    """Apply dark theme to the application."""
    dark_stylesheet = """
    QMainWindow {
        background-color: #2b2b2b;
        color: #ffffff;
    }

    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
    }

    QTextEdit {
        background-color: #1e1e1e;
        color: #ffffff;
        border: 1px solid #555555;
    }

    QLineEdit {
        background-color: #1e1e1e;
        color: #ffffff;
        border: 1px solid #555555;
        padding: 5px;
    }

    QPushButton {
        background-color: #0e639c;
        color: #ffffff;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
    }

    QPushButton:hover {
        background-color: #1177bb;
    }

    QPushButton:pressed {
        background-color: #0a507a;
    }

    QPushButton:disabled {
        background-color: #555555;
        color: #888888;
    }

    QComboBox {
        background-color: #1e1e1e;
        color: #ffffff;
        border: 1px solid #555555;
        padding: 5px;
    }

    QListWidget {
        background-color: #1e1e1e;
        color: #ffffff;
        border: 1px solid #555555;
    }

    QListWidget::item:selected {
        background-color: #0e639c;
    }

    QGroupBox {
        font-weight: bold;
        border: 2px solid #555555;
        border-radius: 5px;
        margin-top: 1ex;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
    }

    QStatusBar {
        background-color: #1e1e1e;
        color: #ffffff;
    }

    QMenuBar {
        background-color: #2b2b2b;
        color: #ffffff;
    }

    QMenuBar::item:selected {
        background-color: #0e639c;
    }

    QMenu {
        background-color: #2b2b2b;
        color: #ffffff;
        border: 1px solid #555555;
    }

    QMenu::item:selected {
        background-color: #0e639c;
    }
    """

    app.setStyleSheet(dark_stylesheet)


def apply_light_theme(app: QApplication):
    """Apply light theme to the application."""
    light_stylesheet = """
    QMainWindow {
        background-color: #ffffff;
        color: #000000;
    }

    QWidget {
        background-color: #ffffff;
        color: #000000;
    }

    QTextEdit {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #cccccc;
    }

    QLineEdit {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #cccccc;
        padding: 5px;
    }

    QPushButton {
        background-color: #0078d4;
        color: #ffffff;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
    }

    QPushButton:hover {
        background-color: #106ebe;
    }

    QPushButton:pressed {
        background-color: #005a9e;
    }

    QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
    }

    QComboBox {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #cccccc;
        padding: 5px;
    }

    QListWidget {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #cccccc;
    }

    QListWidget::item:selected {
        background-color: #0078d4;
        color: #ffffff;
    }

    QGroupBox {
        font-weight: bold;
        border: 2px solid #cccccc;
        border-radius: 5px;
        margin-top: 1ex;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
    }
    """

    app.setStyleSheet(light_stylesheet)


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger = logging.getLogger(__name__)
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    # Show error dialog if QApplication exists
    if QApplication.instance():
        error_msg = f"An unexpected error occurred:\n\n{exc_type.__name__}: {exc_value}"
        QMessageBox.critical(None, "Unexpected Error", error_msg)


def main():
    """Main application entry point."""
    # Set up global exception handling
    sys.excepthook = handle_exception

    # Setup logging
    logger = setup_logging()

    try:
        # Check dependencies
        deps_ok, missing = check_dependencies()
        if not deps_ok:
            print(f"Missing required dependencies: {', '.join(missing)}")
            print("Please install missing dependencies and try again.")
            return 1

        # Create QApplication
        app = QApplication(sys.argv)

        # Create splash screen
        splash = create_splash_screen()

        # Process events to show splash screen
        app.processEvents()

        # Setup application styling
        setup_application_style(app)

        # Update splash screen
        splash.showMessage(
            "GenAI Desktop\nInitializing components...",
            Qt.AlignCenter | Qt.AlignBottom,
            Qt.black
        )
        app.processEvents()

        # Create main window
        try:
            main_window = MainWindow()
        except Exception as e:
            logger.error(f"Failed to create main window: {e}")
            splash.close()
            QMessageBox.critical(None, "Initialization Error",
                               f"Failed to initialize the application:\n{str(e)}")
            return 1

        # Update splash screen
        splash.showMessage(
            "GenAI Desktop\nStarting application...",
            Qt.AlignCenter | Qt.AlignBottom,
            Qt.black
        )
        app.processEvents()

        # Show main window
        main_window.show()

        # Close splash screen after a short delay
        QTimer.singleShot(1000, splash.close)

        logger.info("Application started successfully")

        # Run the application
        return app.exec_()

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        if 'app' in locals():
            QMessageBox.critical(None, "Startup Error",
                               f"Failed to start the application:\n{str(e)}")
        else:
            print(f"Failed to start application: {e}")
        return 1

    finally:
        logger.info("Application shutting down")


if __name__ == "__main__":
    # Ensure proper handling of high DPI displays
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    sys.exit(main())
