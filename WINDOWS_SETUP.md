# Complete Windows Setup Guide for AI Tool Intelligence Platform

> **Enterprise-grade AI tool intelligence platform setup for Windows 10/11**

This guide provides detailed, step-by-step instructions for setting up the AI Tool Intelligence Platform on a new Windows machine. Follow every step carefully to ensure a successful installation.

## 📋 Prerequisites Checklist

Before starting, ensure your Windows machine meets these requirements:

- **Windows 10** (version 1909 or later) or **Windows 11**
- **8GB RAM minimum** (16GB recommended for enterprise features)
- **10GB free disk space** (for dependencies and data)
- **Internet connection** (for downloading dependencies and AWS access)
- **Administrator access** (for installing software)

## 🚀 Complete Installation Process

### Step 1: Install Core Development Tools

> **💡 Enhanced Stability Features**: This platform now includes comprehensive Windows stability features including graceful shutdown, error handling, system monitoring, and crash reporting.

#### 1.1 Install Python 3.10+ (Required for Strands SDK)

**Option A: Download from Python.org (Recommended)**
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download **Python 3.11.x** (latest stable version)
3. **IMPORTANT**: During installation, check these boxes:
   - ✅ "Add Python to PATH"
   - ✅ "Install for all users"
   - ✅ "Add Python to environment variables"
4. Choose "Custom Installation" and select:
   - ✅ Documentation
   - ✅ pip
   - ✅ tcl/tk and IDLE
   - ✅ Python test suite
   - ✅ py launcher

**Option B: Install via Windows Package Manager**
```powershell
# Open PowerShell as Administrator
winget install Python.Python.3.11

# Verify installation
python --version
# Should output: Python 3.11.x
```

**Verify Python Installation:**
```powershell
# Open Command Prompt or PowerShell
python --version
pip --version

# Should show:
# Python 3.11.x
# pip 23.x.x
```

#### 1.2 Install Node.js 18+ (Required for React Frontend)

