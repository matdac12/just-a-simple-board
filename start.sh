#!/bin/bash
# KanbanLite Start Script for Linux/Mac

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/.venv_kanban"
PYTHON_EXE="$VENV_PATH/bin/python"
APP_PATH="$SCRIPT_DIR/app.py"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run the setup script first:"
    echo "  python setup.py"
    echo "  or ./setup.sh"
    exit 1
fi

# Check if Python executable exists
if [ ! -f "$PYTHON_EXE" ]; then
    echo "❌ Python executable not found at: $PYTHON_EXE"
    echo "Please run the setup script to recreate the virtual environment"
    exit 1
fi

# Check if app.py exists
if [ ! -f "$APP_PATH" ]; then
    echo "❌ Application file not found: $APP_PATH"
    exit 1
fi

echo "🚀 Starting KanbanLite Server"
echo "============================"
echo "Server will start at: http://127.0.0.1:8000"
echo "Press Ctrl+C to stop the server"
echo

# Change to script directory and start the server
cd "$SCRIPT_DIR"
exec "$PYTHON_EXE" "$APP_PATH"