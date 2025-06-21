"""
Main window UI component for the GenAI Desktop Client.
"""

import sys
import asyncio
from typing import Optional, List, Dict, Any
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTextEdit, QLineEdit, QPushButton, QComboBox, QSlider, QSpinBox,
    QLabel, QGroupBox, QCheckBox, QListWidget, QListWidgetItem,
    QMenuBar, QMenu, QAction, QStatusBar, QProgressBar, QMessageBox,
    QTabWidget, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, pyqtSlot
from PyQt5.QtGui import QFont, QTextCursor, QIcon, QPixmap

from api.lm_studio_client import LMStudioClient, LMStudioAPIError
from models.chat_session import ChatSession
from models.message import Message, MessageRole
from utils.config import ConfigManager, config_manager
from ui.session_manager import SessionManager
from ui.settings_dialog import SettingsDialog


class ChatWorker(QThread):
    """Worker thread for handling chat API requests."""

    response_received = pyqtSignal(str)  # Full response
    response_chunk = pyqtSignal(str)     # Streaming chunks
    error_occurred = pyqtSignal(str)     # Error messages
    finished = pyqtSignal()              # Request completed

    def __init__(self, client: LMStudioClient, messages: List[Dict],
                 model: str, temperature: float, max_tokens: int, stream: bool = False):
        super().__init__()
        self.client = client
        self.messages = messages
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stream = stream
        self._is_cancelled = False

    def run(self):
        """Execute the chat request."""
        try:
            if self.stream:
                self._run_streaming()
            else:
                self._run_sync()
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()

    def _run_sync(self):
        """Run synchronous chat completion."""
        try:
            response = self.client.send_chat_completion(
                messages=self.messages,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=False
            )

            if not self._is_cancelled:
                message = self.client.create_message_from_response(
                    response, self.model, self.temperature, self.max_tokens
                )
                self.response_received.emit(message.content)

        except LMStudioAPIError as e:
            self.error_occurred.emit(f"API Error: {e}")
        except Exception as e:
            self.error_occurred.emit(f"Unexpected error: {e}")

    def _run_streaming(self):
        """Run streaming chat completion."""
        try:
            response = self.client.send_chat_completion(
                messages=self.messages,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )

            full_response = ""
            for chunk in self.client.parse_streaming_response(response['response']):
                if self._is_cancelled:
                    break

                full_response += chunk
                self.response_chunk.emit(chunk)

            if not self._is_cancelled:
                self.response_received.emit(full_response)

        except LMStudioAPIError as e:
            self.error_occurred.emit(f"API Error: {e}")
        except Exception as e:
            self.error_occurred.emit(f"Unexpected error: {e}")

    def cancel(self):
        """Cancel the current request."""
        self._is_cancelled = True


