#!/usr/bin/env python3
"""
Improved launcher script for GenAI Desktop Client.
This script properly handles Python module imports and paths.
"""

import sys
import os
from pathlib import Path

def setup_python_path():
    """Setup Python path for proper module imports."""
    # Get the directory containing this script
    script_dir = Path(__file__).parent.absolute()
    src_dir = script_dir / 'src'

    # Add src directory to Python path at the beginning
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    # Change working directory to src
    os.chdir(src_dir)

    return src_dir

def check_dependencies():
    """Check if required dependencies are available."""
    required_modules = {
        'PyQt5': 'PyQt5',
        'requests': 'requests',
        'aiohttp': 'aiohttp',
        'yaml': 'PyYAML'
    }

    missing = []
    for module, package in required_modules.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)

    return missing

def main():
    """Main launcher function."""
    # Setup Python path
    src_dir = setup_python_path()

    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("\nTo install missing dependencies:")
        print("1. Activate your virtual environment (if using one)")
        print("2. Run: pip install " + " ".join(missing))
        print("3. Or run the setup script: python setup.py")
        return 1

    # Check if main.py exists
    main_script = Path('main.py')
    if not main_script.exists():
        print(f"❌ main.py not found in {os.getcwd()}")
        print("Make sure you're running this script from the project root directory.")
        return 1

    try:
        # Import and run the application
        import main
        return main.main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed and you're in the correct directory.")
        return 1
    except Exception as e:
        print(f"❌ Application error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
