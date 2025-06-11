# Windows Setup Guide for AI Tool Intelligence Platform

## Prerequisites

### 1. Python 3.10+ Installation
```powershell
# Download Python 3.10+ from python.org
# OR install via winget
winget install Python.Python.3.11

# Verify installation
python --version
# Should show Python 3.10.x or higher
```

### 2. Node.js 18+ Installation
```powershell
# Download from nodejs.org
# OR install via winget
winget install OpenJS.NodeJS

# Verify installation
node --version
npm --version
```

### 3. Git for Windows
```powershell
winget install Git.Git
```

## Installation Steps

### 1. Clone Repository
```powershell
git clone https://github.com/vosbek/ai-tool-intelligence.git
cd ai-tool-intelligence
```

### 2. Create Python Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify you're in the virtual environment
where python
# Should show path to venv\Scripts\python.exe
```

### 3. Install Python Dependencies
```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install requirements
pip install -r backend\requirements.txt

# If you get SSL errors, try:
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r backend\requirements.txt
```

### 4. Install Node.js Dependencies
```powershell
cd frontend
npm install

# If you get permission errors, try:
npm install --cache C:\temp\npm-cache
cd ..
```

### 5. Configure AWS Credentials

**⚠️ IMPORTANT: Use only ONE method to avoid conflicts**

#### Option A: .env File (Recommended for Development)
```powershell
# Copy environment template
copy backend\.env.example backend\.env

# Edit the .env file
notepad backend\.env
```

Add your AWS credentials:
```
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key-here
AWS_SECRET_ACCESS_KEY=your-secret-key-here
```

#### Option B: Environment Variables (Advanced)
```powershell
# Set environment variables for current session
$env:AWS_ACCESS_KEY_ID="your-access-key-here"
$env:AWS_SECRET_ACCESS_KEY="your-secret-key-here"
$env:AWS_REGION="us-east-1"
```

#### Option C: AWS Profile (If you use AWS CLI)
```powershell
# Configure AWS CLI (one-time setup)
aws configure --profile ai-tools

# Then set the profile
$env:AWS_PROFILE="ai-tools"
```

### 6. Validate AWS Setup
```powershell
cd backend
python aws_credential_validator.py
```

Expected output:
```
✅ AWS credentials validated
✅ Bedrock access confirmed in us-east-1  
✅ Claude 3.5 Sonnet available
🎉 AWS setup validation complete!
```

## Running the Application

### Option 1: Use Windows PowerShell Scripts
```powershell
# Start the application (both backend and frontend)
.\windows\Start.ps1

# Check status
.\windows\Status.ps1

# Stop the application
.\windows\Stop.ps1
```

### Option 2: Manual Start
```powershell
# Terminal 1: Start Backend
venv\Scripts\activate
cd backend
python app.py

# Terminal 2: Start Frontend
cd frontend
npm start
```

## Troubleshooting

### Common Issues

#### 1. Python Version Error
```
Error: Python 3.10+ is required
```
**Solution:** Update Python to version 3.10 or higher.

#### 2. Strands SDK Installation Failed
```
Error: Could not install strands-agents
```
**Solutions:**
```powershell
# Try with explicit index
pip install --index-url https://pypi.org/simple/ strands-agents strands-agents-tools

# Or try development version
pip install --pre strands-agents strands-agents-tools
```

#### 3. AWS Credential Confusion
```
Error: Multiple credential sources or wrong region
```
**Solutions:**
1. **Run the credential validator first:**
   ```powershell
   cd backend
   python aws_credential_validator.py
   ```
2. **Use only ONE credential method** (not multiple)
3. **Remove conflicting sources:**
   - If using .env file, don't set environment variables
   - If using AWS profile, don't use .env file
   - Check for ~/.aws/credentials file conflicts

#### 4. AWS Bedrock Access Issues
```
Error: Could not access AWS Bedrock
```
**Solutions:**
1. **Verify region is us-east-1** (not us-west-2)
2. Run credential validator to check access
3. Enable Bedrock in AWS Console → Model access
4. Request Claude 3.5 Sonnet access in us-east-1

#### 4. Port Already in Use
```
Error: Port 3000/5000 already in use
```
**Solution:**
```powershell
# Find and kill processes using the ports
netstat -ano | findstr :3000
netstat -ano | findstr :5000
taskkill /PID <process_id> /F
```

#### 5. Node.js Permission Errors
```
Error: EACCES permission denied
```
**Solutions:**
```powershell
# Run as administrator or:
npm config set cache C:\temp\npm-cache --global
npm config set tmp C:\temp --global
```

#### 6. Virtual Environment Activation Issues
If `venv\Scripts\activate` doesn't work:
```powershell
# Try with full path
C:\path\to\your\project\venv\Scripts\activate.bat

# Or use PowerShell script
venv\Scripts\Activate.ps1

# If execution policy prevents this:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 7. SSL Certificate Errors
```powershell
# Temporary fix for pip SSL issues
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org <package>

# Or set permanently
pip config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org"
```

## Windows-Specific Features

### PowerShell Scripts
The `windows/` directory contains PowerShell scripts for easy management:

- `Setup.ps1` - Complete setup automation
- `Start.ps1` - Start both backend and frontend
- `Stop.ps1` - Stop all processes
- `Status.ps1` - Check application status
- `Reset.ps1` - Reset environment and restart

### Performance Optimization
```powershell
# Enable Windows Developer Mode for better performance
# Settings > Update & Security > For developers > Developer mode

# Exclude project directory from Windows Defender
# Settings > Windows Security > Virus & threat protection > Exclusions
```

## Production Deployment on Windows

### Using IIS (Internet Information Services)
1. Install IIS with CGI support
2. Install Python CGI module
3. Configure IIS to serve the application

### Using Windows Service
```powershell
# Install as Windows service
pip install pywin32
python windows\install_service.py
```

For detailed production deployment, see `docs/WINDOWS_PRODUCTION.md`.