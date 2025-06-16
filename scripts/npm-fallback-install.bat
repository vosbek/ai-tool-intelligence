@echo off
echo ========================================
echo NPM Fallback Installation Script
echo ========================================
echo.
echo This script tries multiple approaches to install NPM packages
echo when Artifactory is giving 404 errors.
echo.

cd frontend
if not exist "package.json" (
    echo ERROR: package.json not found in frontend directory
    pause
    exit /b 1
)

echo Current directory: %CD%
echo.

echo Strategy 1: Try current registry first
echo ======================================
echo.
npm install --verbose
if %ERRORLEVEL% EQU 0 (
    echo ✅ Success with current registry!
    goto :success
)
echo ❌ Failed with current registry
echo.

echo Strategy 2: Use public NPM registry
echo ===================================
echo.
echo Temporarily switching to public NPM...
npm config get registry > original_registry.txt
npm config set registry https://registry.npmjs.org/

npm install --verbose
if %ERRORLEVEL% EQU 0 (
    echo ✅ Success with public NPM!
    echo Restoring original registry...
    set /p ORIGINAL_REGISTRY=<original_registry.txt
    npm config set registry %ORIGINAL_REGISTRY%
    del original_registry.txt
    goto :success
)
echo ❌ Failed with public NPM
echo.

echo Strategy 3: Use Yarn as alternative
echo ===================================
echo.
echo Checking if Yarn is available...
yarn --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Yarn found, trying yarn install...
    yarn install --verbose
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Success with Yarn!
        goto :success
    )
    echo ❌ Failed with Yarn
) else (
    echo Yarn not found, skipping...
)
echo.

echo Strategy 4: Install critical packages only
echo ==========================================
echo.
echo Installing only essential packages...
npm config set registry https://registry.npmjs.org/

echo Installing React and core dependencies...
npm install react react-dom react-scripts --save --verbose
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install React core
    goto :restore_and_fail
)

echo Installing additional dependencies...
npm install axios date-fns lucide-react recharts --save --verbose
npm install tailwindcss @tailwindcss/forms autoprefixer postcss --save-dev --verbose

echo Installing TypeScript support...
npm install typescript @types/node @types/react @types/react-dom --save-dev --verbose

:restore_and_success
echo.
echo Restoring original registry...
if exist "original_registry.txt" (
    set /p ORIGINAL_REGISTRY=<original_registry.txt
    npm config set registry %ORIGINAL_REGISTRY%
    del original_registry.txt
)
goto :success

:restore_and_fail
echo.
echo Restoring original registry...
if exist "original_registry.txt" (
    set /p ORIGINAL_REGISTRY=<original_registry.txt
    npm config set registry %ORIGINAL_REGISTRY%
    del original_registry.txt
)
goto :failure

echo Strategy 5: Manual package.json modification
echo ============================================
echo.
echo Creating minimal package.json for basic functionality...
echo {> package-minimal.json
echo   "name": "ai-tool-intelligence-frontend",>> package-minimal.json
echo   "version": "0.1.0",>> package-minimal.json
echo   "private": true,>> package-minimal.json
echo   "proxy": "http://localhost:5000",>> package-minimal.json
echo   "dependencies": {>> package-minimal.json
echo     "react": "^18.2.0",>> package-minimal.json
echo     "react-dom": "^18.2.0",>> package-minimal.json
echo     "react-scripts": "5.0.1">> package-minimal.json
echo   },>> package-minimal.json
echo   "scripts": {>> package-minimal.json
echo     "start": "react-scripts start",>> package-minimal.json
echo     "build": "react-scripts build",>> package-minimal.json
echo     "test": "react-scripts test",>> package-minimal.json
echo     "eject": "react-scripts eject">> package-minimal.json
echo   }>> package-minimal.json
echo }>> package-minimal.json

echo.
echo Backing up original package.json...
copy package.json package.json.backup

echo Installing with minimal package.json...
copy package-minimal.json package.json
npm install --verbose

if %ERRORLEVEL% EQU 0 (
    echo ✅ Success with minimal package.json!
    echo.
    echo You can now manually add other dependencies one by one:
    echo   npm install axios
    echo   npm install date-fns
    echo   npm install lucide-react
    echo   etc.
    echo.
    echo Original package.json saved as package.json.backup
    goto :success
) else (
    echo ❌ Failed even with minimal package.json
    echo Restoring original package.json...
    copy package.json.backup package.json
    del package-minimal.json
)

:failure
echo.
echo ========================================
echo All installation strategies failed!
echo ========================================
echo.
echo Possible issues:
echo 1. Network connectivity problems
echo 2. Firewall/proxy blocking all NPM registries
echo 3. Node.js installation corrupted
echo 4. Disk space issues
echo 5. Permissions problems
echo.
echo Manual troubleshooting steps:
echo 1. Check internet connection: ping google.com
echo 2. Check disk space: dir c:\
echo 3. Try running as Administrator
echo 4. Contact IT support with error logs
echo 5. Try on a different network (mobile hotspot)
echo.
cd ..
pause
exit /b 1

:success
echo.
echo ========================================
echo Installation Successful!
echo ========================================
echo.
echo You can now start the frontend with:
echo   cd frontend
echo   npm start
echo.
echo If you used a fallback method, you may need to:
echo 1. Manually install missing dependencies
echo 2. Update your original registry configuration
echo 3. Test the application thoroughly
echo.
cd ..
pause
exit /b 0