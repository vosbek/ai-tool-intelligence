# AI Tool Intelligence Platform

> **Enterprise-grade AI tool intelligence platform with automated research, competitive analysis, and comprehensive monitoring capabilities**

A complete competitive intelligence platform that automatically researches AI developer tools, tracks market changes, analyzes competitive landscapes, and provides real-time business intelligence with advanced monitoring and admin capabilities.

## 🚀 Quick Start (Windows Enterprise)

### Automated Setup (Recommended)
```powershell
# Clone repository
git clone <repository-url>
cd ai-tool-intelligence

# Run automated Windows setup
windows\setup-windows.bat

# Start application
windows\start-windows.bat
```

### Manual Setup (Alternative)
```powershell
# Backend setup
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ..\frontend
npm install

# Configure and start
copy backend\.env.example backend\.env
# Edit backend\.env with AWS credentials
windows\start-windows.bat
```

## 🌐 Access Points

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health
- **System Status**: http://localhost:5000/api/system/status

## 🎯 Enterprise Platform Capabilities

### 🔍 **Intelligent Research & Monitoring**
- **Automated Research**: Strands Agents analyze GitHub repos, pricing, company data, documentation, and integrations
- **Real-time Change Detection**: Continuous monitoring of tool updates, pricing changes, and market movements  
- **Quality Scoring**: AI-powered data validation and quality assessment for all collected information
- **Batch Processing**: Systematic competitive monitoring with configurable schedules and priorities

### 📊 **Advanced Competitive Intelligence** 
- **Market Analysis**: Comprehensive competitive landscape analysis with positioning and trend tracking
- **Trend Forecasting**: AI-powered prediction of market movements and technology adoption patterns
- **Competitive Metrics**: Multi-dimensional scoring system for feature analysis, popularity tracking, and market maturity
- **Strategic Insights**: Automated identification of market opportunities and competitive threats

### 🚨 **Enterprise Monitoring & Alerts**
- **Change Alert System**: Configurable notifications for pricing changes, new releases, and competitive moves
- **Real-time Monitoring**: Live system health monitoring with performance metrics and error tracking
- **Comprehensive Logging**: Structured logging across all platform components with audit trails
- **Admin Dashboard**: Complete admin interface for data review, curation, and system management

### 🎛️ **Professional Admin Tools**
- **Data Curation**: Advanced workflows for data review, approval, and quality management
- **Bulk Operations**: Mass processing capabilities for large-scale data management
- **Export Capabilities**: Multi-format data export (JSON, CSV, Excel) for external analysis
- **System Analytics**: Performance tracking, trend analysis, and operational insights

## 🛠️ Technology Stack

- **Backend**: Python Flask, SQLAlchemy, Strands Agents
- **Frontend**: React, JavaScript
- **Database**: SQLite (default), supports PostgreSQL/MySQL
- **AI Research**: AWS Bedrock with Claude 3.5 Sonnet
- **Enterprise Features**: Advanced monitoring, logging, admin interfaces

## 📚 Complete Documentation Hub

**👉 [docs/README.md](docs/README.md) - Master documentation index with all guides organized by use case**

### 🎯 **Essential Quick Links:**
- **🆕 Installing on new machine**: [docs/setup/new-machine-setup.md](docs/setup/new-machine-setup.md) ← **Start here!**
- **🛠️ Issues and solutions**: [docs/setup/troubleshooting.md](docs/setup/troubleshooting.md) ← **Debugging guide**
- **🔌 Complete API reference**: [docs/api/endpoints.md](docs/api/endpoints.md) ← **All endpoints**
- **⚖️ Frontend vs Backend features**: [docs/features/feature-parity.md](docs/features/feature-parity.md) ← **Missing UI features**

### 🔧 **Setup & Configuration:**
- **⚡ 15-minute setup**: [docs/setup/quick-start.md](docs/setup/quick-start.md)
- **🖥️ Windows setup**: [docs/setup/windows-setup.md](docs/setup/windows-setup.md)  
- **☁️ AWS configuration**: [docs/setup/aws-setup.md](docs/setup/aws-setup.md)
- **🏢 Enterprise workflow**: [docs/development/architecture.md](docs/development/architecture.md)

### 📋 **Current Status (June 2025):**
- ✅ **Backend**: 100% functional with enterprise features
- ✅ **Basic Frontend**: Tool management working
- ⚠️ **Advanced Frontend**: 85% of backend features need UI
- ✅ **Documentation**: Complete setup and troubleshooting guides
- ✅ **Testing**: Comprehensive validation scripts

