"""
Session manager UI component for handling session operations.
"""

import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QMessageBox, QFileDialog, QInputDialog,
    QGroupBox, QTextEdit, QSplitter, QWidget, QHeaderView, QTableWidget,
    QTableWidgetItem, QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap

from models.chat_session import ChatSession
from utils.config import ConfigManager


class SessionListWidget(QListWidget):
    """Custom list widget for session management with context menu."""

    session_load_requested = pyqtSignal(str)  # session_id
    session_delete_requested = pyqtSignal(str)  # session_id
    session_rename_requested = pyqtSignal(str, str)  # session_id, new_name
    session_duplicate_requested = pyqtSignal(str)  # session_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        """Show context menu for session operations."""
        item = self.itemAt(position)
        if not item:
            return

        session_id = item.data(Qt.UserRole)
        menu = QMenu(self)

        # Load session
        load_action = QAction("Load Session", self)
        load_action.triggered.connect(lambda: self.session_load_requested.emit(session_id))
        menu.addAction(load_action)

        menu.addSeparator()

        # Rename session
        rename_action = QAction("Rename Session", self)
        rename_action.triggered.connect(lambda: self._rename_session(session_id, item.text()))
        menu.addAction(rename_action)

        # Duplicate session
        duplicate_action = QAction("Duplicate Session", self)
        duplicate_action.triggered.connect(lambda: self.session_duplicate_requested.emit(session_id))
        menu.addAction(duplicate_action)

        menu.addSeparator()

        # Delete session
        delete_action = QAction("Delete Session", self)
        delete_action.triggered.connect(lambda: self.session_delete_requested.emit(session_id))
        menu.addAction(delete_action)

        menu.exec_(self.mapToGlobal(position))

    def _rename_session(self, session_id: str, current_name: str):
        """Handle session rename request."""
        new_name, ok = QInputDialog.getText(
            self, "Rename Session", "Enter new session name:", text=current_name
        )

        if ok and new_name.strip():
            self.session_rename_requested.emit(session_id, new_name.strip())


