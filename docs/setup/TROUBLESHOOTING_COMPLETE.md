# 🔧 AI Tool Intelligence Platform - Complete Troubleshooting Guide

> **Comprehensive solutions for every setup and runtime issue**

This guide provides **tested solutions** for all known issues with the AI Tool Intelligence Platform. Every solution has been verified and includes step-by-step instructions.

---

## 🚨 **Critical Setup Issues**

### **❌ "app.py not found" or "No module named 'app'"**

**Symptoms**:
```bash
FileNotFoundError: [Errno 2] No such file or directory: 'app.py'
ModuleNotFoundError: No module named 'app'
```

**Root Cause**: Scripts expect `app.py` in backend directory but application is organized differently.

**✅ Solution**:
```bash
# The app.py file should now exist at backend/app.py
# If it doesn't exist, create it:
cd backend
cat > app.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from src.ai_tool_intelligence.main import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
EOF

# Then start normally:
python app.py
```

### **❌ Strands Package Installation Fails**

**Symptoms**:
```bash
ERROR: Could not find a version that satisfies the requirement strands-agents-tools
pip install strands-agents-tools: No such package
```

**Root Cause**: Incorrect package names or version conflicts.

**✅ Solution**:
```bash
# 1. Uninstall any existing Strands packages
pip uninstall strands-agents strands-tools strands-agents-tools -y

# 2. Install correct packages
pip install strands-agents>=0.1.0 strands-tools>=0.1.0

# 3. Verify installation
python -c "
try:
    from strands_agents import Agent
    print('✅ strands-agents installed correctly')
except ImportError as e:
    print(f'❌ strands-agents issue: {e}')

try:
    from strands_tools import Tool
    print('✅ strands-tools installed correctly')
except ImportError as e:
    print(f'❌ strands-tools issue: {e}')
"
```

### **❌ AWS Bedrock Access Denied**

**Symptoms**:
```bash
ClientError: An error occurred (AccessDeniedException) when calling the InvokeModel operation
UnauthorizedOperation: You don't have access to the model 'claude-3-5-sonnet'
```

**Root Cause**: AWS credentials not configured or Claude 3.5 Sonnet not enabled.

**✅ Solution**:

**Step 1: Configure AWS Credentials**
```bash
# Option A: AWS CLI
aws configure
# Enter your Access Key ID, Secret Access Key, region (us-east-1)

# Option B: Environment variables
export AWS_ACCESS_KEY_ID="your_key_here"
export AWS_SECRET_ACCESS_KEY="your_secret_here"
export AWS_DEFAULT_REGION="us-east-1"

# Option C: Edit .env file
cd backend
nano .env
# Add:
# AWS_ACCESS_KEY_ID=your_key_here
# AWS_SECRET_ACCESS_KEY=your_secret_here
# AWS_DEFAULT_REGION=us-east-1
```

**Step 2: Enable Claude 3.5 Sonnet in AWS Bedrock**
1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock)
2. **IMPORTANT**: Switch to `us-east-1` region (top-right dropdown)
3. Click "Model access" in left sidebar
4. Click "Manage model access"
5. Find "Claude 3.5 Sonnet" and check the box
6. Click "Save changes"
7. Wait for "Access granted" status (2-3 minutes)

**Step 3: Test Connection**
```bash
cd backend
python -c "
import boto3
try:
    client = boto3.client('bedrock-runtime', region_name='us-east-1')
    response = client.invoke_model(
        modelId='us.anthropic.claude-3-5-sonnet-20241022-v2:0',
        body='{\"messages\":[{\"role\":\"user\",\"content\":\"test\"}],\"max_tokens\":10}',
        contentType='application/json'
    )
    print('✅ AWS Bedrock connection successful')
except Exception as e:
    print(f'❌ AWS connection failed: {e}')
"
```

---

## 🐍 **Python Environment Issues**

### **❌ "Python version not supported"**

**Symptoms**:
```bash
ERROR: Package 'strands-agents' requires Python>=3.10 but you have Python 3.9
Your Python version is too old for this package
```

**✅ Solution**:
```bash
# Check current Python version
python --version

# If Python < 3.10, install Python 3.10+:

# Ubuntu/Debian:
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-pip

# macOS with Homebrew:
brew install python@3.10

# Windows: Download from https://python.org/downloads

# Use specific Python version:
python3.10 -m venv venv
source venv/bin/activate  # Unix
# OR
venv\Scripts\activate     # Windows
```

### **❌ Virtual Environment Issues**

**Symptoms**:
```bash
ModuleNotFoundError: No module named 'flask'
pip: command not found (inside venv)
```

