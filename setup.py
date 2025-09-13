#!/usr/bin/env python3
"""
Kanban Lite Setup Script
Cross-platform setup for the portable Kanban board
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"✓ {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {description} failed")
        print(f"Command: {cmd}")
        print(f"Error: {e.stderr}")
        return False

def create_venv(venv_path):
    """Create virtual environment"""
    if os.path.exists(venv_path):
        print(f"✓ Virtual environment already exists at {venv_path}")
        return True

    return run_command(f'python -m venv "{venv_path}"', "Creating virtual environment")

def get_python_executable(venv_path):
    """Get the path to the Python executable in the virtual environment"""
    system = platform.system()
    if system == "Windows":
        return os.path.join(venv_path, "Scripts", "python.exe")
    else:
        return os.path.join(venv_path, "bin", "python")

def install_requirements(python_exe):
    """Install Python requirements"""
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    return run_command(f'"{python_exe}" -m pip install -r "{req_file}"', "Installing Python dependencies")

def initialize_database(python_exe):
    """Initialize the database"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Use forward slashes and raw string to avoid Windows path issues
    script_dir = script_dir.replace('\\', '/')
    return run_command(f'"{python_exe}" -c "import sys; sys.path.insert(0, r\'{script_dir}\'); from kanban_agent import ensure_setup; ensure_setup(); print(\'Database initialized successfully\')"', "Initializing database")

def main():
    print("🚀 KanbanLite Setup")
    print("==================")

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_name = ".venv_kanban"
    venv_path = os.path.join(script_dir, venv_name)

    print(f"Setting up KanbanLite in: {script_dir}")
    print(f"Virtual environment: {venv_path}")
    print()

    # Step 1: Create virtual environment
    if not create_venv(venv_path):
        print("❌ Setup failed: Could not create virtual environment")
        return False

    # Step 2: Get Python executable path
    python_exe = get_python_executable(venv_path)
    if not os.path.exists(python_exe):
        print(f"❌ Setup failed: Python executable not found at {python_exe}")
        return False

    # Step 3: Upgrade pip
    if not run_command(f'"{python_exe}" -m pip install --upgrade pip', "Upgrading pip"):
        print("❌ Setup failed: Could not upgrade pip")
        return False

    # Step 4: Install requirements
    if not install_requirements(python_exe):
        print("❌ Setup failed: Could not install requirements")
        return False

    # Step 5: Initialize database
    if not initialize_database(python_exe):
        print("❌ Setup failed: Could not initialize database")
        return False

    print()
    print("✅ Setup completed successfully!")
    print()
    print("Next steps:")
    print("1. Start the server:")

    system = platform.system()
    if system == "Windows":
        print("   python start.py")
        print("   or double-click start.bat")
    else:
        print("   python start.py")
        print("   or ./start.sh")

    print("2. Open your browser to: http://127.0.0.1:8000")
    print("3. Start managing your tasks!")
    print()
    print("For CLI usage:")
    print(f'   "{python_exe}" kanban_agent.py --help')

    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)