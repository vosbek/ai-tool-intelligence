#Requires -Version 5.1
<#
.SYNOPSIS
    Advanced NPM Artifactory diagnostics script
.DESCRIPTION
    Comprehensive diagnosis of NPM + Artifactory issues with detailed reporting
.EXAMPLE
    .\diagnose-artifactory.ps1
#>

[CmdletBinding()]
param()

# Colors for output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Step { param($Message) Write-Host "🔍 $Message" -ForegroundColor Blue }

Write-Host @"
🔍 NPM Artifactory Diagnostic Tool
================================================================
This PowerShell script provides advanced diagnostics for NPM + Artifactory issues.

"@ -ForegroundColor White

# Create detailed log
$LogFile = "artifactory-diagnostics-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
$Diagnostics = @{
    timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    computer = $env:COMPUTERNAME
    user = $env:USERNAME
    npm = @{}
    network = @{}
    registry = @{}
    recommendations = @()
}

Write-Step "Gathering NPM configuration..."

# Get NPM configuration
try {
    $NpmVersion = npm --version 2>$null
    $NodeVersion = node --version 2>$null
    $Registry = npm config get registry 2>$null
    $Proxy = npm config get proxy 2>$null
    $HttpsProxy = npm config get https-proxy 2>$null
    $StrictSsl = npm config get strict-ssl 2>$null
    
    $Diagnostics.npm = @{
        version = $NpmVersion
        node_version = $NodeVersion
        registry = $Registry
        proxy = $Proxy
        https_proxy = $HttpsProxy
        strict_ssl = $StrictSsl
        cache_path = npm config get cache 2>$null
        prefix = npm config get prefix 2>$null
    }
    
    Write-Success "NPM configuration collected"
} catch {
    Write-Error "Failed to get NPM configuration: $_"
    $Diagnostics.npm.error = $_.Exception.Message
}

Write-Step "Testing network connectivity..."

# Test network connectivity
if ($Registry) {
    try {
        $RegistryUri = [System.Uri]$Registry
        $RegistryHost = $RegistryUri.Host
        
        # Test DNS resolution
        $DnsResult = Resolve-DnsName $RegistryHost -ErrorAction SilentlyContinue
        
        # Test TCP connectivity
        $TcpTest = Test-NetConnection $RegistryHost -Port $RegistryUri.Port -InformationLevel Quiet -ErrorAction SilentlyContinue
        
        # Test HTTP connectivity
        try {
            $HttpTest = Invoke-WebRequest -Uri $Registry -Method Head -TimeoutSec 10 -UseBasicParsing -ErrorAction SilentlyContinue
            $HttpStatus = $HttpTest.StatusCode
        } catch {
            $HttpStatus = $_.Exception.Response.StatusCode.value__
            $HttpError = $_.Exception.Message
        }
        
        $Diagnostics.network = @{
            registry_host = $RegistryHost
            dns_resolution = $DnsResult -ne $null
            tcp_connection = $TcpTest
            http_status = $HttpStatus
            http_error = $HttpError
        }
        
        if ($DnsResult) { Write-Success "DNS resolution successful" }
        else { Write-Error "DNS resolution failed for $RegistryHost" }
        
        if ($TcpTest) { Write-Success "TCP connection successful" }
        else { Write-Error "TCP connection failed to $RegistryHost" }
        
        if ($HttpStatus -eq 200) { Write-Success "HTTP connection successful" }
        else { Write-Warning "HTTP returned status: $HttpStatus" }
        
    } catch {
        Write-Error "Network testing failed: $_"
        $Diagnostics.network.error = $_.Exception.Message
    }
}

Write-Step "Testing registry functionality..."

# Test registry operations
try {
    # Test npm ping
    $PingResult = npm ping 2>&1
    $PingSuccess = $LASTEXITCODE -eq 0
    
    # Test package search
    $SearchResult = npm search react --no-optional --json 2>$null | ConvertFrom-Json -ErrorAction SilentlyContinue
    $SearchSuccess = $SearchResult -ne $null
    
    # Test authentication
    $WhoamiResult = npm whoami 2>&1
    $AuthSuccess = $LASTEXITCODE -eq 0
    
    $Diagnostics.registry = @{
        ping_success = $PingSuccess
        ping_result = $PingResult -join "`n"
        search_success = $SearchSuccess
        auth_success = $AuthSuccess
        whoami_result = $WhoamiResult -join "`n"
    }
    
    if ($PingSuccess) { Write-Success "Registry ping successful" }
    else { Write-Error "Registry ping failed" }
    
    if ($SearchSuccess) { Write-Success "Package search successful" }
    else { Write-Warning "Package search failed" }
    
    if ($AuthSuccess) { Write-Success "Authentication successful" }
    else { Write-Warning "Authentication failed or not required" }
    
} catch {
    Write-Error "Registry testing failed: $_"
    $Diagnostics.registry.error = $_.Exception.Message
}