**✅ Solution**:
```bash
# Create fresh virtual environment
cd backend
rm -rf venv  # Remove existing broken venv

# Create new venv with correct Python version
python3.10 -m venv venv

# Activate (Unix/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Verify activation (should show venv path)
which python
which pip

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### **❌ "Permission denied" or "Externally managed environment"**

**Symptoms**:
```bash
error: externally-managed-environment
[Errno 13] Permission denied: '/usr/local/lib/python3.10/site-packages'
```

**✅ Solution**:
```bash
# Always use virtual environment (don't install globally)
cd backend
python3.10 -m venv venv
source venv/bin/activate  # Unix
# OR
venv\Scripts\activate     # Windows

# Then install normally
pip install -r requirements.txt

# If still having issues, force virtual env:
python -m pip install --user virtualenv
python -m virtualenv venv
```

---

## 🌐 **Frontend Issues**

### **❌ "npm command not found"**

**Symptoms**:
```bash
bash: npm: command not found
'npm' is not recognized as an internal or external command
```

**✅ Solution**:
```bash
# Install Node.js (includes npm)
# Visit: https://nodejs.org/download

# Verify installation
node --version  # Should show v18+ 
npm --version   # Should show 8+

# If Node.js is installed but npm missing:
# Windows:
npm install -g npm

# macOS with Homebrew:
brew install npm

# Ubuntu/Debian:
sudo apt install npm
```

### **❌ Frontend Build Fails**

**Symptoms**:
```bash
Error: Cannot resolve dependency tree
ERESOLVE unable to resolve dependency tree
Module not found: Can't resolve 'react-scripts'
```

**✅ Solution**:
```bash
cd frontend

# Clear npm cache and node_modules
rm -rf node_modules package-lock.json
npm cache clean --force

# Reinstall dependencies
npm install

# If still failing, use legacy resolver
npm install --legacy-peer-deps

# Verify installation
npm run build  # Should complete without errors
```

### **❌ "Port 3000 already in use"**

**Symptoms**:
```bash
Error: listen EADDRINUSE: address already in use :::3000
Something is already running on port 3000
```

**✅ Solution**:
```bash
# Option A: Kill existing process
# Unix/macOS:
lsof -ti:3000 | xargs kill -9

# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID_NUMBER> /F

# Option B: Use different port
cd frontend
PORT=3001 npm start

# Option C: Set different port permanently
echo "PORT=3001" > .env.local
npm start
```

---

## 🗄️ **Database Issues**

### **❌ Database File Locked or Corrupted**

**Symptoms**:
```bash
sqlite3.OperationalError: database is locked
sqlite3.DatabaseError: database disk image is malformed
```

**✅ Solution**:
```bash
cd backend

# Stop all application processes first
pkill -f "python.*app.py"

# Remove corrupted database
rm -f instance/ai_tools.db
rm -f ai_tools.db  # Legacy location

# Recreate database
python -c "
from src.ai_tool_intelligence.models.database import db
from src.ai_tool_intelligence.main import create_app
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Database recreated successfully')
"
```

### **❌ "No such table" Errors**

**Symptoms**:
```bash
sqlite3.OperationalError: no such table: tools
OperationalError: (sqlite3.OperationalError) no such table: categories
```

**✅ Solution**:
```bash
cd backend

# Initialize database tables
python -c "
import os
import sys
sys.path.insert(0, 'src')
from ai_tool_intelligence.models.database import db
from ai_tool_intelligence.main import create_app

app = create_app()
with app.app_context():
    # Create all tables
    db.create_all()
    
    # Verify tables exist
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f'✅ Created tables: {tables}')
"
```

---

## 🔧 **Configuration Issues**

### **❌ ".env file not found" or Configuration Errors**

**Symptoms**:
```bash
FileNotFoundError: [Errno 2] No such file or directory: '.env'
Warning: AWS credentials not configured
```

**✅ Solution**:
```bash
cd backend

# Create .env from template
cp .env.example .env

# Edit with your configuration
nano .env  # Unix/macOS
notepad .env  # Windows

# Required configuration:
cat .env
# Should contain:
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
DATABASE_URL=sqlite:///instance/ai_tools.db
SECRET_KEY=your-secret-key-here

# Verify configuration
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
required = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_DEFAULT_REGION']
for key in required:
    value = os.getenv(key)
    if value:
        print(f'✅ {key}: configured')
    else:
        print(f'❌ {key}: missing')
