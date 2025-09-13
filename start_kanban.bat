@echo off
REM KanbanLite Start Script for Windows

set SCRIPT_DIR=%~dp0
set VENV_PATH=%SCRIPT_DIR%.venv_kanban
set PYTHON_EXE=%VENV_PATH%\Scripts\python.exe
set APP_PATH=%SCRIPT_DIR%app.py

REM Check if virtual environment exists
if not exist "%VENV_PATH%" (
    echo ❌ Virtual environment not found!
    echo Please run the setup script first:
    echo   python setup.py
    echo   or setup.bat
    pause
    exit /b 1
)

REM Check if Python executable exists
if not exist "%PYTHON_EXE%" (
    echo ❌ Python executable not found at: %PYTHON_EXE%
    echo Please run the setup script to recreate the virtual environment
    pause
    exit /b 1
)

REM Check if app.py exists
if not exist "%APP_PATH%" (
    echo ❌ Application file not found: %APP_PATH%
    pause
    exit /b 1
)

echo 🚀 Starting KanbanLite Server
echo ============================
echo Server will start at: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo.

REM Change to script directory and start the server
cd /d "%SCRIPT_DIR%"
"%PYTHON_EXE%" "%APP_PATH%"
pause