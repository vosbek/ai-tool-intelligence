# Start-Validated.ps1 - Start the AI Tool Intelligence Platform with credential validation

Write-Host "🚀 AI Tool Intelligence Platform - Windows Startup Script" -ForegroundColor Green
Write-Host "=" * 60

# Function to check if a process is running on a port
function Test-Port {
    param($Port)
    try {
        $connection = Test-NetConnection -ComputerName "localhost" -Port $Port -InformationLevel "Quiet" -WarningAction SilentlyContinue
        return $connection
    } catch {
        return $false
    }
}

# Function to stop existing processes
function Stop-ExistingProcesses {
    Write-Host "🔍 Checking for existing processes..." -ForegroundColor Yellow
    
    # Stop processes on port 3000 (React)
    $reactProcess = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
    if ($reactProcess) {
        Write-Host "⚠️  Stopping existing React process on port 3000..." -ForegroundColor Yellow
        Stop-Process -Id $reactProcess.OwningProcess -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
    
    # Stop processes on port 5000 (Flask)
    $flaskProcess = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
    if ($flaskProcess) {
        Write-Host "⚠️  Stopping existing Flask process on port 5000..." -ForegroundColor Yellow
        Stop-Process -Id $flaskProcess.OwningProcess -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
}

# Check if we're in the right directory
if (!(Test-Path "backend\app.py") -or !(Test-Path "frontend\package.json")) {
    Write-Host "❌ Error: Please run this script from the ai-tool-intelligence root directory" -ForegroundColor Red
    Write-Host "💡 Current directory: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

# Check Python installation
Write-Host "🐍 Checking Python installation..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.1[0-9]") {
        Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Python version: $pythonVersion" -ForegroundColor Yellow
        Write-Host "💡 Python 3.10+ recommended for Strands SDK compatibility" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Python not found. Please install Python 3.10+ first." -ForegroundColor Red
    exit 1
}

# Check Node.js installation
Write-Host "📦 Checking Node.js installation..." -ForegroundColor Cyan
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 18+ first." -ForegroundColor Red
    exit 1
}

# Check virtual environment
Write-Host "🔧 Checking Python virtual environment..." -ForegroundColor Cyan
if (!(Test-Path "venv\Scripts\activate.bat")) {
    Write-Host "⚠️  Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    if (!(Test-Path "venv\Scripts\activate.bat")) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Cyan
& "venv\Scripts\Activate.ps1"

# Check backend dependencies
Write-Host "📋 Checking backend dependencies..." -ForegroundColor Cyan
if (!(Test-Path "backend\__pycache__") -or !(pip list | Select-String "Flask")) {
    Write-Host "📦 Installing backend dependencies..." -ForegroundColor Yellow
    Set-Location backend
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install backend dependencies" -ForegroundColor Red
        exit 1
    }
    Set-Location ..
}

# Check frontend dependencies
Write-Host "📋 Checking frontend dependencies..." -ForegroundColor Cyan
if (!(Test-Path "frontend\node_modules")) {
    Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install frontend dependencies" -ForegroundColor Red
        exit 1
    }
    Set-Location ..
}

# Check environment configuration
Write-Host "⚙️  Checking environment configuration..." -ForegroundColor Cyan
if (!(Test-Path "backend\.env")) {
    if (Test-Path "backend\.env.example") {
        Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
        Copy-Item "backend\.env.example" "backend\.env"
        Write-Host "⚠️  Please edit backend\.env with your AWS credentials" -ForegroundColor Yellow
        Write-Host "💡 See AWS_SETUP.md for detailed instructions" -ForegroundColor Cyan
    } else {
        Write-Host "⚠️  No .env file found. You may need to configure AWS credentials." -ForegroundColor Yellow
    }
}

# Validate AWS credentials
Write-Host "🔐 Validating AWS credentials..." -ForegroundColor Cyan
Set-Location backend
$awsValidation = python aws_credential_validator.py 2>&1
$awsExitCode = $LASTEXITCODE