"
```

### **❌ "CORS Error" or API Connection Issues**

**Symptoms**:
```bash
Access to fetch at 'http://localhost:5000/api/health' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**✅ Solution**:
```bash
# Verify backend is running
curl http://localhost:5000/api/health
# Should return: {"status": "healthy"}

# If backend not running, start it:
cd backend
python app.py

# If CORS persists, check configuration:
cd backend
python -c "
from src.ai_tool_intelligence.main import create_app
app = create_app()
print('CORS configured in app creation')
"

# Alternative: Restart both services
pkill -f "python.*app.py"
pkill -f "npm.*start"
make start  # Or start manually
```

---

## 🔍 **Research and AI Issues**

### **❌ Research Fails with "Strands not available"**

**Symptoms**:
```bash
ModuleNotFoundError: No module named 'strands_agents'
ImportError: cannot import name 'Agent' from 'strands'
Research failed: Strands Agents not available
```

**✅ Solution**:
```bash
cd backend
source venv/bin/activate  # Make sure you're in venv

# Check Python version (must be 3.10+)
python --version

# Reinstall Strands packages
pip uninstall strands-agents strands-tools -y
pip install strands-agents>=0.1.0 strands-tools>=0.1.0

# Test imports
python -c "
from strands_agents import Agent
from strands_tools import EnhancedWebScraper, GitHubAnalyzer
print('✅ Strands packages working correctly')
"

# If still failing, check for import conflicts:
python -c "
import sys
print('Python path:')
for p in sys.path:
    print(f'  {p}')
    
try:
    import strands_agents
    print(f'strands_agents location: {strands_agents.__file__}')
except ImportError as e:
    print(f'strands_agents import error: {e}')
"
```

### **❌ "Research takes too long" or Timeout Issues**

**Symptoms**:
```bash
Research operation timed out after 300 seconds
Request timeout: No response from AI service
```

**✅ Solution**:
```bash
# Check AWS Bedrock connection
cd backend
python -c "
import boto3
import time

client = boto3.client('bedrock-runtime', region_name='us-east-1')
start = time.time()
try:
    response = client.invoke_model(
        modelId='us.anthropic.claude-3-5-sonnet-20241022-v2:0',
        body='{\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}],\"max_tokens\":10}',
        contentType='application/json'
    )
    end = time.time()
    print(f'✅ AWS response time: {end-start:.2f} seconds')
except Exception as e:
    print(f'❌ AWS error: {e}')
"

# If AWS is slow, check configuration:
# 1. Verify you're using us-east-1 region
# 2. Check your internet connection
# 3. Try different AWS region if needed

# Reduce research complexity for testing:
# Use single tool research instead of bulk operations
```

### **❌ "Invalid API response" or Malformed JSON**

**Symptoms**:
```bash
JSONDecodeError: Expecting value: line 1 column 1 (char 0)
Invalid response format from AI service
```

**✅ Solution**:
```bash
# Check Claude model ID and format
cd backend
python -c "
import boto3
import json

client = boto3.client('bedrock-runtime', region_name='us-east-1')

# Test minimal request
body = {
    'messages': [{'role': 'user', 'content': 'Say hello'}],
    'max_tokens': 50
}

try:
    response = client.invoke_model(
        modelId='us.anthropic.claude-3-5-sonnet-20241022-v2:0',
        body=json.dumps(body),
        contentType='application/json'
    )
    result = json.loads(response['body'].read())
    print('✅ Valid API response format')
    print(f'Response: {result}')
except Exception as e:
    print(f'❌ API response error: {e}')
"
```

---

## 🖥️ **Platform-Specific Issues**

### **🪟 Windows-Specific Issues**

#### **PowerShell Execution Policy**
```powershell
# Error: Execution of scripts is disabled on this system
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Verify policy
Get-ExecutionPolicy -List
```

#### **Windows Path Issues**
```batch
# Error: 'python' is not recognized
# Add Python to PATH or use full path:
C:\Python310\python.exe app.py

# Or install Python properly from python.org
```

#### **Windows Service Issues**
```powershell
# If Windows scripts fail, run manually:
cd backend
python app.py

# In separate terminal:
cd frontend
npm start
```

### **🍎 macOS-Specific Issues**

#### **Xcode Command Line Tools**
```bash
# Error: clang: error: no such file or directory
xcode-select --install

# Wait for installation to complete, then:
pip install -r requirements.txt
```

#### **Permission Issues**
```bash
# Error: Permission denied
sudo chown -R $(whoami) /usr/local/lib/node_modules
# Or use nvm to manage Node.js versions
```

### **🐧 Linux-Specific Issues**

#### **Missing Build Dependencies**
```bash
# Ubuntu/Debian:
sudo apt update
sudo apt install build-essential python3-dev python3-venv

# CentOS/RHEL:
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel

# Then reinstall packages:
pip install -r requirements.txt
```

