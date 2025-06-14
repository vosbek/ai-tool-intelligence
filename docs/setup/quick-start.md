# 🚀 Quick Start Guide - New Machine Setup

> **Complete installation on a fresh Windows machine in 15-20 minutes**

## 📥 Step 1: Get the Code

```bash
# Option A: Git clone
git clone https://github.com/yourusername/ai-tool-intelligence.git
cd ai-tool-intelligence

# Option B: Download ZIP from GitHub
# Extract to C:\Projects\ai-tool-intelligence
```

## ⚡ Step 2: One-Command Setup

```powershell
# Open PowerShell as Administrator in project directory
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
.\windows\Setup.ps1
```

**This automatically installs everything:**
- ✅ Python 3.11+ (if needed)
- ✅ Node.js 18+ (if needed)  
- ✅ All Python dependencies
- ✅ All frontend packages
- ✅ Virtual environment setup
- ✅ Directory structure
- ✅ Configuration templates

## 🔑 Step 3: Configure AWS

Edit the created environment file:
```powershell
notepad backend\.env
```

Add your AWS credentials:
```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SECRET_KEY=change-this-secret-key
```

## 🤖 Step 4: Enable Claude in AWS

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Switch to **us-east-1** region
3. **Model access** → **Manage model access**
4. Find **Claude 3.5 Sonnet** → **Request access**

## 🚀 Step 5: Start Everything

```powershell
# Enhanced startup with stability features
.\start_windows.bat

# OR PowerShell script
.\windows\Start.ps1
```

## ✅ Step 6: Verify

1. **Frontend**: http://localhost:3000
2. **Health Check**: http://localhost:5000/api/health  
3. **Add a test tool** and click "Research"

## 🛠️ Daily Management Commands

```powershell
# Start the platform
.\windows\Start.ps1

# Check system status  
.\windows\Status.ps1

# View logs
.\windows\Logs.ps1

# Stop everything
.\windows\Stop.ps1

# Monitor system health
python monitor_system.py
```

## 🆘 Quick Troubleshooting

**"Execution Policy" Error:**
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**"Python not found":**
```powershell
.\windows\Setup.ps1 -Force
```

**"AWS validation failed":**
- Check credentials in `backend\.env`
- Verify Claude access in AWS Console
- Temporarily skip: Set `SKIP_AWS_VALIDATION=true`

**"Port already in use":**
```powershell
netstat -ano | findstr :5000
taskkill /PID <process_id> /F
```

## 📚 Complete Documentation

- **[INSTALL.md](INSTALL.md)** - Detailed new machine setup
- **[windows/README.md](windows/README.md)** - Windows management scripts  
- **[WINDOWS_SETUP.md](WINDOWS_SETUP.md)** - Complete Windows guide
- **[STABILITY_FEATURES.md](STABILITY_FEATURES.md)** - Stability features
- **[APPLICATION_WORKFLOW.md](APPLICATION_WORKFLOW.md)** - How it all works

## 🎯 What You Get

Your platform includes:
- ✅ **13 specialized research tools** using AWS Strands Agents
- ✅ **Competitive analysis engine** with market insights
- ✅ **Real-time monitoring** and health checks
- ✅ **Admin interface** with comprehensive management
- ✅ **Windows stability features** with error handling
- ✅ **PowerShell management scripts** for easy operation
- ✅ **Comprehensive logging** and crash reporting

**Total setup time**: 15-20 minutes on a fresh machine! 🎉