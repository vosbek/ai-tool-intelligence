#Requires -Version 5.1
<#
.SYNOPSIS
    Start the AI Tool Intelligence Platform on Windows
.DESCRIPTION
    Starts both the Flask backend and React frontend services with proper error handling
.EXAMPLE
    .\Start.ps1
    Starts the platform with default settings
.EXAMPLE
    .\Start.ps1 -BackendOnly
    Starts only the backend service
.EXAMPLE
    .\Start.ps1 -FrontendOnly  
    Starts only the frontend service
#>

[CmdletBinding()]
param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoBrowser,
    [int]$BackendPort = 5000,
    [int]$FrontendPort = 3000
)

# Colors for output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Step { param($Message) Write-Host "🔄 $Message" -ForegroundColor Blue }

# Get script directory and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Load configuration if available
$ConfigPath = "$ScriptDir\config.json"
if (Test-Path $ConfigPath) {
    $Config = Get-Content $ConfigPath | ConvertFrom-Json
    Write-Info "Loaded Windows configuration"
} else {
    Write-Warning "Configuration not found. Run Setup.ps1 first."
}

Write-Host @"
🚀 Starting AI Tool Intelligence Platform
================================================================
"@ -ForegroundColor White

# Global variables for process tracking
$BackendProcess = $null
$FrontendProcess = $null
$LogFile = "$ScriptDir\logs\platform-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

