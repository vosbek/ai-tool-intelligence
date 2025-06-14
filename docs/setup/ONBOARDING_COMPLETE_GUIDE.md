# 🚀 AI Tool Intelligence Platform - Complete Onboarding Guide

> **New Machine Setup - Zero to Running in 15 Minutes**

This guide will take you from a fresh machine to a fully functional AI Tool Intelligence Platform with **zero errors** and **complete understanding** of what you're installing.

---

## 📋 **What You're Installing**

### **🎯 Platform Overview**
You're setting up an **enterprise-grade AI tool intelligence platform** that:

- **🔬 Automatically researches** AI developer tools using 13 specialized agents
- **📊 Provides competitive analysis** and market intelligence
- **🚨 Monitors tool changes** in real-time with smart alerts
- **🛠️ Offers admin capabilities** for data management and system monitoring
- **⚡ Processes tools in bulk** with intelligent queuing and progress tracking

### **🏗️ Architecture You'll Have Running**
```
Frontend (React)     ←→ Backend (Flask)     ←→ AWS Bedrock
http://localhost:3000    http://localhost:5000    Claude 3.5 Sonnet
     ↓                        ↓                         ↓
Tool Management UI      50+ API Endpoints         AI Research Engine
Admin Dashboard         SQLite Database           Competitive Analysis
Real-time Monitoring    Background Processing     Market Intelligence
```

---

## 🎯 **Prerequisites Check**

### **❗ REQUIRED (Installation will fail without these)**

1. **Python 3.10 or Higher**
   ```bash
   python --version  # Must show 3.10.x or higher
   # If not installed: https://python.org/downloads
   ```

2. **Node.js 18 or Higher**
   ```bash
   node --version  # Must show v18.x.x or higher
   # If not installed: https://nodejs.org/download
   ```

3. **Git**
   ```bash
   git --version  # Must work
   # If not installed: https://git-scm.com/downloads
   ```

4. **AWS Account with Bedrock Access**
   - AWS Account: https://aws.amazon.com/free
   - **⚠️ CRITICAL**: Enable Claude 3.5 Sonnet in AWS Bedrock console (us-east-1 region)
   - Cost: ~$0.01-$0.10 per tool research

### **🔧 Platform-Specific Notes**

#### **Windows Users**
- **PowerShell 5.1+** (built into Windows 10/11)
- **Visual Studio Build Tools** for native modules: https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019

#### **macOS Users**
- **Xcode Command Line Tools**: `xcode-select --install`
- **Homebrew** (recommended): https://brew.sh

#### **Linux Users**
- **build-essential**: `sudo apt update && sudo apt install build-essential`

---

## 🚀 **Installation - Choose Your Path**

### **🔥 Option 1: Express Setup (Recommended)**

#### **Windows PowerShell**
```powershell
# 1. Clone repository
git clone https://github.com/yourusername/ai-tool-intelligence.git
cd ai-tool-intelligence

# 2. Run express setup
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\scripts\setup\Setup.ps1

# 3. Configure AWS credentials (when prompted)
# Script will open .env file for editing

# 4. Start platform
make start
```

#### **macOS/Linux Terminal**
```bash
# 1. Clone repository
git clone https://github.com/yourusername/ai-tool-intelligence.git
cd ai-tool-intelligence

# 2. Run express setup
chmod +x scripts/setup/install.sh
./scripts/setup/install.sh

# 3. Configure AWS credentials
cp .env.example .env
nano .env  # Edit with your AWS credentials

# 4. Start platform
make start
```

### **🔧 Option 2: Manual Setup (If Express Fails)**

<details>
<summary>Click to expand manual setup steps</summary>

#### **Step 1: Environment Setup**
```bash
# Create Python virtual environment
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements-dev.txt
```

#### **Step 2: Frontend Setup**
```bash
# Install frontend dependencies
cd ../frontend
npm install

# Install testing dependencies
cd ../tests
npm install
npx playwright install --with-deps
```

#### **Step 3: Configuration**
```bash
# Create environment file
cd ..
cp .env.example .env

# Edit with your credentials
# Windows: notepad .env
# macOS/Linux: nano .env
```

#### **Step 4: Database Setup**
```bash
cd backend
python -c "from src.ai_tool_intelligence.models.database import db; db.create_all()"
```

</details>

---

## 🔑 **AWS Configuration - Critical Step**

### **🎯 What You Need**
1. **AWS Access Key ID**
2. **AWS Secret Access Key**
3. **AWS Region**: `us-east-1` (required for Claude 3.5 Sonnet)

### **📝 How to Get AWS Credentials**

#### **Option A: AWS CLI (Recommended)**
```bash
# Install AWS CLI: https://aws.amazon.com/cli/
aws configure
# Enter your credentials when prompted
```

#### **Option B: Environment File**
Edit `.env` file with:
```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-1
```

