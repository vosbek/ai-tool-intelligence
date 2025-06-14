#Requires -Version 5.1
<#
.SYNOPSIS
    Main management interface for AI Tool Intelligence Platform on Windows
.DESCRIPTION
    Provides a menu-driven interface for all platform management operations
.EXAMPLE
    .\Manage.ps1
    Shows the main management menu
#>

[CmdletBinding()]
param(
    [string]$Command
)

# Colors for output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Menu { param($Message) Write-Host $Message -ForegroundColor White }

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Clear-Host

Write-Host @"
🤖 AI Tool Intelligence Platform - Windows Management Console
================================================================
Welcome to your AI development tool research platform!

This platform automatically researches AI developer tools using AWS Strands 
Agents and provides comprehensive business intelligence and competitive analysis.

"@ -ForegroundColor Cyan

# Check if setup is completed
function Test-SetupComplete {
    $VenvExists = Test-Path "$ProjectRoot\backend\venv"
    $FrontendDeps = Test-Path "$ProjectRoot\frontend\node_modules"
    $EnvExists = Test-Path "$ProjectRoot\backend\.env"
    
    return $VenvExists -and $FrontendDeps -and $EnvExists
}

# Show current status
function Show-PlatformStatus {
    try {
        $BackendStatus = $null
        $FrontendStatus = $null
        
        # Check backend
        try {
            $Response = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -TimeoutSec 3
            $BackendStatus = if ($Response.status -eq "healthy") { "✅ Running" } else { "⚠️ Issues" }
        } catch {
            $BackendStatus = "❌ Stopped"
        }
        
        # Check frontend
        try {
            $Response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 3 -UseBasicParsing
            $FrontendStatus = if ($Response.StatusCode -eq 200) { "✅ Running" } else { "⚠️ Issues" }
        } catch {
            $FrontendStatus = "❌ Stopped"
        }
        
        Write-Host "📊 Current Status:" -ForegroundColor Blue
        Write-Host "   Backend (Port 5000):  $BackendStatus" -ForegroundColor White
        Write-Host "   Frontend (Port 3000): $FrontendStatus" -ForegroundColor White
        
        if ($BackendStatus -eq "✅ Running" -and $FrontendStatus -eq "✅ Running") {
            Write-Host "   🌐 Platform URL: http://localhost:3000" -ForegroundColor Green
        }
        
    } catch {
        Write-Host "📊 Platform Status: Unable to determine" -ForegroundColor Yellow
    }
}

# Show main menu
function Show-MainMenu {
    Write-Host "`n🎛️ Management Options:" -ForegroundColor Blue
    Write-Host ("=" * 50) -ForegroundColor Gray
    
    Write-Menu "  1️⃣  Start Platform           - Launch backend and frontend"
    Write-Menu "  2️⃣  Stop Platform            - Stop all services"
    Write-Menu "  3️⃣  Check Status             - View detailed system status"
    Write-Menu "  4️⃣  View Logs                - Monitor application logs"
    Write-Menu "  5️⃣  Manage Research          - Research queue and operations"
    Write-Menu "  6️⃣  Create Backup            - Backup data and configuration"
    Write-Menu "  7️⃣  Setup/Reinstall          - Run initial setup"
    Write-Menu "  8️⃣  Reset Platform           - Reset to clean state"
    Write-Menu "  9️⃣  Open Browser             - Open platform in browser"
    Write-Menu "  🔧 Advanced Options          - Additional management tools"
    Write-Menu "  ❌ Exit                      - Close management console"
    
    Write-Host ""
}

# Show advanced menu
function Show-AdvancedMenu {
    Write-Host "`n🔧 Advanced Management Options:" -ForegroundColor Blue
    Write-Host ("=" * 50) -ForegroundColor Gray
    
    Write-Menu "  A1. Backend Only              - Start only backend service"
    Write-Menu "  A2. Frontend Only             - Start only frontend service"
    Write-Menu "  A3. Monitor Logs Real-time    - Tail logs continuously"
    Write-Menu "  A4. Research Specific Tools   - Research custom tool list"
    Write-Menu "  A5. Database Only Backup      - Backup only database"
    Write-Menu "  A6. Configuration Reset       - Reset only configuration"
    Write-Menu "  A7. Clear Logs                - Remove all log files"
    Write-Menu "  A8. System Information        - Show detailed system info"
    Write-Menu "  A9. Export Logs               - Export logs to desktop"
    Write-Menu "  ⬅️  Back to Main Menu         - Return to main options"
    
    Write-Host ""
}

