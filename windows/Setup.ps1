#Requires -Version 5.1
<#
.SYNOPSIS
    Complete setup script for AI Tool Intelligence Platform on Windows
.DESCRIPTION
    This script sets up the AI Tool Intelligence Platform including Python backend, 
    React frontend, and all dependencies on Windows systems.
.EXAMPLE
    .\Setup.ps1
    Sets up the entire platform with default settings
.EXAMPLE
    .\Setup.ps1 -SkipPython
    Skips Python installation check (if already installed)
#>

[CmdletBinding()]
param(
    [switch]$SkipPython,
    [switch]$SkipNode,
    [switch]$Force
)

# Set error handling
$ErrorActionPreference = "Stop"

# Colors for output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Step { param($Message) Write-Host "🔄 $Message" -ForegroundColor Blue }

Write-Host @"
🚀 AI Tool Intelligence Platform Setup for Windows
================================================================
This script will set up your AI development tool research platform.

Prerequisites that will be checked:
- Python 3.9+ with pip
- Node.js 18+ with npm
- Git
- PowerShell 5.1+

The script will:
1. ✅ Check all prerequisites
2. 🐍 Set up Python virtual environment and dependencies  
3. ⚛️  Set up React frontend with dependencies
4. 📁 Create necessary directories and files
5. 🔧 Configure environment templates
6. 📜 Install PowerShell management scripts

"@ -ForegroundColor White

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Step "Checking prerequisites..."

# Check PowerShell version
$PSVersion = $PSVersionTable.PSVersion
if ($PSVersion.Major -lt 5 -or ($PSVersion.Major -eq 5 -and $PSVersion.Minor -lt 1)) {
    Write-Error "PowerShell 5.1+ required, found $($PSVersion.ToString())"
    exit 1
}

# Check Python
if (-not $SkipPython) {
    try {
        $PythonVersion = python --version 2>&1
        if ($PythonVersion -match "Python (\d+)\.(\d+)") {
            $Major = [int]$Matches[1]
            $Minor = [int]$Matches[2]
            if ($Major -lt 3 -or ($Major -eq 3 -and $Minor -lt 9)) {
                Write-Error "Python 3.9+ required, found Python $Major.$Minor"
                Write-Info "Download from: https://python.org/downloads/"
                exit 1
            }
            Write-Success "Python $Major.$Minor found"
        } else {
            throw "Could not determine Python version"
        }
    } catch {
        Write-Error "Python not found or not accessible from PATH"
        Write-Info "Install Python 3.9+ from: https://python.org/downloads/"
        Write-Info "Make sure to check 'Add Python to PATH' during installation"
        exit 1
    }
    
    # Check pip
    try {
        pip --version | Out-Null
        Write-Success "pip found"
    } catch {
        Write-Error "pip not found. Reinstall Python with pip included"
        exit 1
    }
}

# Check Node.js
if (-not $SkipNode) {
    try {
        $NodeVersion = node --version 2>&1
        if ($NodeVersion -match "v(\d+)\.") {
            $Major = [int]$Matches[1]
            if ($Major -lt 18) {
                Write-Error "Node.js 18+ required, found Node.js $Major"
                Write-Info "Download from: https://nodejs.org/"
                exit 1
            }
            Write-Success "Node.js $Major found"
        } else {
            throw "Could not determine Node.js version"
        }
    } catch {
        Write-Error "Node.js not found or not accessible from PATH"
        Write-Info "Install Node.js 18+ from: https://nodejs.org/"
        exit 1
    }
    
    # Check npm
    try {
        npm --version | Out-Null
        Write-Success "npm found"
    } catch {
        Write-Error "npm not found. Reinstall Node.js"
        exit 1
    }
}

# Check Git
try {
    git --version | Out-Null
    Write-Success "Git found"
} catch {
    Write-Error "Git not found. Install from: https://git-scm.com/"
    exit 1
}

Write-Success "Prerequisites check passed"

# Create project structure
Write-Step "Creating project structure..."
$Directories = @(
    "$ProjectRoot\backend\uploads",
    "$ProjectRoot\backend\backups", 
    "$ProjectRoot\backend\logs",
    "$ProjectRoot\frontend\src",
    "$ProjectRoot\windows\logs",
    "$ProjectRoot\docs"
)

foreach ($Dir in $Directories) {
    if (-not (Test-Path $Dir)) {
        New-Item -ItemType Directory -Path $Dir -Force | Out-Null
        Write-Info "Created directory: $Dir"
    }
}

# Backend setup
Write-Step "Setting up Python backend..."
Set-Location "$ProjectRoot\backend"

# Create virtual environment
if (-not (Test-Path "venv") -or $Force) {
    Write-Info "Creating Python virtual environment..."
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment"
        exit 1
    }
}

# Activate virtual environment
Write-Info "Activating virtual environment..."
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Info "Upgrading pip..."
python -m pip install --upgrade pip

# Install Python dependencies
Write-Info "Installing Python dependencies (this may take a few minutes)..."
try {
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "pip install failed"
    }
    Write-Success "Python dependencies installed successfully"
} catch {
    Write-Error "Failed to install Python dependencies: $_"
    Write-Info "You may need to run: pip install --upgrade pip setuptools wheel"
    exit 1
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Info "Creating .env file from template..."
    Copy-Item ".env.example" ".env"
    Write-Warning "IMPORTANT: Edit backend\.env with your AWS credentials before using research features!"
}

