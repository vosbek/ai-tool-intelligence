#Requires -Version 5.1
<#
.SYNOPSIS
    Create backups of the AI Tool Intelligence Platform
.DESCRIPTION
    Backs up database, configuration, and logs with timestamp
.EXAMPLE
    .\Backup.ps1
    Creates a full backup with timestamp
.EXAMPLE
    .\Backup.ps1 -DatabaseOnly
    Backs up only the database
#>

[CmdletBinding()]
param(
    [switch]$DatabaseOnly,
    [switch]$ConfigOnly,
    [string]$BackupPath,
    [switch]$AutoClean
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

Write-Host "💾 AI Tool Intelligence Platform Backup" -ForegroundColor White

# Set backup location
if (-not $BackupPath) {
    $BackupPath = "$ProjectRoot\backend\backups"
}

# Ensure backup directory exists
if (-not (Test-Path $BackupPath)) {
    New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null
    Write-Info "Created backup directory: $BackupPath"
}

# Generate timestamp for backup
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupName = "backup_$Timestamp"
$BackupDir = "$BackupPath\$BackupName"

Write-Step "Creating backup: $BackupName"

# Create backup directory
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

$BackupInfo = @{
    created_date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    platform_version = "MVP"
    backup_type = if ($DatabaseOnly) { "Database Only" } elseif ($ConfigOnly) { "Configuration Only" } else { "Full Backup" }
    files_backed_up = @()
    total_size_mb = 0
}

$TotalSize = 0

# Backup database
if (-not $ConfigOnly) {
    Write-Step "Backing up database..."
    
    $DbPath = "$ProjectRoot\backend\ai_tools.db"
    if (Test-Path $DbPath) {
        $DbBackupPath = "$BackupDir\ai_tools.db"
        Copy-Item $DbPath $DbBackupPath -Force
        
        $DbSize = (Get-Item $DbBackupPath).Length
        $TotalSize += $DbSize
        $BackupInfo.files_backed_up += @{
            file = "ai_tools.db"
            size_bytes = $DbSize
            size_display = "$([math]::Round($DbSize/1KB, 2)) KB"
        }
        
        Write-Success "Database backed up ($([math]::Round($DbSize/1KB, 2)) KB)"
    } else {
        Write-Warning "Database file not found - will be created on first run"
    }
}

# Backup configuration files
if (-not $DatabaseOnly) {
    Write-Step "Backing up configuration..."
    
    # Backend configuration
    $ConfigFiles = @(
        @{ Source = "$ProjectRoot\backend\config.json"; Name = "backend_config.json" }
        @{ Source = "$ProjectRoot\backend\.env.example"; Name = "env_template" }
        @{ Source = "$ProjectRoot\windows\config.json"; Name = "windows_config.json" }
        @{ Source = "$ProjectRoot\frontend\package.json"; Name = "frontend_package.json" }
        @{ Source = "$ProjectRoot\backend\requirements.txt"; Name = "backend_requirements.txt" }
    )
    
    foreach ($Config in $ConfigFiles) {
        if (Test-Path $Config.Source) {
            $ConfigBackupPath = "$BackupDir\$($Config.Name)"
            Copy-Item $Config.Source $ConfigBackupPath -Force
            
            $ConfigSize = (Get-Item $ConfigBackupPath).Length
            $TotalSize += $ConfigSize
            $BackupInfo.files_backed_up += @{
                file = $Config.Name
                size_bytes = $ConfigSize
                size_display = "$([math]::Round($ConfigSize/1KB, 2)) KB"
            }
            
            Write-Success "Backed up: $($Config.Name)"
        }
    }
    
    # Backup .env file (without secrets)
    $EnvPath = "$ProjectRoot\backend\.env"
    if (Test-Path $EnvPath) {
        $EnvContent = Get-Content $EnvPath
        $SafeEnvContent = $EnvContent | Where-Object { 
            $_ -notmatch "SECRET|PASSWORD|TOKEN|KEY" -or $_ -match "your-.*-here"
        }
        
        $SafeEnvPath = "$BackupDir\env_safe_template"
        $SafeEnvContent | Set-Content $SafeEnvPath
        
        $EnvSize = (Get-Item $SafeEnvPath).Length
        $TotalSize += $EnvSize
        $BackupInfo.files_backed_up += @{
            file = "env_safe_template"
            size_bytes = $EnvSize
            size_display = "$([math]::Round($EnvSize/1KB, 2)) KB"
            note = "Secrets excluded for security"
        }
        
        Write-Success "Environment template backed up (secrets excluded)"
    }
}

# Backup recent logs
if (-not $DatabaseOnly -and -not $ConfigOnly) {
    Write-Step "Backing up recent logs..."
    
    $LogsDir = "$ScriptDir\logs"
    if (Test-Path $LogsDir) {
        $RecentLogs = Get-ChildItem $LogsDir -Filter "*.log" | 
                      Sort-Object LastWriteTime -Descending | 
                      Select-Object -First 5
        
        if ($RecentLogs) {
            $LogBackupDir = "$BackupDir\logs"
            New-Item -ItemType Directory -Path $LogBackupDir -Force | Out-Null
            
            foreach ($Log in $RecentLogs) {
                $LogBackupPath = "$LogBackupDir\$($Log.Name)"
                Copy-Item $Log.FullName $LogBackupPath -Force
                
                $LogSize = $Log.Length
                $TotalSize += $LogSize
                $BackupInfo.files_backed_up += @{
                    file = "logs/$($Log.Name)"
                    size_bytes = $LogSize
                    size_display = "$([math]::Round($LogSize/1KB, 2)) KB"
                }
            }
            
            Write-Success "Backed up $($RecentLogs.Count) recent log files"
        } else {
            Write-Info "No log files found to backup"
        }
    }
}

# Backup system information
if (-not $DatabaseOnly -and -not $ConfigOnly) {
    Write-Step "Collecting system information..."
    
    $SystemInfo = @{
        computer_name = $env:COMPUTERNAME
        username = $env:USERNAME
        os_version = (Get-WmiObject Win32_OperatingSystem).Caption
        powershell_version = $PSVersionTable.PSVersion.ToString()
        python_version = try { (python --version 2>&1) } catch { "Not found" }
        node_version = try { (node --version 2>&1) } catch { "Not found" }
        backup_created = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        project_root = $ProjectRoot
        backup_script_version = "1.0"
    }
    
    $SystemInfo | ConvertTo-Json -Depth 3 | Set-Content "$BackupDir\system_info.json"
    Write-Success "System information collected"
}

# Create backup manifest
$BackupInfo.total_size_mb = [math]::Round($TotalSize / 1MB, 2)
$BackupInfo | ConvertTo-Json -Depth 4 | Set-Content "$BackupDir\backup_info.json"

# Create README for the backup
$ReadmeContent = @"
AI Tool Intelligence Platform Backup
===================================

Backup Name: $BackupName
Created: $($BackupInfo.created_date)
Type: $($BackupInfo.backup_type)
Total Size: $($BackupInfo.total_size_mb) MB

Files Included:
$(foreach ($File in $BackupInfo.files_backed_up) { "- $($File.file) ($($File.size_display))" })

Restoration Instructions:
1. Stop the platform: .\windows\Stop.ps1
2. Copy ai_tools.db back to backend\ directory
3. Copy configuration files back to their original locations
4. Restart the platform: .\windows\Start.ps1

Notes:
- This backup was created by the Windows PowerShell backup script
- Environment variables with secrets are excluded for security
- Only recent log files are included to save space
- Full project files are not included - use Git for source code backup

For questions or issues, refer to the project documentation.
"@

$ReadmeContent | Set-Content "$BackupDir\README.txt"

# Auto-cleanup old backups
if ($AutoClean) {
    Write-Step "Cleaning up old backups..."
    
    $AllBackups = Get-ChildItem $BackupPath -Directory | 
                  Where-Object { $_.Name -match "^backup_\d{8}_\d{6}$" } |
                  Sort-Object CreationTime -Descending
    
    # Keep last 10 backups
    $BackupsToDelete = $AllBackups | Select-Object -Skip 10
    
    if ($BackupsToDelete) {
        foreach ($OldBackup in $BackupsToDelete) {
            Remove-Item $OldBackup.FullName -Recurse -Force
            Write-Info "Removed old backup: $($OldBackup.Name)"
        }
        Write-Success "Cleaned up $($BackupsToDelete.Count) old backups"
    } else {
        Write-Info "No old backups to clean up"
    }
}

# Compress backup (optional)
$CompressBackup = Read-Host "Compress backup to ZIP file? (y/n)"
if ($CompressBackup -eq 'y' -or $CompressBackup -eq 'Y') {
    Write-Step "Compressing backup..."
    
    $ZipPath = "$BackupPath\$BackupName.zip"
    
    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        [System.IO.Compression.ZipFile]::CreateFromDirectory($BackupDir, $ZipPath)
        
        $ZipSize = (Get-Item $ZipPath).Length
        $CompressionRatio = [math]::Round((1 - ($ZipSize / $TotalSize)) * 100, 1)
        
        Write-Success "Backup compressed to: $BackupName.zip"
        Write-Info "Compressed size: $([math]::Round($ZipSize/1MB, 2)) MB (${CompressionRatio}% compression)"
        
        # Ask if we should remove the uncompressed backup
        $RemoveOriginal = Read-Host "Remove uncompressed backup folder? (y/n)"
        if ($RemoveOriginal -eq 'y' -or $RemoveOriginal -eq 'Y') {
            Remove-Item $BackupDir -Recurse -Force
            Write-Info "Uncompressed backup folder removed"
        }
    } catch {
        Write-Warning "Could not compress backup: $_"
        Write-Info "Backup is still available uncompressed in: $BackupDir"
    }
}

