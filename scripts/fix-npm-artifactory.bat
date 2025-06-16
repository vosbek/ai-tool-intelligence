@echo off
echo ========================================
echo NPM Artifactory Quick Fix Script
echo ========================================
echo.
echo This script applies common fixes for NPM + Artifactory issues.
echo Run this AFTER the troubleshoot script identifies the problem.
echo.

set /p ARTIFACTORY_URL="Enter your Artifactory NPM registry URL (or press Enter to skip): "
if not "%ARTIFACTORY_URL%"=="" (
    echo Setting registry to: %ARTIFACTORY_URL%
    npm config set registry %ARTIFACTORY_URL%
)

echo.
echo Applying enterprise-friendly NPM settings...
echo.

echo 1. Disabling strict SSL (for corporate certificates)
npm config set strict-ssl false

echo 2. Increasing timeouts for enterprise networks
npm config set fetch-timeout 600000
npm config set fetch-retry-maxtimeout 600000
npm config set fetch-retries 5

echo 3. Setting legacy peer deps for compatibility
npm config set legacy-peer-deps true

echo 4. Clearing NPM cache
npm cache clean --force

echo 5. Setting audit level to moderate (reduces enterprise friction)
npm config set audit-level moderate

echo 6. Disabling fund messages
npm config set fund false

echo.
echo Current NPM configuration:
echo ========================
npm config list

echo.
echo Testing configuration...
echo.
echo Testing registry connectivity:
npm ping

echo.
echo Testing package search:
npm search react --no-optional 2>nul | head -5

echo.
echo ========================================
echo Quick Fix Complete
echo ========================================
echo.
echo If you're still getting 404s, try these specific solutions:
echo.
echo FOR AUTHENTICATION ISSUES:
echo   npm login --registry %ARTIFACTORY_URL%
echo.
echo FOR SPECIFIC PACKAGE 404s:
echo   npm install --registry https://registry.npmjs.org/
echo.
echo FOR FIREWALL/PROXY ISSUES:
echo   Ask IT for the correct proxy settings:
echo   npm config set proxy http://proxy.company.com:port
echo   npm config set https-proxy http://proxy.company.com:port
echo.
echo FOR WRONG ARTIFACTORY URL:
echo   Common formats:
echo   https://company.jfrog.io/artifactory/api/npm/npm-repo/
echo   https://artifactory.company.com/artifactory/api/npm/npm/
echo   https://nexus.company.com/repository/npm-public/
echo.
pause