# Ensure logs directory exists
$LogDir = "$ScriptDir\logs"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Function to log messages
function Write-Log {
    param($Message, $Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Timestamp [$Level] $Message" | Add-Content $LogFile
}

# Function to check if port is available
function Test-Port {
    param([int]$Port)
    try {
        $TcpClient = New-Object System.Net.Sockets.TcpClient
        $TcpClient.Connect("localhost", $Port)
        $TcpClient.Close()
        return $false  # Port is in use
    } catch {
        return $true   # Port is available
    }
}

# Function to cleanup processes on exit
function Stop-Services {
    Write-Step "Stopping services..."
    
    if ($BackendProcess -and -not $BackendProcess.HasExited) {
        Write-Info "Stopping backend service..."
        try {
            $BackendProcess | Stop-Process -Force
            Write-Success "Backend stopped"
        } catch {
            Write-Warning "Could not stop backend process: $_"
        }
    }
    
    if ($FrontendProcess -and -not $FrontendProcess.HasExited) {
        Write-Info "Stopping frontend service..."
        try {
            $FrontendProcess | Stop-Process -Force
            Write-Success "Frontend stopped"
        } catch {
            Write-Warning "Could not stop frontend process: $_"
        }
    }
    
    # Kill any remaining processes on our ports
    try {
        Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue | 
            ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
        Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue | 
            ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    } catch {
        # Ignore errors
    }
    
    Write-Log "Services stopped" "INFO"
    Write-Success "All services stopped"
}

# Register cleanup on Ctrl+C
Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action { Stop-Services }

# Trap Ctrl+C
[Console]::TreatControlCAsInput = $false
$Host.UI.RawUI.KeyAvailable | Out-Null

# Check prerequisites
Write-Step "Checking prerequisites..."

if (-not (Test-Path "$ProjectRoot\backend\venv")) {
    Write-Error "Backend not set up. Run Setup.ps1 first"
    exit 1
}

if (-not $BackendOnly -and -not (Test-Path "$ProjectRoot\frontend\node_modules")) {
    Write-Error "Frontend not set up. Run Setup.ps1 first"  
    exit 1
}

# Check ports
if (-not $FrontendOnly) {
    if (-not (Test-Port $BackendPort)) {
        Write-Error "Port $BackendPort is already in use. Stop other services or use -BackendPort parameter"
        exit 1
    }
}

if (-not $BackendOnly) {
    if (-not (Test-Port $FrontendPort)) {
        Write-Error "Port $FrontendPort is already in use. Stop other services or use -FrontendPort parameter"
        exit 1
    }
}

Write-Success "Prerequisites check passed"

# Start backend
if (-not $FrontendOnly) {
    Write-Step "Starting Flask backend..."
    Set-Location "$ProjectRoot\backend"
    
    # Check .env file
    if (-not (Test-Path ".env")) {
        Write-Warning "Creating .env from template - PLEASE CONFIGURE YOUR AWS CREDENTIALS!"
        Copy-Item ".env.example" ".env"
        Write-Info "Edit backend\.env with your AWS credentials before using research features"
    }
    
    # Activate virtual environment and start backend
    try {
        $BackendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList @(
            "/c", 
            "call venv\Scripts\activate.bat && python app.py"
        ) -PassThru -WindowStyle Hidden
        
        Write-Info "Backend process started with PID: $($BackendProcess.Id)"
        Write-Log "Backend started on port $BackendPort" "INFO"
        
        # Wait for backend to start
        Write-Info "Waiting for backend to initialize..."
        $Timeout = 30
        $Timer = 0
        
        do {
            Start-Sleep 1
            $Timer++
            try {
                $Response = Invoke-RestMethod -Uri "http://localhost:$BackendPort/api/health" -TimeoutSec 2
                if ($Response.status -eq "healthy") {
                    Write-Success "Backend started successfully"
                    break
                }
            } catch {
                if ($Timer -gt $Timeout) {
                    Write-Error "Backend failed to start within $Timeout seconds"
                    Write-Info "Check logs: $LogFile"
                    exit 1
                }
            }
        } while ($Timer -lt $Timeout)
        
    } catch {
        Write-Error "Failed to start backend: $_"
        Write-Log "Backend startup failed: $_" "ERROR"
        exit 1
    }
}

# Start frontend
if (-not $BackendOnly) {
    Write-Step "Starting React frontend..."
    Set-Location "$ProjectRoot\frontend"
    
    # Set environment variables for the frontend process
    $env:BROWSER = if ($NoBrowser) { "none" } else { "default" }
    $env:PORT = $FrontendPort
    
    try {
        $FrontendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList @(
            "/c",
            "npm start"
        ) -PassThru -WindowStyle Hidden
        
        Write-Info "Frontend process started with PID: $($FrontendProcess.Id)"
        Write-Log "Frontend started on port $FrontendPort" "INFO"
        
        # Wait for frontend to start
        Write-Info "Waiting for frontend to initialize..."
        $Timeout = 60
        $Timer = 0
        
        do {
            Start-Sleep 2
            $Timer += 2
            try {
                $Response = Invoke-WebRequest -Uri "http://localhost:$FrontendPort" -TimeoutSec 2 -UseBasicParsing
                if ($Response.StatusCode -eq 200) {
                    Write-Success "Frontend started successfully"
                    break
                }
            } catch {
                if ($Timer -gt $Timeout) {
                    Write-Error "Frontend failed to start within $Timeout seconds"
                    Write-Info "Check logs: $LogFile"
                    exit 1
                }
            }
        } while ($Timer -lt $Timeout)
        
    } catch {
        Write-Error "Failed to start frontend: $_"
        Write-Log "Frontend startup failed: $_" "ERROR"
        exit 1
    }
}

# Display success information
Write-Host ""
Write-Success "✅ Platform started successfully!"
Write-Host ""

if (-not $FrontendOnly) {
    Write-Host "🔌 Backend API: http://localhost:$BackendPort" -ForegroundColor Green
    Write-Host "   Health Check: http://localhost:$BackendPort/api/health" -ForegroundColor Gray
}

if (-not $BackendOnly) {
    Write-Host "🌐 Frontend: http://localhost:$FrontendPort" -ForegroundColor Green
}

Write-Host ""
Write-Host "📖 Next steps:" -ForegroundColor Cyan
if (-not $FrontendOnly) {
    Write-Host "1. Configure AWS credentials in backend\.env" -ForegroundColor White
    Write-Host "2. Enable Claude 3.5 Sonnet access in AWS Bedrock console" -ForegroundColor White
}
if (-not $BackendOnly) {
    Write-Host "3. Open http://localhost:$FrontendPort to start adding tools" -ForegroundColor White
}
Write-Host ""
Write-Host "🔧 Management commands:" -ForegroundColor Cyan
Write-Host "   .\windows\Status.ps1    # Check system status" -ForegroundColor Gray
Write-Host "   .\windows\Logs.ps1      # View logs" -ForegroundColor Gray  
Write-Host "   .\windows\Research.ps1  # Manage research" -ForegroundColor Gray
Write-Host "   .\windows\Stop.ps1      # Stop services" -ForegroundColor Gray
Write-Host ""

# Open browser if requested
if (-not $BackendOnly -and -not $NoBrowser) {
    try {
        Start-Sleep 2
        Start-Process "http://localhost:$FrontendPort"
        Write-Info "Browser opened automatically"
    } catch {
        Write-Warning "Could not open browser automatically"
    }
}

Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Log "Platform startup completed successfully" "INFO"

# Wait for user to stop services
try {
    if ($BackendProcess -or $FrontendProcess) {
        while ($true) {
            Start-Sleep 1
            
            # Check if processes are still running
            if ($BackendProcess -and $BackendProcess.HasExited) {
                Write-Error "Backend process has exited unexpectedly"
                break
            }
            if ($FrontendProcess -and $FrontendProcess.HasExited) {
                Write-Error "Frontend process has exited unexpectedly"  
                break
            }
        }
    }
} finally {
    Stop-Services
}
