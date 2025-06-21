"""
Configuration management utility for the GenAI Desktop.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ApiConfig:
    """Configuration for LM Studio API connection."""
    host: str = "localhost"
    port: int = 1234
    base_url: str = ""
    timeout: int = 30
    max_retries: int = 3

    def __post_init__(self):
        """Set base URL if not provided."""
        if not self.base_url:
            self.base_url = f"http://{self.host}:{self.port}"

    @property
    def models_endpoint(self) -> str:
        """Get the models endpoint URL."""
        return f"{self.base_url}/v1/models"

    @property
    def completions_endpoint(self) -> str:
        """Get the completions endpoint URL."""
        return f"{self.base_url}/v1/chat/completions"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'host': self.host,
            'port': self.port,
            'base_url': self.base_url,
            'timeout': self.timeout,
            'max_retries': self.max_retries
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ApiConfig':
        """Create from dictionary."""
        return cls(
            host=data.get('host', 'localhost'),
            port=data.get('port', 1234),
            base_url=data.get('base_url', ''),
            timeout=data.get('timeout', 30),
            max_retries=data.get('max_retries', 3)
        )


@dataclass
class UIConfig:
    """Configuration for UI settings."""
    theme: str = "default"
    font_family: str = "Arial"
    font_size: int = 10
    window_width: int = 1200
    window_height: int = 800
    auto_scroll: bool = True
    save_window_state: bool = True
    show_timestamps: bool = True
    word_wrap: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'theme': self.theme,
            'font_family': self.font_family,
            'font_size': self.font_size,
            'window_width': self.window_width,
            'window_height': self.window_height,
            'auto_scroll': self.auto_scroll,
            'save_window_state': self.save_window_state,
            'show_timestamps': self.show_timestamps,
            'word_wrap': self.word_wrap
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UIConfig':
        """Create from dictionary."""
        return cls(
            theme=data.get('theme', 'default'),
            font_family=data.get('font_family', 'Arial'),
            font_size=data.get('font_size', 10),
            window_width=data.get('window_width', 1200),
            window_height=data.get('window_height', 800),
            auto_scroll=data.get('auto_scroll', True),
            save_window_state=data.get('save_window_state', True),
            show_timestamps=data.get('show_timestamps', True),
            word_wrap=data.get('word_wrap', True)
        )


@dataclass
class GenerationConfig:
    """Configuration for text generation parameters."""
    default_temperature: float = 0.7
    default_max_tokens: int = 1000
    default_top_p: float = 0.9
    default_frequency_penalty: float = 0.0
    default_presence_penalty: float = 0.0
    enable_streaming: bool = True
    stream_chunk_size: int = 1024

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'default_temperature': self.default_temperature,
            'default_max_tokens': self.default_max_tokens,
            'default_top_p': self.default_top_p,
            'default_frequency_penalty': self.default_frequency_penalty,
            'default_presence_penalty': self.default_presence_penalty,
            'enable_streaming': self.enable_streaming,
            'stream_chunk_size': self.stream_chunk_size
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GenerationConfig':
        """Create from dictionary."""
        return cls(
            default_temperature=data.get('default_temperature', 0.7),
            default_max_tokens=data.get('default_max_tokens', 1000),
            default_top_p=data.get('default_top_p', 0.9),
            default_frequency_penalty=data.get('default_frequency_penalty', 0.0),
            default_presence_penalty=data.get('default_presence_penalty', 0.0),
            enable_streaming=data.get('enable_streaming', True),
            stream_chunk_size=data.get('stream_chunk_size', 1024)
        )


# Predefined personas with system prompts
PERSONAS = {
    "User": {
        "name": "User",
        "description": "Generic user - no specific system prompt",
        "system_prompt": ""
    },
    "Software Engineer": {
        "name": "Software Engineer",
        "description": "Expert software engineer assistant",
        "system_prompt": """You are an expert software engineer with extensive knowledge in multiple programming languages, frameworks, and best practices. You provide clear, concise, and practical solutions to programming problems. You write clean, well-documented code and explain complex concepts in an understandable way. You stay up-to-date with the latest technologies and development methodologies."""
    },
    "Code Reviewer": {
        "name": "Code Reviewer",
        "description": "Code review specialist",
        "system_prompt": """You are a senior code reviewer with expertise in code quality, security, and best practices. You provide constructive feedback on code, identifying potential issues, suggesting improvements, and ensuring adherence to coding standards. You focus on maintainability, performance, security, and readability."""
    },
    "Technical Writer": {
        "name": "Technical Writer",
        "description": "Technical documentation specialist",
        "system_prompt": """You are a skilled technical writer who creates clear, comprehensive documentation. You excel at explaining complex technical concepts in a way that's accessible to the target audience. You write user guides, API documentation, tutorials, and other technical content with proper structure and formatting."""
    },
    "Data Analyst": {
        "name": "Data Analyst",
        "description": "Data analysis and insights specialist",
        "system_prompt": """You are a data analyst with expertise in statistical analysis, data visualization, and deriving insights from data. You help with data interpretation, creating meaningful visualizations, identifying patterns and trends, and providing actionable recommendations based on data analysis."""
    },
    "DevOps Engineer": {
        "name": "DevOps Engineer",
        "description": "DevOps and infrastructure specialist",
        "system_prompt": """You are a DevOps engineer with expertise in CI/CD, containerization, cloud infrastructure, and automation. You help with deployment strategies, infrastructure as code, monitoring solutions, and optimizing development workflows."""
    }
}


