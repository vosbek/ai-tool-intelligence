#!/usr/bin/env python3
"""
Bundle Python dependencies for offline installation.
This script downloads all required packages and creates a bundled installer.
"""

import os
import subprocess
import sys
import zipfile
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Command failed: {cmd}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def bundle_python_packages():
    """Download and bundle Python packages."""
    print("🔄 Bundling Python dependencies...")
    
    # Create bundle directory
    bundle_dir = Path("dependencies-bundle")
    bundle_dir.mkdir(exist_ok=True)
    
    # Download minimal dependencies
    print("📦 Downloading minimal dependencies...")
    if not run_command(f"pip download -r requirements-minimal.txt -d {bundle_dir}/minimal", cwd="."):
        print("❌ Failed to download minimal dependencies")
        return False
    
    # Download AI dependencies (optional)
    print("📦 Downloading AI dependencies...")
    ai_bundle_dir = bundle_dir / "ai"
    ai_bundle_dir.mkdir(exist_ok=True)
    
    # Try to download AI dependencies, but don't fail if they don't work
    try:
        if not run_command(f"pip download -r requirements-ai.txt -d {bundle_dir}/ai", cwd="."):
            print("⚠️  Some AI dependencies may not be available - this is OK")
    except Exception as e:
        print(f"⚠️  AI dependencies download failed: {e}")
    
    print("✅ Python dependencies bundled successfully")
    return True

def bundle_node_packages():
    """Bundle Node.js packages."""
    print("🔄 Bundling Node.js dependencies...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Create node_modules bundle
    if not run_command("npm ci", cwd=frontend_dir):
        print("❌ Failed to install Node.js dependencies")
        return False
    
    # Create a tarball of node_modules
    bundle_dir = Path("dependencies-bundle")
    bundle_dir.mkdir(exist_ok=True)
    
    print("📦 Creating Node.js bundle...")
    if not run_command(f"tar -czf ../dependencies-bundle/node_modules.tar.gz node_modules", cwd=frontend_dir):
        # Try with 7zip as fallback for Windows
        if not run_command(f"7z a ../dependencies-bundle/node_modules.7z node_modules", cwd=frontend_dir):
            print("⚠️  Could not create Node.js bundle - install manually")
            return False
    
    print("✅ Node.js dependencies bundled successfully")
    return True

def create_offline_installer():
    """Create the offline installer."""
    print("🔄 Creating offline installer...")
    
    bundle_dir = Path("dependencies-bundle")
    
    # Create installer script
    installer_script = """@echo off
echo ========================================
echo AI Tool Intelligence - Offline Installer
echo ========================================
echo.
echo Installing from bundled dependencies...
echo.

echo Setting up Python backend...
cd backend

echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Installing minimal Python dependencies from bundle...
venv\\Scripts\\pip.exe install --no-index --find-links ../dependencies-bundle/minimal -r ../requirements-minimal.txt
if errorlevel 1 (
    echo ERROR: Failed to install minimal dependencies
    pause
    exit /b 1
)

echo Creating .env file...
if not exist ".env" (
    copy ".env.example" ".env"
    echo .env file created
)

cd ..

echo Setting up React frontend...
cd frontend

echo Extracting Node.js dependencies...
if exist "../dependencies-bundle/node_modules.tar.gz" (
    tar -xzf "../dependencies-bundle/node_modules.tar.gz"
) else if exist "../dependencies-bundle/node_modules.7z" (
    7z x "../dependencies-bundle/node_modules.7z"
) else (
    echo Installing Node.js dependencies online...
    npm install
)

cd ..

echo ========================================
echo Offline Installation Complete!
echo ========================================
echo.
echo To start the platform:
echo   windows\\start-windows.bat
echo.
echo To install AI features later:
echo   cd backend
echo   venv\\Scripts\\pip.exe install --no-index --find-links ../dependencies-bundle/ai -r ../requirements-ai.txt
echo.
pause
"""
    
    with open(bundle_dir / "install-offline.bat", "w") as f:
        f.write(installer_script)
    
    # Create README for the bundle
    readme_content = """# Offline Installation Bundle

This bundle contains all dependencies needed to install the AI Tool Intelligence Platform offline.

## Contents:
- minimal/ - Core Python dependencies (Flask, SQLAlchemy, etc.)
- ai/ - Optional AI dependencies (boto3, strands-agents, etc.)
- node_modules.tar.gz - Frontend dependencies
- install-offline.bat - Automated installer

## Usage:
1. Copy this entire dependencies-bundle folder to the target machine
2. Run install-offline.bat
3. Start the platform with windows\\start-windows.bat

## Manual Installation:
If the automated installer fails, you can install manually:

### Backend (Core):
```cmd
cd backend
python -m venv venv
venv\\Scripts\\pip.exe install --no-index --find-links ../dependencies-bundle/minimal -r ../requirements-minimal.txt
```

### Backend (AI Features):
```cmd
cd backend
venv\\Scripts\\pip.exe install --no-index --find-links ../dependencies-bundle/ai -r ../requirements-ai.txt
```

### Frontend:
```cmd
cd frontend
tar -xzf ../dependencies-bundle/node_modules.tar.gz
```

## Size Optimization:
- The minimal bundle is ~50MB
- Full bundle with AI features is ~200MB
- Node.js dependencies are ~100MB

This is much more reliable than downloading 100+ packages individually.
"""
    
    with open(bundle_dir / "README.md", "w") as f:
        f.write(readme_content)
    
    print("✅ Offline installer created successfully")
    print(f"📁 Bundle location: {bundle_dir.absolute()}")
    print(f"📊 Bundle size: {get_dir_size(bundle_dir):.1f} MB")
    
    return True

def get_dir_size(path):
    """Get directory size in MB."""
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total += os.path.getsize(filepath)
    return total / (1024 * 1024)

def main():
    """Main function."""
    print("🚀 AI Tool Intelligence - Dependency Bundler")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("requirements-minimal.txt").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Bundle Python packages
    if not bundle_python_packages():
        print("❌ Failed to bundle Python packages")
        sys.exit(1)
    
    # Bundle Node.js packages
    if not bundle_node_packages():
        print("⚠️  Node.js bundling failed, but continuing...")
    
    # Create offline installer
    if not create_offline_installer():
        print("❌ Failed to create offline installer")
        sys.exit(1)
    
    print("\n🎉 Dependency bundling complete!")
    print("\nNext steps:")
    print("1. Copy the 'dependencies-bundle' folder to target machines")
    print("2. Run 'dependencies-bundle/install-offline.bat' on target machines")
    print("3. Start the platform with 'windows/start-windows.bat'")

if __name__ == "__main__":
    main()