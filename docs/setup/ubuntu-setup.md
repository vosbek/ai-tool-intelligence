# Complete Ubuntu Setup Guide for AI Tool Intelligence Platform

> **Enterprise-grade AI tool intelligence platform setup for Ubuntu 20.04+**

This guide provides detailed, step-by-step instructions for setting up the AI Tool Intelligence Platform on Ubuntu systems. Follow every step carefully to ensure a successful installation.

## 📋 Prerequisites Checklist

Before starting, ensure your Ubuntu machine meets these requirements:

- **Ubuntu 20.04 LTS** or later (22.04 LTS recommended)
- **8GB RAM minimum** (16GB recommended for enterprise features)
- **10GB free disk space** (for dependencies and data)
- **Internet connection** (for downloading dependencies and AWS access)
- **sudo access** (for installing system packages)

## 🚀 Complete Installation Process

### Step 1: System Update and Core Dependencies

#### 1.1 Update System Packages

```bash
# Update package lists and upgrade system
sudo apt update && sudo apt upgrade -y

# Install essential build tools and dependencies
sudo apt install -y curl wget git build-essential software-properties-common \
    apt-transport-https ca-certificates gnupg lsb-release
```

#### 1.2 Install Python 3.9+ (Required for Strands SDK)

**Ubuntu 20.04/22.04:**
```bash
# Python 3.9+ should be pre-installed, but let's verify and install if needed
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Verify installation
python3 --version
# Should output: Python 3.9.x or higher

pip3 --version
# Should output: pip 20.x or higher
```

**For older Ubuntu versions or if you need Python 3.11:**
```bash
# Add deadsnakes PPA for newer Python versions
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11 and related packages
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils

# Install pip for Python 3.11
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Verify installation
python3.11 --version
python3.11 -m pip --version

# Create symlinks (optional, for convenience)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
```

#### 1.3 Install Node.js 18+ (Required for React Frontend)

**Option A: Using NodeSource Repository (Recommended)**
```bash
# Add NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -

# Install Node.js
sudo apt install -y nodejs

# Verify installation
node --version
# Should output: v18.x.x or higher

npm --version
# Should output: 9.x.x or higher
```

**Option B: Using Snap Package Manager**
```bash
# Install Node.js via snap
sudo snap install node --classic

# Verify installation
node --version
npm --version
```

#### 1.4 Install Additional System Dependencies

```bash
# Install system dependencies for Python packages
sudo apt install -y libssl-dev libffi-dev libxml2-dev libxslt1-dev \
    zlib1g-dev libjpeg-dev libpng-dev

# Install database dependencies (for SQLite support)
sudo apt install -y sqlite3 libsqlite3-dev

# Install monitoring tools
sudo apt install -y htop iotop lsof net-tools

# Verify all installations
git --version
curl --version
wget --version
```

### Step 2: Download and Setup the Project

#### 2.1 Clone the Repository

```bash
# Navigate to your desired directory (e.g., /home/username/Projects)
cd ~
mkdir -p Projects
cd Projects

# Clone the repository
git clone https://github.com/yourusername/ai-tool-intelligence.git
cd ai-tool-intelligence

# Verify you have all files
ls -la
# Should show: backend/, frontend/, ubuntu/, windows/, scripts/, docs/, etc.
```

#### 2.2 Run the Automated Setup Script

```bash
# Make the setup script executable (if not already)
chmod +x ubuntu/setup.sh

# Run the complete setup
./ubuntu/setup.sh

# The setup script will:
# 1. Check all prerequisites
# 2. Create project structure
# 3. Set up Python virtual environment
# 4. Install Python dependencies
# 5. Set up React frontend
# 6. Create configuration files
# 7. Test the installation
```

**If you encounter permission issues:**
```bash
# Set proper ownership
sudo chown -R $USER:$USER ~/Projects/ai-tool-intelligence

# Run setup again
./ubuntu/setup.sh
```

### Step 3: Manual Setup (Alternative to Automated Setup)

If the automated setup fails, you can perform these steps manually:

#### 3.1 Backend Setup

```bash
# Navigate to backend directory
cd ~/Projects/ai-tool-intelligence/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify virtual environment
which python
# Should show: /home/username/Projects/ai-tool-intelligence/backend/venv/bin/python

# Upgrade pip and install build tools
python -m pip install --upgrade pip setuptools wheel

# Install AWS SDK first
pip install boto3 botocore

# Install Strands Agents SDK
pip install strands-agents strands-agents-tools

# Install remaining dependencies
pip install -r requirements.txt
```

