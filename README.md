# GenAI Desktop

A comprehensive Python desktop application for interacting with LM Studio's REST API. This cross-platform application provides an intuitive interface for chatting with Large Language Models (LLMs) through LM Studio's local server.

## Features

### Core Functionality
- **LM Studio Integration**: Connect to locally running LM Studio server via REST API
- **Multi-Session Support**: Create, save, load, and manage multiple chat sessions
- **Real-time Streaming**: Toggle between streaming and non-streaming responses
- **Cross-Platform**: Runs on Windows, macOS, and Linux

### User Interface
- **Clean Chat Interface**: Intuitive chat window with message history
- **Session Management**: Organize and manage conversation sessions
- **Model Selection**: Choose from available LM Studio models
- **Persona System**: Predefined system prompts for different use cases
- **Parameter Controls**: Adjust temperature, max tokens, and other generation parameters

### Advanced Features
- **Session Export/Import**: Save conversations as JSON or text files
- **Configuration Management**: Customizable settings for API, UI, and generation
- **Dark/Light Themes**: Multiple UI themes available
- **Keyboard Shortcuts**: Efficient navigation and controls
- **Connection Monitoring**: Real-time connection status to LM Studio

## Installation

### Prerequisites

1. **Python 3.13.2**: Ensure you have Python 3.13.2 installed with miniconda
2. **LM Studio**: Download and install [LM Studio](https://lmstudio.ai/) 
3. **Git**: For cloning the repository

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd GenAI.Desktop.Client
   ```

2. **Create Conda Environment**
   ```bash
   conda env create -f environment.yaml
   conda activate genai-desktop-client
   ```

3. **Verify Installation**
   ```bash
   python --version  # Should show Python 3.13.2
   python -c "import PyQt5; print('PyQt5 installed successfully')"
   ```

4. **Run the Application**
   ```bash
   cd src
   python main.py
   ```

### Alternative Installation (Manual)

If you prefer to install dependencies manually:

```bash
# Create conda environment
conda create -n genai-desktop-client python=3.13.2
conda activate genai-desktop-client

# Install conda packages
conda install -c conda-forge pyqt5=5.15.10 requests=2.31.0 aiohttp=3.9.1 numpy=1.26.2 pyyaml=6.0.1

# Install pip packages
pip install asyncio-mqtt==0.16.1 websockets==12.0 markdown==3.5.1 pygments==2.17.2
```

## Configuration

### LM Studio Setup

1. **Start LM Studio**
   - Launch LM Studio application
   - Load a model of your choice
   - Go to the "Local Server" tab
   - Click "Start Server" (default: http://localhost:1234)

2. **Verify Connection**
   - In the GenAI Desktop Client, go to Settings → API Settings
   - Click "Test Connection" to verify the connection to LM Studio

### Application Settings

The application stores configuration in platform-specific directories:
- **Windows**: `%APPDATA%\GenAI_Desktop\`
- **macOS/Linux**: `~/.config/genai_desktop/`

## Usage

### Basic Usage

1. **Start the Application**
   ```bash
   # If using conda
   conda activate genai-desktop-client
   python run_app.py
   
   # If using virtual environment
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python run_app.py
   ```

2. **Create a New Session**
   - Click "New Session" in the left panel
   - Select a model from the dropdown
   - Choose a persona (optional)
   - Start chatting!

3. **Send Messages**
   - Type your message in the input area
   - Press "Send" or use Ctrl+Enter
   - Watch the response appear in real-time (if streaming is enabled)

### Advanced Features

#### Session Management
- **Save Sessions**: Sessions are automatically saved as you chat
- **Load Sessions**: Double-click on a session in the left panel to load it
- **Export Sessions**: Right-click on a session to export as JSON or text
- **Delete Sessions**: Right-click on a session to delete it

#### Personas
The application includes several predefined personas:
- **User**: Generic user with no specific system prompt
- **Software Engineer**: Expert programming assistant
- **Code Reviewer**: Specialized in code review and best practices
- **Technical Writer**: Focused on documentation and technical writing
- **Data Analyst**: Specialized in data analysis and insights
- **DevOps Engineer**: Expert in infrastructure and deployment

#### Parameter Controls
- **Temperature**: Controls randomness (0.0 = deterministic, 1.0 = very random)
- **Max Tokens**: Maximum number of tokens to generate
- **Streaming**: Toggle real-time response streaming

### Keyboard Shortcuts

- **Ctrl+N**: New session
- **Ctrl+O**: Load session
- **Ctrl+S**: Save current session
- **Ctrl+Enter**: Send message
- **Ctrl+L**: Clear chat
- **Ctrl+Q**: Quit application

## Architecture

### Project Structure
```
GenAI.Desktop/
├── src/
│   ├── main.py              # Application entry point
│   ├── ui/                  # User interface components
│   │   ├── main_window.py   # Main application window
│   │   ├── session_manager.py # Session management UI
│   │   └── settings_dialog.py # Settings dialog
│   ├── api/                 # API client
│   │   └── lm_studio_client.py # LM Studio API client
│   ├── models/              # Data models
│   │   ├── chat_session.py  # Chat session model
│   │   └── message.py       # Message model
│   └── utils/               # Utilities
│       └── config.py        # Configuration management
├── environment.yaml         # Conda environment file
├── requirements.txt         # Python dependencies
├── setup.py                # Installation script
├── run_app.py              # Application launcher
└── README.md               # This file
```

### Key Components

1. **Main Window**: Central UI with chat interface and session management
2. **LM Studio Client**: Handles REST API communication with LM Studio
3. **Session Manager**: Manages chat sessions and conversation history
4. **Configuration System**: Handles application settings and preferences
5. **Data Models**: Structured representation of messages and sessions

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Ensure LM Studio is running and the server is started
   - Check that the host and port settings match LM Studio's configuration
   - Verify firewall settings aren't blocking the connection

2. **Application Won't Start**
   - Verify Python 3.10+ is installed and activated
   - Check that all dependencies are installed correctly
   - Run `python run_app.py` from the project root directory

3. **Import Errors**
   - Ensure the conda environment is activated
   - Reinstall dependencies: `conda env remove -n genai-desktop-client && conda env create -f environment.yaml`

4. **UI Issues**
   - Try different themes in Settings → UI Settings
   - Reset UI settings to defaults in the settings dialog

### Performance Tips

1. **Streaming**: Enable streaming for faster response perception
2. **Session Management**: Regular cleanup of old sessions to maintain performance
3. **Model Selection**: Choose appropriate models for your hardware capabilities

## Development

### Setting up for Development

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd GenAI.Desktop.Client
   conda env create -f environment.yaml
   conda activate genai-desktop-client
   ```

2. **Development Dependencies**
   ```bash
   pip install pytest black flake8 mypy
   ```

3. **Code Style**
   - Use Black for code formatting: `black src/`
   - Use flake8 for linting: `flake8 src/`
   - Use mypy for type checking: `mypy src/`

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## API Reference

### LM Studio API Endpoints

The application uses the following LM Studio API endpoints:

- **GET /v1/models**: List available models
- **POST /v1/chat/completions**: Send chat completion requests

### Configuration Files

Configuration is stored in JSON format:
- `config.json`: Main application configuration
- `sessions/*.json`: Individual chat sessions

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Acknowledgments

- [LM Studio](https://lmstudio.ai/) for the excellent local LLM server
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) for the GUI framework
- The open-source community for various dependencies and inspiration

## Support

For issues, questions, or contributions:
1. Check the troubleshooting section above
2. Search existing issues in the repository
3. Create a new issue with detailed information about your problem

## Version History

- **v1.0.0**: Initial release with core functionality
  - LM Studio integration
  - Session management
  - Multi-persona support
  - Cross-platform compatibility
  - Real-time streaming
  - Configuration management