"""
Settings dialog for application configuration.
"""

from typing import Dict, Any
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QGroupBox, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QCheckBox, QComboBox, QPushButton, QMessageBox, QFormLayout,
    QSlider, QTextEdit, QFileDialog, QColorDialog, QFontDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette

from utils.config import ConfigManager


class APISettingsTab(QWidget):
    """Tab for API connection settings."""

    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup the API settings UI."""
        layout = QVBoxLayout(self)

        # Connection settings group
        connection_group = QGroupBox("LM Studio Connection")
        connection_layout = QFormLayout(connection_group)

        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("localhost")
        connection_layout.addRow("Host:", self.host_edit)

        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(1234)
        connection_layout.addRow("Port:", self.port_spin)

        self.base_url_edit = QLineEdit()
        self.base_url_edit.setPlaceholderText("http://localhost:1234")
        connection_layout.addRow("Base URL:", self.base_url_edit)

        # Connection test button
        test_layout = QHBoxLayout()
        self.test_button = QPushButton("Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        test_layout.addWidget(self.test_button)
        test_layout.addStretch()
        self.connection_status = QLabel("Not tested")
        test_layout.addWidget(self.connection_status)

        connection_layout.addRow("", test_layout)

        layout.addWidget(connection_group)

        # Request settings group
        request_group = QGroupBox("Request Settings")
        request_layout = QFormLayout(request_group)

        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 300)
        self.timeout_spin.setSuffix(" seconds")
        request_layout.addRow("Timeout:", self.timeout_spin)

        self.max_retries_spin = QSpinBox()
        self.max_retries_spin.setRange(0, 10)
        request_layout.addRow("Max Retries:", self.max_retries_spin)

        layout.addWidget(request_group)

        layout.addStretch()

    def load_settings(self):
        """Load current settings into the UI."""
        api_config = self.config_manager.api_config

        self.host_edit.setText(api_config.host)
        self.port_spin.setValue(api_config.port)
        self.base_url_edit.setText(api_config.base_url)
        self.timeout_spin.setValue(api_config.timeout)
        self.max_retries_spin.setValue(api_config.max_retries)

    def save_settings(self):
        """Save settings from the UI."""
        self.config_manager.update_api_config(
            host=self.host_edit.text().strip() or "localhost",
            port=self.port_spin.value(),
            base_url=self.base_url_edit.text().strip(),
            timeout=self.timeout_spin.value(),
            max_retries=self.max_retries_spin.value()
        )

    def test_connection(self):
        """Test the connection to LM Studio."""
        from api.lm_studio_client import LMStudioClient

        # Temporarily update config for testing
        temp_config = ConfigManager()
        temp_config.update_api_config(
            host=self.host_edit.text().strip() or "localhost",
            port=self.port_spin.value(),
            base_url=self.base_url_edit.text().strip()
        )

        client = LMStudioClient(temp_config)

        try:
            if client.test_connection():
                self.connection_status.setText("✓ Connected")
                self.connection_status.setStyleSheet("color: green; font-weight: bold;")
                QMessageBox.information(self, "Connection Test", "Successfully connected to LM Studio!")
            else:
                self.connection_status.setText("✗ Failed")
                self.connection_status.setStyleSheet("color: red; font-weight: bold;")
                QMessageBox.warning(self, "Connection Test", "Failed to connect to LM Studio. Please check your settings.")
        except Exception as e:
            self.connection_status.setText("✗ Error")
            self.connection_status.setStyleSheet("color: red; font-weight: bold;")
            QMessageBox.critical(self, "Connection Test", f"Connection test failed:\n{str(e)}")


class UISettingsTab(QWidget):
    """Tab for UI and appearance settings."""

    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup the UI settings UI."""
        layout = QVBoxLayout(self)

        # Appearance group
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout(appearance_group)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Default", "Dark", "Light"])
        appearance_layout.addRow("Theme:", self.theme_combo)

        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(["Arial", "Helvetica", "Times New Roman", "Courier New", "Verdana"])
        appearance_layout.addRow("Font Family:", self.font_family_combo)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        appearance_layout.addRow("Font Size:", self.font_size_spin)

        # Font selection button
        font_layout = QHBoxLayout()
        self.font_button = QPushButton("Choose Font...")
        self.font_button.clicked.connect(self.choose_font)
        font_layout.addWidget(self.font_button)
        font_layout.addStretch()
        self.font_preview = QLabel("Sample Text")
        font_layout.addWidget(self.font_preview)
        appearance_layout.addRow("", font_layout)

        layout.addWidget(appearance_group)

        # Window settings group
        window_group = QGroupBox("Window Settings")
        window_layout = QFormLayout(window_group)

        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(800, 2560)
        window_layout.addRow("Default Width:", self.window_width_spin)

        self.window_height_spin = QSpinBox()
        self.window_height_spin.setRange(600, 1440)
        window_layout.addRow("Default Height:", self.window_height_spin)

        self.save_window_state_check = QCheckBox("Save window size and position")
        window_layout.addRow("", self.save_window_state_check)

        layout.addWidget(window_group)

        # Chat display group
        chat_group = QGroupBox("Chat Display")
        chat_layout = QFormLayout(chat_group)

        self.auto_scroll_check = QCheckBox("Auto-scroll to new messages")
        chat_layout.addRow("", self.auto_scroll_check)

        self.show_timestamps_check = QCheckBox("Show message timestamps")
        chat_layout.addRow("", self.show_timestamps_check)

        self.word_wrap_check = QCheckBox("Word wrap long messages")
        chat_layout.addRow("", self.word_wrap_check)

        layout.addWidget(chat_group)

        layout.addStretch()

    def load_settings(self):
        """Load current settings into the UI."""
        ui_config = self.config_manager.ui_config

        # Set theme
        theme_index = self.theme_combo.findText(ui_config.theme.title())
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)

        # Set font
        font_index = self.font_family_combo.findText(ui_config.font_family)
        if font_index >= 0:
            self.font_family_combo.setCurrentIndex(font_index)

        self.font_size_spin.setValue(ui_config.font_size)
        self.update_font_preview()

        # Set window settings
        self.window_width_spin.setValue(ui_config.window_width)
        self.window_height_spin.setValue(ui_config.window_height)
        self.save_window_state_check.setChecked(ui_config.save_window_state)

        # Set chat display settings
        self.auto_scroll_check.setChecked(ui_config.auto_scroll)
        self.show_timestamps_check.setChecked(ui_config.show_timestamps)
        self.word_wrap_check.setChecked(ui_config.word_wrap)

    def save_settings(self):
        """Save settings from the UI."""
        self.config_manager.update_ui_config(
            theme=self.theme_combo.currentText().lower(),
            font_family=self.font_family_combo.currentText(),
            font_size=self.font_size_spin.value(),
            window_width=self.window_width_spin.value(),
            window_height=self.window_height_spin.value(),
            save_window_state=self.save_window_state_check.isChecked(),
            auto_scroll=self.auto_scroll_check.isChecked(),
            show_timestamps=self.show_timestamps_check.isChecked(),
            word_wrap=self.word_wrap_check.isChecked()
        )

    def choose_font(self):
        """Open font selection dialog."""
        current_font = QFont(self.font_family_combo.currentText(), self.font_size_spin.value())
        font, ok = QFontDialog.getFont(current_font, self)

        if ok:
            self.font_family_combo.setCurrentText(font.family())
            self.font_size_spin.setValue(font.pointSize())
            self.update_font_preview()

    def update_font_preview(self):
        """Update the font preview."""
        font = QFont(self.font_family_combo.currentText(), self.font_size_spin.value())
        self.font_preview.setFont(font)


