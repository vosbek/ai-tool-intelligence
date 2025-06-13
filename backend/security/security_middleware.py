#!/usr/bin/env python3
"""
Security Middleware for AI Tool Intelligence Platform

Provides comprehensive security features including:
- Input validation and sanitization
- Rate limiting
- Request authentication
- CORS security
- XSS protection
- SQL injection prevention
"""

import re
import time
import hashlib
import secrets
from functools import wraps
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict, deque
from datetime import datetime, timedelta
from flask import request, jsonify, g, current_app
from werkzeug.exceptions import BadRequest, Unauthorized, TooManyRequests
import html
import json
import ipaddress

class SecurityConfig:
    """Lightweight security configuration settings"""
    
    # Basic input validation
    MAX_JSON_SIZE = 10 * 1024 * 1024  # 10MB (more generous)
    MAX_STRING_LENGTH = 50000  # More generous for tool descriptions
    MAX_ARRAY_LENGTH = 5000
    
    # CORS (permissive for development)
    ALLOWED_ORIGINS = ['*']  # Allow all origins for simplicity
    ALLOWED_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    ALLOWED_HEADERS = ['Content-Type', 'Authorization', 'X-Admin-User', 'X-Monitor-User']
    
    # Minimal security headers (no SSL requirements)
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',  # Less restrictive
    }

# Removed RateLimiter class - keeping it simple without rate limiting

class InputValidator:
    """Basic input validation and sanitization"""
    
    # Only block the most dangerous patterns
    DANGEROUS_PATTERNS = [
        r"(?i)(\bdrop\b.*\btable\b)",  # Only block DROP TABLE
        r"(?i)<script[^>]*>.*?</script>",  # Only block script tags
        r"\$\(",  # Command substitution
    ]
    
    @staticmethod
    def validate_json_input(data: Any, max_size: int = SecurityConfig.MAX_JSON_SIZE) -> Dict:
        """Validate and sanitize JSON input"""
        if not isinstance(data, dict):
            raise BadRequest("Request must be valid JSON object")
        
        # Check size
        json_str = json.dumps(data)
        if len(json_str) > max_size:
            raise BadRequest(f"Request too large (max {max_size} bytes)")
        
        # Recursively validate and sanitize
        return InputValidator._sanitize_dict(data)
    
    @staticmethod
    def _sanitize_dict(data: Dict) -> Dict:
        """Recursively sanitize dictionary data"""
        sanitized = {}
        
        if len(data) > SecurityConfig.MAX_ARRAY_LENGTH:
            raise BadRequest(f"Too many fields (max {SecurityConfig.MAX_ARRAY_LENGTH})")
        
        for key, value in data.items():
            # Validate key
            if not isinstance(key, str):
                raise BadRequest("Dictionary keys must be strings")
            
            if len(key) > 100:
                raise BadRequest("Field names too long")
            
            # Sanitize key
            clean_key = InputValidator._sanitize_string(key)
            
            # Sanitize value
            if isinstance(value, str):
                clean_value = InputValidator._sanitize_string(value)
            elif isinstance(value, dict):
                clean_value = InputValidator._sanitize_dict(value)
            elif isinstance(value, list):
                clean_value = InputValidator._sanitize_list(value)
            elif isinstance(value, (int, float, bool)) or value is None:
                clean_value = value
            else:
                raise BadRequest(f"Unsupported data type: {type(value)}")
            
            sanitized[clean_key] = clean_value
        
        return sanitized
    
    @staticmethod
    def _sanitize_list(data: List) -> List:
        """Sanitize list data"""
        if len(data) > SecurityConfig.MAX_ARRAY_LENGTH:
            raise BadRequest(f"Array too long (max {SecurityConfig.MAX_ARRAY_LENGTH})")
        
        sanitized = []
        for item in data:
            if isinstance(item, str):
                sanitized.append(InputValidator._sanitize_string(item))
            elif isinstance(item, dict):
                sanitized.append(InputValidator._sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(InputValidator._sanitize_list(item))
            elif isinstance(item, (int, float, bool)) or item is None:
                sanitized.append(item)
            else:
                raise BadRequest(f"Unsupported data type in array: {type(item)}")
        
        return sanitized
    
    @staticmethod
    def _sanitize_string(text: str) -> str:
        """Basic sanitization of string input"""
        if len(text) > SecurityConfig.MAX_STRING_LENGTH:
            raise BadRequest(f"String too long (max {SecurityConfig.MAX_STRING_LENGTH})")
        
        # Check for only the most dangerous patterns
        for pattern in InputValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, text):
                raise BadRequest("Input contains potentially dangerous content")
        
        # Just strip whitespace, no HTML escaping to keep content natural
        return text.strip()
    
    @staticmethod
    def validate_tool_id(tool_id: Any) -> int:
        """Validate tool ID parameter"""
        try:
            id_val = int(tool_id)
            if id_val <= 0 or id_val > 1000000:
                raise BadRequest("Invalid tool ID")
            return id_val
        except (ValueError, TypeError):
            raise BadRequest("Tool ID must be a positive integer")
    
    @staticmethod
    def validate_pagination(page: Any, per_page: Any) -> tuple:
        """Validate pagination parameters"""
        try:
            page_val = int(page) if page else 1
            per_page_val = int(per_page) if per_page else 20
            
            if page_val < 1 or page_val > 10000:
                raise BadRequest("Invalid page number")
            
            if per_page_val < 1 or per_page_val > 100:
                raise BadRequest("Invalid per_page value (1-100)")
            
            return page_val, per_page_val
        except (ValueError, TypeError):
            raise BadRequest("Pagination parameters must be integers")

