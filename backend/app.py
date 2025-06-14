#!/usr/bin/env python3
"""
app.py - Main application entry point for AI Tool Intelligence Platform
This file provides the traditional Flask app.py entry point that scripts expect.
"""

import os
import sys

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ai_tool_intelligence.main import create_app

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Development server configuration
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    
    print(f"🚀 Starting AI Tool Intelligence Platform...")
    print(f"📍 Running on http://{host}:{port}")
    print(f"🔧 Debug mode: {debug_mode}")
    print(f"📁 Working directory: {os.getcwd()}")
    
    app.run(debug=debug_mode, host=host, port=port)