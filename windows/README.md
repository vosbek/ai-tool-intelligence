# Windows PowerShell Management Scripts

This directory contains PowerShell scripts that make the AI Tool Intelligence Platform easy to configure, manage, and use on Windows systems.

## 🚀 Quick Start

1. **Run the main setup:**
   ```powershell
   .\windows\Setup.ps1
   ```

2. **Start the platform:**
   ```powershell
   .\windows\Start.ps1
   ```

3. **Use the management console:**
   ```powershell
   .\windows\Manage.ps1
   ```

## 📜 Available Scripts

### Core Management

| Script | Purpose | Usage |
|--------|---------|-------|
| `Setup.ps1` | Complete platform setup | `.\Setup.ps1` |
| `Start.ps1` | Start backend and frontend services | `.\Start.ps1` |
| `Stop.ps1` | Stop all running services | `.\Stop.ps1` |
| `Status.ps1` | Check system status and health | `.\Status.ps1` |
| `Manage.ps1` | Interactive management console | `.\Manage.ps1` |

### Research Operations

| Script | Purpose | Usage |
|--------|---------|-------|
| `Research.ps1` | Manage research queue and operations | `.\Research.ps1 -Status` |
| | Process specific tools | `.\Research.ps1 -Process "Cursor,GitHub Copilot"` |
| | Process by category | `.\Research.ps1 -Category "Agentic IDEs"` |
| | Start automated scheduler | `.\Research.ps1 -Scheduler` |

### Data Management

| Script | Purpose | Usage |
|--------|---------|-------|
| `Backup.ps1` | Create system backups | `.\Backup.ps1` |
| `Reset.ps1` | Reset platform to clean state | `.\Reset.ps1` |
| `Logs.ps1` | View and manage application logs | `.\Logs.ps1` |

## 🛠️ Script Details

### Setup.ps1
**Complete platform setup for Windows**

```powershell
# Full setup with dependency checking
.\Setup.ps1

# Skip Python installation check
.\Setup.ps1 -SkipPython

# Force reinstall even if already set up
.\Setup.ps1 -Force
```

**What it does:**
- ✅ Checks all prerequisites (Python 3.9+, Node.js 18+, Git)
- 🐍 Creates Python virtual environment and installs dependencies
- ⚛️ Sets up React frontend with all packages
- 📁 Creates necessary directories and configuration files
- 🔧 Configures environment templates
- 📜 Installs all management scripts

### Start.ps1
**Start platform services with advanced options**

```powershell
# Start both backend and frontend
.\Start.ps1

# Start only backend service
.\Start.ps1 -BackendOnly

# Start only frontend service
.\Start.ps1 -FrontendOnly

# Start without opening browser
.\Start.ps1 -NoBrowser

# Use custom ports
.\Start.ps1 -BackendPort 8000 -FrontendPort 4000
```

**Features:**
- 🔍 Prerequisites validation
- 🚦 Port availability checking
- 📊 Health monitoring during startup
- 🌐 Automatic browser opening
- 🔄 Process monitoring and cleanup
- 📝 Comprehensive logging

### Status.ps1
**Comprehensive system status and health monitoring**

```powershell
# Full system status
.\Status.ps1

# Quick status check only
.\Status.ps1 -Quick

# JSON output for automation
.\Status.ps1 -Json
```

**Provides:**
- 🔌 Service status (backend/frontend)
- ⚙️ Configuration validation
- 💾 Database information
- 🖥️ System resources (memory, CPU, disk)
- 📊 Health metrics
- 🔍 Recent activity logs

### Research.ps1
**Advanced research queue management**

```powershell
# Show research status
.\Research.ps1 -Status

# List all tools
.\Research.ps1 -List

# Show failed tools
.\Research.ps1 -Failed

# Retry all failed tools
.\Research.ps1 -Retry

# Process specific tools
.\Research.ps1 -Process "Cursor,GitHub Copilot,Tabnine"

# Process all tools in a category
.\Research.ps1 -Category "Agentic IDEs"

# Start automated scheduler
.\Research.ps1 -Scheduler
```

**Features:**
- 📊 Real-time queue monitoring
- 🔄 Batch processing with rate limiting
- ⚡ Progress tracking with timeouts
- 🔁 Automatic retry for failed tools
- 📅 Scheduled research automation
- 🎯 Category-based processing

### Backup.ps1
**Comprehensive backup and archival**

```powershell
# Full backup
.\Backup.ps1

# Database only
.\Backup.ps1 -DatabaseOnly

# Configuration only
.\Backup.ps1 -ConfigOnly

# Custom backup location
.\Backup.ps1 -BackupPath "D:\Backups"

# Auto-cleanup old backups
.\Backup.ps1 -AutoClean
```

**Includes:**
- 🗄️ SQLite database
- ⚙️ Configuration files (secrets excluded)
- 📝 Recent log files
- 🖥️ System information
- 📋 Backup manifest with metadata
- 🗜️ Optional ZIP compression

### Logs.ps1
**Advanced log viewing and management**

```powershell
# View recent logs
.\Logs.ps1

# Monitor logs in real-time
.\Logs.ps1 -Tail

# Filter by log level
.\Logs.ps1 -Level ERROR

# Show specific number of lines
.\Logs.ps1 -Lines 100

# Filter by service
.\Logs.ps1 -Service Backend

# Show logs from specific date
.\Logs.ps1 -Date "2024-01-15"

# Export logs to desktop
.\Logs.ps1 -Export

# Clear all log files
.\Logs.ps1 -Clear
```