if ($awsExitCode -eq 0) {
    Write-Host "✅ AWS credentials validated successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ AWS credential validation failed:" -ForegroundColor Red
    Write-Host $awsValidation -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🛠️  Options to proceed:" -ForegroundColor Cyan
    Write-Host "1. Fix AWS credentials (recommended) - see AWS_SETUP.md" -ForegroundColor White
    Write-Host "2. Skip validation for development: set SKIP_AWS_VALIDATION=1" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Continue anyway? (y/N)"
    if ($choice -ne "y" -and $choice -ne "Y") {
        Write-Host "💡 Run 'python aws_credential_validator.py' for detailed diagnostics" -ForegroundColor Cyan
        Set-Location ..
        exit 1
    } else {
        Write-Host "⚠️  Starting with AWS validation skipped..." -ForegroundColor Yellow
        $env:SKIP_AWS_VALIDATION = "1"
    }
}
Set-Location ..

# Stop any existing processes
Stop-ExistingProcesses

# Start backend
Write-Host "🚀 Starting backend server..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location $args[0]
    & "venv\Scripts\Activate.ps1"
    Set-Location backend
    python app.py
} -ArgumentList (Get-Location)

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Check if backend started successfully
if (Test-Port 5000) {
    Write-Host "✅ Backend started successfully on http://localhost:5000" -ForegroundColor Green
} else {
    Write-Host "❌ Backend failed to start on port 5000" -ForegroundColor Red
    Write-Host "🔍 Backend job output:" -ForegroundColor Yellow
    Receive-Job $backendJob
    Stop-Job $backendJob
    Remove-Job $backendJob
    exit 1
}

# Start frontend
Write-Host "🎨 Starting frontend..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $args[0]
    Set-Location frontend
    npm start
} -ArgumentList (Get-Location)

# Wait for frontend to start
Write-Host "⏳ Waiting for frontend to start..." -ForegroundColor Yellow
$frontendStarted = $false
$attempts = 0
$maxAttempts = 30

while (!$frontendStarted -and $attempts -lt $maxAttempts) {
    Start-Sleep -Seconds 2
    $attempts++
    if (Test-Port 3000) {
        $frontendStarted = $true
    }
    Write-Host "." -NoNewline -ForegroundColor Yellow
}

Write-Host ""

if ($frontendStarted) {
    Write-Host "✅ Frontend started successfully on http://localhost:3000" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend failed to start on port 3000" -ForegroundColor Red
    Write-Host "🔍 Frontend job output:" -ForegroundColor Yellow
    Receive-Job $frontendJob
}

# Display status
Write-Host ""
Write-Host "🎉 AI Tool Intelligence Platform Status:" -ForegroundColor Green
Write-Host "=" * 50
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:5000" -ForegroundColor Cyan
Write-Host "Health:   http://localhost:5000/api/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Logs:" -ForegroundColor Yellow
Write-Host "Backend Job ID: $($backendJob.Id)" -ForegroundColor White
Write-Host "Frontend Job ID: $($frontendJob.Id)" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop: Run .\windows\Stop.ps1" -ForegroundColor Yellow
Write-Host "📊 To check status: Run .\windows\Status.ps1" -ForegroundColor Yellow
Write-Host "🔧 To view logs: Receive-Job <Job-ID>" -ForegroundColor Yellow

# Keep script running
Write-Host ""
Write-Host "Press Ctrl+C to stop all services..." -ForegroundColor Cyan

try {
    while ($true) {
        Start-Sleep -Seconds 5
        
        # Check if jobs are still running
        if ((Get-Job $backendJob.Id).State -eq "Failed") {
            Write-Host "❌ Backend job failed!" -ForegroundColor Red
            Receive-Job $backendJob
            break
        }
        
        if ((Get-Job $frontendJob.Id).State -eq "Failed") {
            Write-Host "❌ Frontend job failed!" -ForegroundColor Red
            Receive-Job $frontendJob
            break
        }
    }
} catch {
    Write-Host "🛑 Stopping services..." -ForegroundColor Yellow
} finally {
    # Cleanup
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Stop-Job $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $frontendJob -ErrorAction SilentlyContinue
    
    Write-Host "✅ Services stopped." -ForegroundColor Green
}