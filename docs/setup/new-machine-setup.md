# 🖥️ New Machine Setup Guide - AI Tool Intelligence Platform

> **Complete setup guide tested and validated on fresh systems**

This guide provides **step-by-step instructions** for setting up the AI Tool Intelligence Platform on a new machine, with **validation at each step**.

---

## 🎯 **Quick Setup Summary**

**Total Time**: ~20-30 minutes  
**Prerequisites**: Administrator access to install software  
**Result**: Fully functional platform ready for use

---

## 📋 **Pre-Installation Checklist**

### System Requirements
- [ ] **Operating System**: Windows 10/11, macOS, or Linux
- [ ] **Python**: 3.8+ (3.12 recommended)
- [ ] **Node.js**: 16+ (Latest LTS recommended)
- [ ] **Git**: Latest version
- [ ] **Internet**: Stable connection for package downloads
- [ ] **Disk Space**: ~2GB free space
- [ ] **Ports**: 3000 and 5000 available

### Administrator Privileges
- [ ] Can install Python packages
- [ ] Can install Node.js packages
- [ ] Can modify system PATH if needed
- [ ] Can create directories and files

---

## 🚀 **Step 1: System Dependencies**

### 1.1 Install Python (if not present)
```bash
# Check current version
python3 --version

# If < 3.8, install latest Python from python.org
# Ensure 'Add to PATH' is checked during installation
```

### 1.2 Install Node.js (if not present)
```bash
# Check current version
node --version
npm --version

# If not installed, download from nodejs.org
# Use LTS version for stability
```

### 1.3 Verify Git Installation
```bash
# Check git version
git --version

# If not installed, download from git-scm.com
```

**✅ Validation**:
```bash
python3 --version  # Should show 3.8+
node --version     # Should show 16+
npm --version      # Should show 8+
git --version      # Should show 2.x+
```

---

## 📦 **Step 2: Clone and Setup Repository**

### 2.1 Clone Repository
```bash
# Clone the repository
git clone <repository-url> ai-tool-intelligence
cd ai-tool-intelligence

# Verify structure
ls -la
# Should see: backend/, frontend/, scripts/, *.md files
```

### 2.2 Create Required Directories
```bash
# Create working directories
mkdir -p logs backups data temp

# Verify creation
ls -la
# Should see: logs/, backups/, data/, temp/
```

**✅ Validation**: Repository cloned with correct structure

---

## 🐍 **Step 3: Backend Setup**

### 3.1 Navigate to Backend
```bash
cd backend
ls -la
# Should see: app.py, requirements.txt, config/, models/, etc.
```

### 3.2 Install Python Dependencies
```bash
# Option A: Use system packages (recommended for quick setup)
pip3 install --break-system-packages flask flask-cors flask-sqlalchemy python-dotenv requests beautifulsoup4 boto3 botocore psutil

# Option B: Use virtual environment (recommended for production)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3.3 Test Backend Installation
```bash
# Test imports
python3 -c "import flask, flask_cors, flask_sqlalchemy; print('✅ Core packages imported successfully')"

# Test basic startup (will exit quickly due to missing config)
python3 -c "from app import app; print('✅ App imports successfully')"
```

**✅ Validation**: All imports work without errors

---

## ⚛️ **Step 4: Frontend Setup**

### 4.1 Navigate to Frontend
```bash
cd ../frontend
ls -la
# Should see: package.json, src/, public/
```

### 4.2 Install Node Dependencies
```bash
# Install all dependencies
npm install

# This will take 2-5 minutes depending on connection speed
```

### 4.3 Verify Package Installation
```bash
# Check key dependencies
npm list react react-dom axios --depth=0

# Should show versions without errors
```

**✅ Validation**: Dependencies installed successfully

---

## 🔧 **Step 5: Configuration**

### 5.1 Backend Configuration
```bash
cd ../backend

# Create environment file (optional for basic setup)
cp .env.example .env 2>/dev/null || echo "# Basic setup - no .env needed for testing" > .env

# Verify configuration files exist
ls -la config/
ls -la models/
```

### 5.2 Frontend Configuration
```bash
cd ../frontend

# Verify proxy configuration in package.json
grep -A 1 '"proxy"' package.json
# Should show: "proxy": "http://localhost:5000"
```

**✅ Validation**: Configuration files in place

---

## 🧪 **Step 6: Initial Testing**

### 6.1 Test Backend Startup
```bash
cd ../backend

# Start backend with AWS validation skipped
SKIP_AWS_VALIDATION=1 python3 app.py &

# Wait a few seconds for startup
sleep 5

# Test health endpoint
curl http://localhost:5000/api/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "...",
#   "version": "MVP"
# }

# Stop backend for now
pkill -f "python3 app.py"
```

### 6.2 Test Frontend Startup
```bash
cd ../frontend

# Start frontend (will take ~30 seconds)
npm start &

# Wait for startup
sleep 30

# Test frontend accessibility
curl http://localhost:3000

# Should return HTML content
# Stop frontend for now
pkill -f "npm start"
```

**✅ Validation**: Both backend and frontend start successfully

---

## 🎯 **Step 7: Complete System Test**

### 7.1 Run Comprehensive Test
```bash
cd ..

# Run the complete test suite
python3 test_application.py

