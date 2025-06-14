#Requires -Version 5.1
<#
.SYNOPSIS
    Check the status of AI Tool Intelligence Platform
.DESCRIPTION
    Displays comprehensive status information about the platform services and configuration
.EXAMPLE
    .\Status.ps1
    Shows full system status
.EXAMPLE
    .\Status.ps1 -Quick
    Shows only basic service status
#>

[CmdletBinding()]
param(
    [switch]$Quick,
    [switch]$Json
)

# Colors for output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Section { param($Title) Write-Host "`n📊 $Title" -ForegroundColor Blue; Write-Host ("=" * 50) -ForegroundColor Gray }

# Get script directory and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

$Status = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    platform_status = "unknown"
    services = @{}
    configuration = @{}
    health = @{}
    errors = @()
}

if (-not $Json) {
    Write-Host @"
📊 AI Tool Intelligence Platform Status
================================================================
Timestamp: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@ -ForegroundColor White
}

# Check service status
function Test-ServiceStatus {
    param($ServiceName, $Port, $Endpoint = "/")
    
    $ServiceStatus = @{
        name = $ServiceName
        port = $Port
        running = $false
        responding = $false
        process_id = $null
        url = "http://localhost:$Port$Endpoint"
        response_time = $null
    }
    
    try {
        # Check if port is in use
        $Connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($Connection) {
            $ServiceStatus.running = $true
            $ServiceStatus.process_id = $Connection[0].OwningProcess
            
            # Test HTTP response
            $StartTime = Get-Date
            try {
                if ($ServiceName -eq "Backend") {
                    $Response = Invoke-RestMethod -Uri "http://localhost:$Port/api/health" -TimeoutSec 5
                    $ServiceStatus.responding = ($Response.status -eq "healthy")
                } else {
                    $Response = Invoke-WebRequest -Uri "http://localhost:$Port" -TimeoutSec 5 -UseBasicParsing
                    $ServiceStatus.responding = ($Response.StatusCode -eq 200)
                }
                $ServiceStatus.response_time = (Get-Date) - $StartTime
            } catch {
                $ServiceStatus.responding = $false
                $Status.errors += "Service $ServiceName not responding: $_"
            }
        }
    } catch {
        $Status.errors += "Error checking $ServiceName`: $_"
    }
    
    return $ServiceStatus
}

# Check services
Write-Section "Service Status"

$BackendStatus = Test-ServiceStatus -ServiceName "Backend" -Port 5000 -Endpoint "/api/health"
$FrontendStatus = Test-ServiceStatus -ServiceName "Frontend" -Port 3000

$Status.services.backend = $BackendStatus
$Status.services.frontend = $FrontendStatus

if (-not $Json) {
    # Backend status
    $BackendIcon = if ($BackendStatus.running -and $BackendStatus.responding) { "✅" } 
                   elseif ($BackendStatus.running) { "⚠️" } 
                   else { "❌" }
    
    Write-Host "$BackendIcon Backend Service (Port 5000)" -ForegroundColor $(
        if ($BackendStatus.running -and $BackendStatus.responding) { "Green" }
        elseif ($BackendStatus.running) { "Yellow" }
        else { "Red" }
    )
    
    if ($BackendStatus.running) {
        Write-Host "   Process ID: $($BackendStatus.process_id)" -ForegroundColor Gray
        Write-Host "   Responding: $($BackendStatus.responding)" -ForegroundColor Gray
        if ($BackendStatus.response_time) {
            Write-Host "   Response Time: $([math]::Round($BackendStatus.response_time.TotalMilliseconds, 2))ms" -ForegroundColor Gray
        }
        Write-Host "   Health URL: http://localhost:5000/api/health" -ForegroundColor Gray
    } else {
        Write-Host "   Status: Not running" -ForegroundColor Red
    }
    
    # Frontend status
    $FrontendIcon = if ($FrontendStatus.running -and $FrontendStatus.responding) { "✅" } 
                    elseif ($FrontendStatus.running) { "⚠️" } 
                    else { "❌" }
    
    Write-Host "$FrontendIcon Frontend Service (Port 3000)" -ForegroundColor $(
        if ($FrontendStatus.running -and $FrontendStatus.responding) { "Green" }
        elseif ($FrontendStatus.running) { "Yellow" }
        else { "Red" }
    )
    
    if ($FrontendStatus.running) {
        Write-Host "   Process ID: $($FrontendStatus.process_id)" -ForegroundColor Gray
        Write-Host "   Responding: $($FrontendStatus.responding)" -ForegroundColor Gray
        if ($FrontendStatus.response_time) {
            Write-Host "   Response Time: $([math]::Round($FrontendStatus.response_time.TotalMilliseconds, 2))ms" -ForegroundColor Gray
        }
        Write-Host "   App URL: http://localhost:3000" -ForegroundColor Gray
    } else {
        Write-Host "   Status: Not running" -ForegroundColor Red
    }
}

# Overall platform status
if ($BackendStatus.running -and $BackendStatus.responding -and $FrontendStatus.running -and $FrontendStatus.responding) {
    $Status.platform_status = "fully_operational"
} elseif ($BackendStatus.running -and $BackendStatus.responding) {
    $Status.platform_status = "backend_only"
} elseif ($FrontendStatus.running -and $FrontendStatus.responding) {
    $Status.platform_status = "frontend_only"
} elseif ($BackendStatus.running -or $FrontendStatus.running) {
    $Status.platform_status = "partially_running"
} else {
    $Status.platform_status = "stopped"
}

