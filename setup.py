#!/usr/bin/env python3
"""
Setup script for GenAI Desktop.

This script provides easy installation and setup for the GenAI Desktop application.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major != 3 or version.minor < 10:
        print(f"Error: This application requires Python 3.10 or higher")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        print("Please upgrade your Python version.")
        sys.exit(1)

    print(f"Using Python {version.major}.{version.minor}.{version.micro}")

def check_conda():
    """Check if conda is available."""
    try:
        subprocess.run(['conda', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def setup_conda_environment():
    """Setup conda environment."""
    print("Setting up conda environment...")

    env_file = Path(__file__).parent / 'environment.yaml'
    if not env_file.exists():
        print("Error: environment.yaml not found!")
        return False

    try:
        # Remove existing environment if it exists
        subprocess.run(['conda', 'env', 'remove', '-n', 'genai-desktop', '-y'],
                      capture_output=True)

        # Create new environment
        subprocess.run(['conda', 'env', 'create', '-f', str(env_file)],
                      check=True)

        print("✓ Conda environment created successfully!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error creating conda environment: {e}")
        return False

def setup_pip_environment():
    """Setup pip virtual environment."""
    print("Setting up pip virtual environment...")

    venv_dir = Path(__file__).parent / 'venv'
    requirements_file = Path(__file__).parent / 'requirements.txt'

    if not requirements_file.exists():
        print("Error: requirements.txt not found!")
        return False

    try:
        # Create virtual environment
        subprocess.run([sys.executable, '-m', 'venv', str(venv_dir)], check=True)

        # Determine activation script path
        if platform.system() == 'Windows':
            pip_path = venv_dir / 'Scripts' / 'pip.exe'
            python_path = venv_dir / 'Scripts' / 'python.exe'
        else:
            pip_path = venv_dir / 'bin' / 'pip'
            python_path = venv_dir / 'bin' / 'python'

        # Upgrade pip
        subprocess.run([str(python_path), '-m', 'pip', 'install', '--upgrade', 'pip'],
                      check=True)

        # Install requirements
        subprocess.run([str(pip_path), 'install', '-r', str(requirements_file)],
                      check=True)

        print("✓ Virtual environment created successfully!")
        print(f"Virtual environment location: {venv_dir}")
        return True, venv_dir

    except subprocess.CalledProcessError as e:
        print(f"Error creating virtual environment: {e}")
        return False, None

def create_launcher_scripts(venv_dir=None):
    """Create launcher scripts for easy application startup."""
    run_app_script = Path(__file__).parent / 'run_app.py'

    if not run_app_script.exists():
        print("Warning: run_app.py not found, skipping launcher creation")
        return

    # Create batch file for Windows
    if platform.system() == 'Windows':
        if venv_dir:
            launcher_content = f"""@echo off
"{venv_dir}\\Scripts\\python.exe" run_app.py
pause
"""
        else:
            launcher_content = f"""@echo off
call conda activate genai-desktop
python run_app.py
pause
"""

        launcher_path = Path(__file__).parent / 'run_genai.bat'
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        print(f"✓ Windows launcher created: {launcher_path}")

    # Create shell script for Unix-like systems
    else:
        if venv_dir:
            launcher_content = f"""#!/bin/bash
"{venv_dir}/bin/python" run_app.py
"""
        else:
            launcher_content = f"""#!/bin/bash
source $(conda info --base)/etc/profile.d/conda.sh
conda activate genai-desktop
python run_app.py
"""

        launcher_path = Path(__file__).parent / 'run_genai.sh'
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)

        # Make executable
        os.chmod(launcher_path, 0o755)
        print(f"✓ Unix launcher created: {launcher_path}")

def test_installation(venv_dir=None):
    """Test if the installation works."""
    print("\nTesting installation...")

    src_dir = Path(__file__).parent / 'src'

    try:
        if venv_dir:
            # Test with venv python
            if platform.system() == 'Windows':
                python_path = venv_dir / 'Scripts' / 'python.exe'
            else:
                python_path = venv_dir / 'bin' / 'python'
        else:
            # Test with conda environment
            result = subprocess.run(['conda', 'run', '-n', 'genai-desktop-client', 'python',
                                   '-c', 'import PyQt5; print("PyQt5 OK")'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ Installation test passed!")
                return True
            else:
                print(f"✗ Installation test failed: {result.stderr}")
                return False

        # Test imports for pip installation
        test_script = """