**Option A: Download from nodejs.org**
1. Go to [nodejs.org](https://nodejs.org/)
2. Download the **LTS version** (18.x or higher)
3. Run the installer with default settings
4. Restart your computer after installation

**Option B: Install via Windows Package Manager**
```powershell
# Open PowerShell as Administrator
winget install OpenJS.NodeJS

# Verify installation
node --version
npm --version

# Should show:
# v18.x.x or higher
# 9.x.x or higher
```

#### 1.3 Install Git for Windows

**Download and Install:**
1. Go to [git-scm.com/download/win](https://git-scm.com/download/win)
2. Download the latest version
3. During installation, select these options:
   - ✅ "Git from the command line and also from 3rd-party software"
   - ✅ "Use the OpenSSL library"
   - ✅ "Checkout Windows-style, commit Unix-style line endings"
   - ✅ "Use MinTTY (the default terminal of MSYS2)"

**Option B: Install via Windows Package Manager**
```powershell
winget install Git.Git
```

**Verify Git Installation:**
```powershell
git --version
# Should show: git version 2.x.x
```

#### 1.4 Install Visual Studio Code (Recommended IDE)

```powershell
winget install Microsoft.VisualStudioCode
```

**Recommended VS Code Extensions:**
- Python
- ES7+ React/Redux/React-Native snippets
- REST Client
- GitLens

### Step 2: Download and Setup the Project

#### 2.1 Clone the Repository

```powershell
# Navigate to your desired directory (e.g., C:\Projects)
cd C:\
mkdir Projects
cd Projects

# Clone the repository
git clone https://github.com/yourusername/ai-tool-intelligence.git
cd ai-tool-intelligence

# Verify you have all files
dir
# Should show: backend/, frontend/, windows/, scripts/, etc.
```

#### 2.2 Create Python Virtual Environment

```powershell
# Ensure you're in the project root directory
cd C:\Projects\ai-tool-intelligence

# Create virtual environment
python -m venv venv

# Verify virtual environment was created
dir venv
# Should show: Include/, Lib/, Scripts/, pyvenv.cfg

# Activate virtual environment
venv\Scripts\activate

# Verify activation (your prompt should show (venv))
# Command prompt should now show: (venv) C:\Projects\ai-tool-intelligence>

# Verify Python is using virtual environment
where python
# Should show: C:\Projects\ai-tool-intelligence\venv\Scripts\python.exe
```

**Important Virtual Environment Notes:**
- Always activate the virtual environment before running Python commands
- If you close your terminal, you'll need to activate it again
- To deactivate: run `deactivate`

### Step 3: Install Python Dependencies

#### 3.1 Upgrade pip and Install Core Packages

```powershell
# Ensure virtual environment is activated (you should see (venv) in prompt)
# If not activated, run: venv\Scripts\activate

# Upgrade pip to latest version
python -m pip install --upgrade pip setuptools wheel

# Install core requirements
cd backend
pip install -r requirements.txt

# This will install:
# - Flask and web framework dependencies
# - AWS Strands Agents and tools
# - SQLAlchemy for database management
# - All competitive analysis components
# - Admin interface dependencies
# - Monitoring and logging systems
```

**If you encounter SSL certificate errors:**
```powershell
# Use trusted hosts
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
```

**If you encounter Strands SDK installation issues:**
```powershell
# Try installing with specific index
pip install --index-url https://pypi.org/simple/ strands-agents strands-agents-tools

# Or try pre-release version
pip install --pre strands-agents strands-agents-tools

# Verify installation
python -c "import strands; print('Strands SDK installed successfully')"
```

#### 3.2 Verify Python Installation

```powershell
# Test all major components
python -c "
import flask
import sqlalchemy
import psutil
import pandas
import numpy
print('✅ All Python dependencies installed successfully')
"

# Test Strands SDK specifically
python -c "
try:
    from strands import Agent
    from strands.models import BedrockModel
    print('✅ Strands SDK installed successfully')
except ImportError as e:
    print('❌ Strands SDK issue:', e)
"
```

### Step 4: Install Frontend Dependencies

#### 4.1 Install Node.js Packages

```powershell
# Navigate to frontend directory
cd ..\frontend

# Clear npm cache (prevents common issues)
npm cache clean --force

# Install dependencies
npm install

# This installs React, admin dashboard components, and all UI dependencies
# Installation may take 3-5 minutes
```

**If you encounter permission errors:**
```powershell
# Set npm to use a different cache directory
npm config set cache C:\temp\npm-cache --global
npm config set tmp C:\temp --global

# Create temp directories if they don't exist
mkdir C:\temp\npm-cache -ErrorAction SilentlyContinue

# Try installation again
npm install
```

#### 4.2 Verify Frontend Installation

```powershell
# Test React build process
npm run build

# Should complete without errors and create build/ directory
# Output should end with: "The build folder is ready to be deployed."

# Return to project root
cd ..
```

### Step 5: Configure AWS Credentials

#### 5.1 Obtain AWS Credentials

Before proceeding, you need:
1. **AWS Account** with Bedrock access
2. **IAM User** with Bedrock permissions
3. **Access Key ID** and **Secret Access Key**

**Required IAM Permissions:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        }
    ]
}
```

#### 5.2 Enable Claude 3.5 Sonnet in AWS Bedrock

1. Go to **AWS Console** → **Bedrock** → **Model access**
2. Ensure you're in **us-east-1** region
3. Click **"Manage model access"**
4. Find **"Claude 3.5 Sonnet"** by Anthropic
5. Click **"Request access"** (usually instant approval)
6. Wait for status to change to **"Access granted"**

#### 5.3 Configure Credentials (Choose ONE Method)

**Option A: Environment File (Recommended for Development)**

```powershell
# Navigate to backend directory
cd backend

# Copy environment template
copy .env.example .env

# Edit the environment file
notepad .env

# Add your credentials:
```

In the `.env` file, add:
```
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Application Configuration
DATABASE_URL=sqlite:///ai_tools.db
SKIP_AWS_VALIDATION=false
ENABLE_MONITORING=true
MONITORING_INTERVAL_SECONDS=60
ENABLE_REAL_TIME_MONITORING=false

