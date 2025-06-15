# Windows Installation Guide

## Quick Start (Recommended)

1. **Download and install prerequisites:**
   - [Python 3.10+](https://python.org/downloads/) - **IMPORTANT: Check "Add Python to PATH"**
   - [Node.js 18+](https://nodejs.org/) - Choose the LTS version
   - [Git](https://git-scm.com/download/win) - Use default settings

2. **Run the simple setup:**
   ```cmd
   setup-windows-simple.bat
   ```

3. **Start the platform:**
   ```cmd
   windows\start-windows.bat
   ```

4. **Open your browser:** http://localhost:3000

## Advanced Setup (PowerShell)

If you prefer PowerShell or need more control:

```powershell
# Run as Administrator or with execution policy bypass
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\windows\Setup.ps1
```

## Troubleshooting Common Issues

### Issue: "Python not found" or "pip not found"
**Solution:** 
- Reinstall Python from python.org
- **MUST check "Add Python to PATH" during installation**
- Restart Command Prompt/PowerShell after installation

### Issue: "Flask not found" or "Module not found"
**Solution:**
- The virtual environment isn't activated properly
- Run setup again: `setup-windows-simple.bat`
- Check that `backend\venv\Scripts\python.exe` exists

### Issue: Virtual environment activation fails
**Solution:**
- Use the fixed setup scripts which call venv executables directly
- Don't manually activate - scripts handle this automatically

### Issue: Strands Agents installation fails
**This is expected and OK!** The platform works without AI features.
- Basic tool research will work
- AI-powered analysis requires AWS credentials
- Skip this if you just want to try the platform

### Issue: Node.js or npm installation fails
**Solution:**
- Clear npm cache: `npm cache clean --force`
- Delete `frontend\node_modules` and `frontend\package-lock.json`
- Run `npm install` again from the frontend directory

### Issue: Port already in use
**Solution:**
- Kill existing processes:
  ```cmd
  netstat -ano | findstr :5000
  netstat -ano | findstr :3000
  taskkill /F /PID <process_id>
  ```

### Issue: PowerShell execution policy errors
**Solution:**
- Run as Administrator:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- Or use bypass flag:
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\windows\Setup.ps1
  ```

## Manual Installation Steps

If automated setup fails, you can install manually:

### 1. Backend Setup
```cmd
cd backend
python -m venv venv
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\pip.exe install Flask Flask-SQLAlchemy Flask-CORS SQLAlchemy
venv\Scripts\pip.exe install -r requirements.txt
copy .env.example .env
```

### 2. Frontend Setup
```cmd
cd frontend
npm install
```

### 3. Test Installation
```cmd
cd backend
venv\Scripts\python.exe -c "from flask import Flask; print('Flask OK')"
```

## Configuration

### AWS Setup (Optional - for AI features)
1. Edit `backend\.env`
2. Add your AWS credentials:
   ```
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your-key-here
   AWS_SECRET_ACCESS_KEY=your-secret-here
   ```
3. Enable Claude 3.5 Sonnet in AWS Bedrock Console

### Without AWS (Basic functionality)
The platform works without AWS credentials:
- Tool database management
- Manual research input
- Basic competitive analysis
- No AI-powered research

## Starting the Platform

### Option 1: Batch Files (Simplest)
```cmd
windows\start-windows.bat    # Start both frontend and backend
windows\stop-windows.bat     # Stop all services
```

### Option 2: PowerShell Scripts (More features)
```powershell
.\windows\Start.ps1          # Start with logging and monitoring
.\windows\Stop.ps1           # Clean shutdown
.\windows\Status.ps1         # Check service status
```

### Option 3: Manual Start
```cmd
# Terminal 1 - Backend
cd backend
venv\Scripts\python.exe app.py

# Terminal 2 - Frontend  
cd frontend
npm start
```

## Verification

1. **Backend health check:** http://localhost:5000/api/health
2. **Frontend:** http://localhost:3000
3. **Database:** Check `backend\instance\ai_tools.db` exists

## Next Steps

1. **Add your first tool:**
   - Go to http://localhost:3000
   - Click "Add New Tool"
   - Enter tool information

2. **Enable AI features (optional):**
   - Configure AWS credentials in `backend\.env`
   - Click "Research" to get AI-powered analysis

3. **Import existing tools:**
   - Use the bulk import feature
   - CSV format supported

## Getting Help

If you're still having issues:

1. Check logs in `backend\logs\` and `windows\logs\`
2. Try the simple batch file setup first
3. Ensure all prerequisites are properly installed
4. Restart your computer after installing Python/Node.js

## File Structure After Installation

```
ai-tool-intelligence/
├── backend/
│   ├── venv/                # Virtual environment
│   ├── instance/           # Database and uploads
│   ├── .env                # Your configuration
│   └── app.py              # Main Flask app
├── frontend/
│   ├── node_modules/       # Node.js dependencies
│   └── package.json        # Frontend config
└── windows/
    ├── start-windows.bat   # Simple start script
    └── Setup.ps1           # Advanced setup
```

The installation creates isolated environments so dependencies don't conflict with your system.