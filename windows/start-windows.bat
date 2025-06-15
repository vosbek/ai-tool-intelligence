@echo off
REM Start script for AI Tool Intelligence Platform on Windows

echo 🚀 Starting AI Tool Intelligence Platform...
echo.

REM Navigate to project root
cd /d "%~dp0.."

REM Check if setup was completed
if not exist "backend\venv" (
    echo ❌ Backend not set up. Please run windows\setup-windows.bat first
    pause
    exit /b 1
)

if not exist "frontend\node_modules" (
    echo ❌ Frontend not set up. Please run windows\setup-windows.bat first
    pause
    exit /b 1
)

REM Check if .env exists
if not exist "backend\.env" (
    echo ⚠️  Creating .env from template...
    copy backend\.env.example backend\.env
    echo 💡 IMPORTANT: Configure AWS credentials in backend\.env for research features
    echo.
)

REM Start backend in a new window
echo 🔄 Starting Flask backend...
start "AI Tool Intelligence - Backend" cmd /k "cd /d backend && venv\Scripts\activate.bat && python app.py"

REM Wait a moment for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend in a new window
echo 🔄 Starting React frontend...
start "AI Tool Intelligence - Frontend" cmd /k "cd /d frontend && npm start"

echo.
echo ✅ Platform started successfully!
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔌 Backend API: http://localhost:5000
echo 🏥 Health Check: http://localhost:5000/api/health
echo.
echo 📋 Both backend and frontend are running in separate windows
echo 💡 Close those windows or press Ctrl+C in them to stop the services
echo.
pause