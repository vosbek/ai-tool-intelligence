# 🚀 New Machine Installation Guide

> **Quick Setup for AI Tool Intelligence Platform on a fresh Windows machine**

This guide gets you from zero to running in **15-20 minutes** on a new Windows machine.

## 📋 Before You Start

Ensure your machine has:
- **Windows 10** (1909+) or **Windows 11**
- **8GB RAM minimum** (16GB recommended)
- **10GB free disk space**
- **Internet connection**
- **Administrator access**

## 🎯 Step-by-Step Installation

### Step 1: Download the Project
```bash
# Option A: If you have Git
git clone https://github.com/yourusername/ai-tool-intelligence.git
cd ai-tool-intelligence

# Option B: Download ZIP from GitHub
# Extract to C:\Projects\ai-tool-intelligence or similar
```

### Step 2: Run Windows Setup (One Command!)
```powershell
# Open PowerShell as Administrator in the project directory
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
.\windows\Setup.ps1
```

**This automatically installs:**
- ✅ Python 3.11+ (if needed)
- ✅ Node.js 18+ (if needed)
- ✅ Git (if needed)
- ✅ All Python dependencies
- ✅ All frontend dependencies
- ✅ Creates virtual environment
- ✅ Sets up directory structure
- ✅ Creates configuration templates

### Step 3: Configure AWS Credentials

Edit the environment file that was created:
```powershell
notepad backend\.env
```

Add your AWS credentials:
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Application Configuration
DATABASE_URL=sqlite:///ai_tools.db
SKIP_AWS_VALIDATION=false
SECRET_KEY=your-secret-key-change-this
```

### Step 4: Enable Claude in AWS Bedrock

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Switch to **us-east-1** region
3. Go to **Model access**
4. Click **"Manage model access"**
5. Find **"Claude 3.5 Sonnet"** by Anthropic
6. Click **"Request access"** (usually instant)

### Step 5: Start the Platform
```powershell
# Enhanced startup with stability features
.\start_windows.bat

# OR use PowerShell script
.\windows\Start.ps1
```

### Step 6: Verify Installation
1. **Open browser** to http://localhost:3000
2. **Check health** at http://localhost:5000/api/health
3. **Add a test tool** to verify research functionality

## 🛠️ Available Management Scripts

Once installed, you have these Windows PowerShell scripts:

| Script | Purpose | Command |
|--------|---------|---------|
| **Setup.ps1** | Complete platform setup | `.\windows\Setup.ps1` |
| **Start.ps1** | Start services | `.\windows\Start.ps1` |
| **Stop.ps1** | Stop all services | `.\windows\Stop.ps1` |
| **Status.ps1** | Check system health | `.\windows\Status.ps1` |
| **Manage.ps1** | Interactive management | `.\windows\Manage.ps1` |
| **Research.ps1** | Manage research queue | `.\windows\Research.ps1 -Status` |
| **Backup.ps1** | Create backups | `.\windows\Backup.ps1` |
| **Logs.ps1** | View/manage logs | `.\windows\Logs.ps1` |

## 🎯 Daily Usage Commands

```powershell
# Start the platform
.\windows\Start.ps1

# Check if everything is running
.\windows\Status.ps1

# Monitor research queue
.\windows\Research.ps1 -Status

# View recent logs
.\windows\Logs.ps1

# Stop everything when done
.\windows\Stop.ps1
```

## 🔍 Enhanced Features Available

Your installation includes:

### 🛡️ **Stability Features**
- **Error Handling**: Circuit breakers and graceful degradation
- **Windows Optimization**: Process management and crash reporting
- **Health Monitoring**: Real-time system health endpoints
- **Graceful Shutdown**: Clean shutdowns with resource cleanup

### 📊 **Monitoring**
- **System Health**: `/api/system/health`
- **Component Status**: `/api/system/status`
- **Real-time Monitoring**: `python monitor_system.py`

### 🎛️ **Admin Tools**
- **Admin Interface**: Headers: `X-Admin-User: admin`
- **Data Curation**: Quality scoring and validation
- **Competitive Analysis**: Market analysis and trend tracking
- **Batch Processing**: Automated research scheduling

## 🐛 Quick Troubleshooting

### Common Issues

**"Execution Policy" Error:**
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**"Python not found":**
```powershell
# Re-run setup to install Python
.\windows\Setup.ps1 -Force
```

**"AWS validation failed":**
```powershell
# Check credentials in backend\.env
# Verify Claude access in AWS Bedrock Console
# Skip for testing: Set SKIP_AWS_VALIDATION=true in .env
```

**"Port already in use":**
```powershell
# Find and kill processes
netstat -ano | findstr :5000
taskkill /PID <process_id> /F
```

**Application not responding:**
```powershell
# Check status and restart
.\windows\Status.ps1
.\windows\Stop.ps1
.\windows\Start.ps1
```

### Get Help
```powershell
# Check detailed system status
.\windows\Status.ps1

# View error logs
.\windows\Logs.ps1 -Level ERROR

# Create backup before changes
.\windows\Backup.ps1

# Reset if needed
.\windows\Reset.ps1
```

## 🔄 Alternative Installation Methods

### Method 1: Enhanced Startup Script
```powershell
# Enhanced startup with validation
python start_stable.py
```

### Method 2: Manual Installation
Follow the detailed guide in [WINDOWS_SETUP.md](WINDOWS_SETUP.md)

### Method 3: PowerShell Management
```powershell
# Interactive management console
.\windows\Manage.ps1
```

## 📁 Project Structure After Installation

```
ai-tool-intelligence/
├── backend/              # Python Flask API
├── frontend/             # React frontend
├── windows/              # Windows PowerShell scripts
├── logs/                 # Application logs
├── backups/              # System backups
├── start_windows.bat     # Quick start script
├── start_stable.py       # Enhanced startup script
├── monitor_system.py     # Health monitoring
└── venv/                 # Python virtual environment
```

## ✅ Verification Checklist

After installation, verify these work:

- [ ] **Frontend loads**: http://localhost:3000
- [ ] **API responds**: http://localhost:5000/api/health
- [ ] **Admin access**: Headers with `X-Admin-User: admin`
- [ ] **System health**: http://localhost:5000/api/system/status
- [ ] **Add tool**: Create and research a test tool
- [ ] **View logs**: `.\windows\Logs.ps1`
- [ ] **Check status**: `.\windows\Status.ps1`

## 🎉 You're Ready!

Your AI Tool Intelligence Platform is now fully operational with:
- ✅ **Enterprise research capabilities**
- ✅ **Windows stability features**  
- ✅ **Real-time monitoring**
- ✅ **Admin management tools**
- ✅ **Comprehensive logging**
- ✅ **Error handling and recovery**

**Next Steps:**
1. Add your first AI tool via the web interface
2. Explore the admin capabilities
3. Set up automated research schedules
4. Review the competitive analysis features

For detailed documentation, see:
- **[Windows Management Scripts](windows/README.md)**
- **[Complete Setup Guide](WINDOWS_SETUP.md)**
- **[Stability Features](STABILITY_FEATURES.md)**
- **[Application Workflow](APPLICATION_WORKFLOW.md)**