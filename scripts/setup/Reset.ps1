#Requires -Version 5.1
<#
.SYNOPSIS
    Reset the AI Tool Intelligence Platform to clean state
.DESCRIPTION
    Clears database, logs, and resets configuration to defaults
.EXAMPLE
    .\Reset.ps1
    Interactive reset with confirmation prompts
.EXAMPLE
    .\Reset.ps1 -Force
    Force reset without prompts (USE WITH CAUTION)
#>

[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$DatabaseOnly,
    [switch]$LogsOnly,
    [switch]$ConfigOnly
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

Write-Host @"
🔄 AI Tool Intelligence Platform Reset
================================================================
WARNING: This will remove data and reset the platform to a clean state.

Available reset options:
- Full Reset: Database + Logs + Configuration
- Database Only: Clear all tools and research data
- Logs Only: Clear all log files
- Configuration Only: Reset to default configuration

"@ -ForegroundColor Yellow

# Check if platform is running
function Test-PlatformRunning {
    try {
        $BackendRunning = (Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue) -ne $null
        $FrontendRunning = (Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue) -ne $null
        return $BackendRunning -or $FrontendRunning
    } catch {
        return $false
    }
}

if (Test-PlatformRunning) {
    Write-Error "Platform is currently running. Stop it first with: .\Stop.ps1"
    exit 1
}

# Determine what to reset
$ResetDatabase = $Force -or $DatabaseOnly -or (-not $LogsOnly -and -not $ConfigOnly)
$ResetLogs = $Force -or $LogsOnly -or (-not $DatabaseOnly -and -not $ConfigOnly)
$ResetConfig = $Force -or $ConfigOnly -or (-not $DatabaseOnly -and -not $LogsOnly)

# Interactive confirmation if not forced
if (-not $Force) {
    Write-Host "The following will be reset:" -ForegroundColor Yellow
    if ($ResetDatabase) { Write-Host "  ❌ Database (all tools and research data)" -ForegroundColor Red }
    if ($ResetLogs) { Write-Host "  ❌ Log files" -ForegroundColor Red }
    if ($ResetConfig) { Write-Host "  ❌ Configuration files" -ForegroundColor Red }
    
    Write-Host ""
    $Confirm = Read-Host "Are you sure you want to proceed? Type 'RESET' to confirm"
    
    if ($Confirm -ne "RESET") {
        Write-Info "Reset cancelled"
        exit 0
    }
}

Write-Step "Starting platform reset..."

# Create backup before reset
if (-not $Force) {
    $CreateBackup = Read-Host "Create backup before reset? (recommended) (y/n)"
    if ($CreateBackup -eq 'y' -or $CreateBackup -eq 'Y') {
        Write-Step "Creating backup..."
        & "$ScriptDir\Backup.ps1"
        Write-Success "Backup created"
    }
}

$ResetActions = @()

# Reset database
if ($ResetDatabase) {
    Write-Step "Resetting database..."
    
    $DbPath = "$ProjectRoot\backend\ai_tools.db"
    if (Test-Path $DbPath) {
        try {
            Remove-Item $DbPath -Force
            Write-Success "Database removed"
            $ResetActions += "Database cleared"
        } catch {
            Write-Error "Could not remove database: $_"
        }
    } else {
        Write-Info "Database file not found (already clean)"
    }
    
    # Clear uploads directory
    $UploadsDir = "$ProjectRoot\backend\uploads"
    if (Test-Path $UploadsDir) {
        try {
            Get-ChildItem $UploadsDir | Remove-Item -Recurse -Force
            Write-Success "Uploads directory cleared"
            $ResetActions += "Uploads cleared"
        } catch {
            Write-Warning "Could not clear uploads directory: $_"
        }
    }
}

# Reset logs
if ($ResetLogs) {
    Write-Step "Resetting logs..."
    
    $LogDirs = @(
        "$ScriptDir\logs",
        "$ProjectRoot\backend\logs"
    )
    
    foreach ($LogDir in $LogDirs) {
        if (Test-Path $LogDir) {
            try {
                Get-ChildItem $LogDir -Filter "*.log" | Remove-Item -Force
                Write-Success "Cleared logs in: $LogDir"
                $ResetActions += "Logs cleared"
            } catch {
                Write-Warning "Could not clear logs in $LogDir`: $_"
            }
        }
    }
}

# Reset configuration
if ($ResetConfig) {
    Write-Step "Resetting configuration..."
    
    # Reset backend .env
    $EnvPath = "$ProjectRoot\backend\.env"
    $EnvExamplePath = "$ProjectRoot\backend\.env.example"
    
    if (Test-Path $EnvExamplePath) {
        try {
            Copy-Item $EnvExamplePath $EnvPath -Force
            Write-Success "Backend .env reset to defaults"
            $ResetActions += "Backend configuration reset"
        } catch {
            Write-Warning "Could not reset backend .env: $_"
        }
    }
    
    # Reset backend config.json if it exists
    $BackendConfigPath = "$ProjectRoot\backend\config.json"
    if (Test-Path $BackendConfigPath) {
        $DefaultConfig = @{
            strands_agent = @{
                model_provider = "bedrock"
                model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
                temperature = 0.1
                max_tokens = 4000
                timeout_seconds = 300
                rate_limit_delay = 5
                max_retries = 3
            }
            batch_processing = @{
                max_concurrent_tools = 3
                daily_limit = 50
                weekly_limit = 200
                priority_categories = @("Agentic IDEs", "AI Code Assistants")
                exclude_weekends = $false
                start_hour = 6
                end_hour = 22
            }
            notifications = @{
                enable_email = $false
                email_recipients = @()
                enable_slack = $false
                slack_webhook_url = ""
                alert_on_failures = $true
                daily_summary = $true
                weekly_report = $true
            }
            debug_mode = $true
            log_level = "INFO"
            data_retention_days = 90
            backup_enabled = $true
        }
        
        try {
            $DefaultConfig | ConvertTo-Json -Depth 5 | Set-Content $BackendConfigPath
            Write-Success "Backend config.json reset to defaults"
            $ResetActions += "Backend config reset"
        } catch {
            Write-Warning "Could not reset backend config.json: $_"
        }
    }
    
    # Reset Windows configuration
    $WindowsConfigPath = "$ScriptDir\config.json"
    if (Test-Path $WindowsConfigPath) {
        $WindowsConfig = @{
            project_root = $ProjectRoot
            python_path = try { (Get-Command python).Source } catch { "python" }
            node_path = try { (Get-Command node).Source } catch { "node" }
            npm_path = try { (Get-Command npm).Source } catch { "npm" }
            backend_port = 5000
            frontend_port = 3000
            auto_open_browser = $true
            log_level = "INFO"
            created = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            reset_date = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        }
        
        try {
            $WindowsConfig | ConvertTo-Json -Depth 3 | Set-Content $WindowsConfigPath
            Write-Success "Windows configuration reset"
            $ResetActions += "Windows config reset"
        } catch {
            Write-Warning "Could not reset Windows configuration: $_"
        }
    }
}

# Clear any cached Python bytecode
Write-Step "Clearing Python cache..."
$PycacheDir = "$ProjectRoot\backend\__pycache__"
if (Test-Path $PycacheDir) {
    try {
        Remove-Item $PycacheDir -Recurse -Force
        Write-Success "Python cache cleared"
        $ResetActions += "Python cache cleared"
    } catch {
        Write-Warning "Could not clear Python cache: $_"
    }
}

# Clear npm cache (if needed)
if ($ResetConfig) {
    Write-Step "Clearing npm cache..."
    try {
        Set-Location "$ProjectRoot\frontend"
        npm cache clean --force 2>$null
        Write-Success "npm cache cleared"
        $ResetActions += "npm cache cleared"
    } catch {
        Write-Warning "Could not clear npm cache: $_"
    } finally {
        Set-Location $ProjectRoot
    }
}

# Summary
Write-Host "`n📊 Reset Summary" -ForegroundColor Blue
Write-Host ("=" * 40) -ForegroundColor Gray
Write-Host "Reset completed: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
Write-Host "Actions performed:" -ForegroundColor White

if ($ResetActions) {
    foreach ($Action in $ResetActions) {
        Write-Host "  ✅ $Action" -ForegroundColor Green
    }
} else {
    Write-Host "  ⚠️  No actions were performed" -ForegroundColor Yellow
}

Write-Host "`n🚀 Next Steps:" -ForegroundColor Blue
Write-Host "1. Configure AWS credentials: Edit backend\.env" -ForegroundColor White
Write-Host "2. Start the platform: .\Start.ps1" -ForegroundColor White
Write-Host "3. Open frontend: http://localhost:3000" -ForegroundColor White
Write-Host "4. Add your first tools and begin research" -ForegroundColor White

Write-Success "`n✅ Platform reset completed successfully!"

Write-Host @"

🔄 Reset Management Commands:

Full Reset:
  .\Reset.ps1                         # Interactive full reset
  .\Reset.ps1 -Force                  # Force reset (no prompts)

Partial Reset:
  .\Reset.ps1 -DatabaseOnly           # Clear only database
  .\Reset.ps1 -LogsOnly               # Clear only logs
  .\Reset.ps1 -ConfigOnly             # Reset only configuration

Recovery:
  .\Backup.ps1                        # Create backup before reset
  .\Setup.ps1                         # Re-run setup if needed

IMPORTANT: Always create a backup before resetting in production!

"@ -ForegroundColor Gray
