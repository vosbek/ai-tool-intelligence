# tests/__init__.py - Test package initialization
"""
Unit testing framework for AI Tool Intelligence Platform

This package contains comprehensive unit tests for all enhanced strand agent tools
and supporting infrastructure including free APIs integration and Firecrawl MCP.
"""

import os
import sys

# Add backend directory to path for importing modules under test
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)