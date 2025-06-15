@echo off
REM Setup script for AI Tool Intelligence Platform on Windows
REM This script installs dependencies and sets up the environment

echo 🚀 Setting up AI Tool Intelligence Platform for Windows...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo 💡 Please install Python 3.11+ from https://python.org/downloads/
    echo    Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Check if Node.js is installed
node --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Node.js is not installed or not in PATH
    echo 💡 Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js found
node --version

REM Navigate to project root
cd /d "%~dp0.."

REM Setup backend
echo.
echo 🔄 Setting up backend dependencies...
cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install Python dependencies
pip install -r requirements.txt

REM Copy environment template if .env doesn't exist
if not exist ".env" (
    echo 📋 Creating .env configuration file...
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANT: Edit backend\.env with your AWS credentials
    echo    AWS_ACCESS_KEY_ID=your-access-key-here
    echo    AWS_SECRET_ACCESS_KEY=your-secret-key-here
    echo    AWS_REGION=us-east-1
    echo.
)

cd ..

REM Setup frontend
echo 🔄 Setting up frontend dependencies...
cd frontend

REM Install Node.js dependencies
npm install

cd ..

echo.
echo ✅ Setup completed successfully!
echo.
echo 📋 Next steps:
echo 1. Configure AWS credentials in backend\.env (for research features)
echo 2. Run windows\start-windows.bat to start the application
echo 3. Open http://localhost:3000 in your browser
echo.
echo 💡 For troubleshooting, see docs\setup\windows-setup.md
pause