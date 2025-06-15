@echo off
echo ========================================
echo AI Tool Intelligence Platform Setup
echo ========================================
echo.
echo This will set up the AI Tool Intelligence Platform on Windows.
echo.
echo Prerequisites:
echo - Python 3.10+ installed and in PATH
echo - Node.js 18+ installed and in PATH
echo - Git installed
echo.
pause

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.10+ from https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found! Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo Creating project directories...
if not exist "backend\uploads" mkdir "backend\uploads"
if not exist "backend\backups" mkdir "backend\backups"
if not exist "backend\logs" mkdir "backend\logs"
if not exist "windows\logs" mkdir "windows\logs"

echo Setting up Python backend...
cd backend

echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Installing Python dependencies...
echo This may take several minutes...
venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel

echo Installing Flask and core dependencies...
venv\Scripts\pip.exe install Flask Flask-SQLAlchemy Flask-CORS SQLAlchemy boto3 botocore

echo Installing remaining dependencies...
venv\Scripts\pip.exe install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some dependencies may have failed to install
    echo The platform should still work with basic functionality
)

echo Testing Flask installation...
venv\Scripts\python.exe -c "from flask import Flask; print('Flask OK')"
if errorlevel 1 (
    echo ERROR: Flask installation failed
    pause
    exit /b 1
)

echo Creating .env file...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo .env file created from template
    ) else (
        echo # Flask Configuration > .env
        echo FLASK_APP=app.py >> .env
        echo FLASK_ENV=development >> .env
        echo SECRET_KEY=dev-secret-key-change-in-production >> .env
        echo DATABASE_URL=sqlite:///instance/ai_tools.db >> .env
        echo.
        echo # AWS Configuration for AI Features >> .env
        echo AWS_ACCESS_KEY_ID=your-access-key-here >> .env
        echo AWS_SECRET_ACCESS_KEY=your-secret-key-here >> .env
        echo AWS_REGION=us-west-2 >> .env
        echo .env file created with default values
    )
)

cd ..

echo Setting up React frontend...
cd frontend

echo Installing Node.js dependencies...
npm install
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies
    echo Try running: npm cache clean --force
    pause
    exit /b 1
)

cd ..

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit backend\.env with your AWS credentials (optional for AI features)
echo 2. Run: windows\Start.ps1 or windows\start-windows.bat
echo 3. Open http://localhost:3000 in your browser
echo.
echo Available scripts:
echo   windows\start-windows.bat  - Start the platform
echo   windows\stop-windows.bat   - Stop the platform
echo.
pause