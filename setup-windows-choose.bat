@echo off
cls
echo ========================================
echo AI Tool Intelligence Platform Setup
echo ========================================
echo.
echo Choose your installation type:
echo.
echo 1. MINIMAL (Recommended - includes Strands SDK)
echo    - Core dependencies + Strands AI (~20 packages)
echo    - Web interface, database, and AI research
echo    - Requires AWS credentials for AI features
echo    - Most reliable installation
echo.
echo 2. ENHANCED (All features, more complex)
echo    - All dependencies (~40+ packages)
echo    - Advanced data processing, GitHub API
echo    - May have version conflicts
echo    - Builds on minimal installation
echo.
echo 3. OFFLINE (Pre-bundled dependencies)
echo    - Install from local bundle
echo    - No internet required during install
echo    - Must create bundle first
echo.
echo 4. EXIT
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto minimal
if "%choice%"=="2" goto full
if "%choice%"=="3" goto offline
if "%choice%"=="4" goto exit
goto invalid

:minimal
echo.
echo Starting minimal installation...
call setup-windows-minimal.bat
goto end

:full
echo.
echo Starting enhanced installation...
echo This installs minimal setup first, then adds enhanced features.
echo Warning: Enhanced features may have dependency conflicts.
pause
call setup-windows-minimal.bat
echo.
echo Now installing enhanced features...
cd backend
venv\Scripts\pip.exe install -r ..\requirements-ai.txt
if errorlevel 1 (
    echo WARNING: Some enhanced features failed to install
    echo The minimal platform should still work
)
cd ..
echo Enhanced installation complete!
goto end

:offline
echo.
echo Starting offline installation...
if not exist "dependencies-bundle" (
    echo ERROR: Dependencies bundle not found!
    echo.
    echo To create a bundle:
    echo 1. Run: scripts\bundle-dependencies.bat
    echo 2. Copy the dependencies-bundle folder to this machine
    echo 3. Run this script again
    echo.
    pause
    goto end
)
call dependencies-bundle\install-offline.bat
goto end

:invalid
echo.
echo Invalid choice. Please enter 1, 2, 3, or 4.
echo.
pause
goto start

:exit
echo.
echo Installation cancelled.
goto end

:end
echo.
echo Setup script finished.
pause