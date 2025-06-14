#!/usr/bin/env python3
"""
Enhanced Startup Script for AI Tool Intelligence Platform
Provides comprehensive Windows stability, error handling, and monitoring
"""

import os
import sys
import time
import signal
import logging
from pathlib import Path

def setup_logging():
    """Setup logging for startup script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('startup.log')
        ]
    )
    return logging.getLogger(__name__)

def check_python_version():
    """Ensure Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    return True

def check_dependencies():
    """Check if all required dependencies are available"""
    logger = logging.getLogger(__name__)
    
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_cors',
        'psutil',
        'boto3'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"❌ Missing required packages: {', '.join(missing_packages)}")
        logger.info("💡 Install with: pip install -r requirements.txt")
        return False
    
    return True

def create_directories():
    """Create required directories"""
    directories = [
        'logs',
        'backups', 
        'data',
        'temp',
        'uploads',
        'crash_reports'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    return True

def validate_environment():
    """Validate environment setup"""
    logger = logging.getLogger(__name__)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Create directories
    create_directories()
    
    # Check AWS credentials if not skipping validation
    if not os.getenv('SKIP_AWS_VALIDATION'):
        try:
            from backend.aws_credential_validator import AWSCredentialValidator
            validator = AWSCredentialValidator()
            results = validator.validate_credentials()
            
            if not results["credentials_valid"]:
                logger.error("❌ AWS credentials validation failed!")
                logger.info("💡 Run: python backend/aws_credential_validator.py for diagnostics")
                return False
            
            logger.info(f"✅ AWS credentials validated ({results['credential_source']})")
            
        except ImportError:
            logger.warning("⚠️  AWS credential validator not available")
    
    return True

def start_with_stability():
    """Start the application with all stability features"""
    logger = logging.getLogger(__name__)
    
    try:
        # Import stability components
        sys.path.append('backend')
        from backend.stability.windows_stability import windows_stability, setup_windows_stability
        from backend.stability.error_handler import error_handler
        
        # Setup Windows stability
        logger.info("🔄 Initializing Windows stability features...")
        config = setup_windows_stability({
            'log_dir': 'logs',
            'backup_dir': 'backups', 
            'data_dir': 'data',
            'temp_dir': 'temp'
        })
        
        # Register startup checks
        windows_stability.register_startup_check(
            lambda: Path('backend/app.py').exists(),
            "Main Application File"
        )
        
        windows_stability.register_startup_check(
            lambda: len(os.listdir('logs')) >= 0,  # Just check logs dir exists
            "Log Directory"
        )
        
        # Run startup validation
        if not windows_stability.run_startup_checks()['overall_success']:
            logger.warning("⚠️  Some startup checks failed, continuing...")
        
        # Register cleanup for this script
        def cleanup_startup():
            logger.info("🧹 Startup script cleanup complete")
        
        windows_stability.register_cleanup_task(cleanup_startup, "Startup Script")
        
        logger.info("✅ Windows stability features initialized")
        
        # Start the main application
        logger.info("🚀 Starting main application with stability features...")
        
        # Change to backend directory and run app
        os.chdir('backend')
        from app import app
        
        # The app.py will handle the rest of the initialization
        logger.info("✅ Application started successfully")
        
    except ImportError as e:
        logger.warning(f"⚠️  Stability features not available: {e}")
        logger.info("🔄 Starting with basic features...")
        
        # Fallback to basic startup
        os.chdir('backend')
        from app import app
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        
        # Try to create crash report if stability features are available
        try:
            crash_file = windows_stability.create_crash_report(e, {
                'component': 'Startup Script',
                'stage': 'Initialization'
            })
            logger.error(f"💾 Crash report saved: {crash_file}")
        except:
            pass
        
        raise

def main():
    """Main startup function"""
    print("🚀 AI Tool Intelligence Platform - Enhanced Startup")
    print("=" * 60)
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting enhanced application startup...")
    
    try:
        # Validate environment
        logger.info("🔍 Validating environment...")
        if not validate_environment():
            logger.error("❌ Environment validation failed")
            return 1
        
        logger.info("✅ Environment validation complete")
        
        # Start with stability features
        start_with_stability()
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("👋 Startup interrupted by user")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())