Write-Step "Analyzing common issues..."

# Analyze and provide recommendations
$Recommendations = @()

# Check registry URL format
if ($Registry -match "artifactory") {
    if ($Registry -notmatch "/api/npm/") {
        $Recommendations += @{
            issue = "Registry URL format"
            description = "Artifactory URL should include '/api/npm/' path"
            solution = "Try: npm config set registry https://your-artifactory.com/artifactory/api/npm/npm-repo/"
            priority = "High"
        }
    }
}

# Check SSL issues
if ($StrictSsl -eq "true" -and $Diagnostics.network.http_status -ne 200) {
    $Recommendations += @{
        issue = "SSL Certificate"
        description = "Strict SSL may be blocking corporate certificates"
        solution = "Try: npm config set strict-ssl false"
        priority = "Medium"
    }
}

# Check authentication
if (-not $AuthSuccess -and $Registry -match "artifactory") {
    $Recommendations += @{
        issue = "Authentication"
        description = "Artifactory may require authentication"
        solution = "Try: npm login --registry $Registry"
        priority = "High"
    }
}

# Check proxy settings
if (-not $TcpTest -and (-not $Proxy -and -not $HttpsProxy)) {
    $Recommendations += @{
        issue = "Proxy Configuration"
        description = "Corporate network may require proxy settings"
        solution = "Ask IT for proxy settings and use: npm config set proxy http://proxy:port"
        priority = "High"
    }
}

# Check cache issues
if ($PingSuccess -but -not $SearchSuccess) {
    $Recommendations += @{
        issue = "NPM Cache"
        description = "Corrupted cache may cause search failures"
        solution = "Try: npm cache clean --force"
        priority = "Low"
    }
}

$Diagnostics.recommendations = $Recommendations

Write-Step "Generating recommendations..."

Write-Host "`n📋 DIAGNOSTIC SUMMARY" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Yellow

Write-Host "`nConfiguration:" -ForegroundColor Cyan
Write-Host "  Registry: $Registry"
Write-Host "  NPM Version: $NpmVersion"
Write-Host "  Node Version: $NodeVersion"
Write-Host "  Strict SSL: $StrictSsl"

Write-Host "`nConnectivity:" -ForegroundColor Cyan
Write-Host "  DNS Resolution: $(if ($Diagnostics.network.dns_resolution) { '✅ Working' } else { '❌ Failed' })"
Write-Host "  TCP Connection: $(if ($Diagnostics.network.tcp_connection) { '✅ Working' } else { '❌ Failed' })"
Write-Host "  HTTP Status: $($Diagnostics.network.http_status)"

Write-Host "`nRegistry Functions:" -ForegroundColor Cyan
Write-Host "  Ping: $(if ($PingSuccess) { '✅ Working' } else { '❌ Failed' })"
Write-Host "  Search: $(if ($SearchSuccess) { '✅ Working' } else { '❌ Failed' })"
Write-Host "  Auth: $(if ($AuthSuccess) { '✅ Working' } else { '⚠️ Not authenticated' })"

if ($Recommendations.Count -gt 0) {
    Write-Host "`n🔧 RECOMMENDATIONS" -ForegroundColor Yellow
    Write-Host "================================================================" -ForegroundColor Yellow
    
    foreach ($rec in $Recommendations) {
        $priorityColor = switch ($rec.priority) {
            "High" { "Red" }
            "Medium" { "Yellow" }
            "Low" { "Green" }
        }
        
        Write-Host "`n[$($rec.priority) Priority] $($rec.issue)" -ForegroundColor $priorityColor
        Write-Host "  Issue: $($rec.description)"
        Write-Host "  Solution: $($rec.solution)" -ForegroundColor Cyan
    }
} else {
    Write-Success "No issues detected! Your NPM + Artifactory setup looks good."
}

# Save detailed log
$Diagnostics | ConvertTo-Json -Depth 10 | Out-File $LogFile -Encoding UTF8
Write-Info "Detailed diagnostics saved to: $LogFile"

Write-Host "`n🚀 QUICK FIX COMMANDS" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host "If you're getting 404s, try these commands in order:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Clear cache and reset settings:" -ForegroundColor White
Write-Host "   npm cache clean --force"
Write-Host "   npm config set strict-ssl false"
Write-Host "   npm config set fetch-timeout 300000"
Write-Host ""
Write-Host "2. Test with public registry:" -ForegroundColor White
Write-Host "   npm install --registry https://registry.npmjs.org/"
Write-Host ""
Write-Host "3. Login to Artifactory:" -ForegroundColor White
Write-Host "   npm login --registry $Registry"
Write-Host ""
Write-Host "4. Check registry URL format:" -ForegroundColor White
Write-Host "   npm config set registry https://your-company.jfrog.io/artifactory/api/npm/npm/"

Write-Host "`nDiagnostics complete! Check $LogFile for detailed technical information." -ForegroundColor Green