# Admin Configuration
LOG_DIR=logs
SECRET_KEY=your-secret-key-for-production
```

**Option B: Windows Environment Variables (Advanced)**

```powershell
# Set system environment variables permanently
[Environment]::SetEnvironmentVariable("AWS_ACCESS_KEY_ID", "AKIAXXXXXXXXXXXXXXXX", "User")
[Environment]::SetEnvironmentVariable("AWS_SECRET_ACCESS_KEY", "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "User")
[Environment]::SetEnvironmentVariable("AWS_REGION", "us-east-1", "User")

# Restart PowerShell after setting environment variables
```

#### 5.4 Validate AWS Configuration

```powershell
# Ensure you're in backend directory with virtual environment activated
# (venv) C:\Projects\ai-tool-intelligence\backend>

python aws_credential_validator.py
```

**Expected Successful Output:**
```
🔍 Validating AWS setup...
✅ AWS credentials validated (environment_variables/profile/iam_role)
✅ Bedrock access confirmed in us-east-1
✅ Claude 3.5 Sonnet available
🎉 AWS setup validation complete!
```

**If validation fails:**
1. Check that credentials are correct
2. Verify you're using us-east-1 region
3. Ensure Claude 3.5 Sonnet access is approved
4. Check IAM permissions

### Step 6: Initialize the Database and System

#### 6.1 Database Setup

```powershell
# Ensure you're in backend directory with virtual environment activated
# Initialize the database with enhanced schema
python -c "
from app import app, db
from migrations.migrate_to_enhanced_schema import run_migration

with app.app_context():
    db.create_all()
    run_migration()
    print('✅ Database initialized with enhanced schema')
"
```

#### 6.2 Verify System Components

```powershell
# Test all major system components
python -c "
from models.enhanced_schema import *
from data_curation.curation_engine import CurationEngine
from competitive_analysis.market_analyzer import MarketAnalyzer
from admin_interface.admin_manager import AdminInterfaceManager
from logging_monitoring.system_logger import get_logger
print('✅ All enterprise components loaded successfully')
"
```

### Step 7: Start the Application

#### 7.1 Using Windows Batch Scripts (Recommended)

```powershell
# Start the application using Windows scripts
.\windows\start-windows.bat

# This will:
# 1. Activate virtual environment
# 2. Start backend on port 5000
# 3. Start frontend on port 3000
# 4. Open browser automatically
```

#### 7.2 Manual Start (Alternative)

**Terminal 1 - Backend:**
```powershell
# Navigate to project root
cd C:\Projects\ai-tool-intelligence

# Activate virtual environment
venv\Scripts\activate

# Start backend
cd backend
python app.py

# Should show:
# 🚀 Starting AI Tool Intelligence Platform
# ✅ Enhanced schema initialized
# ✅ Enhanced competitive intelligence system ready
# ✅ Logging and monitoring system initialized
# * Running on http://0.0.0.0:5000
```

**Terminal 2 - Frontend:**
```powershell
# Open new PowerShell window
cd C:\Projects\ai-tool-intelligence\frontend

# Start frontend
npm start

# Should automatically open browser to http://localhost:3000
```

### Step 8: Verify Installation

#### 8.1 Test Core Functionality

1. **Open Browser** to `http://localhost:3000`
2. **Verify Homepage** loads without errors
3. **Check API Health**:
   - Go to `http://localhost:5000/api/health`
   - Should return: `{"status": "healthy", "timestamp": "...", "version": "MVP"}`

#### 8.2 Test Enterprise Features

**Admin Interface:**
- Go to `http://localhost:5000/api/admin/dashboard`
- Add header: `X-Admin-User: admin`
- Should return dashboard data

**Monitoring System:**
- Go to `http://localhost:5000/api/monitoring/status`
- Should show monitoring system status

**Competitive Analysis:**
- Go to `http://localhost:5000/api/system/status`
- Should show all enterprise components as available

#### 8.3 Add Your First Tool

1. Click **"Add New Tool"** on the dashboard
2. Enter tool information:
   ```
   Name: Cursor
   Category: Agentic IDEs
   Website: https://cursor.sh
   GitHub: https://github.com/getcursor/cursor
   Documentation: https://docs.cursor.sh
   ```
3. Click **"Research"** to trigger automated analysis
4. Wait 2-3 minutes for comprehensive results

**Expected Results:**
- Tool should appear in the database
- Research should complete successfully
- Comprehensive data should be populated
- Quality score should be calculated

## 🛠️ Windows-Specific Tools and Scripts

### PowerShell Management Scripts

The `windows/` directory contains Windows-specific management tools:

```powershell
# Complete system setup (run once)
.\windows\setup-windows.bat

# Start application services
.\windows\start-windows.bat

# Stop all services
.\windows\stop-windows.bat

# Check system status
.\windows\status-windows.bat

# View logs
.\windows\logs-windows.bat

# Backup system
.\windows\backup-windows.bat
```

### Windows Performance Optimization

#### Enable Developer Mode
1. Go to **Settings** → **Update & Security** → **For developers**
2. Select **"Developer mode"**
3. Restart your computer

#### Optimize Windows Defender
1. Go to **Settings** → **Windows Security** → **Virus & threat protection**
2. Click **"Manage settings"** under Virus & threat protection settings
3. Add exclusions for:
   - `C:\Projects\ai-tool-intelligence\`
   - `C:\Projects\ai-tool-intelligence\venv\`
   - `C:\Projects\ai-tool-intelligence\node_modules\`

#### Increase PowerShell Execution Policy
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 🐛 Troubleshooting Guide

### Common Installation Issues

#### 1. Python Installation Problems

**Error: "Python is not recognized as an internal or external command"**
```powershell
# Solution 1: Reinstall Python with PATH option checked
# Solution 2: Manually add Python to PATH
$env:PATH += ";C:\Python311;C:\Python311\Scripts"

# Verify
python --version
```

**Error: "Python 3.10+ is required"**
```powershell
# Check current version
python --version

# If version is too old, uninstall and reinstall Python 3.11+
```

#### 2. Virtual Environment Issues

**Error: "venv\Scripts\activate is not recognized"**
```powershell
# Try full path
C:\Projects\ai-tool-intelligence\venv\Scripts\activate.bat

# Or use PowerShell activation
venv\Scripts\Activate.ps1

# If execution policy prevents this:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Error: Virtual environment not working properly**
```powershell
# Delete and recreate virtual environment
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r backend\requirements.txt
```

#### 3. Node.js and npm Issues

**Error: "npm install fails with EACCES"**
```powershell
# Run PowerShell as Administrator
# OR set npm cache to different location
npm config set cache C:\temp\npm-cache --global
npm config set tmp C:\temp --global
mkdir C:\temp\npm-cache
```

**Error: "Node is not recognized"**
```powershell
# Restart computer after Node.js installation
# OR manually add to PATH
$env:PATH += ";C:\Program Files\nodejs"
```

#### 4. AWS Configuration Issues

**Error: "AWS credentials validation failed"**
```powershell
# Step 1: Verify credentials are correct
# Step 2: Check region is us-east-1
# Step 3: Verify Claude 3.5 Sonnet access in AWS Console
# Step 4: Check IAM permissions

# Debug credentials
python -c "
import os
print('AWS_ACCESS_KEY_ID:', os.getenv('AWS_ACCESS_KEY_ID', 'Not set'))
print('AWS_SECRET_ACCESS_KEY:', 'Set' if os.getenv('AWS_SECRET_ACCESS_KEY') else 'Not set')
print('AWS_REGION:', os.getenv('AWS_REGION', 'Not set'))
"
```

**Error: "Bedrock access denied"**
1. Go to AWS Console → Bedrock → Model access
2. Ensure you're in **us-east-1** region
3. Request access to Claude 3.5 Sonnet
4. Wait for approval (usually instant)

#### 5. Database Issues

**Error: "Database initialization failed"**
```powershell
# Delete existing database and recreate
del backend\ai_tools.db
cd backend
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database recreated')
"
```

#### 6. Port Conflicts

**Error: "Port 3000/5000 already in use"**
```powershell
# Find processes using the ports
netstat -ano | findstr :3000
netstat -ano | findstr :5000

# Kill the processes (replace PID with actual process ID)
taskkill /PID 1234 /F
```

#### 7. Strands SDK Issues

**Error: "Could not install strands-agents"**
```powershell
# Try different installation methods
pip install --index-url https://pypi.org/simple/ strands-agents strands-agents-tools

# Or try pre-release
pip install --pre strands-agents strands-agents-tools

# Or install from git (if available)
pip install git+https://github.com/strand-ai/strands-python.git
```

#### 8. SSL Certificate Errors

**Error: SSL certificate verify failed**
```powershell
# Temporary fix for pip
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Permanent configuration
pip config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org"
```

### Application Runtime Issues

#### 1. Research Operations Failing

**Symptoms:** Tools research returns errors or no data
```powershell
# Check AWS credentials again
cd backend
python aws_credential_validator.py

# Check Strands SDK
python -c "
from strands import Agent
from strands.models import BedrockModel
print('Strands SDK working')
"

# Test with simple tool
# Go to web interface and add a tool with just name and website
```

#### 2. Frontend Not Loading

**Symptoms:** Browser shows connection errors
```powershell
# Check if backend is running
curl http://localhost:5000/api/health

# Check if frontend is running
curl http://localhost:3000

# Restart both services
# Kill existing processes and restart
```

#### 3. Admin Interface Issues

**Symptoms:** Admin endpoints return 503 errors
```powershell
# Verify enhanced features are loaded
python -c "
from app import ENHANCED_FEATURES_AVAILABLE
print('Enhanced features:', ENHANCED_FEATURES_AVAILABLE)
"

# Check admin interface
curl -H "X-Admin-User: admin" http://localhost:5000/api/admin/dashboard
```

### Performance Issues

#### 1. Slow Research Operations

```powershell
# Reduce concurrent operations in backend/config.py
# Set max_concurrent_tools to 1

# Monitor system resources
# Task Manager → Performance tab
```

#### 2. High Memory Usage

```powershell
# Check monitoring dashboard
curl http://localhost:5000/api/monitoring/status

# Restart application if memory usage is high
.\windows\stop-windows.bat
.\windows\start-windows.bat
```

## 📊 System Health Monitoring

### Built-in Health Checks

**API Health Check:**
```powershell
curl http://localhost:5000/api/health
```

**System Status:**
```powershell
curl http://localhost:5000/api/system/status
```

**Monitoring Dashboard:**
```powershell
curl -H "X-Monitor-User: admin" http://localhost:5000/api/monitoring/health
```

### Log File Locations

- **Application Logs:** `backend\logs\application.log`
- **Error Logs:** `backend\logs\errors.log`
- **Performance Logs:** `backend\logs\performance.log`
- **Admin Logs:** `backend\logs\audit.log`

### Windows Service Installation (Optional)

For production environments, you can install as a Windows service:

```powershell
# Install service dependencies
pip install pywin32

# Install as Windows service
python windows\install_service.py

# Start service
sc start "AI Tool Intelligence Platform"

# Stop service
sc stop "AI Tool Intelligence Platform"
```

## 🚀 Next Steps

After successful installation:

1. **Read the User Guide:** See `docs/USER_GUIDE.md`
2. **Explore Admin Interface:** Access admin features at `/api/admin/*`
3. **Configure Monitoring:** Set up real-time monitoring and alerts
4. **Add Tools:** Start adding AI tools to your intelligence database
5. **Review Analytics:** Use the competitive analysis features

## 📞 Getting Help

If you encounter issues not covered in this guide:

1. **Check GitHub Issues:** [Repository Issues](https://github.com/yourusername/ai-tool-intelligence/issues)
2. **Review Documentation:** Check `docs/` directory for detailed guides
3. **Discord Support:** Join our support community
4. **Professional Support:** Contact for enterprise support options

---

**🎉 Congratulations!** You now have a fully functional AI Tool Intelligence Platform running on Windows with enterprise-grade features including competitive analysis, real-time monitoring, admin interface, and comprehensive logging.

Start by adding your first AI tool and exploring the powerful intelligence capabilities!