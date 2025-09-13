#!/bin/bash
# KanbanLite Setup Script for Linux/Mac

echo "🚀 KanbanLite Setup"
echo "=================="

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/.venv_kanban"

echo "Setting up KanbanLite in: $SCRIPT_DIR"
echo "Virtual environment: $VENV_PATH"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Error: Python is not installed or not in PATH"
        echo "Please install Python 3.7 or higher"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "✓ Using Python: $PYTHON_CMD"

# Create virtual environment
if [ -d "$VENV_PATH" ]; then
    echo "✓ Virtual environment already exists"
else
    echo "✓ Creating virtual environment..."
    if ! $PYTHON_CMD -m venv "$VENV_PATH"; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"
PYTHON_EXE="$VENV_PATH/bin/python"

# Upgrade pip
echo "✓ Upgrading pip..."
if ! "$PYTHON_EXE" -m pip install --upgrade pip; then
    echo "❌ Failed to upgrade pip"
    exit 1
fi

# Install requirements
echo "✓ Installing Python dependencies..."
if ! "$PYTHON_EXE" -m pip install -r "$SCRIPT_DIR/requirements.txt"; then
    echo "❌ Failed to install requirements"
    exit 1
fi

# Initialize database
echo "✓ Initializing database..."
cd "$SCRIPT_DIR"
if ! "$PYTHON_EXE" -c "from kanban_agent import ensure_setup; ensure_setup(); print('Database initialized successfully')"; then
    echo "❌ Failed to initialize database"
    exit 1
fi

echo
echo "✅ Setup completed successfully!"
echo
echo "Next steps:"
echo "1. Start the server:"
echo "   python start.py"
echo "   or ./start.sh"
echo "2. Open your browser to: http://127.0.0.1:8000"
echo "3. Start managing your tasks!"
echo
echo "For CLI usage:"
echo "   $PYTHON_EXE kanban_agent.py --help"
echo

# Make start script executable
chmod +x "$SCRIPT_DIR/start.sh" 2>/dev/null || true