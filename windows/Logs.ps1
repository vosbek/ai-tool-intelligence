#Requires -Version 5.1
<#
.SYNOPSIS
    View and manage logs for the AI Tool Intelligence Platform
.DESCRIPTION
    Displays application logs, filters by date/level, and provides log management
.EXAMPLE
    .\Logs.ps1
    Shows recent logs from all services
.EXAMPLE
    .\Logs.ps1 -Tail
    Continuously monitors logs in real-time
.EXAMPLE
    .\Logs.ps1 -Level ERROR
    Shows only error-level logs
#>

[CmdletBinding()]
param(
    [switch]$Tail,
    [switch]$Clear,
    [string]$Level = "ALL",
    [int]$Lines = 50,
    [string]$Service = "ALL",
    [string]$Date,
    [switch]$Export
)

# Colors for output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }

# Get script directory and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$LogDir = "$ScriptDir\logs"

Write-Host "📋 AI Tool Intelligence Platform Logs" -ForegroundColor White

# Ensure logs directory exists
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    Write-Info "Created logs directory: $LogDir"
}

# Function to format log entry
function Format-LogEntry {
    param($Line, $Source = "System")
    
    if ($Line -match "^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] (.+)$") {
        $Timestamp = $Matches[1]
        $LogLevel = $Matches[2]
        $Message = $Matches[3]
        
        $Color = switch ($LogLevel) {
            "ERROR" { "Red" }
            "WARN" { "Yellow" }
            "INFO" { "Green" }
            "DEBUG" { "Gray" }
            default { "White" }
        }
        
        if ($Level -eq "ALL" -or $LogLevel -eq $Level) {
            Write-Host "[$Timestamp] " -NoNewline -ForegroundColor Gray
            Write-Host "[$LogLevel] " -NoNewline -ForegroundColor $Color
            Write-Host "[$Source] " -NoNewline -ForegroundColor Cyan
            Write-Host $Message -ForegroundColor White
            return $true
        }
    } else {
        # Unformatted log line
        if ($Level -eq "ALL") {
            Write-Host "[$Source] $Line" -ForegroundColor Gray
            return $true
        }
    }
    return $false
}

# Function to get backend logs via API
function Get-BackendLogs {
    try {
        # Check if backend is running
        $Response = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -TimeoutSec 3
        if ($Response.status -eq "healthy") {
            Write-Info "Backend is running - logs available via API"
            # Could extend this to fetch logs from backend if it provides a logs endpoint
        }
    } catch {
        Write-Warning "Backend not accessible - showing file-based logs only"
    }
}

# Clear logs
if ($Clear) {
    $Confirm = Read-Host "Clear all log files? This cannot be undone. (y/n)"
    if ($Confirm -eq 'y' -or $Confirm -eq 'Y') {
        Get-ChildItem $LogDir -Filter "*.log" | Remove-Item -Force
        Write-Success "All log files cleared"
    } else {
        Write-Info "Log clearing cancelled"
    }
    exit 0
}

# Export logs
if ($Export) {
    $ExportPath = "$([Environment]::GetFolderPath('Desktop'))\ai-tool-logs-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"
    Write-Info "Exporting logs to: $ExportPath"
    
    "AI Tool Intelligence Platform Logs" | Out-File $ExportPath
    "Exported: $(Get-Date)" | Out-File $ExportPath -Append
    "=" * 60 | Out-File $ExportPath -Append
    
    Get-ChildItem $LogDir -Filter "*.log" | ForEach-Object {
        "`n--- $($_.Name) ---" | Out-File $ExportPath -Append
        Get-Content $_.FullName | Out-File $ExportPath -Append
    }
    
    Write-Success "Logs exported to: $ExportPath"
    exit 0
}

# Get available log files
$LogFiles = Get-ChildItem $LogDir -Filter "*.log" | Sort-Object LastWriteTime -Descending

if (-not $LogFiles) {
    Write-Warning "No log files found in $LogDir"
    Write-Info "Logs will be created when you start the platform"
    exit 0
}

Write-Host "`n📂 Available Log Files:" -ForegroundColor Blue
Write-Host ("=" * 50) -ForegroundColor Gray

foreach ($LogFile in $LogFiles) {
    $Size = [math]::Round($LogFile.Length / 1KB, 2)
    $LastModified = $LogFile.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
    Write-Host "📄 $($LogFile.Name) - ${Size}KB - $LastModified" -ForegroundColor White
}