# Test basic imports
Write-Info "Testing Python dependencies..."
try {
    python -c "from flask import Flask; from flask_sqlalchemy import SQLAlchemy; print('✅ Flask dependencies OK')"
    python -c "try:`n  from strands import Agent`n  print('✅ Strands Agents available')`nexcept ImportError:`n  print('⚠️  Strands Agents not available - research features will be limited')"
} catch {
    Write-Warning "Some dependencies may have issues, but basic functionality should work"
}

Write-Success "Backend setup complete"

# Frontend setup  
Write-Step "Setting up React frontend..."
Set-Location "$ProjectRoot\frontend"

# Install frontend dependencies
Write-Info "Installing frontend dependencies..."
try {
    npm install
    if ($LASTEXITCODE -ne 0) {
        throw "npm install failed"
    }
    Write-Success "Frontend dependencies installed successfully"
} catch {
    Write-Error "Failed to install frontend dependencies: $_"
    Write-Info "Try running: npm cache clean --force"
    exit 1
}

# Add proxy configuration to package.json if not present
$PackageJsonPath = "package.json"
if (Test-Path $PackageJsonPath) {
    $PackageJson = Get-Content $PackageJsonPath | ConvertFrom-Json
    if (-not $PackageJson.proxy) {
        $PackageJson | Add-Member -Name "proxy" -Value "http://localhost:5000" -MemberType NoteProperty
        $PackageJson | ConvertTo-Json -Depth 10 | Set-Content $PackageJsonPath
        Write-Info "Added proxy configuration to package.json"
    }
}

Write-Success "Frontend setup complete"

# Create Windows-specific configuration
Write-Step "Creating Windows configuration..."
Set-Location "$ProjectRoot\windows"

# Create configuration file
$Config = @{
    project_root = $ProjectRoot
    python_path = (Get-Command python).Source
    node_path = (Get-Command node).Source
    npm_path = (Get-Command npm).Source
    backend_port = 5000
    frontend_port = 3000
    auto_open_browser = $true
    log_level = "INFO"
    created = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
}

$Config | ConvertTo-Json -Depth 3 | Set-Content "config.json"
Write-Info "Created Windows configuration file"

# Test backend startup
Write-Step "Testing backend startup..."
Set-Location "$ProjectRoot\backend"
& ".\venv\Scripts\Activate.ps1"

$TestProcess = Start-Process -FilePath "python" -ArgumentList "app.py" -PassThru -WindowStyle Hidden
Start-Sleep 3

if (-not $TestProcess.HasExited) {
    # Test health endpoint
    try {
        $Response = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -TimeoutSec 5
        if ($Response.status -eq "healthy") {
            Write-Success "Backend test successful"
        }
    } catch {
        Write-Warning "Backend started but health check failed"
    }
    
    # Stop test process
    $TestProcess | Stop-Process -Force
} else {
    Write-Warning "Backend test failed - check logs when you start the platform"
}

# Final instructions
Set-Location $ProjectRoot

Write-Host @"

🎉 Setup Complete!
================================================================

Your AI Tool Intelligence Platform is ready to use!

📋 Next Steps:
1. Configure AWS credentials:
   • Edit: backend\.env
   • Add your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
   • Set AWS_REGION=us-west-2

2. Enable AWS Bedrock access:
   • Go to AWS Bedrock Console → Model access
   • Request access for Claude 3.7 Sonnet in us-west-2 region
   • Wait for approval (usually instant)

3. Start the platform:
   .\windows\Start.ps1

4. Open your browser:
   http://localhost:3000

🔧 Available PowerShell Scripts:
   .\windows\Start.ps1         # Start the platform
   .\windows\Stop.ps1          # Stop all services  
   .\windows\Status.ps1        # Check system status
   .\windows\Backup.ps1        # Create system backup
   .\windows\Research.ps1      # Manage research operations
   .\windows\Logs.ps1          # View application logs
   .\windows\Reset.ps1         # Reset to clean state

📖 Documentation:
   • README.md - Full documentation
   • backend\.env.example - Configuration template
   • frontend\package.json - Frontend dependencies

💡 Quick Start:
   1. .\windows\Start.ps1
   2. Open http://localhost:3000
   3. Click "Add New Tool"
   4. Enter tool info and click "Research"

"@ -ForegroundColor Green

Write-Warning "Remember to configure your AWS credentials in backend\.env before using research features!"

# Create desktop shortcut
$CreateShortcut = Read-Host "Create desktop shortcut for easy access? (y/n)"
if ($CreateShortcut -eq 'y' -or $CreateShortcut -eq 'Y') {
    try {
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("$([Environment]::GetFolderPath('Desktop'))\AI Tool Intelligence.lnk")
        $Shortcut.TargetPath = "powershell.exe"
        $Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$ProjectRoot\windows\Start.ps1`""
        $Shortcut.WorkingDirectory = $ProjectRoot
        $Shortcut.IconLocation = "powershell.exe,0"
        $Shortcut.Description = "Start AI Tool Intelligence Platform"
        $Shortcut.Save()
        Write-Success "Desktop shortcut created"
    } catch {
        Write-Warning "Could not create desktop shortcut: $_"
    }
}

Write-Success "Setup completed successfully! Run .\windows\Start.ps1 to begin."
