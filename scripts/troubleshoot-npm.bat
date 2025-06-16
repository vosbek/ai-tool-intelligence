@echo off
echo ========================================
echo NPM Artifactory Troubleshooting Script
echo ========================================
echo.
echo This script will help diagnose and fix NPM issues with enterprise Artifactory.
echo.

REM Create log file
set LOG_FILE=npm-troubleshoot-%date:~-4,4%%date:~-10,2%%date:~-7,2%-%time:~0,2%%time:~3,2%%time:~6,2%.log
echo NPM Troubleshooting Log - %date% %time% > %LOG_FILE%
echo. >> %LOG_FILE%

echo Step 1: Current NPM Configuration
echo ================================
echo.
echo Registry configuration:
npm config get registry
npm config get registry >> %LOG_FILE%
echo.

echo Proxy settings:
npm config get proxy
npm config get https-proxy
npm config get proxy >> %LOG_FILE%
npm config get https-proxy >> %LOG_FILE%
echo.

echo NPM version and Node version:
npm --version
node --version
npm --version >> %LOG_FILE%
node --version >> %LOG_FILE%
echo.

echo Step 2: Network Connectivity Tests
echo =================================
echo.
echo Testing connectivity to registry...
npm config get registry > temp_registry.txt
set /p REGISTRY=<temp_registry.txt
del temp_registry.txt

echo Testing ping to registry host...
for /f "tokens=3 delims=/" %%a in ("%REGISTRY%") do set REGISTRY_HOST=%%a
ping -n 1 %REGISTRY_HOST%
echo Ping result: %ERRORLEVEL% >> %LOG_FILE%

echo.
echo Testing HTTP connection to registry...
curl -I %REGISTRY% 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Registry is reachable via HTTP
    echo Registry reachable via HTTP >> %LOG_FILE%
) else (
    echo ❌ Registry not reachable via HTTP
    echo Registry NOT reachable via HTTP >> %LOG_FILE%
)

echo.
echo Step 3: Detailed NPM Diagnostics
echo ===============================
echo.
echo Running npm doctor...
npm doctor
npm doctor >> %LOG_FILE% 2>&1

echo.
echo NPM cache info:
npm cache verify
npm cache verify >> %LOG_FILE% 2>&1

echo.
echo Step 4: Common Artifactory Fixes
echo ===============================
echo.

set /p FIX_CHOICE="Do you want to try common fixes? (y/n): "
if /i not "%FIX_CHOICE%"=="y" goto :skip_fixes

echo Applying common fixes...
echo.

echo Fix 1: Setting strict SSL to false (for corporate certificates)
npm config set strict-ssl false
echo strict-ssl set to false >> %LOG_FILE%

echo Fix 2: Clearing NPM cache
npm cache clean --force
echo NPM cache cleared >> %LOG_FILE%

echo Fix 3: Setting registry timeout (for slow enterprise networks)
npm config set fetch-timeout 300000
npm config set fetch-retry-maxtimeout 300000
echo Timeouts increased >> %LOG_FILE%

echo Fix 4: Setting legacy peer deps (for compatibility)
npm config set legacy-peer-deps true
echo Legacy peer deps enabled >> %LOG_FILE%

echo.
echo Step 5: Testing with Verbose Output
echo =================================
echo.
echo Testing npm install with verbose output...
echo This will show exactly where the 404 error occurs.
echo.
cd frontend
npm install --verbose --loglevel=verbose 2>&1 | tee ../npm-verbose.log
cd ..

goto :test_results

:skip_fixes
echo Skipped automatic fixes.
echo.

:test_results
echo.
echo Step 6: Registry Health Check
echo ===========================
echo.
echo Testing specific package fetch...
npm view react --registry %REGISTRY% 2>&1
echo React package test result: %ERRORLEVEL% >> %LOG_FILE%

echo.
echo Whoami check (for authentication):
npm whoami 2>&1
echo Whoami result: %ERRORLEVEL% >> %LOG_FILE%

echo.
echo Step 7: Alternative Solutions
echo ============================
echo.
echo If you're still getting 404s, try these manual solutions:
echo.
echo Solution A: Use public NPM temporarily
echo   npm config set registry https://registry.npmjs.org/
echo   npm install
echo   npm config set registry %REGISTRY%
echo.
echo Solution B: Use --registry flag for specific installs
echo   npm install --registry https://registry.npmjs.org/
echo.
echo Solution C: Check if you need authentication
echo   npm login --registry %REGISTRY%
echo.
echo Solution D: Use yarn instead of npm
echo   yarn install
echo.
echo Solution E: Check your .npmrc file for conflicts
echo   type %USERPROFILE%\.npmrc
echo.
echo Solution F: Try different Artifactory endpoint
echo   npm config set registry https://your-company.jfrog.io/artifactory/api/npm/npm/
echo.

echo.
echo Step 8: Environment Information
echo ==============================
echo.
echo Current working directory: %CD%
echo User: %USERNAME%
echo Computer: %COMPUTERNAME%
echo Path: %PATH%
echo.
echo Environment variables related to NPM:
set | findstr /i npm
set | findstr /i proxy
set | findstr /i registry
echo.

echo Current working directory: %CD% >> %LOG_FILE%
echo User: %USERNAME% >> %LOG_FILE%
echo Computer: %COMPUTERNAME% >> %LOG_FILE%
set | findstr /i npm >> %LOG_FILE%
set | findstr /i proxy >> %LOG_FILE%
set | findstr /i registry >> %LOG_FILE%

echo.
echo ========================================
echo Troubleshooting Complete
echo ========================================
echo.
echo Log saved to: %LOG_FILE%
echo Verbose log saved to: npm-verbose.log (if generated)
echo.
echo Common 404 causes in enterprise environments:
echo 1. Wrong registry URL format
echo 2. Missing authentication
echo 3. Proxy/firewall blocking requests
echo 4. SSL certificate issues
echo 5. Package not available in Artifactory mirror
echo 6. Artifactory repository configuration issues
echo.
echo If issues persist:
echo 1. Contact your IT team with the log files
echo 2. Verify Artifactory is configured for npm packages
echo 3. Check if you need VPN connection
echo 4. Verify your user has access to the Artifactory repository
echo.
pause