## 🚀 Quick Start (15 Minutes to MVP)

### Prerequisites

- **Python 3.10+** and **Node.js 18+** (Required for Strands SDK compatibility)
- **AWS Account** with Bedrock access
- **Claude 3.5 Sonnet** enabled in AWS Bedrock (us-east-1 region)

### 🔥 Express Setup (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/ai-tool-intelligence.git
cd ai-tool-intelligence

# 2. One-command setup and start
make setup
make start

# 3. Configure AWS credentials when prompted
# Follow the setup guide: docs/setup/ONBOARDING_COMPLETE_GUIDE.md
```

### 📋 Alternative Platform-Specific Setup

#### **Windows PowerShell**
```powershell
# Clone and setup
git clone https://github.com/yourusername/ai-tool-intelligence.git
cd ai-tool-intelligence

# Install dependencies
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

cd ..\frontend
npm install

# Configure and start
copy .env.example .env
notepad .env  # Add AWS credentials
make start
```

#### **macOS/Linux Terminal**
```bash
# Clone and setup  
git clone https://github.com/yourusername/ai-tool-intelligence.git
cd ai-tool-intelligence

# Install dependencies
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd ../frontend
npm install

# Configure and start
cp .env.example .env
nano .env  # Add AWS credentials
make start
```

## 🎯 **Critical Setup Steps**

### **⚠️ BEFORE YOU START - READ THIS**

1. **📋 Complete Onboarding Guide**: [docs/setup/ONBOARDING_COMPLETE_GUIDE.md](docs/setup/ONBOARDING_COMPLETE_GUIDE.md) ← **Essential reading**
2. **🔧 Troubleshooting Guide**: [docs/setup/TROUBLESHOOTING_COMPLETE.md](docs/setup/TROUBLESHOOTING_COMPLETE.md) ← **If anything fails**
3. **⚡ Prerequisites Check**: Python 3.10+, Node.js 18+, AWS Account with Bedrock
4. **🔑 AWS Configuration**: Enable Claude 3.5 Sonnet in AWS Bedrock (us-east-1) **BEFORE** research

### **🚀 First Use - Test Everything Works**

1. **Open Frontend**: http://localhost:3000
2. **Verify Backend**: http://localhost:5000/api/health (should return `{"status": "healthy"}`)
3. **Add Test Tool**:
   ```
   Name: Cursor
   Category: Code Assistants  
   Website: https://cursor.sh
   Description: AI-first code editor
   ```
4. **Click "Research"** → Should start AI analysis (2-3 minutes)
5. **Check Results** → Comprehensive analysis with GitHub stats, pricing, features
6. **Test Admin Features** → Add header `X-Admin-User: admin` to requests

### **🆘 If Something Fails**

1. **Check the troubleshooting guide**: [docs/setup/TROUBLESHOOTING_COMPLETE.md](docs/setup/TROUBLESHOOTING_COMPLETE.md)
2. **Run health check**: `make monitor`
3. **Reset if needed**: Follow "Complete Platform Reset" in troubleshooting guide

## 🏢 Enterprise Features Overview

### 🎯 **Core Intelligence Engine**

**🔄 Advanced Data Curation**
- AI-powered change detection across all tool dimensions
- Quality scoring with confidence metrics and validation rules
- Automated data enrichment and gap filling
- Version tracking and historical change analysis

**📈 Competitive Analysis Engine**
- Market positioning analysis with leader/challenger classification
- Feature adoption trend tracking and forecasting
- Pricing evolution analysis and competitive benchmarking
- Technology shift detection and emerging trend identification

**🚨 Intelligent Alert System**
- Configurable alert rules with severity thresholds
- Multi-channel notifications (email, Slack, webhook)
- Smart filtering to reduce notification noise
- Alert analytics and effectiveness tracking

### 🛠️ **Enterprise Administration**

**👥 Admin Interface**
- Comprehensive dashboard with system health metrics
- Data review workflows with approval/rejection capabilities
- Bulk operations for mass data management
- User activity tracking and audit trails

**📊 Real-time Monitoring**
- System performance monitoring with real-time metrics
- Application health assessment and component status
- Performance analytics and bottleneck identification
- Resource utilization tracking and optimization insights

**📝 Advanced Logging**
- Structured logging across all platform components
- Performance tracking with execution time monitoring
- Security event logging and audit trail maintenance
- Multi-format log output (JSON, console, database, files)

### 🔬 Comprehensive Tool Analysis

Each tool undergoes analysis across **13 specialized research dimensions** with **enterprise-grade data quality**:

**📈 Repository Analysis**

- GitHub stars, forks, contributors, activity patterns
- Release frequency and version tracking
- Technology stack and programming languages

**💰 Business Intelligence**
- Pricing tiers, subscription models, enterprise options
- Company funding history and financial data
- Team size, headquarters, key executives

**🔧 Technical Deep Dive**
- Feature extraction and capability analysis
- Integration ecosystem (IDEs, CI/CD, cloud platforms)
- Documentation quality and developer experience

**🏆 Market Position**
- Direct competitors and alternatives
- Social sentiment from Reddit, HN, Twitter
- Strategic positioning and differentiation

### 📊 Advanced Analytics & Intelligence

**🎯 Market Intelligence**
- Real-time competitive landscape analysis with market positioning
- Trend forecasting with statistical confidence intervals
- Technology adoption pattern recognition and prediction
- Market opportunity identification and threat assessment

**💰 Business Intelligence**
- Pricing strategy analysis and benchmarking
- Investment tracking and funding round analysis
- Market share estimation and competitive dynamics
- Strategic recommendation engine for tool adoption

**📈 Operational Analytics**
- Data quality metrics and improvement tracking
- Platform performance analytics and optimization insights
- User activity patterns and system utilization metrics
- Cost analysis and ROI tracking for research operations

## 🚀 New Features Usage Guide

### Bulk Research Operations
```
1. Check the boxes next to tools you want to research
2. Use "Select All" checkbox in the table header for all visible tools
3. Click "Research Selected (X)" button to start batch processing
4. Monitor progress in the top progress bar and research queue
```

### Real-time Notifications
```
- Enable browser notifications when prompted for completion alerts
- Watch in-app notifications (top-right) for operation status
- Research queue (bottom-right) shows live progress
- Progress bars show estimated completion times
```

### Research Queue Management
```
- View active/completed/failed research in the bottom-right queue
- Click "Clear" to remove completed items
- Monitor individual tool progress in real-time
- Get browser notifications when research completes
```

### Keyboard Shortcuts
```
- R: Research selected tool (when viewing tool details)
- E: Edit selected tool (when viewing tool details)
- Esc: Close current modal/view
- Ctrl+A: Select all visible tools (when table is focused)
```

## 🏢 Enterprise Architecture

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                     ENTERPRISE AI TOOL INTELLIGENCE PLATFORM                     │
├────────────────────────────────────────────────────────────────────────────────┤
│ 📱 Frontend Layer          💾 Core Engine              🔬 Intelligence Engine     │
│ ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐ │
│ │ • Admin Dashboard     │  │ • Flask Backend API │  │ • Market Analyzer    │ │
│ │ • Tool Management     │  │ • Enhanced Database │  │ • Trend Tracker      │ │
│ │ • Analytics UI        │  │ • Curation Engine   │  │ • Quality Scorer     │ │
│ │ • Monitoring Console  │  │ • Change Detection  │  │ • Alert Manager      │ │
│ └─────────────────────┘  └─────────────────────┘  └─────────────────────┘ │
├────────────────────────────────────────────────────────────────────────────────┤
│ 📊 Admin & Monitoring       🔍 Research & Analysis       🌐 External Integrations   │
│ ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐ │
│ │ • System Logger       │  │ • AWS Strands Agent │  │ • AWS Bedrock API    │ │
│ │ • Monitoring Dashboard│  │ • 13 Research Tools │  │ • Claude 3.5 Sonnet  │ │
│ │ • Admin Interface     │  │ • Web Scraping      │  │ • External APIs      │ │
│ │ • Performance Metrics │  │ • Data Validation   │  │ • Notification APIs  │ │
│ └─────────────────────┘  └─────────────────────┘  └─────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 🔬 Enterprise Intelligence Components

**🎯 Core Research Tools (13 Specialized Agents)**
1. **`github_analyzer`** - Repository metrics and activity analysis
2. **`pricing_extractor`** - Pricing tiers and subscription models  
3. **`company_lookup`** - Company background and team information
4. **`documentation_analyzer`** - Documentation quality assessment
5. **`integration_detector`** - IDE, CI/CD, and platform integrations
6. **`version_tracker`** - Release patterns and update frequency
7. **`changelog_analyzer`** - Development velocity metrics
8. **`feature_extractor`** - Capability identification and categorization
9. **`funding_lookup`** - Investment history and valuations
10. **`stock_tracker`** - Stock prices for public companies
11. **`employee_counter`** - Team size estimation
12. **`competitor_finder`** - Market positioning analysis
13. **`social_sentiment`** - Community perception tracking

**📊 Intelligence Analysis Engines**
- **Market Analyzer** - Competitive positioning and market dynamics
- **Trend Tracker** - Technology adoption and market trend analysis
- **Quality Scorer** - Data validation and confidence assessment
- **Alert Manager** - Change detection and notification system

**🛠️ Enterprise Management Systems**
- **Curation Engine** - Automated data processing and enhancement
- **Admin Interface** - Complete administrative control and monitoring
- **System Logger** - Comprehensive logging and audit trails
- **Monitoring Dashboard** - Real-time system health and performance

## 📁 Enterprise Project Structure

```
ai-tool-intelligence/
├── backend/                               # Enterprise Backend Engine
│   ├── app.py                            # Main Flask application with all integrations
│   ├── strands_research_tools.py         # 13 specialized AWS Strands research tools
│   ├── models/
│   │   ├── enhanced_schema.py             # Complete database schema
│   │   └── base_schema.py                 # Core data models
│   ├── data_curation/
│   │   ├── curation_engine.py             # Automated data processing engine
│   │   └── batch_processor.py             # Systematic monitoring and processing
│   ├── competitive_analysis/
│   │   ├── market_analyzer.py             # Market analysis and competitive intelligence
│   │   ├── trend_tracker.py               # Trend analysis and forecasting
│   │   ├── competitive_cli.py             # Command-line competitive analysis tools
│   │   └── competitive_integration.py     # Integration manager for competitive systems
│   ├── change_detection/
│   │   ├── alert_manager.py               # Change detection and alert system
│   │   └── README.md                      # Alert system documentation
│   ├── data_validation/
│   │   ├── quality_scorer.py              # Data quality assessment and scoring
│   │   └── README.md                      # Quality validation documentation
│   ├── admin_interface/
│   │   ├── admin_manager.py               # Administrative management engine
│   │   ├── admin_api.py                   # Admin REST API endpoints
│   │   ├── admin_cli.py                   # Command-line admin tools
│   │   └── README.md                      # Admin interface documentation
│   ├── logging_monitoring/
│   │   ├── system_logger.py               # Comprehensive logging system
│   │   ├── monitoring_dashboard.py        # Real-time monitoring and metrics
│   │   └── monitoring_api.py              # Monitoring API endpoints
│   ├── migrations/
│   │   └── migrate_to_enhanced_schema.py  # Database migration scripts
│   ├── requirements.txt                # Python dependencies
│   └── .env.example                    # Environment configuration template
├── frontend/                             # React Admin Dashboard
│   ├── src/App.js                        # Main React application
│   ├── package.json                      # Node.js dependencies
│   └── public/                           # Static assets
├── windows/                              # Windows-specific setup and tools
│   ├── setup-windows.bat                 # Windows automated setup
│   ├── start-windows.bat                 # Windows startup script
│   └── README.md                         # Windows setup documentation
├── scripts/                              # Cross-platform utility scripts
│   ├── start.sh                          # Start platform (development)
│   ├── backup.sh                         # Create system backup
│   ├── monitor.sh                        # System health monitoring
│   └── research.sh                       # Research queue management
├── docs/                                 # Comprehensive documentation
│   ├── API.md                            # Complete API documentation
│   ├── DEPLOYMENT.md                     # Production deployment guide
│   └── ADMIN_GUIDE.md                    # Administrator user guide
├── docker/                               # Production deployment
│   ├── docker-compose.yml                # Container orchestration
│   └── Dockerfile                        # Container definitions
├── APPLICATION_WORKFLOW.md               # Complete system workflow documentation
├── WINDOWS_SETUP.md                      # Detailed Windows installation guide
├── AWS_SETUP.md                          # AWS configuration guide
├── PROJECT_STATUS.md                     # Current project status and roadmap
└── setup.sh                              # Automated setup script
```

## 🎛️ Management Commands

```bash
# System monitoring
./scripts/monitor.sh                 # Check system health
./scripts/research.sh status         # Research queue status

