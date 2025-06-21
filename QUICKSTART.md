# GenAI Desktop - Quick Start Guide

Get up and running with the GenAI Desktop in just a few minutes!

## Prerequisites

Before you begin, make sure you have:

1. **Python 3.13.2** installed with miniconda or anaconda
2. **LM Studio** downloaded and installed from [lmstudio.ai](https://lmstudio.ai/)
3. **Git** for cloning the repository (optional)

## Step 1: Get the Application

### Option A: Clone from Repository
```bash
git clone <repository-url>
cd GenAI.Desktop
```

### Option B: Download ZIP
1. Download the project ZIP file
2. Extract to your desired location
3. Open terminal/command prompt in the extracted folder

## Step 2: Install Dependencies

### Automatic Setup (Recommended)
```bash
python setup.py
```
This script will:
- Detect your Python environment
- Install all required dependencies
- Create launcher scripts
- Test the installation

### Manual Setup with Conda
```bash
# Create and activate environment
conda env create -f environment.yaml
conda activate genai-desktop-client

# Verify installation
python -c "import PyQt5; print('Installation successful!')"
```

### Manual Setup with Pip
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Set Up LM Studio

1. **Launch LM Studio**
2. **Download a Model**:
   - Go to the "Explore" tab
   - Download a model (e.g., "llama-2-7b-chat" or "mistral-7b-instruct")
   - Wait for download to complete

3. **Load the Model**:
   - Go to "Chat" tab
   - Select your downloaded model
   - Click "Load Model"

4. **Start Local Server**:
   - Go to "Local Server" tab
   - Click "Start Server"
   - Note the server URL (usually `http://localhost:1234`)

## Step 4: Run the Application

### Using Launcher Scripts (if created by setup.py)
- **Windows**: Double-click `run_genai_client.bat`
- **macOS/Linux**: Run `./run_genai_client.sh`

### Direct Launch (Recommended)
```bash
python run_app.py
```

### Manual Launch
```bash
# If using conda
conda activate genai-desktop-client
python run_app.py

# If using pip/venv
# First activate your virtual environment, then:
python run_app.py
```

## Step 5: First Use

1. **Application Startup**:
   - The application will start with a splash screen
   - Wait for the main window to appear

2. **Check Connection**:
   - Look at the bottom status bar
   - Should show "Connected to LM Studio" in green
   - If red, check LM Studio is running and server is started

3. **Start Chatting**:
   - Click "New Session" in the left panel
   - Select your model from the dropdown
   - Choose a persona (optional)
   - Type a message and click "Send" or press Ctrl+Enter

## Troubleshooting

### Common Issues

**"Connection failed" or red status**
- Ensure LM Studio is running
- Check that Local Server is started in LM Studio
- Verify the server URL in Settings → API Settings

**"Module not found" errors**
- Make sure you activated the correct environment
- Reinstall dependencies: `pip install -r requirements.txt`

**Application won't start**
- Check Python version: `python --version`
- Try running: `python run_app.py`
- Make sure you're in the project root directory

**UI looks broken or missing**
- Try different themes in Settings → UI Settings
- Reinstall PyQt5: `pip uninstall PyQt5 && pip install PyQt5`

### Quick Fixes

```bash
# Reset environment (conda)
conda env remove -n genai-desktop
conda env create -f environment.yaml

# Reset environment (pip)
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Test installation
python run_app.py
```

## Next Steps

Once you have the application running:

1. **Explore Personas**: Try different personas like "Software Engineer" or "Data Analyst"
2. **Adjust Parameters**: Experiment with temperature and max tokens
3. **Session Management**: Save and load different conversations
4. **Settings**: Customize the UI and API settings to your preference

## Getting Help

- **Documentation**: See `README.md` for detailed information
- **Settings**: Use Settings → API Settings to test connection
- **Logs**: Check application logs in your config directory
- **Issues**: Check the project repository for known issues

## Configuration Locations

Your settings and sessions are saved in:
- **Windows**: `%APPDATA%\GenAI_Desktop\`
- **macOS**: `~/Library/Application Support/genai_desktop/`
- **Linux**: `~/.config/genai_desktop/`

## Quick Commands Summary

```bash
# Setup
python setup.py

# Run (conda)
conda activate genai-desktop && python run_app.py

# Run (pip)
source venv/bin/activate && python run_app.py

# Direct run
python run_app.py
```

That's it! You should now have a fully functional GenAI Desktop connected to LM Studio. Happy chatting! 🚀