class MainWindow(QMainWindow):
    """
    Main application window with chat interface and session management.
    """

    def __init__(self):
        super().__init__()
        self.config_manager = config_manager
        self.lm_client = LMStudioClient(self.config_manager)

        # Current session and state
        self.current_session: Optional[ChatSession] = None
        self.available_models: List[Dict[str, Any]] = []
        self.chat_worker: Optional[ChatWorker] = None

        # UI Components
        self.session_manager: Optional[SessionManager] = None
        self.settings_dialog: Optional[SettingsDialog] = None

        # Initialize UI
        self.init_ui()
        self.load_models()
        self.create_new_session()

        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_connection_status)
        self.status_timer.start(30000)  # Update every 30 seconds

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("GenAI Desktop - LM Studio Interface")
        self.setGeometry(100, 100,
                        self.config_manager.ui_config.window_width,
                        self.config_manager.ui_config.window_height)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Create main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)

        # Left panel - Session management
        self.create_session_panel(main_splitter)

        # Right panel - Chat interface
        self.create_chat_panel(main_splitter)

        # Set splitter proportions
        main_splitter.setSizes([300, 900])

        # Create menu bar
        self.create_menu_bar()

        # Create status bar
        self.create_status_bar()

        # Apply styling
        self.apply_styling()

    def create_session_panel(self, parent):
        """Create the session management panel."""
        session_widget = QWidget()
        session_layout = QVBoxLayout(session_widget)

        # Session controls
        session_controls = QGroupBox("Sessions")
        controls_layout = QVBoxLayout(session_controls)

        # New session button
        self.new_session_btn = QPushButton("New Session")
        self.new_session_btn.clicked.connect(self.create_new_session)
        controls_layout.addWidget(self.new_session_btn)

        # Load session button
        self.load_session_btn = QPushButton("Load Session")
        self.load_session_btn.clicked.connect(self.load_session)
        controls_layout.addWidget(self.load_session_btn)

        # Delete session button
        self.delete_session_btn = QPushButton("Delete Session")
        self.delete_session_btn.clicked.connect(self.delete_session)
        controls_layout.addWidget(self.delete_session_btn)

        session_layout.addWidget(session_controls)

        # Sessions list
        self.sessions_list = QListWidget()
        self.sessions_list.itemDoubleClicked.connect(self.on_session_double_click)
        session_layout.addWidget(self.sessions_list)

        # Configuration panel
        self.create_config_panel(session_layout)

        parent.addWidget(session_widget)

    def create_config_panel(self, parent_layout):
        """Create the configuration panel."""
        config_group = QGroupBox("Configuration")
        config_layout = QVBoxLayout(config_group)

        # Model selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        model_layout.addWidget(self.model_combo)
        config_layout.addLayout(model_layout)

        # Persona selection
        persona_layout = QHBoxLayout()
        persona_layout.addWidget(QLabel("Persona:"))
        self.persona_combo = QComboBox()
        personas = self.config_manager.get_available_personas()
        for persona_name in personas.keys():
            self.persona_combo.addItem(persona_name)
        self.persona_combo.currentTextChanged.connect(self.on_persona_changed)
        config_layout.addLayout(persona_layout)

        # Temperature control
        temp_layout = QVBoxLayout()
        temp_layout.addWidget(QLabel("Temperature:"))
        temp_control_layout = QHBoxLayout()
        self.temperature_slider = QSlider(Qt.Horizontal)
        self.temperature_slider.setRange(0, 100)
        self.temperature_slider.setValue(int(self.config_manager.generation_config.default_temperature * 100))
        self.temperature_slider.valueChanged.connect(self.on_temperature_changed)
        temp_control_layout.addWidget(self.temperature_slider)
        self.temperature_label = QLabel("0.70")
        temp_control_layout.addWidget(self.temperature_label)
        temp_layout.addLayout(temp_control_layout)
        config_layout.addLayout(temp_layout)

        # Max tokens control
        tokens_layout = QHBoxLayout()
        tokens_layout.addWidget(QLabel("Max Tokens:"))
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(1, 4096)
        self.max_tokens_spin.setValue(self.config_manager.generation_config.default_max_tokens)
        self.max_tokens_spin.valueChanged.connect(self.on_max_tokens_changed)
        tokens_layout.addWidget(self.max_tokens_spin)
        config_layout.addLayout(tokens_layout)

        # Streaming toggle
        self.streaming_check = QCheckBox("Enable Streaming")
        self.streaming_check.setChecked(self.config_manager.generation_config.enable_streaming)
        self.streaming_check.toggled.connect(self.on_streaming_toggled)
        config_layout.addWidget(self.streaming_check)

        parent_layout.addWidget(config_group)

    def create_chat_panel(self, parent):
        """Create the main chat interface panel."""
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)

        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont(self.config_manager.ui_config.font_family,
                                      self.config_manager.ui_config.font_size))
        chat_layout.addWidget(self.chat_display)

        # Input area
        input_group = QGroupBox("Message Input")
        input_layout = QVBoxLayout(input_group)

        # Message input
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(100)
        self.message_input.setPlaceholderText("Type your message here...")
        input_layout.addWidget(self.message_input)

        # Input controls
        input_controls = QHBoxLayout()

        # Send button
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setDefault(True)
        input_controls.addWidget(self.send_btn)

        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_request)
        self.cancel_btn.setEnabled(False)
        input_controls.addWidget(self.cancel_btn)

        # Clear button
        self.clear_btn = QPushButton("Clear Chat")
        self.clear_btn.clicked.connect(self.clear_chat)
        input_controls.addWidget(self.clear_btn)

        input_controls.addStretch()

        # Auto-scroll toggle
        self.auto_scroll_check = QCheckBox("Auto-scroll")
        self.auto_scroll_check.setChecked(self.config_manager.ui_config.auto_scroll)
        input_controls.addWidget(self.auto_scroll_check)

        input_layout.addLayout(input_controls)
        chat_layout.addWidget(input_group)

        parent.addWidget(chat_widget)

    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        new_action = QAction('New Session', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.create_new_session)
        file_menu.addAction(new_action)

        load_action = QAction('Load Session...', self)
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.load_session)
        file_menu.addAction(load_action)

        save_action = QAction('Save Session', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_current_session)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        export_action = QAction('Export Chat...', self)
        export_action.triggered.connect(self.export_chat)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu('Edit')

        clear_action = QAction('Clear Chat', self)
        clear_action.setShortcut('Ctrl+L')
        clear_action.triggered.connect(self.clear_chat)
        edit_menu.addAction(clear_action)

        # Settings menu
        settings_menu = menubar.addMenu('Settings')

        preferences_action = QAction('Preferences...', self)
        preferences_action.triggered.connect(self.show_settings)
        settings_menu.addAction(preferences_action)

        # Help menu
        help_menu = menubar.addMenu('Help')

        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Connection status
        self.connection_status = QLabel("Checking connection...")
        self.status_bar.addWidget(self.connection_status)

        # Progress bar for requests
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Session info
        self.session_info = QLabel("No session")
        self.status_bar.addPermanentWidget(self.session_info)

    def apply_styling(self):
        """Apply custom styling to the interface."""
        # Set font for chat display
        chat_font = QFont(self.config_manager.ui_config.font_family,
                         self.config_manager.ui_config.font_size)
        self.chat_display.setFont(chat_font)

        # Style the chat display
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
            }
        """)

        # Style input area
        self.message_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #007bff;
                border-radius: 4px;
                padding: 4px;
            }
        """)

    def load_models(self):
        """Load available models from LM Studio."""
        try:
            self.available_models = self.lm_client.get_available_models()
            self.model_combo.clear()

            if self.available_models:
                for model in self.available_models:
                    model_name = model.get('id', 'Unknown')
                    self.model_combo.addItem(model_name)
                self.connection_status.setText("Connected to LM Studio")
                self.connection_status.setStyleSheet("color: green;")
            else:
                self.connection_status.setText("No models available")
                self.connection_status.setStyleSheet("color: orange;")

        except Exception as e:
            self.connection_status.setText(f"Connection failed: {str(e)}")
            self.connection_status.setStyleSheet("color: red;")
            QMessageBox.warning(self, "Connection Error",
                              f"Failed to connect to LM Studio:\n{str(e)}")

    def update_connection_status(self):
        """Update connection status periodically."""
        if self.lm_client.test_connection():
            self.connection_status.setText("Connected to LM Studio")
            self.connection_status.setStyleSheet("color: green;")
        else:
            self.connection_status.setText("Connection lost")
            self.connection_status.setStyleSheet("color: red;")

    def create_new_session(self):
        """Create a new chat session."""
        from datetime import datetime

        session_id = f"session_{int(datetime.now().timestamp())}"
        persona = self.persona_combo.currentText()
        persona_config = self.config_manager.get_persona(persona)

        self.current_session = ChatSession(
            session_id=session_id,
            title="New Chat Session",
            persona=persona,
            system_prompt=persona_config['system_prompt'],
            model_name=self.model_combo.currentText(),
            default_temperature=self.temperature_slider.value() / 100.0,
            default_max_tokens=self.max_tokens_spin.value()
        )

        self.chat_display.clear()
        self.update_session_info()
        self.load_sessions_list()

    def save_current_session(self):
        """Save the current session to file."""
        if not self.current_session:
            return

        sessions_dir = self.config_manager.get_sessions_directory()
        file_path = sessions_dir / f"{self.current_session.session_id}.json"

        try:
            self.current_session.save_to_file(str(file_path))
            self.status_bar.showMessage("Session saved", 3000)
            self.load_sessions_list()
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save session:\n{str(e)}")

    def load_session(self):
        """Load a session from file."""
        # This would typically open a file dialog
        # For now, we'll implement basic session management
        pass

    def delete_session(self):
        """Delete the selected session."""
        current_item = self.sessions_list.currentItem()
        if not current_item:
            return

        session_id = current_item.data(Qt.UserRole)
        sessions_dir = self.config_manager.get_sessions_directory()
        file_path = sessions_dir / f"{session_id}.json"

        reply = QMessageBox.question(self, "Delete Session",
                                   "Are you sure you want to delete this session?")

        if reply == QMessageBox.Yes:
            try:
                file_path.unlink(missing_ok=True)
                self.load_sessions_list()
                self.status_bar.showMessage("Session deleted", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Delete Error", f"Failed to delete session:\n{str(e)}")

    def load_sessions_list(self):
        """Load and display available sessions."""
        self.sessions_list.clear()
        sessions_dir = self.config_manager.get_sessions_directory()

        try:
            for session_file in sessions_dir.glob("*.json"):
                try:
                    session = ChatSession.load_from_file(str(session_file))
                    item = QListWidgetItem(session.title)
                    item.setData(Qt.UserRole, session.session_id)
                    item.setToolTip(f"Created: {session.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                                  f"Messages: {len(session.messages)}\n"
                                  f"Model: {session.model_name or 'Unknown'}")
                    self.sessions_list.addItem(item)
                except Exception as e:
                    print(f"Error loading session {session_file}: {e}")

        except Exception as e:
            print(f"Error loading sessions directory: {e}")

    def on_session_double_click(self, item):
        """Handle double-click on session item."""
        session_id = item.data(Qt.UserRole)
        sessions_dir = self.config_manager.get_sessions_directory()
        file_path = sessions_dir / f"{session_id}.json"

        try:
            self.current_session = ChatSession.load_from_file(str(file_path))
            self.load_session_to_ui()
            self.status_bar.showMessage("Session loaded", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load session:\n{str(e)}")

    def load_session_to_ui(self):
        """Load session data into the UI."""
        if not self.current_session:
            return

        # Clear chat display
        self.chat_display.clear()

        # Load messages
        for message in self.current_session.messages:
            if not message.is_system_message():
                self.append_message_to_display(message)

        # Update UI controls
        if self.current_session.model_name:
            index = self.model_combo.findText(self.current_session.model_name)
            if index >= 0:
                self.model_combo.setCurrentIndex(index)

        self.persona_combo.setCurrentText(self.current_session.persona)
        self.temperature_slider.setValue(int(self.current_session.default_temperature * 100))
        self.max_tokens_spin.setValue(self.current_session.default_max_tokens)

        self.update_session_info()

    def send_message(self):
        """Send user message and get AI response."""
        message_text = self.message_input.toPlainText().strip()
        if not message_text:
            return

        if not self.current_session:
            self.create_new_session()

        # Add user message
        user_message = Message(
            content=message_text,
            role=MessageRole.USER
        )
        self.current_session.add_message(user_message)
        self.append_message_to_display(user_message)

        # Clear input
        self.message_input.clear()

        # Prepare API request
        model = self.model_combo.currentText()
        if not model:
            QMessageBox.warning(self, "No Model", "Please select a model first.")
            return

        temperature = self.temperature_slider.value() / 100.0
        max_tokens = self.max_tokens_spin.value()
        stream = self.streaming_check.isChecked()

        # Get conversation history
        messages = self.current_session.get_conversation_history()

        # Start API request in worker thread
        self.chat_worker = ChatWorker(
            self.lm_client, messages, model, temperature, max_tokens, stream
        )
        self.chat_worker.response_received.connect(self.on_response_received)
        self.chat_worker.response_chunk.connect(self.on_response_chunk)
        self.chat_worker.error_occurred.connect(self.on_api_error)
        self.chat_worker.finished.connect(self.on_request_finished)

        # Update UI state
        self.send_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        # Start request
        self.chat_worker.start()

    def cancel_request(self):
        """Cancel the current API request."""
        if self.chat_worker and self.chat_worker.isRunning():
            self.chat_worker.cancel()

    @pyqtSlot(str)
    def on_response_received(self, response_text):
        """Handle complete response from API."""
        if not self.current_session:
            return

        # Create assistant message
        assistant_message = Message(
            content=response_text,
            role=MessageRole.ASSISTANT,
            model_used=self.model_combo.currentText(),
            temperature=self.temperature_slider.value() / 100.0,
            max_tokens=self.max_tokens_spin.value()
        )

        self.current_session.add_message(assistant_message)

        if not self.streaming_check.isChecked():
            self.append_message_to_display(assistant_message)

        # Auto-save session
        self.save_current_session()

    @pyqtSlot(str)
    def on_response_chunk(self, chunk):
        """Handle streaming response chunk."""
        # Append chunk to display in real-time
        self.chat_display.insertPlainText(chunk)

        if self.auto_scroll_check.isChecked():
            cursor = self.chat_display.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.chat_display.setTextCursor(cursor)

    @pyqtSlot(str)
    def on_api_error(self, error_message):
        """Handle API errors."""
        QMessageBox.critical(self, "API Error", error_message)

    @pyqtSlot()
    def on_request_finished(self):
        """Handle request completion."""
        self.send_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.update_session_info()

    def append_message_to_display(self, message: Message):
        """Append a message to the chat display."""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)

        # Format message content
        content_html = message.content.replace('\n', '<br>')

        # Format message
        if message.is_user_message():
            html_template = """
                <div style="margin: 10px 0; padding: 10px; background-color: #e3f2fd; border-left: 4px solid #2196f3;">
                    <b>You</b> <small>({time})</small><br>
                    {content}
                </div>
            """
            cursor.insertHtml(html_template.format(
                time=message.get_display_time(),
                content=content_html
            ))
        elif message.is_assistant_message():
            html_template = """
                <div style="margin: 10px 0; padding: 10px; background-color: #f3e5f5; border-left: 4px solid #9c27b0;">
                    <b>Assistant</b> <small>({time})</small><br>
                    {content}
                </div>
            """
            cursor.insertHtml(html_template.format(
                time=message.get_display_time(),
                content=content_html
            ))

        # Auto-scroll if enabled
        if self.auto_scroll_check.isChecked():
            cursor.movePosition(QTextCursor.End)
            self.chat_display.setTextCursor(cursor)

    def clear_chat(self):
        """Clear the chat display and session history."""
        reply = QMessageBox.question(self, "Clear Chat",
                                   "Are you sure you want to clear the chat history?")

        if reply == QMessageBox.Yes:
            self.chat_display.clear()
            if self.current_session:
                self.current_session.clear_conversation(keep_system=True)
                self.update_session_info()

    def update_session_info(self):
        """Update session information display."""
        if self.current_session:
            message_counts = self.current_session.get_message_count()
            info = f"Session: {len(self.current_session.messages)} messages"
            self.session_info.setText(info)
        else:
            self.session_info.setText("No session")

    def on_model_changed(self, model_name):
        """Handle model selection change."""
        if self.current_session:
            self.current_session.model_name = model_name

    def on_persona_changed(self, persona_name):
        """Handle persona selection change."""
        if self.current_session:
            persona_config = self.config_manager.get_persona(persona_name)
            self.current_session.persona = persona_name
            self.current_session.update_system_prompt(persona_config['system_prompt'])

    def on_temperature_changed(self, value):
        """Handle temperature slider change."""
        temp_value = value / 100.0
        self.temperature_label.setText(f"{temp_value:.2f}")
        if self.current_session:
            self.current_session.default_temperature = temp_value

    def on_max_tokens_changed(self, value):
        """Handle max tokens change."""
        if self.current_session:
            self.current_session.default_max_tokens = value

    def on_streaming_toggled(self, enabled):
        """Handle streaming toggle."""
        self.config_manager.update_generation_config(enable_streaming=enabled)

    def show_settings(self):
        """Show settings dialog."""
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog(self.config_manager, self)

        if self.settings_dialog.exec_() == self.settings_dialog.Accepted:
            # Reload models if API settings changed
            self.load_models()
            # Apply UI changes
            self.apply_styling()

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About GenAI Desktop Client",
                         """
                         <h3>GenAI Desktop</h3>
                         <p>Version 1.0.0</p>
                         <p>A desktop client for interacting with LM Studio's REST API.</p>
                         <p>Built with PyQt5 and Python.</p>
                         """)

    def export_chat(self):
        """Export current chat to text file."""
        if not self.current_session:
            QMessageBox.information(self, "No Session", "No active session to export.")
            return

        from PyQt5.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Chat", f"{self.current_session.title}.txt",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                text_content = self.current_session.export_to_text()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                self.status_bar.showMessage("Chat exported successfully", 3000)
                QMessageBox.information(self, "Export Complete", f"Chat exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export chat:\n{str(e)}")

    def closeEvent(self, event):
        """Handle application close event."""
        # Save current session if it exists
        if self.current_session:
            self.save_current_session()

        # Save window state if enabled
        if self.config_manager.ui_config.save_window_state:
            self.config_manager.update_ui_config(
                window_width=self.width(),
                window_height=self.height()
            )

        # Close API client
        try:
            asyncio.create_task(self.lm_client.close())
        except:
            pass

        event.accept()

    def keyPressEvent(self, event):
        """Handle key press events."""
        # Send message on Ctrl+Enter
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            if self.message_input.hasFocus():
                self.send_message()
                return

        super().keyPressEvent(event)