# Execute command
function Invoke-Command {
    param($Command, $Arguments = @())
    
    try {
        $ScriptPath = "$ScriptDir\$Command.ps1"
        if (Test-Path $ScriptPath) {
            & $ScriptPath @Arguments
            Write-Host "`nPress any key to continue..." -ForegroundColor Gray
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        } else {
            Write-Error "Script not found: $Command.ps1"
        }
    } catch {
        Write-Error "Error executing $Command`: $_"
        Write-Host "`nPress any key to continue..." -ForegroundColor Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

# Handle direct command execution
if ($Command) {
    switch ($Command.ToLower()) {
        "start" { Invoke-Command "Start" }
        "stop" { Invoke-Command "Stop" }
        "status" { Invoke-Command "Status" }
        "logs" { Invoke-Command "Logs" }
        "research" { Invoke-Command "Research" }
        "backup" { Invoke-Command "Backup" }
        "setup" { Invoke-Command "Setup" }
        "reset" { Invoke-Command "Reset" }
        default { Write-Error "Unknown command: $Command" }
    }
    exit
}

# Main interactive loop
$InAdvancedMenu = $false

while ($true) {
    Clear-Host
    
    Write-Host @"
🤖 AI Tool Intelligence Platform - Windows Management Console
================================================================
"@ -ForegroundColor Cyan
    
    # Show setup status
    if (Test-SetupComplete) {
        Write-Success "Platform is set up and ready to use"
    } else {
        Write-Warning "Platform setup incomplete - run option 7 (Setup/Reinstall)"
    }
    
    # Show current status
    Show-PlatformStatus
    
    # Show appropriate menu
    if ($InAdvancedMenu) {
        Show-AdvancedMenu
    } else {
        Show-MainMenu
    }
    
    # Get user input
    $Choice = Read-Host "Select an option"
    
    # Handle menu choices
    if ($InAdvancedMenu) {
        switch ($Choice.ToUpper()) {
            "A1" { 
                Write-Info "Starting backend only..."
                Invoke-Command "Start" @("-BackendOnly")
            }
            "A2" { 
                Write-Info "Starting frontend only..."
                Invoke-Command "Start" @("-FrontendOnly")
            }
            "A3" { 
                Write-Info "Monitoring logs in real-time..."
                Invoke-Command "Logs" @("-Tail")
            }
            "A4" { 
                $Tools = Read-Host "Enter tool names (comma-separated)"
                if ($Tools) {
                    Invoke-Command "Research" @("-Process", $Tools)
                }
            }
            "A5" { 
                Write-Info "Creating database-only backup..."
                Invoke-Command "Backup" @("-DatabaseOnly")
            }
            "A6" { 
                Write-Info "Resetting configuration only..."
                Invoke-Command "Reset" @("-ConfigOnly")
            }
            "A7" { 
                Write-Info "Clearing logs..."
                Invoke-Command "Logs" @("-Clear")
            }
            "A8" { 
                Write-Info "Showing system information..."
                Invoke-Command "Status"
            }
            "A9" { 
                Write-Info "Exporting logs..."
                Invoke-Command "Logs" @("-Export")
            }
            { $_ -in @("BACK", "B", "⬅️") } { 
                $InAdvancedMenu = $false
                continue
            }
            default { 
                Write-Warning "Invalid option: $Choice"
                Start-Sleep 1
            }
        }
    } else {
        switch ($Choice) {
            "1" { 
                Write-Info "Starting platform..."
                Invoke-Command "Start"
            }
            "2" { 
                Write-Info "Stopping platform..."
                Invoke-Command "Stop"
            }
            "3" { 
                Write-Info "Checking status..."
                Invoke-Command "Status"
            }
            "4" { 
                Write-Info "Viewing logs..."
                Invoke-Command "Logs"
            }
            "5" { 
                Write-Info "Managing research..."
                Invoke-Command "Research"
            }
            "6" { 
                Write-Info "Creating backup..."
                Invoke-Command "Backup"
            }
            "7" { 
                Write-Info "Running setup..."
                Invoke-Command "Setup"
            }
            "8" { 
                Write-Warning "Resetting platform..."
                Invoke-Command "Reset"
            }
            "9" { 
                Write-Info "Opening browser..."
                try {
                    Start-Process "http://localhost:3000"
                    Write-Success "Browser opened to http://localhost:3000"
                } catch {
                    Write-Error "Could not open browser. Navigate manually to: http://localhost:3000"
                }
                Start-Sleep 2
            }
            { $_ -in @("ADVANCED", "ADV", "A", "🔧") } { 
                $InAdvancedMenu = $true
                continue
            }
            { $_ -in @("EXIT", "QUIT", "Q", "X", "❌") } { 
                Write-Info "Goodbye! 👋"
                exit 0
            }
            default { 
                Write-Warning "Invalid option: $Choice"
                Start-Sleep 1
            }
        }
    }
}