# Tail logs in real-time
if ($Tail) {
    Write-Host "`n🔄 Monitoring logs in real-time (Ctrl+C to stop)..." -ForegroundColor Yellow
    Write-Host ("=" * 50) -ForegroundColor Gray
    
    # Get the most recent log file to tail
    $RecentLogFile = $LogFiles[0]
    Write-Info "Tailing: $($RecentLogFile.Name)"
    
    # Track file position
    $LastPosition = $RecentLogFile.Length
    
    try {
        while ($true) {
            Start-Sleep 1
            
            # Check if file has grown
            $CurrentFile = Get-Item $RecentLogFile.FullName -ErrorAction SilentlyContinue
            if ($CurrentFile -and $CurrentFile.Length -gt $LastPosition) {
                # Read new content
                $FileStream = [System.IO.FileStream]::new($CurrentFile.FullName, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
                $FileStream.Seek($LastPosition, [System.IO.SeekOrigin]::Begin) | Out-Null
                
                $Reader = [System.IO.StreamReader]::new($FileStream)
                $NewContent = $Reader.ReadToEnd()
                $Reader.Close()
                $FileStream.Close()
                
                if ($NewContent) {
                    $NewContent -split "`n" | Where-Object { $_.Trim() } | ForEach-Object {
                        Format-LogEntry $_ $RecentLogFile.BaseName
                    }
                }
                
                $LastPosition = $CurrentFile.Length
            }
            
            # Check for newer log files
            $NewestFile = Get-ChildItem $LogDir -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            if ($NewestFile.FullName -ne $RecentLogFile.FullName) {
                Write-Info "`nSwitching to newer log file: $($NewestFile.Name)"
                $RecentLogFile = $NewestFile
                $LastPosition = 0
            }
        }
    } catch {
        Write-Warning "`nLog monitoring stopped: $_"
    }
    exit 0
}

# Display recent logs
Write-Host "`n📋 Recent Logs (Last $Lines lines):" -ForegroundColor Blue
Write-Host ("=" * 50) -ForegroundColor Gray

$DisplayedLines = 0
$TargetDate = if ($Date) { [DateTime]::Parse($Date) } else { $null }

foreach ($LogFile in $LogFiles) {
    if ($Service -ne "ALL" -and $LogFile.BaseName -notlike "*$Service*") {
        continue
    }
    
    Write-Host "`n--- $($LogFile.Name) ---" -ForegroundColor Cyan
    
    try {
        $LogContent = Get-Content $LogFile.FullName -ErrorAction Stop
        $RecentLines = $LogContent | Select-Object -Last $Lines
        
        foreach ($Line in $RecentLines) {
            if ($DisplayedLines -ge $Lines) { break }
            
            # Filter by date if specified
            if ($TargetDate) {
                if ($Line -match "^(\d{4}-\d{2}-\d{2})") {
                    $LineDate = [DateTime]::Parse($Matches[1])
                    if ($LineDate.Date -ne $TargetDate.Date) {
                        continue
                    }
                }
            }
            
            if (Format-LogEntry $Line $LogFile.BaseName) {
                $DisplayedLines++
            }
        }
    } catch {
        Write-Warning "Could not read $($LogFile.Name): $_"
    }
    
    if ($DisplayedLines -ge $Lines) { break }
}

if ($DisplayedLines -eq 0) {
    Write-Warning "No logs match the specified criteria"
    Write-Info "Try: .\Logs.ps1 -Level ALL or .\Logs.ps1 -Service ALL"
}

# Show log statistics
Write-Host "`n📊 Log Statistics:" -ForegroundColor Blue
Write-Host ("=" * 30) -ForegroundColor Gray

$TotalSize = ($LogFiles | Measure-Object Length -Sum).Sum
$TotalSizeKB = [math]::Round($TotalSize / 1KB, 2)

Write-Host "Total log files: $($LogFiles.Count)" -ForegroundColor White
Write-Host "Total size: ${TotalSizeKB}KB" -ForegroundColor White
Write-Host "Oldest log: $($LogFiles[-1].LastWriteTime.ToString('yyyy-MM-dd HH:mm'))" -ForegroundColor White
Write-Host "Newest log: $($LogFiles[0].LastWriteTime.ToString('yyyy-MM-dd HH:mm'))" -ForegroundColor White

# Check for backend logs via API
Get-BackendLogs

Write-Host @"

🔧 Log Management Commands:

View Logs:
  .\Logs.ps1                          # Show recent logs
  .\Logs.ps1 -Lines 100               # Show last 100 lines
  .\Logs.ps1 -Level ERROR             # Show only errors
  .\Logs.ps1 -Service Backend         # Show only backend logs
  .\Logs.ps1 -Date "2024-01-15"       # Show logs from specific date

Real-time Monitoring:
  .\Logs.ps1 -Tail                    # Monitor logs in real-time

Management:
  .\Logs.ps1 -Clear                   # Clear all log files
  .\Logs.ps1 -Export                  # Export logs to desktop

Log Levels: ALL, ERROR, WARN, INFO, DEBUG
Services: ALL, Backend, Frontend, System

"@ -ForegroundColor Gray