if (-not $Quick -and -not $Json) {
    # Configuration check
    Write-Section "Configuration Status"
    
    # Check backend configuration
    $BackendEnvPath = "$ProjectRoot\backend\.env"
    if (Test-Path $BackendEnvPath) {
        $EnvContent = Get-Content $BackendEnvPath
        $HasAwsKey = $EnvContent | Where-Object { $_ -match "AWS_ACCESS_KEY_ID=.+" -and $_ -notmatch "your-access-key-here" }
        $HasAwsSecret = $EnvContent | Where-Object { $_ -match "AWS_SECRET_ACCESS_KEY=.+" -and $_ -notmatch "your-secret-key-here" }
        
        if ($HasAwsKey -and $HasAwsSecret) {
            Write-Success "AWS credentials configured"
            $Status.configuration.aws_configured = $true
        } else {
            Write-Warning "AWS credentials not configured in backend\.env"
            $Status.configuration.aws_configured = $false
        }
    } else {
        Write-Error "Backend .env file not found"
        $Status.configuration.aws_configured = $false
    }
    
    # Check virtual environment
    if (Test-Path "$ProjectRoot\backend\venv") {
        Write-Success "Python virtual environment found"
        $Status.configuration.venv_exists = $true
    } else {
        Write-Error "Python virtual environment not found"
        $Status.configuration.venv_exists = $false
    }
    
    # Check frontend node_modules
    if (Test-Path "$ProjectRoot\frontend\node_modules") {
        Write-Success "Frontend dependencies installed"
        $Status.configuration.frontend_deps = $true
    } else {
        Write-Error "Frontend dependencies not installed"
        $Status.configuration.frontend_deps = $false
    }
    
    # Database check
    $DbPath = "$ProjectRoot\backend\ai_tools.db"
    if (Test-Path $DbPath) {
        $DbSize = (Get-Item $DbPath).Length
        Write-Success "Database file found ($([math]::Round($DbSize/1KB, 2)) KB)"
        $Status.configuration.database_exists = $true
        $Status.configuration.database_size = $DbSize
    } else {
        Write-Warning "Database file not found (will be created on first run)"
        $Status.configuration.database_exists = $false
    }
    
    # System resources
    Write-Section "System Resources"
    
    $MemoryUsage = Get-Counter "\Memory\Available MBytes" -ErrorAction SilentlyContinue
    if ($MemoryUsage) {
        $AvailableMemoryMB = $MemoryUsage.CounterSamples[0].CookedValue
        Write-Info "Available Memory: $([math]::Round($AvailableMemoryMB, 0)) MB"
        $Status.health.available_memory_mb = $AvailableMemoryMB
    }
    
    $CpuUsage = Get-Counter "\Processor(_Total)\% Processor Time" -ErrorAction SilentlyContinue
    if ($CpuUsage) {
        $CpuPercent = $CpuUsage.CounterSamples[0].CookedValue
        Write-Info "CPU Usage: $([math]::Round($CpuPercent, 1))%"
        $Status.health.cpu_usage_percent = $CpuPercent
    }
    
    # Disk space check
    $Drive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DeviceID -eq (Get-Location).Drive.Name }
    if ($Drive) {
        $FreeSpaceGB = [math]::Round($Drive.FreeSpace / 1GB, 2)
        Write-Info "Free Disk Space: $FreeSpaceGB GB"
        $Status.health.free_disk_space_gb = $FreeSpaceGB
    }
    
    # Log files
    Write-Section "Recent Activity"
    
    $LogDir = "$ScriptDir\logs"
    if (Test-Path $LogDir) {
        $RecentLogs = Get-ChildItem $LogDir -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 3
        if ($RecentLogs) {
            Write-Info "Recent log files:"
            foreach ($Log in $RecentLogs) {
                Write-Host "   $($Log.Name) - $($Log.LastWriteTime)" -ForegroundColor Gray
            }
        } else {
            Write-Info "No log files found"
        }
    }
    
    # Backend health details
    if ($BackendStatus.running -and $BackendStatus.responding) {
        Write-Section "Backend Health Details"
        try {
            $HealthResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -TimeoutSec 5
            Write-Success "Backend Version: $($HealthResponse.version)"
            Write-Info "Backend Timestamp: $($HealthResponse.timestamp)"
            $Status.health.backend_version = $HealthResponse.version
            $Status.health.backend_timestamp = $HealthResponse.timestamp
        } catch {
            Write-Warning "Could not retrieve backend health details"
        }
    }
}

# Display errors if any
if ($Status.errors.Count -gt 0 -and -not $Json) {
    Write-Section "Errors & Warnings"
    foreach ($Error in $Status.errors) {
        Write-Warning $Error
    }
}

# Final status summary
if (-not $Json) {
    Write-Section "Overall Status"
    
    switch ($Status.platform_status) {
        "fully_operational" { 
            Write-Success "Platform is fully operational" 
            Write-Info "Frontend: http://localhost:3000"
            Write-Info "Backend: http://localhost:5000"
        }
        "backend_only" { 
            Write-Warning "Only backend service is running"
            Write-Info "Backend: http://localhost:5000"
            Write-Info "Start frontend with: .\Start.ps1 -FrontendOnly"
        }
        "frontend_only" { 
            Write-Warning "Only frontend service is running"
            Write-Info "Frontend: http://localhost:3000"
            Write-Info "Start backend with: .\Start.ps1 -BackendOnly"
        }
        "partially_running" { 
            Write-Warning "Platform services are partially running but not responding properly"
            Write-Info "Try restarting with: .\Stop.ps1; .\Start.ps1"
        }
        "stopped" { 
            Write-Error "Platform is not running"
            Write-Info "Start with: .\Start.ps1"
        }
    }
    
    Write-Host ""
    Write-Info "For detailed management: .\Research.ps1, .\Logs.ps1, .\Backup.ps1"
} else {
    # Output JSON for programmatic use
    $Status | ConvertTo-Json -Depth 5
}