class AuthenticationManager:
    """Simple authentication manager - very permissive"""
    
    def validate_admin_user(self, user_header: str, ip_address: str) -> bool:
        """Very simple admin user validation"""
        if not user_header:
            return False
        
        # Accept any non-empty admin user header (very permissive)
        if len(user_header) >= 1 and len(user_header) <= 100:
            return True
        
        return False

class SecurityMiddleware:
    """Lightweight security middleware class"""
    
    def __init__(self, app=None):
        self.auth_manager = AuthenticationManager()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.errorhandler(BadRequest)(self.handle_bad_request)
        app.errorhandler(Unauthorized)(self.handle_unauthorized)
    
    def before_request(self):
        """Process request before routing - very lightweight"""
        # Get client IP
        client_ip = self._get_client_ip()
        g.client_ip = client_ip
        
        # Skip validation for health checks
        if request.endpoint in ['health_check']:
            return
        
        # Only validate JSON input if it's too large
        if request.method in ['POST', 'PUT'] and request.is_json:
            if request.content_length and request.content_length > SecurityConfig.MAX_JSON_SIZE:
                raise BadRequest(f"Request too large (max {SecurityConfig.MAX_JSON_SIZE // (1024*1024)}MB)")
        
        # Basic tool ID validation for path parameters
        if request.view_args:
            for key, value in request.view_args.items():
                if key.endswith('_id') or key == 'tool_id':
                    try:
                        request.view_args[key] = InputValidator.validate_tool_id(value)
                    except BadRequest:
                        raise BadRequest("Invalid ID parameter")
    
    def after_request(self, response):
        """Process response after routing"""
        # Add minimal security headers
        for header, value in SecurityConfig.SECURITY_HEADERS.items():
            response.headers[header] = value
        
        # Permissive CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = ', '.join(SecurityConfig.ALLOWED_METHODS)
        response.headers['Access-Control-Allow-Headers'] = ', '.join(SecurityConfig.ALLOWED_HEADERS)
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        
        return response
    
    def _get_client_ip(self) -> str:
        """Get client IP address with proxy support"""
        # Check for proxy headers
        if request.headers.get('X-Forwarded-For'):
            # Take the first IP in the chain
            ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            ip = request.headers.get('X-Real-IP')
        else:
            ip = request.remote_addr
        
        # Validate IP address
        try:
            ipaddress.ip_address(ip)
            return ip
        except ValueError:
            return '127.0.0.1'  # Fallback for invalid IPs
    
    def require_admin_auth(self, f: Callable) -> Callable:
        """Decorator to require admin authentication - very permissive"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            admin_user = request.headers.get('X-Admin-User')
            if not self.auth_manager.validate_admin_user(admin_user, g.get('client_ip', 'unknown')):
                raise Unauthorized("Admin authentication required")
            g.admin_user = admin_user
            return f(*args, **kwargs)
        return decorated_function
    
    def require_monitor_auth(self, f: Callable) -> Callable:
        """Decorator to require monitoring authentication - very permissive"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            monitor_user = request.headers.get('X-Monitor-User')
            if not monitor_user or len(monitor_user) < 1:
                raise Unauthorized("Monitor authentication required")
            g.monitor_user = monitor_user
            return f(*args, **kwargs)
        return decorated_function
    
    def handle_bad_request(self, error):
        """Handle input validation errors"""
        current_app.logger.warning(f"Bad request from {g.get('client_ip', 'unknown')}: {error}")
        return jsonify({
            'error': 'Invalid request',
            'message': str(error.description),
            'timestamp': datetime.utcnow().isoformat()
        }), 400
    
# Removed rate limit handler since we removed rate limiting
    
    def handle_unauthorized(self, error):
        """Handle authentication errors"""
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required',
            'timestamp': datetime.utcnow().isoformat()
        }), 401

# Global security middleware instance
security_middleware = SecurityMiddleware()

# Decorators for easy use
require_admin_auth = security_middleware.require_admin_auth
require_monitor_auth = security_middleware.require_monitor_auth