# Research management
./scripts/research.sh process "Cursor,GitHub Copilot"  # Research specific tools
./scripts/research.sh category "Agentic IDEs"          # Research entire category
./scripts/research.sh failed                           # Retry failed tools

# System maintenance
./scripts/backup.sh                  # Create system backup
python backend/config.py status     # Detailed system status
```

## 📊 Sample Research Output

When you research "Cursor", you get comprehensive data like:

```json
{
  "tool": {
    "name": "Cursor",
    "description": "AI-first code editor built for pair-programming with AI models",
    "ai_capabilities": ["Code completion", "Chat with codebase", "Code generation"],
    "latest_version": "v0.42.3"
  },
  "company": {
    "name": "Anysphere",
    "founded_year": 2022,
    "employee_count": 25,
    "total_funding": 60000000,
    "funding_stage": "Series A"
  },
  "github_stats": {
    "stars": 25000,
    "forks": 1200,
    "release_frequency": "frequent (2-4 weeks)"
  },
  "pricing": {
    "model": "freemium",
    "tiers": [
      {"name": "Hobby", "price": 0},
      {"name": "Pro", "price": 20},
      {"name": "Business", "price": 40}
    ]
  },
  "market_analysis": {
    "competitors": ["GitHub Copilot", "Tabnine", "CodeT5"],
    "competitive_advantages": ["VS Code compatibility", "Multiple AI models"]
  }
}
```

## 🔧 Configuration

### Basic Configuration (`backend/config.json`)

```json
{
  "strands_agent": {
    "model_provider": "bedrock",
    "model_id": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "temperature": 0.1,
    "rate_limit_delay": 5
  },
  "batch_processing": {
    "max_concurrent_tools": 3,
    "daily_limit": 50
  }
}
```

### Cost Optimization

- **Estimated cost**: $0.01-$0.10 per tool research
- **Daily limits**: Configurable research limits to control costs
- **Rate limiting**: Built-in delays to respect API limits

## 🚀 Production Deployment

### Docker Deployment (Recommended)

```bash
# Production deployment with Docker
cp .env.example .env
# Configure production values