**Features:**
- 🎨 Color-coded log levels
- 🔄 Real-time monitoring
- 🔍 Advanced filtering options
- 📤 Export functionality
- 📊 Log statistics
- 🧹 Cleanup management

### Reset.ps1
**Safe platform reset with backup options**

```powershell
# Interactive full reset
.\Reset.ps1

# Force reset without prompts (DANGEROUS)
.\Reset.ps1 -Force

# Reset only database
.\Reset.ps1 -DatabaseOnly

# Reset only logs
.\Reset.ps1 -LogsOnly

# Reset only configuration
.\Reset.ps1 -ConfigOnly
```

**Safety features:**
- ⚠️ Multiple confirmation prompts
- 💾 Automatic backup creation option
- 🎯 Selective reset options
- 🔄 Default configuration restoration
- 📝 Reset activity logging

### Manage.ps1
**Interactive management console**

```powershell
# Launch interactive console
.\Manage.ps1

# Direct command execution
.\Manage.ps1 -Command start
.\Manage.ps1 -Command status
```

**Features:**
- 🎛️ Menu-driven interface
- 📊 Real-time status display
- 🔧 Advanced options menu
- 🚀 Quick access to all functions
- 💡 Context-aware suggestions

## ⚙️ Configuration

### Environment Variables
The scripts use these environment variables:

```powershell
# Set in backend\.env
$env:AWS_REGION = "us-west-2"
$env:AWS_ACCESS_KEY_ID = "your-key"
$env:AWS_SECRET_ACCESS_KEY = "your-secret"
$env:GITHUB_TOKEN = "optional-github-token"
```

### Windows Configuration
Located in `windows\config.json`:

```json
{
  "project_root": "C:\\devl\\ai-tool-intelligence",
  "python_path": "C:\\Python39\\python.exe",
  "node_path": "C:\\Program Files\\nodejs\\node.exe",
  "backend_port": 5000,
  "frontend_port": 3000,
  "auto_open_browser": true,
  "log_level": "INFO"
}
```

## 🔧 Advanced Usage

### Automation Examples

**Scheduled Research:**
```powershell
# Start automated research scheduler
.\Research.ps1 -Scheduler

# Process specific tools daily
$Tools = "Cursor,GitHub Copilot,Tabnine"
.\Research.ps1 -Process $Tools
```

**Monitoring Integration:**
```powershell
# Get status as JSON for monitoring systems
$Status = .\Status.ps1 -Json | ConvertFrom-Json
if ($Status.platform_status -ne "fully_operational") {
    # Send alert
}
```

**Backup Automation:**
```powershell
# Daily backup with cleanup
.\Backup.ps1 -AutoClean

# Weekly full backup to external drive
.\Backup.ps1 -BackupPath "E:\AIToolBackups"
```

### Development Workflow

```powershell
# 1. Development setup
.\Setup.ps1

# 2. Start development environment
.\Start.ps1

# 3. Monitor logs during development
.\Logs.ps1 -Tail

# 4. Test research functionality
.\Research.ps1 -Process "TestTool"

# 5. Create backup before major changes
.\Backup.ps1

# 6. Reset to clean state for testing
.\Reset.ps1 -DatabaseOnly
```

## 🛡️ Security Considerations

### Credential Management
- ✅ Secrets excluded from backups
- ✅ Environment templates use placeholders
- ✅ No sensitive data in logs
- ✅ Secure backup handling

### Access Control
- ✅ Requires local administrator for setup
- ✅ Process isolation for services
- ✅ Port binding validation
- ✅ Safe reset with confirmations

## 🐛 Troubleshooting

### Common Issues

**"Execution Policy" Error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**"Backend not responding":**
```powershell
# Check if port is blocked
.\Status.ps1
# Try different port
.\Start.ps1 -BackendPort 8000
```

**"Python virtual environment issues":**
```powershell
# Reinstall virtual environment
.\Reset.ps1 -ConfigOnly
.\Setup.ps1 -Force
```

**"Frontend build failures":**
```powershell
# Clear npm cache and reinstall
cd frontend
npm cache clean --force
npm install
```

### Log Analysis
```powershell
# Check for errors
.\Logs.ps1 -Level ERROR

# Monitor startup issues
.\Logs.ps1 -Tail

# Export logs for support
.\Logs.ps1 -Export
```

### Performance Issues
```powershell
# Check system resources
.\Status.ps1

# Reduce concurrent research
# Edit: backend\config.json
# Set: "max_concurrent_tools": 1
```

## 📚 Additional Resources

- **Main Documentation:** `../README.md`
- **API Documentation:** `../docs/API.md`
- **Deployment Guide:** `../docs/DEPLOYMENT.md`
- **Project Structure:** See main README

## 🆘 Getting Help

1. **Check Status:** `.\Status.ps1`
2. **View Logs:** `.\Logs.ps1 -Level ERROR`
3. **Create Support Package:** `.\Logs.ps1 -Export` + `.\Backup.ps1`
4. **Reset if Needed:** `.\Reset.ps1`
5. **Reinstall:** `.\Setup.ps1 -Force`

---

**Happy researching! 🚀**

The AI Tool Intelligence Platform is designed to automate the tedious work of researching developer tools, giving you comprehensive insights in minutes instead of hours.
