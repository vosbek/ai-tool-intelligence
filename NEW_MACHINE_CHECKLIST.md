# ✅ New Machine Installation Checklist

> **Follow this checklist to install on your new machine today**

## Pre-Installation

- [ ] **Windows 10/11** with Administrator access
- [ ] **Internet connection** for downloads
- [ ] **AWS account** with Bedrock access
- [ ] **AWS credentials** (Access Key ID + Secret)

## Installation Steps

### 1. Get the Project
- [ ] Download/clone from GitHub to your machine
- [ ] Open PowerShell as Administrator in project directory

### 2. Run Automated Setup
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
.\windows\Setup.ps1
```
- [ ] Setup script completes without errors
- [ ] Virtual environment created
- [ ] Dependencies installed

### 3. Configure AWS
```powershell
notepad backend\.env
```
- [ ] Add your `AWS_ACCESS_KEY_ID`
- [ ] Add your `AWS_SECRET_ACCESS_KEY`  
- [ ] Set `AWS_REGION=us-east-1`
- [ ] Change `SECRET_KEY` to something unique

### 4. Enable Claude in AWS Bedrock
- [ ] Go to AWS Bedrock Console
- [ ] Switch to **us-east-1** region
- [ ] Request access to **Claude 3.5 Sonnet**
- [ ] Wait for approval (usually instant)

### 5. Start the Platform
```powershell
.\start_windows.bat
```
- [ ] Backend starts successfully (port 5000)
- [ ] Frontend starts successfully (port 3000)
- [ ] No error messages in startup

## Verification

### Test Basic Functionality
- [ ] **Frontend loads**: http://localhost:3000
- [ ] **Health check works**: http://localhost:5000/api/health
- [ ] **System status**: http://localhost:5000/api/system/status
- [ ] **Admin access**: Add header `X-Admin-User: admin`

### Test Research Capability
- [ ] Add a test tool (e.g., name="Test", website="https://github.com")
- [ ] Click "Research" button
- [ ] Research completes successfully (2-3 minutes)
- [ ] Tool data populated with details

### Test Management Scripts
```powershell
.\windows\Status.ps1      # Should show system status
.\windows\Logs.ps1        # Should show recent logs
```
- [ ] Status script shows healthy system
- [ ] Logs script shows application logs

## Troubleshooting Checks

### If Setup Fails:
- [ ] Try: `.\windows\Setup.ps1 -Force`
- [ ] Check: PowerShell execution policy
- [ ] Verify: Internet connection and administrator access

### If AWS Validation Fails:
- [ ] Double-check credentials in `backend\.env`
- [ ] Verify Claude access in AWS Bedrock Console
- [ ] Temporarily skip: Set `SKIP_AWS_VALIDATION=true`

### If Research Fails:
- [ ] Check AWS credentials are correct
- [ ] Verify Claude 3.5 Sonnet access approved
- [ ] Test with simple tool first

### If Ports Are Busy:
```powershell
netstat -ano | findstr :5000
taskkill /PID <process_id> /F
```
- [ ] Kill existing processes on ports 3000/5000
- [ ] Restart with `.\windows\Start.ps1`

## Success Criteria ✅

You're successful when:
- [ ] ✅ Web interface loads at http://localhost:3000
- [ ] ✅ API responds at http://localhost:5000/api/health
- [ ] ✅ Can add and research tools successfully
- [ ] ✅ Admin features work with proper headers
- [ ] ✅ System health monitoring shows green status
- [ ] ✅ Management scripts work properly

## Quick Commands Reference

```powershell
# Start platform
.\windows\Start.ps1

# Check status
.\windows\Status.ps1

# View logs  
.\windows\Logs.ps1

# Stop platform
.\windows\Stop.ps1

# Reset if needed
.\windows\Reset.ps1
```

## Documentation Quick Links

- **[QUICK_START.md](QUICK_START.md)** - Fastest setup guide
- **[INSTALL.md](INSTALL.md)** - Complete installation guide  
- **[windows/README.md](windows/README.md)** - Windows script details
- **[STABILITY_FEATURES.md](STABILITY_FEATURES.md)** - Stability features

---

**🎉 Once all items are checked, your AI Tool Intelligence Platform is ready to use!**

**Estimated total time**: 15-20 minutes on a fresh machine.