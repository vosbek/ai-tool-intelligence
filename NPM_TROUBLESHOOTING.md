# NPM Artifactory Troubleshooting Guide

## Quick Start

If you're getting 404 errors from your enterprise Artifactory, run these scripts in order:

1. **Diagnose the problem:**
   ```cmd
   scripts\troubleshoot-npm.bat
   ```

2. **Apply common fixes:**
   ```cmd
   scripts\fix-npm-artifactory.bat
   ```

3. **If still failing, try fallback installation:**
   ```cmd
   scripts\npm-fallback-install.bat
   ```

4. **For detailed PowerShell analysis:**
   ```powershell
   .\scripts\diagnose-artifactory.ps1
   ```

## Common Artifactory 404 Causes

### 1. Wrong Registry URL Format
**Symptoms:** All packages give 404 errors
**Solution:** Artifactory URLs must include `/api/npm/` path
```cmd
# Wrong:
npm config set registry https://company.jfrog.io/artifactory/npm/

# Correct:
npm config set registry https://company.jfrog.io/artifactory/api/npm/npm-repo/
```

### 2. Authentication Issues
**Symptoms:** Some packages work, others give 404
**Solution:** Login to Artifactory
```cmd
npm login --registry https://your-artifactory-url/
```

### 3. SSL Certificate Problems
**Symptoms:** CERT_UNTRUSTED or SSL errors
**Solution:** Disable strict SSL for corporate certs
```cmd
npm config set strict-ssl false
```

### 4. Proxy/Firewall Blocking
**Symptoms:** Connection timeouts or network errors
**Solution:** Configure NPM proxy settings
```cmd
npm config set proxy http://proxy.company.com:8080
npm config set https-proxy http://proxy.company.com:8080
```

### 5. Package Not in Artifactory
**Symptoms:** Specific packages give 404, others work
**Solution:** Use public registry for missing packages
```cmd
npm install package-name --registry https://registry.npmjs.org/
```

## Emergency Workarounds

### Option A: Temporary Public Registry
```cmd
# Switch to public NPM temporarily
npm config set registry https://registry.npmjs.org/
npm install
# Switch back when done
npm config set registry https://your-artifactory-url/
```

### Option B: Use Yarn Instead
```cmd
# Install Yarn if not available
npm install -g yarn --registry https://registry.npmjs.org/
# Use Yarn for package installation
yarn install
```

### Option C: Mixed Registry Approach
```cmd
# Use different registries for different scopes
npm config set @company:registry https://artifactory.company.com/
npm config set registry https://registry.npmjs.org/
```

## Registry URL Formats by Platform

### JFrog Artifactory
```
https://company.jfrog.io/artifactory/api/npm/npm-repo/
```

### Sonatype Nexus
```
https://nexus.company.com/repository/npm-public/
```

### Azure Artifacts
```
https://pkgs.dev.azure.com/company/_packaging/feed/npm/registry/
```

### AWS CodeArtifact
```
https://company-domain.d.codeartifact.region.amazonaws.com/npm/repository/
```

## Advanced Troubleshooting

### Check Registry Health
```cmd
# Test registry connectivity
npm ping

# Test package search
npm search react --no-optional

# Check authentication
npm whoami
```

### Clear All NPM Data
```cmd
# Nuclear option - clears everything
npm cache clean --force
rm -rf node_modules
rm package-lock.json
npm install
```

### Debug with Verbose Logging
```cmd
# See exactly what NPM is doing
npm install --verbose --loglevel=verbose
```

### Check Network Connectivity
```cmd
# Test DNS resolution
nslookup your-artifactory-host.com

# Test HTTP connectivity
curl -I https://your-artifactory-url/

# Test with specific headers
curl -H "User-Agent: npm" https://your-artifactory-url/
```

## Environment-Specific Fixes

### Windows Corporate Environment
```cmd
# Disable Windows certificate validation
npm config set strict-ssl false
npm config set cafile ""

# Increase timeouts for slow networks
npm config set fetch-timeout 600000
npm config set fetch-retry-maxtimeout 600000
```

### Behind Corporate Proxy
```cmd
# Set proxy with authentication
npm config set proxy http://username:password@proxy:port
npm config set https-proxy http://username:password@proxy:port

# Use registry with proxy bypass
npm config set registry https://registry.npmjs.org/ --proxy=false
```

### VPN Required Networks
```cmd
# Check if VPN affects registry access
# Try with/without VPN connection
# May need different registry URLs for internal vs external access
```

## Configuration Files

### Global NPM Config (~/.npmrc)
```ini
registry=https://your-artifactory-url/
strict-ssl=false
fetch-timeout=300000
legacy-peer-deps=true
```

### Project-Specific (.npmrc in project root)
```ini
registry=https://your-artifactory-url/
@company:registry=https://internal-registry.company.com/
```

### Package.json Registry Override
```json
{
  "publishConfig": {
    "registry": "https://your-artifactory-url/"
  }
}
```

## IT Department Questions

When contacting IT support, provide this information:

1. **Registry URL format:** What's the exact Artifactory NPM endpoint?
2. **Authentication:** Do I need credentials? What type?
3. **Proxy settings:** What are the proxy server details?
4. **VPN requirements:** Must I be on VPN to access Artifactory?
5. **Package availability:** Are all public NPM packages mirrored?
6. **SSL certificates:** Are there custom corporate certificates?
7. **Firewall rules:** Are there any blocked domains or ports?

## Success Verification

After applying fixes, verify with:

```cmd
# Test basic functionality
npm ping
npm search react
npm install --dry-run

# Test in your project
cd frontend
npm install
npm start
```

If everything works, commit your .npmrc settings to avoid future issues.

## Script Reference

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `troubleshoot-npm.bat` | Comprehensive diagnostics | First step when having issues |
| `fix-npm-artifactory.bat` | Apply common fixes | After identifying the problem |
| `npm-fallback-install.bat` | Multiple installation strategies | When fixes don't work |
| `diagnose-artifactory.ps1` | Advanced PowerShell analysis | For detailed technical diagnosis |

All scripts create log files for IT support if needed.