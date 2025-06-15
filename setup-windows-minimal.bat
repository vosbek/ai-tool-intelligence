@echo off
echo ========================================
echo AI Tool Intelligence - Minimal Setup
echo ========================================
echo.
echo This installs core dependencies including Strands SDK for AI features.
echo This is the most reliable installation option.
echo.
echo Features that will work:
echo - Tool database management
echo - Web interface
echo - AI-powered tool research (with AWS credentials)
echo - Basic competitive analysis
echo.
echo Features that require enhanced setup later:
echo - Advanced data processing
echo - GitHub API integration
echo - Background monitoring
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
if not exist "backend\instance" mkdir "backend\instance"

echo Setting up Python backend with minimal dependencies...
cd backend

echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Upgrading pip...
venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel

echo Installing core dependencies including Strands SDK...
echo This may take 5-10 minutes depending on your connection...
echo.

echo Step 1: Installing Flask and core web framework...
venv\Scripts\pip.exe install Flask==2.3.3 Flask-SQLAlchemy==3.0.5 Flask-CORS==4.0.0 Werkzeug==2.3.7 Jinja2==3.1.2
if errorlevel 1 (
    echo ERROR: Failed to install Flask framework
    pause
    exit /b 1
)

echo Step 2: Installing database support...
venv\Scripts\pip.exe install SQLAlchemy==2.0.21
if errorlevel 1 (
    echo ERROR: Failed to install database support
    pause
    exit /b 1
)

echo Step 3: Installing AWS SDK (required for Strands)...
venv\Scripts\pip.exe install boto3==1.34.0 botocore==1.34.0
if errorlevel 1 (
    echo ERROR: Failed to install AWS SDK
    echo Strands SDK requires AWS SDK to function
    pause
    exit /b 1
)

echo Step 4: Installing Strands Agents SDK...
echo This is the core AI functionality - may take a few minutes...
venv\Scripts\pip.exe install strands-agents strands-agents-tools
if errorlevel 1 (
    echo WARNING: Failed to install Strands SDK
    echo The platform will work but without AI features
    echo You can install manually later with AWS credentials configured
)

echo Step 5: Installing web utilities...
venv\Scripts\pip.exe install requests==2.31.0 beautifulsoup4==4.12.2 python-dotenv==1.0.0 click==8.1.7
if errorlevel 1 (
    echo ERROR: Failed to install web utilities
    pause
    exit /b 1
)

echo Step 6: Installing production server...
venv\Scripts\pip.exe install gunicorn==21.2.0
if errorlevel 1 (
    echo WARNING: Failed to install gunicorn (production server)
    echo This is OK for development use
)

echo Creating .env file...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo .env file created from template
        echo.
        echo IMPORTANT: Edit backend\.env with your AWS credentials to enable AI features!
        echo Example:
        echo   AWS_ACCESS_KEY_ID=your-access-key-here
        echo   AWS_SECRET_ACCESS_KEY=your-secret-key-here
        echo   AWS_REGION=us-east-1
    ) else (
        echo # Flask Configuration > .env
        echo FLASK_APP=app.py >> .env
        echo FLASK_ENV=development >> .env
        echo SECRET_KEY=dev-secret-key-please-change-in-production >> .env
        echo DATABASE_URL=sqlite:///instance/ai_tools.db >> .env
        echo. >> .env
        echo # AWS Configuration for Strands SDK >> .env
        echo # Add your credentials to enable AI features >> .env
        echo AWS_ACCESS_KEY_ID=your-access-key-here >> .env
        echo AWS_SECRET_ACCESS_KEY=your-secret-key-here >> .env
        echo AWS_REGION=us-east-1 >> .env
        echo. >> .env
        echo # Optional: Skip AWS validation during development >> .env
        echo #SKIP_AWS_VALIDATION=1 >> .env
        echo .env file created with default values
        echo.
        echo IMPORTANT: Edit backend\.env with your AWS credentials to enable AI features!
    )
)

echo Testing Flask installation...
venv\Scripts\python.exe -c "from flask import Flask; app = Flask(__name__); print('✅ Flask working!')"
if errorlevel 1 (
    echo ERROR: Flask test failed
    pause
    exit /b 1
)

echo Testing database...
venv\Scripts\python.exe -c "from flask_sqlalchemy import SQLAlchemy; print('✅ Database support working!')"
if errorlevel 1 (
    echo ERROR: Database test failed
    pause
    exit /b 1
)

echo Testing Strands SDK...
venv\Scripts\python.exe -c "try:
    from strands import Agent
    print('✅ Strands SDK core working!')
    try:
        from strands_tools import calculator
        print('✅ Strands tools working!')
    except ImportError as e:
        print('⚠️  Strands tools partially available:', str(e))
except ImportError as e:
    print('❌ Strands SDK not available:', str(e))
    print('   This usually means AWS credentials are needed')
    print('   The platform will work but without AI features')"
echo Note: Strands may require AWS credentials to fully initialize

cd ..

echo Setting up React frontend...
cd frontend

echo Installing Node.js dependencies...
npm install --production
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies
    echo Trying with cache clean...
    npm cache clean --force
    npm install --production
    if errorlevel 1 (
        echo ERROR: Frontend installation failed
        pause
        exit /b 1
    )
)

cd ..

echo ========================================
echo Minimal Setup Complete!
echo ========================================
echo.
echo ✅ Core functionality with AI is ready:
echo   - Tool database and management
echo   - Web interface
echo   - Strands SDK for AI research (needs AWS credentials)
echo   - Basic competitive analysis
echo.
echo 🚀 To start the platform:
echo   windows\start-windows.bat
echo.
echo 🌐 Then open: http://localhost:3000
echo.
echo 🔑 To enable AI features:
echo   1. Edit backend\.env with your AWS credentials
echo   2. Enable Claude 3.5 Sonnet in AWS Bedrock Console
echo   3. Restart the platform
echo.
echo 🧠 To add enhanced features later:
echo   Run: cd backend ^&^& venv\Scripts\pip install -r ..\requirements-ai.txt
echo   This adds: pandas, GitHub API, advanced monitoring
echo.
echo 📁 Dependencies installed:
echo   - Flask web framework
echo   - SQLite database
echo   - Strands SDK + AWS SDK
echo   - React frontend
echo   - Web scraping tools
echo.
echo Total dependencies: ~20 packages (core + AI ready!)
echo.
pause