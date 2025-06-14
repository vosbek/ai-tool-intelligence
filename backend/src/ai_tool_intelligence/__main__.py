#!/usr/bin/env python3
"""
AI Tool Intelligence Platform - Main Entry Point
Entry point for running the application as a module
"""

from .main import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)