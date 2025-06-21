# GenAI Desktop - Development Guide

This guide provides comprehensive information for developers who want to contribute to or modify the GenAI Desktop.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Project Architecture](#project-architecture)
- [Code Structure](#code-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Standards](#code-standards)
- [API Documentation](#api-documentation)
- [Building and Packaging](#building-and-packaging)
- [Contributing](#contributing)
- [Debugging](#debugging)

## Development Environment Setup

### Prerequisites

- Python 3.13.2 (miniconda/anaconda recommended)
- Git
- Code editor (VS Code, PyCharm, etc.)
- LM Studio for testing

### Setup Steps

1. **Clone and Setup Environment**
   ```bash
   git clone <repository-url>
   cd GenAI.Desktop
   
   # Create development environment
   conda env create -f environment.yaml
   conda activate genai-desktop
   
   # Install development dependencies
   pip install pytest black flake8 mypy pre-commit
   ```

2. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

3. **Configure IDE**
   - Set Python interpreter to the conda environment
   - Configure linting (flake8) and formatting (black)
   - Set up debugging configuration

### Development Dependencies

```bash
# Code quality tools
pip install black==23.7.0          # Code formatting
pip install flake8==6.0.0          # Linting
pip install mypy==1.5.0            # Type checking
pip install isort==5.12.0          # Import sorting

# Testing
pip install pytest==7.4.0          # Testing framework
pip install pytest-asyncio==0.21.1 # Async testing
pip install pytest-qt==4.2.0       # Qt testing
pip install pytest-cov==4.1.0      # Coverage

# Documentation
pip install sphinx==7.1.2          # Documentation
pip install sphinx-rtd-theme==1.3.0

# Development utilities
pip install pre-commit==3.3.3      # Git hooks
pip install bump2version==1.0.1    # Version management
```

## Project Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UI Layer      │    │  Business Logic │    │  Data Layer     │
│                 │    │                 │    │                 │
│ - MainWindow    │◄──►│ - API Client    │◄──►│ - Models        │
│ - Dialogs       │    │ - Session Mgmt  │    │ - Config        │
│ - Widgets       │    │ - Threading     │    │ - File I/O      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  External APIs  │
                    │                 │
                    │ - LM Studio     │
                    │ - File System   │
                    └─────────────────┘
```

### Component Relationships

- **UI Components** (PyQt5-based) handle user interactions
- **Business Logic** manages application state and operations
- **Data Models** represent core entities (sessions, messages, config)
- **API Client** handles external communication with LM Studio
- **Configuration System** manages persistent settings

## Code Structure

### Directory Layout

```
GenAI.Desktop/
├── src/                    # Source code
│   ├── main.py            # Application entry point
│   ├── ui/                # UI components
│   │   ├── __init__.py
│   │   ├── main_window.py # Main application window
│   │   ├── session_manager.py # Session management UI
│   │   └── settings_dialog.py # Settings configuration
│   ├── api/               # API clients
│   │   ├── __init__.py
│   │   └── lm_studio_client.py # LM Studio REST API client
│   ├── models/            # Data models
│   │   ├── __init__.py
│   │   ├── chat_session.py # Chat session model
│   │   └── message.py     # Message model
│   └── utils/             # Utilities
│       ├── __init__.py
│       └── config.py      # Configuration management
├── tests/                 # Test files
├── docs/                  # Documentation
├── scripts/               # Build and utility scripts
├── environment.yaml       # Conda environment
├── requirements.txt       # Python dependencies
└── setup.py              # Installation script
```

### Key Design Patterns

1. **Model-View Pattern**: Clear separation between data models and UI
2. **Factory Pattern**: For creating UI components and API clients
3. **Observer Pattern**: For UI updates and event handling
4. **Strategy Pattern**: For different API communication methods
5. **Singleton Pattern**: For configuration management

## Development Workflow

### Git Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow code standards
   - Add tests for new functionality
   - Update documentation

3. **Pre-commit Checks**
   ```bash
   # Format code
   black src/
   
   # Sort imports
   isort src/
   
   # Lint code
   flake8 src/
   
   # Type checking
   mypy src/
   
   # Run tests
   pytest
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**

### Commit Message Convention

Follow conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test additions/modifications
- `chore:` - Maintenance tasks

## Testing

### Test Structure

```
tests/
├── __init__.py
├── unit/                  # Unit tests
│   ├── test_models.py
│   ├── test_api_client.py
│   └── test_config.py
├── integration/           # Integration tests
│   ├── test_ui_integration.py
│   └── test_api_integration.py
├── fixtures/             # Test data
│   ├── sample_sessions.json
│   └── mock_responses.json
└── conftest.py           # Pytest configuration
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_session"
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch
from src.models.message import Message, MessageRole

class TestMessage:
    def test_message_creation(self):
        message = Message(
            content="Hello, world!",
            role=MessageRole.USER
        )
        assert message.content == "Hello, world!"
        assert message.role == MessageRole.USER
        assert message.is_user_message()

    @patch('src.api.lm_studio_client.requests')
    def test_api_client_connection(self, mock_requests):
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.get.return_value = mock_response
        
        # Test connection
        from src.api.lm_studio_client import LMStudioClient
        client = LMStudioClient(config_manager)
        assert client.test_connection() is True
```

### UI Testing

```python
import pytest
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from src.ui.main_window import MainWindow

@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for testing."""
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    yield app
    app.quit()

def test_main_window_creation(qapp):
    window = MainWindow()
    assert window.windowTitle() == "GenAI Desktop Client - LM Studio Interface"
    
def test_send_button_click(qapp):
    window = MainWindow()
    # Simulate button click
    QTest.mouseClick(window.send_btn, Qt.LeftButton)
    # Assert expected behavior
```

## Code Standards

### Python Style Guide

Follow PEP 8 with these specific guidelines:

1. **Line Length**: 88 characters (Black default)
2. **Imports**: Organized with isort
3. **Docstrings**: Google style docstrings
4. **Type Hints**: Use for all public methods

### Code Formatting

```python
def example_function(
    param1: str,
    param2: int,
    param3: Optional[Dict[str, Any]] = None
) -> Tuple[bool, str]:
    """
    Example function with proper formatting.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2
        param3: Optional parameter with default value
    
    Returns:
        Tuple containing success status and message
    
    Raises:
        ValueError: If param2 is negative
    """
    if param2 < 0:
        raise ValueError("param2 must be non-negative")
    
    # Implementation here
    return True, "Success"
```

### Linting Configuration

Create `.flake8` file:
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    venv,
    build,
    dist
```

## API Documentation

### LM Studio API Integration

The application integrates with LM Studio's REST API:

- **Base URL**: `http://localhost:1234` (default)
- **Models Endpoint**: `GET /v1/models`
- **Chat Completions**: `POST /v1/chat/completions`

### API Client Usage

```python
from src.api.lm_studio_client import LMStudioClient
from src.utils.config import config_manager

# Initialize client
client = LMStudioClient(config_manager)

# Test connection
if client.test_connection():
    print("Connected to LM Studio")

# Get available models
models = client.get_available_models()

# Send chat completion
response = client.send_chat_completion(
    messages=[{"role": "user", "content": "Hello!"}],
    model="llama-2-7b-chat",
    temperature=0.7,
    max_tokens=100
)
```

## Building and Packaging

### Development Build

```bash
# Install in development mode
pip install -e .

# Create standalone executable (PyInstaller)
pip install pyinstaller
pyinstaller --windowed --onefile src/main.py
```

### Distribution

```bash
# Create source distribution
python setup.py sdist

# Create wheel distribution
python setup.py bdist_wheel

# Upload to PyPI (if applicable)
twine upload dist/*
```

### Cross-Platform Considerations

- **File paths**: Use `pathlib.Path` for cross-platform compatibility
- **Configuration**: Platform-specific config directories
- **Icons**: Different formats for different platforms
- **Dependencies**: Ensure all dependencies support target platforms

## Contributing

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes following the style guide
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request with detailed description

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and pass
- [ ] Documentation is updated
- [ ] No breaking changes (or properly documented)
- [ ] Performance impact considered
- [ ] Security implications reviewed

## Debugging

### Debug Configuration

**VS Code launch.json**:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "GenAI Desktop",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/run_app.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        }
    ]
}
```

### Logging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Debug Scenarios

1. **UI Issues**: Use Qt Designer for layout debugging
2. **API Issues**: Monitor network traffic with tools like Wireshark
3. **Threading Issues**: Use thread-safe logging and debugging
4. **Memory Issues**: Use memory profilers like `memory_profiler`

### Performance Profiling

```python
import cProfile
import pstats

# Profile the application
cProfile.run('main()', 'profile_stats')
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative').print_stats(10)
```

## Release Process

1. **Version Bump**
   ```bash
   bump2version patch  # or minor, major
   ```

2. **Update Changelog**
   - Document new features
   - Document bug fixes
   - Document breaking changes

3. **Tag Release**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

4. **Build and Distribute**
   ```bash
   python setup.py sdist bdist_wheel
   ```

## Additional Resources

- [PyQt5 Documentation](https://doc.qt.io/qtforpython/)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [LM Studio API Documentation](https://lmstudio.ai/docs)
- [Pytest Documentation](https://docs.pytest.org/)

## Getting Help

- **Documentation**: Check this guide and README.md
- **Issues**: Search existing GitHub issues
- **Discussions**: Use GitHub discussions for questions
- **Code Review**: Request review from maintainers