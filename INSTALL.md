# Installation Guide

Quick installation guide for GenAI Desktop.

## Prerequisites

- **Python 3.10+** (Python 3.12 recommended)
- **LM Studio** installed and running
- **Git** (optional, for cloning)

## Quick Install

### Option 1: Automatic Setup (Recommended)
```bash
# Clone or download the project
git clone <repository-url>
cd GenAI.Desktop

# Run automatic setup
python setup.py
```

### Option 2: Manual Installation

#### Using Conda
```bash
# Create environment
conda env create -f environment.yaml
conda activate genai-desktop

# Run the application
python run_app.py
```

#### Using pip + Virtual Environment
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

# Run the application
python run_app.py
```

## Running the Application

After installation, start the application with:
```bash
python run_app.py
```

## LM Studio Setup

1. **Install LM Studio** from [lmstudio.ai](https://lmstudio.ai)
2. **Download a model** (e.g., llama-2-7b-chat)
3. **Load the model** in LM Studio
4. **Start Local Server** (usually http://localhost:1234)

## Troubleshooting

- **PyQt5 issues**: Try `pip install --only-binary=all PyQt5`
- **Import errors**: Make sure you're running from the project root
- **Connection issues**: Verify LM Studio server is running

For detailed instructions, see [QUICKSTART.md](QUICKSTART.md) or [README.md](README.md).