#### **Option C: IAM Role (Production)**
For production environments, use IAM roles instead of access keys.

### **🚨 Enable Claude 3.5 Sonnet in AWS Bedrock**

**⚠️ CRITICAL**: Without this step, research will fail!

1. **Go to AWS Bedrock Console**: https://console.aws.amazon.com/bedrock
2. **Switch to us-east-1 region** (top-right dropdown)
3. **Click "Model access"** in left sidebar
4. **Click "Manage model access"**
5. **Find "Claude 3.5 Sonnet"** and check the box
6. **Click "Save changes"**
7. **Wait for "Access granted"** status (may take 2-3 minutes)

---

## ✅ **Validation - Ensure Everything Works**

### **🧪 Step 1: Basic Validation**
```bash
# Check Python version
python --version  # Should show 3.10+

# Check Node version
node --version    # Should show v18+

# Check if backend starts
cd backend
python src/ai_tool_intelligence/main.py
# Should show: "✅ Flask app running on http://localhost:5000"
# Press Ctrl+C to stop
```

### **🧪 Step 2: Frontend Validation**
```bash
# Check if frontend builds
cd frontend
npm run build
# Should complete without errors

# Start frontend (in separate terminal)
npm start
# Should open http://localhost:3000 automatically
```

### **🧪 Step 3: AWS Connection Test**
```bash
# Test AWS credentials
cd backend
python -c "
import boto3
try:
    client = boto3.client('bedrock-runtime', region_name='us-east-1')
    print('✅ AWS connection successful')
except Exception as e:
    print(f'❌ AWS connection failed: {e}')
"
```

### **🧪 Step 4: Full Platform Test**
```bash
# Start complete platform
make start

# Wait 30 seconds, then check:
# Frontend: http://localhost:3000 (should load interface)
# Backend: http://localhost:5000/api/health (should return {"status": "healthy"})
```

---

## 🎉 **First Use - Your First AI Tool Research**

### **🎯 Test the Complete Workflow**

1. **Open Frontend**: http://localhost:3000
2. **Add a Test Tool**:
   ```
   Name: Cursor
   Category: Code Assistants
   Website: https://cursor.sh
   Description: AI-first code editor
   ```
3. **Click "Save Tool"** - should appear in table
4. **Click "Research" button** - starts AI analysis
5. **Watch Progress**:
   - Progress bar appears at top
   - Research queue shows in bottom-right
   - Browser notification when complete (if enabled)
6. **View Results**: Click "View" to see comprehensive analysis

### **🔍 What the Research Provides**
- **GitHub Statistics**: Stars, forks, activity, releases
- **Company Information**: Funding, team size, leadership
- **Pricing Analysis**: Tiers, models, competitive positioning
- **Feature Extraction**: Capabilities, integrations, platform support
- **Market Intelligence**: Competitors, positioning, social sentiment
- **Technical Details**: Tech stack, documentation quality, developer experience

---

## 🛠️ **Platform Capabilities Overview**

### **🎯 Core Features You Now Have**

#### **1. Tool Management**
- ✅ **Add/Edit/Delete** AI tools with comprehensive metadata
- ✅ **Category Organization** with hierarchical structure
- ✅ **Bulk Operations** for mass processing
- ✅ **Search and Filtering** across all tool attributes
- ✅ **Data Export** in multiple formats (JSON, CSV)

#### **2. AI-Powered Research**
- ✅ **13 Specialized Research Agents** for comprehensive analysis
- ✅ **Automated Data Collection** from multiple sources
- ✅ **Quality Scoring** with confidence metrics
- ✅ **Bulk Processing** with intelligent queuing
- ✅ **Progress Tracking** with real-time updates

#### **3. Competitive Intelligence**
- ✅ **Market Analysis** with positioning insights
- ✅ **Trend Tracking** across technology categories
- ✅ **Competitive Benchmarking** and comparative analysis
- ✅ **Investment Tracking** and funding analysis
- ✅ **Social Sentiment** monitoring across platforms

#### **4. Enterprise Administration**
- ✅ **Admin Dashboard** with system health metrics
- ✅ **Data Quality Management** with review workflows
- ✅ **System Monitoring** with performance tracking
- ✅ **Audit Trails** for all platform activities
- ✅ **Bulk Data Operations** for enterprise-scale management

#### **5. Real-Time Monitoring**
- ✅ **Change Detection** for tool updates and pricing changes
- ✅ **Alert System** with configurable notifications
- ✅ **System Health** monitoring with automated diagnostics
- ✅ **Performance Analytics** with optimization insights

### **🔌 API Capabilities**
The platform provides **50+ REST API endpoints** for:
- Tool management and CRUD operations
- Research workflow automation
- Competitive analysis data access
- Admin operations and monitoring
- Data export and integration capabilities