# Deploy
docker-compose up -d

# Services available at:
# Frontend: http://localhost
# API: http://localhost/api
# Monitoring: http://localhost:9090
```

### Manual Deployment

```bash
# Backend
cd backend
pip install -r requirements.txt
gunicorn --bind 0.0.0.0:5000 app:app

# Frontend  
cd frontend
npm install && npm run build
serve -s build -l 3000
```

## 📈 Analytics & Insights

### Dashboard Metrics
- **Tool coverage** across AI categories
- **Market trends** and funding patterns
- **Technology adoption** insights
- **Competitive landscape** analysis

### Business Intelligence Reports
- **Investment opportunities** in emerging categories
- **Pricing strategy** analysis across tools
- **Market positioning** recommendations
- **Technology stack** trend analysis

## 🛡️ Security & Compliance

- **AWS IAM roles** with minimal permissions
- **Rate limiting** to prevent abuse
- **Data encryption** at rest and in transit
- **Audit logging** for all research activities

## 🔄 Automation Features

### Scheduled Research
- **Weekly updates** for all tools
- **Daily priority** updates for new tools
- **Failed tool retry** with exponential backoff
- **Automated cleanup** of old research logs

### Monitoring & Alerts
- **System health** monitoring
- **Research failure** alerts
- **Resource usage** tracking
- **Cost threshold** notifications

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**AWS Bedrock Access Denied**

```bash
# Check model access in AWS console
aws bedrock list-foundation-models --region us-east-1 | grep claude
```

**Strands Agents Installation Failed**

```bash
# Ensure Python 3.10+ is installed
python --version