import sys
try:
    import PyQt5
    print("✓ PyQt5 imported successfully")
except ImportError as e:
    print(f"✗ PyQt5 import failed: {e}")
    sys.exit(1)

try:
    import requests
    print("✓ requests imported successfully")
except ImportError as e:
    print(f"✗ requests import failed: {e}")
    sys.exit(1)

try:
    import aiohttp
    print("✓ aiohttp imported successfully")
except ImportError as e:
    print(f"✗ aiohttp import failed: {e}")
    sys.exit(1)

print("✓ All dependencies imported successfully!")
"""

        result = subprocess.run([str(python_path), '-c', test_script],
                              capture_output=True, text=True, cwd=src_dir)

        if result.returncode == 0:
            print("✓ Installation test passed!")
            print(result.stdout)
            return True
        else:
            print(f"✗ Installation test failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"✗ Installation test failed: {e}")
        return False

def print_usage_instructions(use_conda=True, venv_dir=None):
    """Print usage instructions."""
    print("\n" + "="*60)
    print("🎉 INSTALLATION COMPLETE!")
    print("="*60)

    if use_conda:
        print("\nTo run the application:")
        print("1. Activate the conda environment:")
        print("   conda activate genai-desktop")
        print("2. Navigate to the src directory and run:")
        print("   python run_app.py")
        print("\nOr use the launcher script:")
        if platform.system() == 'Windows':
            print("   Double-click: run_genai.bat")
        else:
            print("   ./run_genai.sh")
    else:
        print("\nTo run the application:")
        print("1. Activate the virtual environment:")
        if platform.system() == 'Windows':
            print(f"   {venv_dir}\\Scripts\\activate")
        else:
            print(f"   source {venv_dir}/bin/activate")
        print("2. Navigate to the src directory and run:")
        print("   python run_app.py")
        print("\nOr use the launcher script:")
        if platform.system() == 'Windows':
            print("   Double-click: run_genai.bat")
        else:
            print("   ./run_genai.sh")

    print("\n📋 Before running:")
    print("1. Make sure LM Studio is installed and running")
    print("2. Load a model in LM Studio")
    print("3. Start the Local Server in LM Studio (usually http://localhost:1234)")

    print("\n🔧 Configuration:")
    print("- Settings are stored in your user config directory")
    print("- Use Settings → API Settings to configure LM Studio connection")
    print("- Use Settings → UI Settings to customize the interface")

    print("\n📖 For more information, see README.md")
    print("="*60)

def main():
    """Main setup function."""
    print("GenAI Desktop - Setup Script")
    print("="*40)

    # Check Python version
    check_python_version()

    # Check if conda is available
    has_conda = check_conda()

    print(f"\nDetected system: {platform.system()}")
    print(f"Python version: {sys.version}")
    print(f"Conda available: {'Yes' if has_conda else 'No'}")

    # Choose installation method
    if has_conda:
        print("\nInstallation options:")
        print("1. Use conda (recommended)")
        print("2. Use pip + virtual environment")
        choice = input("Choose installation method (1/2): ").strip()

        if choice == '1' or choice == '':
            use_conda = True
        elif choice == '2':
            use_conda = False
        else:
            print("Invalid choice. Using conda.")
            use_conda = True
    else:
        print("\nConda not found. Using pip + virtual environment.")
        use_conda = False

    venv_dir = None
    success = False

    if use_conda:
        success = setup_conda_environment()
    else:
        success, venv_dir = setup_pip_environment()

    if not success:
        print("\n❌ Setup failed!")
        sys.exit(1)

    # Create launcher scripts
    create_launcher_scripts(venv_dir)

    # Test installation
    if test_installation(venv_dir):
        print_usage_instructions(use_conda, venv_dir)
    else:
        print("\n⚠️  Setup completed but testing failed.")
        print("You may need to manually install missing dependencies.")

if __name__ == '__main__':
    main()