class ConfigManager:
    """
    Manages application configuration settings.
    """

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_dir (Optional[str]): Custom configuration directory
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Use platform-appropriate config directory
            if os.name == 'nt':  # Windows
                self.config_dir = Path(os.environ.get('APPDATA', '')) / 'GenAI_Desktop'
            elif os.name == 'posix':  # macOS/Linux
                self.config_dir = Path.home() / '.config' / 'genai_desktop'
            else:
                self.config_dir = Path.home() / '.genai_desktop'

        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / 'config.json'
        self.sessions_dir = self.config_dir / 'sessions'
        self.sessions_dir.mkdir(exist_ok=True)

        # Configuration objects
        self.api_config = ApiConfig()
        self.ui_config = UIConfig()
        self.generation_config = GenerationConfig()

        # Load existing configuration
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from file."""
        if not self.config_file.exists():
            self.save_config()  # Create default config
            return

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.api_config = ApiConfig.from_dict(data.get('api', {}))
            self.ui_config = UIConfig.from_dict(data.get('ui', {}))
            self.generation_config = GenerationConfig.from_dict(data.get('generation', {}))

        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading config: {e}")
            # Use default configuration
            self.save_config()

    def save_config(self) -> None:
        """Save configuration to file."""
        config_data = {
            'api': self.api_config.to_dict(),
            'ui': self.ui_config.to_dict(),
            'generation': self.generation_config.to_dict(),
            'version': '1.0.0'
        }

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_sessions_directory(self) -> Path:
        """Get the sessions directory path."""
        return self.sessions_dir

    def get_config_directory(self) -> Path:
        """Get the configuration directory path."""
        return self.config_dir

    def reset_to_defaults(self) -> None:
        """Reset all configuration to default values."""
        self.api_config = ApiConfig()
        self.ui_config = UIConfig()
        self.generation_config = GenerationConfig()
        self.save_config()

    def update_api_config(self, **kwargs) -> None:
        """Update API configuration."""
        for key, value in kwargs.items():
            if hasattr(self.api_config, key):
                setattr(self.api_config, key, value)
        self.save_config()

    def update_ui_config(self, **kwargs) -> None:
        """Update UI configuration."""
        for key, value in kwargs.items():
            if hasattr(self.ui_config, key):
                setattr(self.ui_config, key, value)
        self.save_config()

    def update_generation_config(self, **kwargs) -> None:
        """Update generation configuration."""
        for key, value in kwargs.items():
            if hasattr(self.generation_config, key):
                setattr(self.generation_config, key, value)
        self.save_config()

    def get_persona(self, name: str) -> Dict[str, str]:
        """
        Get persona configuration by name.

        Args:
            name (str): Persona name

        Returns:
            Dict[str, str]: Persona configuration
        """
        return PERSONAS.get(name, PERSONAS["User"])

    def get_available_personas(self) -> Dict[str, Dict[str, str]]:
        """Get all available personas."""
        return PERSONAS.copy()

    def export_config(self, file_path: str) -> None:
        """
        Export configuration to file.

        Args:
            file_path (str): Path to export file
        """
        config_data = {
            'api': self.api_config.to_dict(),
            'ui': self.ui_config.to_dict(),
            'generation': self.generation_config.to_dict(),
            'personas': PERSONAS,
            'exported_at': str(datetime.now()),
            'version': '1.0.0'
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

    def import_config(self, file_path: str) -> None:
        """
        Import configuration from file.

        Args:
            file_path (str): Path to import file
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'api' in data:
            self.api_config = ApiConfig.from_dict(data['api'])
        if 'ui' in data:
            self.ui_config = UIConfig.from_dict(data['ui'])
        if 'generation' in data:
            self.generation_config = GenerationConfig.from_dict(data['generation'])

        self.save_config()


# Global configuration instance
config_manager = ConfigManager()
