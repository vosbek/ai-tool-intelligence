#Requires -Version 5.1
<#
.SYNOPSIS
    Stop all AI Tool Intelligence Platform services
.DESCRIPTION
    Gracefully stops all running backend and frontend processes
.EXAMPLE
    .\Stop.ps1
    Stops all platform services
#>

[CmdletBinding()]
param(
    [switch]$Force
)

# Colors for output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }

Write-Host "🛑 Stopping AI Tool Intelligence Platform" -ForegroundColor White

$Stopped = $false

# Function to stop processes on specific ports
function Stop-ProcessOnPort {
    param([int]$Port, [string]$ServiceName)
    
    try {
        $Connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($Connections) {
            foreach ($Connection in $Connections) {
                $Process = Get-Process -Id $Connection.OwningProcess -ErrorAction SilentlyContinue
                if ($Process) {
                    Write-Info "Stopping $ServiceName process: $($Process.ProcessName) (PID: $($Process.Id))"
                    if ($Force) {
                        $Process | Stop-Process -Force
                    } else {
                        $Process | Stop-Process
                    }
                    Write-Success "$ServiceName stopped"
                    $script:Stopped = $true
                }
            }
        }
    } catch {
        Write-Warning "Could not stop process on port $Port`: $_"
    }
}

# Stop backend (port 5000)
Write-Info "Checking for backend services on port 5000..."
Stop-ProcessOnPort -Port 5000 -ServiceName "Backend"

# Stop frontend (port 3000)  
Write-Info "Checking for frontend services on port 3000..."
Stop-ProcessOnPort -Port 3000 -ServiceName "Frontend"

# Stop any Python processes running app.py
try {
    $PythonProcesses = Get-Process python -ErrorAction SilentlyContinue | 
        Where-Object { $_.CommandLine -like "*app.py*" }
    
    foreach ($Process in $PythonProcesses) {
        Write-Info "Stopping Python backend process (PID: $($Process.Id))"
        if ($Force) {
            $Process | Stop-Process -Force
        } else {
            $Process | Stop-Process
        }
        Write-Success "Python backend stopped"
        $Stopped = $true
    }
} catch {
    # Process cmdline access may be restricted on some systems
}

# Stop any Node.js processes running React
try {
    $NodeProcesses = Get-Process node -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like "*react-scripts*" }
        
    foreach ($Process in $NodeProcesses) {
        Write-Info "Stopping Node.js frontend process (PID: $($Process.Id))"
        if ($Force) {
            $Process | Stop-Process -Force  
        } else {
            $Process | Stop-Process
        }
        Write-Success "Node.js frontend stopped"
        $Stopped = $true
    }
} catch {
    # Process cmdline access may be restricted on some systems
}

# Alternative approach - stop by process name if nothing found
if (-not $Stopped) {
    Write-Info "No platform processes detected on standard ports."
    Write-Info "Checking for Python and Node.js processes that might be running the platform..."
    
    # List running Python processes
    $PythonProcesses = Get-Process python -ErrorAction SilentlyContinue
    if ($PythonProcesses) {
        Write-Info "Found $($PythonProcesses.Count) Python process(es)"
        if ($Force) {
            $PythonProcesses | Stop-Process -Force
            Write-Success "All Python processes stopped"
            $Stopped = $true
        }
    }
    
    # List running Node.js processes
    $NodeProcesses = Get-Process node -ErrorAction SilentlyContinue
    if ($NodeProcesses) {
        Write-Info "Found $($NodeProcesses.Count) Node.js process(es)"
        if ($Force) {
            $NodeProcesses | Stop-Process -Force
            Write-Success "All Node.js processes stopped"
            $Stopped = $true
        }
    }
    
    if ($PythonProcesses -or $NodeProcesses) {
        if (-not $Force) {
            Write-Warning "Use -Force parameter to stop all Python/Node.js processes"
        }
    }
}

if ($Stopped) {
    Write-Success "Platform services stopped successfully"
} else {
    Write-Info "No platform services were found running"
}

# Clean up any remaining connections on our ports
Write-Info "Cleaning up network connections..."
$PortsToCheck = @(3000, 5000)

foreach ($Port in $PortsToCheck) {
    try {
        $Connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($Connections) {
            Write-Warning "Port $Port still has active connections"
        } else {
            Write-Success "Port $Port is now available"
        }
    } catch {
        # Ignore errors in connection checking
    }
}

Write-Host ""
Write-Success "Stop operation completed"
Write-Info "To restart the platform, run: .\Start.ps1"
