@echo off
echo ========================================
echo AI Tool Intelligence - Dependency Bundler
echo ========================================
echo.
echo This will create an offline installation bundle.
echo.
echo What this does:
echo - Downloads all Python dependencies to a local folder
echo - Bundles Node.js dependencies
echo - Creates an offline installer
echo.
echo Requirements:
echo - Python with pip installed
echo - Node.js with npm installed
echo - Internet connection (for this bundling process only)
echo.
pause

echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found!
    pause
    exit /b 1
)

echo Creating bundle directory...
if not exist "dependencies-bundle" mkdir "dependencies-bundle"
if not exist "dependencies-bundle\minimal" mkdir "dependencies-bundle\minimal"
if not exist "dependencies-bundle\ai" mkdir "dependencies-bundle\ai"

echo.
echo Downloading minimal Python dependencies...
pip download -r requirements-minimal.txt -d dependencies-bundle\minimal
if errorlevel 1 (
    echo ERROR: Failed to download minimal dependencies
    pause
    exit /b 1
)

echo.
echo Downloading AI Python dependencies...
echo Note: Some may fail - this is OK
pip download -r requirements-ai.txt -d dependencies-bundle\ai

echo.
echo Setting up Node.js dependencies...
cd frontend
call npm ci
if errorlevel 1 (
    echo ERROR: Failed to install Node.js dependencies
    cd ..
    pause
    exit /b 1
)

echo Creating Node.js bundle...
tar -czf ..\dependencies-bundle\node_modules.tar.gz node_modules 2>nul
if errorlevel 1 (
    echo Could not create tar.gz, trying alternative...
    powershell -Command "Compress-Archive -Path node_modules -DestinationPath ..\dependencies-bundle\node_modules.zip"
)

cd ..