class GenerationSettingsTab(QWidget):
    """Tab for text generation settings."""

    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup the generation settings UI."""
        layout = QVBoxLayout(self)

        # Default parameters group
        defaults_group = QGroupBox("Default Generation Parameters")
        defaults_layout = QFormLayout(defaults_group)

        # Temperature
        temp_layout = QHBoxLayout()
        self.temperature_slider = QSlider(Qt.Horizontal)
        self.temperature_slider.setRange(0, 100)
        self.temperature_slider.valueChanged.connect(self.update_temperature_label)
        temp_layout.addWidget(self.temperature_slider)
        self.temperature_label = QLabel("0.70")
        temp_layout.addWidget(self.temperature_label)
        defaults_layout.addRow("Temperature:", temp_layout)

        # Max tokens
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(1, 8192)
        defaults_layout.addRow("Max Tokens:", self.max_tokens_spin)

        # Top-p
        top_p_layout = QHBoxLayout()
        self.top_p_slider = QSlider(Qt.Horizontal)
        self.top_p_slider.setRange(0, 100)
        self.top_p_slider.valueChanged.connect(self.update_top_p_label)
        top_p_layout.addWidget(self.top_p_slider)
        self.top_p_label = QLabel("0.90")
        top_p_layout.addWidget(self.top_p_label)
        defaults_layout.addRow("Top-p:", top_p_layout)

        # Frequency penalty
        freq_layout = QHBoxLayout()
        self.frequency_penalty_slider = QSlider(Qt.Horizontal)
        self.frequency_penalty_slider.setRange(-200, 200)
        self.frequency_penalty_slider.valueChanged.connect(self.update_frequency_penalty_label)
        freq_layout.addWidget(self.frequency_penalty_slider)
        self.frequency_penalty_label = QLabel("0.00")
        freq_layout.addWidget(self.frequency_penalty_label)
        defaults_layout.addRow("Frequency Penalty:", freq_layout)

        # Presence penalty
        pres_layout = QHBoxLayout()
        self.presence_penalty_slider = QSlider(Qt.Horizontal)
        self.presence_penalty_slider.setRange(-200, 200)
        self.presence_penalty_slider.valueChanged.connect(self.update_presence_penalty_label)
        pres_layout.addWidget(self.presence_penalty_slider)
        self.presence_penalty_label = QLabel("0.00")
        pres_layout.addWidget(self.presence_penalty_label)
        defaults_layout.addRow("Presence Penalty:", pres_layout)

        layout.addWidget(defaults_group)

        # Streaming settings group
        streaming_group = QGroupBox("Streaming Settings")
        streaming_layout = QFormLayout(streaming_group)

        self.enable_streaming_check = QCheckBox("Enable streaming by default")
        streaming_layout.addRow("", self.enable_streaming_check)

        self.stream_chunk_size_spin = QSpinBox()
        self.stream_chunk_size_spin.setRange(64, 4096)
        self.stream_chunk_size_spin.setSuffix(" bytes")
        streaming_layout.addRow("Stream Chunk Size:", self.stream_chunk_size_spin)

        layout.addWidget(streaming_group)

        # Reset button
        reset_layout = QHBoxLayout()
        reset_layout.addStretch()
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_to_defaults)
        reset_layout.addWidget(self.reset_button)
        layout.addLayout(reset_layout)

        layout.addStretch()

    def load_settings(self):
        """Load current settings into the UI."""
        gen_config = self.config_manager.generation_config

        self.temperature_slider.setValue(int(gen_config.default_temperature * 100))
        self.update_temperature_label()

        self.max_tokens_spin.setValue(gen_config.default_max_tokens)

        self.top_p_slider.setValue(int(gen_config.default_top_p * 100))
        self.update_top_p_label()

        self.frequency_penalty_slider.setValue(int(gen_config.default_frequency_penalty * 100))
        self.update_frequency_penalty_label()

        self.presence_penalty_slider.setValue(int(gen_config.default_presence_penalty * 100))
        self.update_presence_penalty_label()

        self.enable_streaming_check.setChecked(gen_config.enable_streaming)
        self.stream_chunk_size_spin.setValue(gen_config.stream_chunk_size)

    def save_settings(self):
        """Save settings from the UI."""
        self.config_manager.update_generation_config(
            default_temperature=self.temperature_slider.value() / 100.0,
            default_max_tokens=self.max_tokens_spin.value(),
            default_top_p=self.top_p_slider.value() / 100.0,
            default_frequency_penalty=self.frequency_penalty_slider.value() / 100.0,
            default_presence_penalty=self.presence_penalty_slider.value() / 100.0,
            enable_streaming=self.enable_streaming_check.isChecked(),
            stream_chunk_size=self.stream_chunk_size_spin.value()
        )

    def update_temperature_label(self):
        """Update temperature label."""
        value = self.temperature_slider.value() / 100.0
        self.temperature_label.setText(f"{value:.2f}")

    def update_top_p_label(self):
        """Update top-p label."""
        value = self.top_p_slider.value() / 100.0
        self.top_p_label.setText(f"{value:.2f}")

    def update_frequency_penalty_label(self):
        """Update frequency penalty label."""
        value = self.frequency_penalty_slider.value() / 100.0
        self.frequency_penalty_label.setText(f"{value:.2f}")

    def update_presence_penalty_label(self):
        """Update presence penalty label."""
        value = self.presence_penalty_slider.value() / 100.0
        self.presence_penalty_label.setText(f"{value:.2f}")

    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self, "Reset to Defaults",
            "Are you sure you want to reset all generation settings to their default values?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            from utils.config import GenerationConfig
            default_config = GenerationConfig()

            self.temperature_slider.setValue(int(default_config.default_temperature * 100))
            self.max_tokens_spin.setValue(default_config.default_max_tokens)
            self.top_p_slider.setValue(int(default_config.default_top_p * 100))
            self.frequency_penalty_slider.setValue(int(default_config.default_frequency_penalty * 100))
            self.presence_penalty_slider.setValue(int(default_config.default_presence_penalty * 100))
            self.enable_streaming_check.setChecked(default_config.enable_streaming)
            self.stream_chunk_size_spin.setValue(default_config.stream_chunk_size)

            # Update labels
            self.update_temperature_label()
            self.update_top_p_label()
            self.update_frequency_penalty_label()
            self.update_presence_penalty_label()


class PersonasTab(QWidget):
    """Tab for managing personas and system prompts."""

    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.setup_ui()
        self.load_personas()

    def setup_ui(self):
        """Setup the personas UI."""
        layout = QVBoxLayout(self)

        # Persona selection
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Persona:"))
        self.persona_combo = QComboBox()
        self.persona_combo.currentTextChanged.connect(self.on_persona_changed)
        selection_layout.addWidget(self.persona_combo)
        selection_layout.addStretch()
        layout.addLayout(selection_layout)

        # Persona details
        details_group = QGroupBox("Persona Details")
        details_layout = QFormLayout(details_group)

        self.persona_name_edit = QLineEdit()
        self.persona_name_edit.setReadOnly(True)
        details_layout.addRow("Name:", self.persona_name_edit)

        self.persona_description_edit = QLineEdit()
        self.persona_description_edit.setReadOnly(True)
        details_layout.addRow("Description:", self.persona_description_edit)

        layout.addWidget(details_group)

        # System prompt
        prompt_group = QGroupBox("System Prompt")
        prompt_layout = QVBoxLayout(prompt_group)

        self.system_prompt_edit = QTextEdit()
        self.system_prompt_edit.setReadOnly(True)
        self.system_prompt_edit.setMaximumHeight(200)
        prompt_layout.addWidget(self.system_prompt_edit)

        layout.addWidget(prompt_group)

        # Note about persona management
        note_label = QLabel(
            "<i>Note: Personas are currently read-only. Custom persona creation "
            "will be available in a future version.</i>"
        )
        note_label.setWordWrap(True)
        layout.addWidget(note_label)

        layout.addStretch()

    def load_personas(self):
        """Load available personas."""
        personas = self.config_manager.get_available_personas()
        self.persona_combo.clear()

        for persona_name in personas.keys():
            self.persona_combo.addItem(persona_name)

        if personas:
            self.on_persona_changed(list(personas.keys())[0])

    def on_persona_changed(self, persona_name: str):
        """Handle persona selection change."""
        if not persona_name:
            return

        persona = self.config_manager.get_persona(persona_name)

        self.persona_name_edit.setText(persona['name'])
        self.persona_description_edit.setText(persona['description'])
        self.system_prompt_edit.setPlainText(persona['system_prompt'])

    def save_settings(self):
        """Save settings (currently no-op for personas)."""
        pass


class SettingsDialog(QDialog):
    """
    Main settings dialog with tabbed interface for all configuration options.
    """

    settings_changed = pyqtSignal()

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setup_ui()

    def setup_ui(self):
        """Setup the settings dialog UI."""
        self.setWindowTitle("Settings")
        self.setGeometry(300, 300, 600, 500)

        layout = QVBoxLayout(self)

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Add tabs
        self.api_tab = APISettingsTab(self.config_manager)
        self.tab_widget.addTab(self.api_tab, "API Settings")

        self.ui_tab = UISettingsTab(self.config_manager)
        self.tab_widget.addTab(self.ui_tab, "UI Settings")

        self.generation_tab = GenerationSettingsTab(self.config_manager)
        self.tab_widget.addTab(self.generation_tab, "Generation")

        self.personas_tab = PersonasTab(self.config_manager)
        self.tab_widget.addTab(self.personas_tab, "Personas")

        layout.addWidget(self.tab_widget)

        # Button layout
        button_layout = QHBoxLayout()

        # Import/Export buttons
        self.import_button = QPushButton("Import Settings...")
        self.import_button.clicked.connect(self.import_settings)
        button_layout.addWidget(self.import_button)

        self.export_button = QPushButton("Export Settings...")
        self.export_button.clicked.connect(self.export_settings)
        button_layout.addWidget(self.export_button)

        button_layout.addStretch()

        # Reset all button
        self.reset_all_button = QPushButton("Reset All")
        self.reset_all_button.clicked.connect(self.reset_all_settings)
        button_layout.addWidget(self.reset_all_button)

        # Standard buttons
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept_settings)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)

        layout.addLayout(button_layout)

    def accept_settings(self):
        """Accept and save all settings."""
        self.apply_settings()
        self.accept()

    def apply_settings(self):
        """Apply all settings without closing dialog."""
        try:
            self.api_tab.save_settings()
            self.ui_tab.save_settings()
            self.generation_tab.save_settings()
            self.personas_tab.save_settings()

            self.settings_changed.emit()
            QMessageBox.information(self, "Settings Applied", "Settings have been applied successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Settings Error", f"Failed to apply settings:\n{str(e)}")

    def import_settings(self):
        """Import settings from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Settings", "",
            "JSON Files (*.json);;All Files (*)"
        )

        if not file_path:
            return

        try:
            self.config_manager.import_config(file_path)

            # Reload all tabs
            self.api_tab.load_settings()
            self.ui_tab.load_settings()
            self.generation_tab.load_settings()
            self.personas_tab.load_personas()

            QMessageBox.information(self, "Import Successful", "Settings imported successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import settings:\n{str(e)}")

    def export_settings(self):
        """Export settings to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Settings", "genai_settings.json",
            "JSON Files (*.json);;All Files (*)"
        )

        if not file_path:
            return

        try:
            self.config_manager.export_config(file_path)
            QMessageBox.information(self, "Export Successful", f"Settings exported to {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export settings:\n{str(e)}")

    def reset_all_settings(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self, "Reset All Settings",
            "Are you sure you want to reset ALL settings to their default values?\n\n"
            "This will affect API settings, UI preferences, and generation parameters.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.config_manager.reset_to_defaults()

                # Reload all tabs
                self.api_tab.load_settings()
                self.ui_tab.load_settings()
                self.generation_tab.load_settings()
                self.personas_tab.load_personas()

                QMessageBox.information(self, "Reset Complete", "All settings have been reset to defaults.")

            except Exception as e:
                QMessageBox.critical(self, "Reset Error", f"Failed to reset settings:\n{str(e)}")
