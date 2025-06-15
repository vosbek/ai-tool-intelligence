@echo off
REM Stop script for AI Tool Intelligence Platform on Windows

echo 🛑 Stopping AI Tool Intelligence Platform...
echo.

REM Kill Flask processes (Python running on port 5000)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000"') do (
    echo Stopping backend process %%a
    taskkill /f /pid %%a >nul 2>&1
)

REM Kill Node.js processes (React dev server on port 3000)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000"') do (
    echo Stopping frontend process %%a
    taskkill /f /pid %%a >nul 2>&1
)

REM Also kill by process name as backup
taskkill /f /im "python.exe" /fi "WINDOWTITLE eq AI Tool Intelligence - Backend*" >nul 2>&1
taskkill /f /im "node.exe" /fi "WINDOWTITLE eq AI Tool Intelligence - Frontend*" >nul 2>&1

echo ✅ All services stopped
echo.
pause