#### 3.2 Frontend Setup

```bash
# Navigate to frontend directory
cd ~/Projects/ai-tool-intelligence/frontend

# Clear npm cache (prevents common issues)
npm cache clean --force

# Install dependencies
npm install

# Add proxy configuration to package.json (if not present)
node -e "
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
if (!pkg.proxy) {
    pkg.proxy = 'http://localhost:5000';
    fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2));
    console.log('Added proxy configuration');
}
"
```

### Step 4: Configure AWS Credentials

#### 4.1 Obtain AWS Credentials

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

#### 4.2 Enable Claude 3.5 Sonnet in AWS Bedrock

1. Go to **AWS Console** → **Bedrock** → **Model access**
2. Ensure you're in **us-west-2** region
3. Click **"Manage model access"**
4. Find **"Claude 3.5 Sonnet"** by Anthropic
5. Click **"Request access"** (usually instant approval)
6. Wait for status to change to **"Access granted"**

#### 4.3 Configure Credentials

```bash
# Navigate to backend directory
cd ~/Projects/ai-tool-intelligence/backend

# Copy environment template
cp .env.example .env

# Edit the environment file
nano .env

# Add your credentials (replace with your actual values):
```

In the `.env` file, add:
```bash
# AWS Configuration
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Application Configuration
DATABASE_URL=sqlite:///ai_tools.db
SECRET_KEY=your-secret-key-change-this-in-production

# Optional: Development settings
FLASK_ENV=development
FLASK_DEBUG=True
```

#### 4.4 Validate AWS Configuration

```bash
# Ensure you're in backend directory with virtual environment activated
cd ~/Projects/ai-tool-intelligence/backend
source venv/bin/activate

# Test AWS credentials (if you have an AWS validation script)
python -c "
import boto3
try:
    client = boto3.client('bedrock', region_name='us-west-2')
    response = client.list_foundation_models()
    print('✅ AWS credentials valid')
    print('✅ Bedrock access confirmed')
except Exception as e:
    print(f'❌ AWS validation failed: {e}')
"
```

### Step 5: Start the Application

#### 5.1 Using Ubuntu Scripts (Recommended)

```bash
# Navigate to project root
cd ~/Projects/ai-tool-intelligence

# Start the application
./ubuntu/start.sh

# This will:
# 1. Activate virtual environment
# 2. Start backend on port 5000
# 3. Start frontend on port 3000
# 4. Open browser automatically (if in desktop environment)
```

#### 5.2 Manual Start (Alternative)

**Terminal 1 - Backend:**
```bash
# Navigate to backend directory
cd ~/Projects/ai-tool-intelligence/backend

# Activate virtual environment
source venv/bin/activate

# Start backend
python app.py

# Should show:
# 🚀 Starting AI Tool Intelligence Platform
# * Running on http://0.0.0.0:5000
```

**Terminal 2 - Frontend:**
```bash
# Open new terminal
cd ~/Projects/ai-tool-intelligence/frontend

# Start frontend
npm start

# Should automatically open browser to http://localhost:3000
```

### Step 6: Verify Installation

#### 6.1 Test Core Functionality

1. **Open Browser** to `http://localhost:3000`
2. **Verify Homepage** loads without errors
3. **Check API Health**:
   ```bash
   curl http://localhost:5000/api/health
   # Should return: {"status": "healthy", "timestamp": "...", "version": "MVP"}
   ```

#### 6.2 Check System Status

```bash
# Use the status script
./ubuntu/status.sh

# Should show:
# - Backend running status
# - Frontend running status
# - Health check results
# - System resources
```

#### 6.3 Add Your First Tool

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

## 🛠️ Ubuntu-Specific Tools and Scripts

### Management Scripts

The `ubuntu/` directory contains comprehensive management tools:

```bash
# Complete system setup (run once)
./ubuntu/setup.sh

# Start application services
./ubuntu/start.sh

# Stop all services
./ubuntu/stop.sh

# Check system status
./ubuntu/status.sh

# View application logs
./ubuntu/logs.sh [backend|frontend|both|errors|live]

# Create system backup
./ubuntu/backup.sh

# Manage research operations
./ubuntu/research.sh [status|failed|retry|process|category|scheduler]

# Reset to clean state
./ubuntu/reset.sh
```

### Script Usage Examples

