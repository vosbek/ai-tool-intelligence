@echo off
REM AI Tool Intelligence Platform - Quick Launcher
REM This batch file provides easy access to the PowerShell management console

title AI Tool Intelligence Platform

echo.
echo 🤖 AI Tool Intelligence Platform - Quick Launcher
echo ================================================================
echo.

REM Check if PowerShell is available
powershell -Command "exit 0" >nul 2>&1
if errorlevel 1 (
    echo ❌ PowerShell is not available or not in PATH
    echo Please ensure PowerShell 5.1+ is installed
    pause
    exit /b 1
)

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

REM Check if we're in the windows directory
if not exist "%SCRIPT_DIR%Manage.ps1" (
    echo ❌ Management scripts not found
    echo Please run this from the windows directory
    pause
    exit /b 1
)

echo ✅ Starting PowerShell Management Console...
echo.

REM Launch the PowerShell management console
powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%Manage.ps1"

REM Check exit code
if errorlevel 1 (
    echo.
    echo ⚠️  Management console exited with errors
    echo Check the output above for details
    pause
)

echo.
echo Management console closed. Have a great day! 👋
timeout /t 3 /nobreak >nul