class SessionPreviewWidget(QWidget):
    """Widget for previewing session details."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_session: Optional[ChatSession] = None

    def setup_ui(self):
        """Setup the preview UI."""
        layout = QVBoxLayout(self)

        # Session info group
        info_group = QGroupBox("Session Information")
        info_layout = QVBoxLayout(info_group)

        self.session_title = QLabel("No session selected")
        self.session_title.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addWidget(self.session_title)

        self.session_details = QLabel("")
        self.session_details.setWordWrap(True)
        info_layout.addWidget(self.session_details)

        layout.addWidget(info_group)

        # Preview group
        preview_group = QGroupBox("Message Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.message_preview = QTextEdit()
        self.message_preview.setReadOnly(True)
        self.message_preview.setMaximumHeight(200)
        preview_layout.addWidget(self.message_preview)

        layout.addWidget(preview_group)

        # Statistics group
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_group)

        self.stats_label = QLabel("")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)

        layout.addWidget(stats_group)

    def set_session(self, session: Optional[ChatSession]):
        """Set the session to preview."""
        self.current_session = session
        self.update_preview()

    def update_preview(self):
        """Update the preview display."""
        if not self.current_session:
            self.session_title.setText("No session selected")
            self.session_details.setText("")
            self.message_preview.clear()
            self.stats_label.setText("")
            return

        # Update title
        self.session_title.setText(self.current_session.title)

        # Update details
        details = f"""
        <b>ID:</b> {self.current_session.session_id}<br>
        <b>Created:</b> {self.current_session.created_at.strftime('%Y-%m-%d %H:%M:%S')}<br>
        <b>Updated:</b> {self.current_session.updated_at.strftime('%Y-%m-%d %H:%M:%S')}<br>
        <b>Model:</b> {self.current_session.model_name or 'Unknown'}<br>
        <b>Persona:</b> {self.current_session.persona}
        """
        self.session_details.setText(details)

        # Update message preview
        self.message_preview.clear()
        recent_messages = self.current_session.get_last_n_messages(3, include_system=False)

        for msg in recent_messages:
            role = "You" if msg.is_user_message() else "Assistant"
            timestamp = msg.get_display_time()
            content = msg.content[:100] + ("..." if len(msg.content) > 100 else "")

            self.message_preview.append(f"[{role} - {timestamp}] {content}\n")

        # Update statistics
        message_counts = self.current_session.get_message_count()
        total_tokens = self.current_session.get_total_tokens()

        stats = f"""
        <b>Messages:</b> {message_counts['user']} user, {message_counts['assistant']} assistant, {message_counts['system']} system<br>
        <b>Total Messages:</b> {len(self.current_session.messages)}<br>
        <b>Total Tokens:</b> {total_tokens if total_tokens > 0 else 'Unknown'}
        """
        self.stats_label.setText(stats)


class SessionManager(QDialog):
    """
    Session management dialog for loading, saving, and organizing chat sessions.
    """

    session_loaded = pyqtSignal(ChatSession)  # Emitted when a session is loaded

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.sessions_dir = config_manager.get_sessions_directory()
        self.sessions: Dict[str, ChatSession] = {}

        self.setup_ui()
        self.load_sessions()

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_sessions)
        self.refresh_timer.start(10000)  # Refresh every 10 seconds

    def setup_ui(self):
        """Setup the session manager UI."""
        self.setWindowTitle("Session Manager")
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout(self)

        # Create main splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Left panel - Session list
        left_panel = self.create_session_list_panel()
        splitter.addWidget(left_panel)

        # Right panel - Session preview
        self.preview_widget = SessionPreviewWidget()
        splitter.addWidget(self.preview_widget)

        # Set splitter proportions
        splitter.setSizes([400, 400])

        # Bottom buttons
        button_layout = QHBoxLayout()

        self.load_button = QPushButton("Load Session")
        self.load_button.clicked.connect(self.load_selected_session)
        self.load_button.setEnabled(False)
        button_layout.addWidget(self.load_button)

        self.import_button = QPushButton("Import Session...")
        self.import_button.clicked.connect(self.import_session)
        button_layout.addWidget(self.import_button)

        self.export_button = QPushButton("Export Session...")
        self.export_button.clicked.connect(self.export_selected_session)
        self.export_button.setEnabled(False)
        button_layout.addWidget(self.export_button)

        button_layout.addStretch()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_sessions)
        button_layout.addWidget(self.refresh_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def create_session_list_panel(self) -> QWidget:
        """Create the session list panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Header
        header = QLabel("Saved Sessions")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(header)

        # Session list
        self.session_list = SessionListWidget()
        self.session_list.itemSelectionChanged.connect(self.on_session_selected)
        self.session_list.itemDoubleClicked.connect(self.on_session_double_clicked)

        # Connect custom signals
        self.session_list.session_load_requested.connect(self.load_session_by_id)
        self.session_list.session_delete_requested.connect(self.delete_session_by_id)
        self.session_list.session_rename_requested.connect(self.rename_session)
        self.session_list.session_duplicate_requested.connect(self.duplicate_session)

        layout.addWidget(self.session_list)

        # Quick stats
        self.stats_label = QLabel("0 sessions")
        layout.addWidget(self.stats_label)

        return panel

    def load_sessions(self):
        """Load all sessions from the sessions directory."""
        self.sessions.clear()
        self.session_list.clear()

        if not self.sessions_dir.exists():
            self.sessions_dir.mkdir(parents=True, exist_ok=True)

        session_files = list(self.sessions_dir.glob("*.json"))
        session_count = 0

        for session_file in session_files:
            try:
                session = ChatSession.load_from_file(str(session_file))
                self.sessions[session.session_id] = session

                # Add to list widget
                item = QListWidgetItem()
                item.setText(session.title)
                item.setData(Qt.UserRole, session.session_id)

                # Set tooltip with session info
                tooltip = f"""
                Title: {session.title}
                Created: {session.created_at.strftime('%Y-%m-%d %H:%M')}
                Messages: {len(session.messages)}
                Model: {session.model_name or 'Unknown'}
                Persona: {session.persona}
                """
                item.setToolTip(tooltip.strip())

                self.session_list.addItem(item)
                session_count += 1

            except Exception as e:
                print(f"Error loading session {session_file}: {e}")

        # Update stats
        self.stats_label.setText(f"{session_count} sessions")

        # Sort sessions by update time (most recent first)
        self.session_list.sortItems(Qt.DescendingOrder)

    def on_session_selected(self):
        """Handle session selection change."""
        current_item = self.session_list.currentItem()

        if current_item:
            session_id = current_item.data(Qt.UserRole)
            session = self.sessions.get(session_id)

            self.preview_widget.set_session(session)
            self.load_button.setEnabled(True)
            self.export_button.setEnabled(True)
        else:
            self.preview_widget.set_session(None)
            self.load_button.setEnabled(False)
            self.export_button.setEnabled(False)

    def on_session_double_clicked(self, item):
        """Handle double-click on session item."""
        self.load_selected_session()

    def load_selected_session(self):
        """Load the currently selected session."""
        current_item = self.session_list.currentItem()
        if not current_item:
            return

        session_id = current_item.data(Qt.UserRole)
        self.load_session_by_id(session_id)

    def load_session_by_id(self, session_id: str):
        """Load a session by its ID."""
        session = self.sessions.get(session_id)
        if session:
            self.session_loaded.emit(session)
            self.accept()  # Close dialog
        else:
            QMessageBox.warning(self, "Session Not Found",
                              f"Session with ID {session_id} could not be found.")

    def delete_session_by_id(self, session_id: str):
        """Delete a session by its ID."""
        session = self.sessions.get(session_id)
        if not session:
            return

        reply = QMessageBox.question(
            self, "Delete Session",
            f"Are you sure you want to delete the session '{session.title}'?\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                session_file = self.sessions_dir / f"{session_id}.json"
                session_file.unlink(missing_ok=True)
                self.load_sessions()  # Refresh list
                QMessageBox.information(self, "Session Deleted",
                                      f"Session '{session.title}' has been deleted.")
            except Exception as e:
                QMessageBox.critical(self, "Delete Error",
                                   f"Failed to delete session:\n{str(e)}")

    def rename_session(self, session_id: str, new_name: str):
        """Rename a session."""
        session = self.sessions.get(session_id)
        if not session:
            return

        try:
            # Update session title
            session.title = new_name
            session.updated_at = session.created_at.__class__.now()

            # Save updated session
            session_file = self.sessions_dir / f"{session_id}.json"
            session.save_to_file(str(session_file))

            # Refresh list
            self.load_sessions()

            QMessageBox.information(self, "Session Renamed",
                                  f"Session renamed to '{new_name}'.")

        except Exception as e:
            QMessageBox.critical(self, "Rename Error",
                               f"Failed to rename session:\n{str(e)}")

    def duplicate_session(self, session_id: str):
        """Duplicate a session."""
        session = self.sessions.get(session_id)
        if not session:
            return

        try:
            # Create new session with copied data
            from datetime import datetime

            new_session_id = f"session_{int(datetime.now().timestamp())}"
            new_session = ChatSession(
                session_id=new_session_id,
                title=f"{session.title} (Copy)",
                messages=session.messages.copy(),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                model_name=session.model_name,
                persona=session.persona,
                system_prompt=session.system_prompt,
                default_temperature=session.default_temperature,
                default_max_tokens=session.default_max_tokens,
                metadata=session.metadata.copy()
            )

            # Save new session
            session_file = self.sessions_dir / f"{new_session_id}.json"
            new_session.save_to_file(str(session_file))

            # Refresh list
            self.load_sessions()

            QMessageBox.information(self, "Session Duplicated",
                                  f"Session duplicated as '{new_session.title}'.")

        except Exception as e:
            QMessageBox.critical(self, "Duplicate Error",
                               f"Failed to duplicate session:\n{str(e)}")

    def import_session(self):
        """Import a session from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Session", "",
            "JSON Files (*.json);;All Files (*)"
        )

        if not file_path:
            return

        try:
            # Load session from file
            imported_session = ChatSession.load_from_file(file_path)

            # Generate new session ID to avoid conflicts
            from datetime import datetime
            new_session_id = f"session_{int(datetime.now().timestamp())}"
            imported_session.session_id = new_session_id
            imported_session.title = f"{imported_session.title} (Imported)"

            # Save to sessions directory
            session_file = self.sessions_dir / f"{new_session_id}.json"
            imported_session.save_to_file(str(session_file))

            # Refresh list
            self.load_sessions()

            QMessageBox.information(self, "Import Successful",
                                  f"Session '{imported_session.title}' imported successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Import Error",
                               f"Failed to import session:\n{str(e)}")

    def export_selected_session(self):
        """Export the selected session to file."""
        current_item = self.session_list.currentItem()
        if not current_item:
            return

        session_id = current_item.data(Qt.UserRole)
        session = self.sessions.get(session_id)
        if not session:
            return

        # Choose export format
        reply = QMessageBox.question(
            self, "Export Format",
            "Choose export format:\n\n"
            "Yes - JSON format (can be imported later)\n"
            "No - Text format (human readable)\n"
            "Cancel - Cancel export",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Cancel:
            return

        export_json = (reply == QMessageBox.Yes)

        # Get export file path
        if export_json:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Session", f"{session.title}.json",
                "JSON Files (*.json);;All Files (*)"
            )
        else:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Session", f"{session.title}.txt",
                "Text Files (*.txt);;All Files (*)"
            )

        if not file_path:
            return

        try:
            if export_json:
                session.save_to_file(file_path)
            else:
                text_content = session.export_to_text()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text_content)

            QMessageBox.information(self, "Export Successful",
                                  f"Session exported to {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error",
                               f"Failed to export session:\n{str(e)}")

    def closeEvent(self, event):
        """Handle dialog close event."""
        self.refresh_timer.stop()
        event.accept()