```bash
# View real-time logs
./ubuntu/logs.sh live

# Show only error messages
./ubuntu/logs.sh errors

# Process specific tools
./ubuntu/research.sh process "Cursor,GitHub Copilot"

# Process tools by category
./ubuntu/research.sh category "Agentic IDEs"

# Create compressed backup
./ubuntu/backup.sh

# Reset and reinstall
./ubuntu/reset.sh
```

### System Service Installation (Optional)

For production environments, you can install as a systemd service:

```bash
# Create service file
sudo tee /etc/systemd/system/ai-tool-intelligence.service > /dev/null << EOF
[Unit]
Description=AI Tool Intelligence Platform
After=network.target

[Service]
Type=forking
User=$USER
Group=$USER
WorkingDirectory=$HOME/Projects/ai-tool-intelligence
ExecStart=$HOME/Projects/ai-tool-intelligence/ubuntu/start.sh
ExecStop=$HOME/Projects/ai-tool-intelligence/ubuntu/stop.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ai-tool-intelligence
sudo systemctl start ai-tool-intelligence

# Check status
sudo systemctl status ai-tool-intelligence
```

## 🐛 Troubleshooting Guide

### Common Installation Issues

#### 1. Python Installation Problems

**Error: "python3: command not found"**
```bash
# Install Python
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Verify installation
python3 --version
```

**Error: "Python 3.9+ required"**
```bash
# Check current version
python3 --version

# Install newer Python if needed
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip
```

#### 2. Virtual Environment Issues

**Error: "virtual environment creation failed"**
```bash
# Install venv module
sudo apt install python3-venv

# Try creating again
cd ~/Projects/ai-tool-intelligence/backend
python3 -m venv venv
```

**Error: "pip installation fails"**
```bash
# Upgrade pip and try again
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel

# If SSL errors persist
pip install --trusted-host pypi.org --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org -r requirements.txt
```

#### 3. Node.js and npm Issues

**Error: "node: command not found"**
```bash
# Install Node.js via NodeSource
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version
npm --version
```

**Error: "npm install fails with permission errors"**
```bash
# Fix npm permissions
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Try installation again
cd ~/Projects/ai-tool-intelligence/frontend
npm install
```

#### 4. AWS Configuration Issues

**Error: "AWS credentials validation failed"**
```bash
# Debug credentials
echo "AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID"
echo "AWS_SECRET_ACCESS_KEY: $([ -n "$AWS_SECRET_ACCESS_KEY" ] && echo "Set" || echo "Not set")"
echo "AWS_REGION: $AWS_REGION"

# Test credentials manually
aws sts get-caller-identity  # If AWS CLI is installed
```

**Error: "Bedrock access denied"**
1. Go to AWS Console → Bedrock → Model access
2. Ensure you're in **us-west-2** region
3. Request access to Claude 3.5 Sonnet
4. Wait for approval

#### 5. Port Conflicts

**Error: "Port 3000/5000 already in use"**
```bash
# Find processes using the ports
sudo lsof -i :3000
sudo lsof -i :5000

# Kill the processes (replace PID with actual process ID)
sudo kill -9 PID

# Or use the stop script
./ubuntu/stop.sh
```

#### 6. Permission Issues

**Error: "Permission denied" errors**
```bash
# Fix ownership
sudo chown -R $USER:$USER ~/Projects/ai-tool-intelligence

# Make scripts executable
chmod +x ~/Projects/ai-tool-intelligence/ubuntu/*.sh

# Fix virtual environment permissions
sudo chown -R $USER:$USER ~/Projects/ai-tool-intelligence/backend/venv
```

### Application Runtime Issues

#### 1. Research Operations Failing

**Symptoms:** Tools research returns errors or no data
```bash
# Check AWS credentials
cd ~/Projects/ai-tool-intelligence/backend
source venv/bin/activate
python -c "import boto3; print('AWS SDK working')"

# Check Strands SDK
python -c "from strands import Agent; print('Strands SDK working')"

# Check backend logs
./ubuntu/logs.sh backend
```

#### 2. Frontend Not Loading

**Symptoms:** Browser shows connection errors
```bash
# Check if services are running
./ubuntu/status.sh

# Check backend health
curl http://localhost:5000/api/health

# Check frontend
curl http://localhost:3000

# Restart services
./ubuntu/stop.sh
./ubuntu/start.sh
```

#### 3. Database Issues

**Symptoms:** Database errors in logs
```bash
# Reset database
cd ~/Projects/ai-tool-intelligence/backend
source venv/bin/activate
rm -f ai_tools.db
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database recreated')
"
```