# Install with specific version
pip install strands-agents>=0.1.0 strands-agents-tools>=0.1.0 --force-reinstall

# For Windows users, see WINDOWS_SETUP.md for detailed troubleshooting
```

**Research Takes Too Long**

```bash
# Use bulk research with progress indicators for better experience
# Select multiple tools and use "Research Selected" button
# Monitor progress in real-time with the new progress indicators

# Reduce concurrent processing if needed
nano backend/config.json
# Set "max_concurrent_tools": 1
```

**Browser Notifications Not Working**

```bash
# Check browser notification permissions
# Click "Allow" when prompted during first research
# Or manually enable in browser settings for your domain
```

**Research Queue Not Updating**

```bash
# Refresh the page if queue appears stuck
# Clear completed items using "Clear" button
# Check browser console for any JavaScript errors
```

### Getting Help

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check `docs/` directory for detailed guides
- **API Reference**: See `docs/API.md` for endpoint documentation

---

## 🎉 Success Stories

> *"Reduced our AI tool research time from 4 hours to 10 minutes per tool, saving our team 200+ hours monthly while providing deeper insights than manual research."*

> *"The competitive intelligence helped us identify investment opportunities and make data-driven tool adoption decisions."*

---

**Ready to get started?** Run `./setup.sh` and have your AI tool intelligence platform running in 15 minutes! 🚀