echo.
echo Creating offline installer...
echo @echo off > dependencies-bundle\install-offline.bat
echo echo ======================================== >> dependencies-bundle\install-offline.bat
echo echo AI Tool Intelligence - Offline Installer >> dependencies-bundle\install-offline.bat
echo echo ======================================== >> dependencies-bundle\install-offline.bat
echo echo. >> dependencies-bundle\install-offline.bat
echo echo Installing from bundled dependencies... >> dependencies-bundle\install-offline.bat
echo echo. >> dependencies-bundle\install-offline.bat
echo. >> dependencies-bundle\install-offline.bat
echo echo Setting up Python backend... >> dependencies-bundle\install-offline.bat
echo cd backend >> dependencies-bundle\install-offline.bat
echo. >> dependencies-bundle\install-offline.bat
echo echo Creating virtual environment... >> dependencies-bundle\install-offline.bat
echo python -m venv venv >> dependencies-bundle\install-offline.bat
echo if errorlevel 1 ^( >> dependencies-bundle\install-offline.bat
echo     echo ERROR: Failed to create virtual environment >> dependencies-bundle\install-offline.bat
echo     pause >> dependencies-bundle\install-offline.bat
echo     exit /b 1 >> dependencies-bundle\install-offline.bat
echo ^) >> dependencies-bundle\install-offline.bat
echo. >> dependencies-bundle\install-offline.bat
echo echo Installing Python dependencies from bundle... >> dependencies-bundle\install-offline.bat
echo venv\Scripts\pip.exe install --no-index --find-links ..\dependencies-bundle\minimal -r ..\requirements-minimal.txt >> dependencies-bundle\install-offline.bat
echo if errorlevel 1 ^( >> dependencies-bundle\install-offline.bat
echo     echo ERROR: Failed to install dependencies >> dependencies-bundle\install-offline.bat
echo     pause >> dependencies-bundle\install-offline.bat
echo     exit /b 1 >> dependencies-bundle\install-offline.bat
echo ^) >> dependencies-bundle\install-offline.bat
echo. >> dependencies-bundle\install-offline.bat
echo echo Creating .env file... >> dependencies-bundle\install-offline.bat
echo if not exist ".env" ^( >> dependencies-bundle\install-offline.bat
echo     copy ".env.example" ".env" >> dependencies-bundle\install-offline.bat
echo     echo .env file created >> dependencies-bundle\install-offline.bat
echo ^) >> dependencies-bundle\install-offline.bat
echo. >> dependencies-bundle\install-offline.bat
echo cd .. >> dependencies-bundle\install-offline.bat
echo. >> dependencies-bundle\install-offline.bat
echo echo Setting up React frontend... >> dependencies-bundle\install-offline.bat
echo cd frontend >> dependencies-bundle\install-offline.bat
echo. >> dependencies-bundle\install-offline.bat
echo echo Extracting Node.js dependencies... >> dependencies-bundle\install-offline.bat
echo if exist "..\dependencies-bundle\node_modules.tar.gz" ^( >> dependencies-bundle\install-offline.bat
echo     tar -xzf "..\dependencies-bundle\node_modules.tar.gz" >> dependencies-bundle\install-offline.bat
echo ^) else if exist "..\dependencies-bundle\node_modules.zip" ^( >> dependencies-bundle\install-offline.bat
echo     powershell -Command "Expand-Archive -Path '..\dependencies-bundle\node_modules.zip' -DestinationPath '.'" >> dependencies-bundle\install-offline.bat
echo ^) else ^( >> dependencies-bundle\install-offline.bat
echo     echo No Node.js bundle found, installing online... >> dependencies-bundle\install-offline.bat
echo     npm install >> dependencies-bundle\install-offline.bat
echo ^) >> dependencies-bundle\install-offline.bat
echo. >> dependencies-bundle\install-offline.bat
echo cd .. >> dependencies-bundle\install-offline.bat
echo. >> dependencies-bundle\install-offline.bat
echo echo ======================================== >> dependencies-bundle\install-offline.bat
echo echo Offline Installation Complete! >> dependencies-bundle\install-offline.bat
echo echo ======================================== >> dependencies-bundle\install-offline.bat
echo echo. >> dependencies-bundle\install-offline.bat
echo echo To start the platform: >> dependencies-bundle\install-offline.bat
echo echo   windows\start-windows.bat >> dependencies-bundle\install-offline.bat
echo echo. >> dependencies-bundle\install-offline.bat
echo echo To install AI features later: >> dependencies-bundle\install-offline.bat
echo echo   cd backend >> dependencies-bundle\install-offline.bat
echo echo   venv\Scripts\pip.exe install --no-index --find-links ..\dependencies-bundle\ai -r ..\requirements-ai.txt >> dependencies-bundle\install-offline.bat
echo echo. >> dependencies-bundle\install-offline.bat
echo pause >> dependencies-bundle\install-offline.bat

echo.
echo Creating bundle README...
echo # Offline Installation Bundle > dependencies-bundle\README.md
echo. >> dependencies-bundle\README.md
echo This bundle contains all dependencies for offline installation. >> dependencies-bundle\README.md
echo. >> dependencies-bundle\README.md
echo ## Usage: >> dependencies-bundle\README.md
echo 1. Copy this dependencies-bundle folder to the target machine >> dependencies-bundle\README.md
echo 2. Run install-offline.bat >> dependencies-bundle\README.md
echo 3. Start with windows\start-windows.bat >> dependencies-bundle\README.md
echo. >> dependencies-bundle\README.md
echo ## Contents: >> dependencies-bundle\README.md
echo - minimal/ - Core Python dependencies >> dependencies-bundle\README.md
echo - ai/ - Optional AI dependencies >> dependencies-bundle\README.md
echo - node_modules bundle - Frontend dependencies >> dependencies-bundle\README.md

echo.
echo ========================================
echo Bundle Creation Complete!
echo ========================================
echo.
echo Bundle location: dependencies-bundle\
echo.
echo To use on target machines:
echo 1. Copy the entire 'dependencies-bundle' folder
echo 2. Run 'dependencies-bundle\install-offline.bat'
echo 3. Start with 'windows\start-windows.bat'
echo.
echo The bundle works without internet connection!
echo.
pause