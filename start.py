#!/usr/bin/env python3
"""
Kanban Lite Start Script
Cross-platform launcher for the Kanban web server
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def find_python_executable():
    """Find the Python executable in the virtual environment"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_path = os.path.join(script_dir, ".venv_kanban")

    # Check if virtual environment exists
    if not os.path.exists(venv_path):
        print("❌ Virtual environment not found!")
        print("Please run the setup script first:")
        print("  python setup.py")
        print("  or setup.bat (Windows)")
        print("  or ./setup.sh (Linux/Mac)")
        return None

    # Get Python executable path based on platform
    system = platform.system()
    if system == "Windows":
        python_exe = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        python_exe = os.path.join(venv_path, "bin", "python")

    if not os.path.exists(python_exe):
        print(f"❌ Python executable not found at: {python_exe}")
        print("Please run the setup script to recreate the virtual environment")
        return None

    return python_exe

def start_server():
    """Start the Kanban web server"""
    python_exe = find_python_executable()
    if not python_exe:
        return False

    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "app.py")

    if not os.path.exists(app_path):
        print(f"❌ Application file not found: {app_path}")
        return False

    print("🚀 Starting KanbanLite Server")
    print("============================")
    print(f"Server will start at: http://127.0.0.1:8000")
    print(f"Press Ctrl+C to stop the server")
    print()

    try:
        # Start the FastAPI server
        subprocess.run([python_exe, app_path], cwd=script_dir)
        return True
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        return True
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def main():
    """Main entry point"""
    if not start_server():
        print("\n❌ Failed to start server")
        sys.exit(1)

if __name__ == "__main__":
    main()