---

## 📖 **Quick Reference - Daily Usage**

### **🚀 Starting the Platform**
```bash
make start
# Opens frontend at http://localhost:3000
# Backend API at http://localhost:5000
```

### **🔬 Research Operations**
```bash
# Research specific tool
make research TOOL="GitHub Copilot"

# Bulk research multiple tools
make research-bulk TOOLS="Cursor,GitHub Copilot,TabNine"

# Check research queue status
make research-status
```

### **🧪 Testing and Quality**
```bash
# Run all tests
make test

# Check code quality
make lint

# Format code
make format
```

### **📊 Monitoring and Maintenance**
```bash
# Check system health
make monitor

# View logs
make logs

# Create backup
make backup

# Clean temporary files
make clean
```

---

## 🆘 **Troubleshooting - Common Issues & Solutions**

### **❌ "Python not found" or "Node not found"**
**Solution**: Install required versions:
- Python 3.10+: https://python.org/downloads
- Node.js 18+: https://nodejs.org/download

### **❌ "AWS credentials not configured"**
**Solution**: Configure AWS credentials:
```bash
aws configure
# OR edit .env file with your credentials
```

### **❌ "Claude 3.5 Sonnet not available"**
**Solution**: Enable model access in AWS Bedrock:
1. Go to AWS Bedrock console → us-east-1 region
2. Model access → Manage model access
3. Enable Claude 3.5 Sonnet → Save changes

### **❌ "Permission denied" on scripts**
**Solution**: Make scripts executable:
```bash
chmod +x scripts/setup/install.sh
chmod +x scripts/development/start.sh
```

### **❌ "Port already in use"**
**Solution**: Kill existing processes:
```bash
# Kill backend processes
pkill -f "python.*main.py"

# Kill frontend processes  
pkill -f "npm.*start"

# Then restart
make start
```

### **❌ "Research fails with Strands error"**
**Solutions**:
1. **Check Python version**: Must be 3.10+
2. **Reinstall Strands packages**:
   ```bash
   pip uninstall strands-agents strands-agents-tools
   pip install strands-agents>=0.1.0 strands-agents-tools>=0.1.0
   ```
3. **Check AWS credentials and Bedrock access**

### **❌ "Frontend won't load"**
**Solution**: Check dependencies and rebuild:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### **❌ "Database errors"**
**Solution**: Reset database:
```bash
cd backend
rm -f instance/ai_tools.db
python -c "from src.ai_tool_intelligence.models.database import db; db.create_all()"
```

---

## 🎯 **Next Steps - What to Do After Setup**

### **🚀 Immediate Actions**
1. **✅ Test the platform** with your first tool research
2. **✅ Explore the admin interface** (add header: `X-Admin-User: admin`)
3. **✅ Review the API documentation** at `docs/api/endpoints.md`
4. **✅ Set up monitoring** alerts for your tools

### **📈 Advanced Usage**
1. **Bulk Import Tools**: Use the bulk operations for large datasets
2. **API Integration**: Connect external systems via the REST API
3. **Custom Research**: Configure specialized research workflows
4. **Competitive Monitoring**: Set up automated competitive tracking

### **🔧 Customization**
1. **Configure Research Agents**: Adjust the 13 research tools for your needs
2. **Set Up Alerts**: Configure change detection and notifications
3. **Admin Workflows**: Set up data review and approval processes
4. **Integration Setup**: Connect to external data sources and systems

---

## 📞 **Support & Resources**

### **📚 Documentation**
- **Complete API Reference**: `docs/api/endpoints.md`
- **Admin Guide**: `docs/features/admin-interface.md`
- **Troubleshooting**: `docs/setup/troubleshooting.md`
- **Architecture Overview**: `docs/development/architecture.md`

### **🆘 Getting Help**
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check the comprehensive docs in `/docs/`
- **Code Examples**: Review test files for usage patterns
- **Community**: Join discussions in GitHub Discussions

### **🔗 Key Links**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Health**: http://localhost:5000/api/health
- **Admin Interface**: Add header `X-Admin-User: admin` to any request

---

## ✅ **Success Checklist**

- [ ] **Prerequisites installed** (Python 3.10+, Node 18+, Git)
- [ ] **Repository cloned** and setup script completed
- [ ] **AWS credentials configured** and Bedrock access enabled
- [ ] **Platform starts successfully** (frontend + backend)
- [ ] **First tool researched** and results displayed
- [ ] **API endpoints accessible** and returning data
- [ ] **Admin interface tested** (with admin header)
- [ ] **Documentation reviewed** and bookmarked
- [ ] **Troubleshooting guide** understood and available

**🎉 Congratulations! You now have a fully functional AI Tool Intelligence Platform running on your machine!**

---

*Need help? Check the troubleshooting section above or review the comprehensive documentation in the `/docs/` directory.*