# Final summary
Write-Host "`n📊 Backup Summary" -ForegroundColor Blue
Write-Host ("=" * 40) -ForegroundColor Gray
Write-Host "Backup Name: $BackupName" -ForegroundColor White
Write-Host "Location: $BackupDir" -ForegroundColor White
Write-Host "Type: $($BackupInfo.backup_type)" -ForegroundColor White
Write-Host "Files: $($BackupInfo.files_backed_up.Count)" -ForegroundColor White
Write-Host "Size: $($BackupInfo.total_size_mb) MB" -ForegroundColor White
Write-Host "Created: $($BackupInfo.created_date)" -ForegroundColor White

Write-Host "`n📋 Files Backed Up:" -ForegroundColor Blue
foreach ($File in $BackupInfo.files_backed_up) {
    $Note = if ($File.note) { " ($($File.note))" } else { "" }
    Write-Host "  ✓ $($File.file) - $($File.size_display)$Note" -ForegroundColor Gray
}

Write-Success "`n✅ Backup completed successfully!"

Write-Host @"

💾 Backup Management Commands:

Create Backups:
  .\Backup.ps1                        # Full backup
  .\Backup.ps1 -DatabaseOnly          # Database only
  .\Backup.ps1 -ConfigOnly            # Configuration only
  .\Backup.ps1 -AutoClean             # Backup and cleanup old ones

Backup Location: $BackupPath

Restoration:
1. Stop platform: .\Stop.ps1
2. Copy files from backup to original locations
3. Start platform: .\Start.ps1

Note: Use Git for source code backup and version control.

"@ -ForegroundColor Gray