### Performance Issues

#### 1. Slow Research Operations

```bash
# Monitor system resources
htop

# Check disk usage
df -h

# Monitor network
sudo netstat -tuln

# Reduce concurrent operations in config
nano ~/Projects/ai-tool-intelligence/backend/config.json
# Set "max_concurrent_tools": 1
```

#### 2. High Memory Usage

```bash
# Check memory usage
free -h

# Monitor processes
ps aux | grep python
ps aux | grep node

# Restart if needed
./ubuntu/stop.sh
./ubuntu/start.sh
```

## 📊 System Monitoring and Maintenance

### Health Checks

**API Health Check:**
```bash
curl http://localhost:5000/api/health
```

**System Status:**
```bash
./ubuntu/status.sh
```

**Real-time Monitoring:**
```bash
# Monitor logs
./ubuntu/logs.sh live

# Monitor system resources
htop
iotop
```

### Log Management

**Log Locations:**
- Application logs: `ubuntu/logs/backend.log`, `ubuntu/logs/frontend.log`
- System logs: `/var/log/syslog`

**Log Rotation (Optional):**
```bash
# Create logrotate configuration
sudo tee /etc/logrotate.d/ai-tool-intelligence > /dev/null << EOF
/home/$USER/Projects/ai-tool-intelligence/ubuntu/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF
```

### Backup and Restore

**Create Backup:**
```bash
./ubuntu/backup.sh
```

**Restore from Backup:**
```bash
# Stop services
./ubuntu/stop.sh

# Restore database
cp backend/backups/backup_YYYYMMDD_HHMMSS/ai_tools.db backend/

# Restore configuration
cp backend/backups/backup_YYYYMMDD_HHMMSS/config.json backend/

# Start services
./ubuntu/start.sh
```

### Updates and Maintenance

**Update System Packages:**
```bash
sudo apt update && sudo apt upgrade -y
```

**Update Python Dependencies:**
```bash
cd ~/Projects/ai-tool-intelligence/backend
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

**Update Frontend Dependencies:**
```bash
cd ~/Projects/ai-tool-intelligence/frontend
npm update
```

## 🚀 Next Steps

After successful installation:

1. **Read the User Guide:** See `docs/USER_GUIDE.md`
2. **Configure Monitoring:** Set up system monitoring and alerts
3. **Add Tools:** Start adding AI tools to your intelligence database
4. **Explore Analytics:** Use the competitive analysis features
5. **Schedule Research:** Set up automated research operations
6. **Create Backups:** Establish regular backup routines

## 📞 Getting Help

If you encounter issues not covered in this guide:

1. **Check GitHub Issues:** [Repository Issues](https://github.com/yourusername/ai-tool-intelligence/issues)
2. **Review Logs:** Use `./ubuntu/logs.sh` to check application logs
3. **System Status:** Run `./ubuntu/status.sh` for diagnostic information
4. **Ubuntu Community:** Ask on Ubuntu forums for system-specific issues
5. **Professional Support:** Contact for enterprise support options

## 🔧 Ubuntu-Specific Optimizations

### Performance Tuning

**Increase File Descriptors:**
```bash
# Add to ~/.bashrc
echo 'ulimit -n 65536' >> ~/.bashrc
source ~/.bashrc
```

**Optimize TCP Settings:**
```bash
# Add to /etc/sysctl.conf (requires sudo)
sudo tee -a /etc/sysctl.conf > /dev/null << EOF
net.core.somaxconn = 65536
net.ipv4.tcp_max_syn_backlog = 65536
net.core.netdev_max_backlog = 5000
EOF

sudo sysctl -p
```

### Security Hardening

**Firewall Configuration:**
```bash
# Enable UFW firewall
sudo ufw enable

# Allow SSH (if using remote access)
sudo ufw allow ssh

# Allow application ports
sudo ufw allow 3000/tcp comment 'AI Tool Intelligence Frontend'
sudo ufw allow 5000/tcp comment 'AI Tool Intelligence Backend'

# Check status
sudo ufw status
```

**Automatic Security Updates:**
```bash
# Install unattended upgrades
sudo apt install unattended-upgrades

# Configure automatic updates
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

**🎉 Congratulations!** You now have a fully functional AI Tool Intelligence Platform running on Ubuntu with enterprise-grade features including competitive analysis, real-time monitoring, comprehensive logging, and automated management scripts.

Start by adding your first AI tool and exploring the powerful intelligence capabilities!