---

## 🔄 **Recovery Procedures**

### **🚨 Complete Platform Reset**

When everything is broken and you need to start fresh:

```bash
# 1. Stop all processes
pkill -f "python.*app"
pkill -f "npm.*start"
pkill -f "react-scripts"

# 2. Clean Python environment
cd backend
rm -rf venv
rm -rf __pycache__
rm -rf src/ai_tool_intelligence/__pycache__
rm -f *.pyc

# 3. Clean frontend
cd ../frontend
rm -rf node_modules
rm -f package-lock.json

# 4. Clean tests
cd ../tests
rm -rf node_modules
rm -f package-lock.json

# 5. Reset database
cd ../backend
rm -f instance/ai_tools.db
rm -f ai_tools.db

# 6. Fresh installation
cd ..
make clean
make install-dev

# 7. Reconfigure
cp .env.example .env
# Edit .env with your AWS credentials

# 8. Start fresh
make start
```

### **🔧 Quick Health Check Script**

Create this script to diagnose issues quickly:

```bash
#!/bin/bash
# health-check.sh

echo "🔍 AI Tool Intelligence Platform Health Check"
echo "=============================================="

# Check Python version
echo "🐍 Python version:"
python --version || echo "❌ Python not found"

# Check Node version  
echo "📦 Node.js version:"
node --version || echo "❌ Node.js not found"

# Check if virtual environment exists
echo "🔧 Virtual environment:"
if [ -d "backend/venv" ]; then
    echo "✅ Virtual environment exists"
else
    echo "❌ Virtual environment missing"
fi

# Check if dependencies are installed
echo "📚 Python dependencies:"
cd backend
source venv/bin/activate 2>/dev/null || echo "❌ Cannot activate venv"
python -c "import flask; print('✅ Flask installed')" 2>/dev/null || echo "❌ Flask not installed"
python -c "import strands_agents; print('✅ Strands agents installed')" 2>/dev/null || echo "❌ Strands agents not installed"

# Check if frontend dependencies exist
echo "⚛️ Frontend dependencies:"
if [ -d "../frontend/node_modules" ]; then
    echo "✅ Frontend dependencies installed"
else
    echo "❌ Frontend dependencies missing"
fi

# Check AWS configuration
echo "☁️ AWS configuration:"
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    if grep -q "AWS_ACCESS_KEY_ID" .env; then
        echo "✅ AWS credentials configured"
    else
        echo "❌ AWS credentials missing in .env"
    fi
else
    echo "❌ .env file missing"
fi

# Check if ports are available
echo "🌐 Port availability:"
if ! lsof -i:5000 >/dev/null 2>&1; then
    echo "✅ Port 5000 available"
else
    echo "⚠️ Port 5000 in use"
fi

if ! lsof -i:3000 >/dev/null 2>&1; then
    echo "✅ Port 3000 available"
else
    echo "⚠️ Port 3000 in use"
fi

echo ""
echo "Health check complete! Fix any ❌ issues above."
```

---

## 📞 **Getting Additional Help**

### **🔍 Debug Information Collection**

When reporting issues, include this information:

```bash
# System information
echo "System: $(uname -a)"
echo "Python: $(python --version)"
echo "Node: $(node --version)"
echo "NPM: $(npm --version)"

# Package versions
pip list | grep -E "(flask|strands|boto3)"
npm list react react-scripts

# Log files
tail -50 backend/backend.log
tail -50 frontend/npm-debug.log
```

### **📚 Documentation References**
- **Complete Setup Guide**: `docs/setup/ONBOARDING_COMPLETE_GUIDE.md`
- **API Documentation**: `docs/api/endpoints.md`
- **Architecture Overview**: `docs/development/architecture.md`
- **Feature Documentation**: `docs/features/`

### **🆘 Support Channels**
- **GitHub Issues**: Report bugs with debug information
- **GitHub Discussions**: Ask questions and share solutions
- **Documentation**: Check `/docs/` directory for detailed guides

---

## ✅ **Prevention Checklist**

To avoid common issues:

- [ ] **Always use Python 3.10+** for Strands compatibility
- [ ] **Always use virtual environments** - never install globally
- [ ] **Keep AWS credentials secure** and properly configured
- [ ] **Enable Claude 3.5 Sonnet** in AWS Bedrock before research
- [ ] **Check port availability** before starting services
- [ ] **Use the health check script** regularly
- [ ] **Keep dependencies updated** with `make deps-update`
- [ ] **Run tests** before deploying with `make test`

**Remember**: Most issues are environment-related and can be resolved by following the specific solutions above. When in doubt, try the complete platform reset procedure.