# Expected output:
# ✅ Health endpoint working
# ✅ Tools endpoint working (5 tools found)
# ✅ Categories endpoint working (10 categories found)
# ✅ Research endpoint working (expected error without strands packages)
# ✅ CORS configured correctly
# 🎉 OVERALL STATUS: ✅ READY FOR USE
```

### 7.2 Manual Verification
```bash
# Start both services
cd backend
SKIP_AWS_VALIDATION=1 nohup python3 app.py > backend.log 2>&1 &

cd ../frontend
nohup npm start > frontend.log 2>&1 &

# Wait for both to start
sleep 30

# Test API endpoints
curl http://localhost:5000/api/health
curl http://localhost:5000/api/tools
curl http://localhost:5000/api/categories

# Test frontend
curl http://localhost:3000

# All should return successful responses
```

**✅ Validation**: Complete system working

---

## 🔗 **Step 8: Access and Verification**

### 8.1 Access the Application
1. **Open browser** to `http://localhost:3000`
2. **Verify interface loads** - should see tool management interface
3. **Test basic functionality**:
   - View tools list
   - Try adding a new tool
   - Test research button (will show expected error)

### 8.2 Backend API Access
1. **API Base URL**: `http://localhost:5000/api`
2. **Health Check**: `http://localhost:5000/api/health`
3. **Tools API**: `http://localhost:5000/api/tools`
4. **Categories API**: `http://localhost:5000/api/categories`

**✅ Validation**: Full application accessible and functional

---

## 🛠️ **Step 9: Optional Enhancements**

### 9.1 Install Strands Packages (for full functionality)
```bash
# Install official packages when available
pip3 install --break-system-packages strands-agents strands-tools

# Or use development versions
# pip3 install --break-system-packages git+https://github.com/strands/agents.git
```

### 9.2 AWS Configuration (for AI research)
```bash
# Configure AWS credentials
nano backend/.env

# Add:
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=your-key
# AWS_SECRET_ACCESS_KEY=your-secret

# Test AWS connection
cd backend
python3 aws_credential_validator.py
```

### 9.3 Windows Scripts (if on Windows)
```bash
# Use PowerShell scripts for management
./windows/Start.ps1    # Start platform
./windows/Stop.ps1     # Stop platform
./windows/Status.ps1   # Check status
./windows/Logs.ps1     # View logs
```

---

## 📁 **Directory Structure After Setup**

```
ai-tool-intelligence/
├── 📂 backend/
│   ├── 🐍 app.py                     # Main Flask application
│   ├── 📋 requirements.txt           # Python dependencies
│   ├── 🗃️ ai_tools.db               # SQLite database (auto-created)
│   ├── 📄 backend.log                # Application logs
│   └── 📁 venv/ (if using virtualenv)
├── 📂 frontend/
│   ├── ⚛️ package.json               # Node.js dependencies
│   ├── 📁 node_modules/              # Installed packages
│   ├── 📁 src/App.js                 # React application
│   └── 📄 frontend.log               # Frontend logs
├── 📂 logs/                          # System logs
├── 📂 backups/                       # Database backups
├── 📂 scripts/                       # Management scripts
├── 🧪 test_application.py            # Test suite
├── 📖 TROUBLESHOOTING.md             # Issue resolution
└── 📚 Documentation files...
```

---

## 🎉 **Setup Complete!**

Your AI Tool Intelligence Platform is now ready to use:

### ✅ **What's Working**
- **Backend API**: Full REST API with tool management
- **Frontend Interface**: React-based tool management UI
- **Database**: SQLite with sample data
- **Error Handling**: Graceful error responses
- **CORS**: Properly configured for frontend-backend communication
- **Health Monitoring**: System status endpoints

### ⚠️ **What Needs Configuration**
- **Strands Packages**: For AI-powered research (optional)
- **AWS Credentials**: For Claude AI integration (optional)
- **Production Setup**: For deployment (optional)

### 🔄 **Next Steps**
1. **Start using the platform**: Add tools and explore features
2. **Configure AI features**: Set up AWS and Strands packages
3. **Customize**: Modify for your specific needs
4. **Scale**: Deploy to production environment

---

## 🆘 **Need Help?**

**Issues during setup?** → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)  
**API documentation?** → [API_DOCUMENTATION.md](API_DOCUMENTATION.md)  
**Feature questions?** → [FEATURE_PARITY.md](FEATURE_PARITY.md)  
**Daily operations?** → [windows/README.md](windows/README.md)

---

## 🔄 **Regular Maintenance**

### Daily Operations
```bash
# Start platform
cd backend && SKIP_AWS_VALIDATION=1 python3 app.py &
cd frontend && npm start &

# Stop platform
pkill -f "python3 app.py"
pkill -f "npm start"

# Check health
python3 test_application.py
```

### Weekly Maintenance
```bash
# Update dependencies
cd backend && pip install --upgrade -r requirements.txt
cd frontend && npm update

# Clean logs
truncate -s 0 backend.log frontend.log

# Backup database
cp backend/ai_tools.db backups/backup_$(date +%Y%m%d).db
```

---

**📅 Last Updated**: June 14, 2025  
**🧪 Tested On**: Linux (WSL2), Node.js 18+, Python 3.12  
**✅ Validation**: Complete setup process verified working