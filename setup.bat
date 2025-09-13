@echo off
REM KanbanLite Setup Script for Windows

echo 🚀 KanbanLite Setup
echo ==================

REM Get script directory
set SCRIPT_DIR=%~dp0
set VENV_PATH=%SCRIPT_DIR%.venv_kanban

echo Setting up KanbanLite in: %SCRIPT_DIR%
echo Virtual environment: %VENV_PATH%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://python.org
    pause
    exit /b 1
)

echo ✓ Python found

REM Create virtual environment
if exist "%VENV_PATH%" (
    echo ✓ Virtual environment already exists
) else (
    echo ✓ Creating virtual environment...
    python -m venv "%VENV_PATH%"
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

set PYTHON_EXE=%VENV_PATH%\Scripts\python.exe

REM Upgrade pip
echo ✓ Upgrading pip...
"%PYTHON_EXE%" -m pip install --upgrade pip
if errorlevel 1 (
    echo ❌ Failed to upgrade pip
    pause
    exit /b 1
)

REM Install requirements
echo ✓ Installing Python dependencies...
"%PYTHON_EXE%" -m pip install -r "%SCRIPT_DIR%requirements.txt"
if errorlevel 1 (
    echo ❌ Failed to install requirements
    pause
    exit /b 1
)

REM Initialize database
echo ✓ Initializing database...
cd /d "%SCRIPT_DIR%"
"%PYTHON_EXE%" -c "from kanban_agent import ensure_setup; ensure_setup(); print('Database initialized successfully')"
if errorlevel 1 (
    echo ❌ Failed to initialize database
    pause
    exit /b 1
)

echo.
echo ✅ Setup completed successfully!
echo.
echo Next steps:
echo 1. Start the server:
echo    python start.py
echo    or double-click start.bat
echo 2. Open your browser to: http://127.0.0.1:8000
echo 3. Start managing your tasks!
echo.
echo For CLI usage:
echo    "%PYTHON_EXE%" kanban_agent.py --help
echo.
pause