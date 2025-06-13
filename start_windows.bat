@echo off
echo AI Tool Intelligence Platform - Windows Startup
echo ================================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "backend\app.py" (
    echo ERROR: Please run this script from the ai-tool-intelligence directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo Creating Python virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo WARNING: Some dependencies may not have installed correctly
)

REM Set environment variables for Windows
set FLASK_ENV=development
set PYTHONPATH=%CD%\backend

REM Check if user wants to skip AWS validation
if "%1"=="--skip-aws" (
    set SKIP_AWS_VALIDATION=1
    echo AWS validation will be skipped
)

REM Start the application with stability features
echo.
echo Starting AI Tool Intelligence Platform...
echo.
python start_stable.py

REM Keep window open if there was an error
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error code: %errorlevel%
    pause
)