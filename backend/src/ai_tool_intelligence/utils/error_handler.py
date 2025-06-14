#!/usr/bin/env python3
"""
Comprehensive Error Handling and Recovery System

Provides:
- Global exception handling
- Circuit breaker pattern for external services
- Graceful degradation
- Recovery mechanisms
- Error tracking and reporting
"""

import time
import traceback
import threading
from enum import Enum
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict, deque
from flask import current_app, request, jsonify, g
import logging
import json

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing recovery

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for classification"""
    NETWORK = "network"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    PROCESSING = "processing"
    SYSTEM = "system"
    UNKNOWN = "unknown"

class CircuitBreakerConfig:
    """Configuration for circuit breakers"""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 expected_exception: type = Exception,
                 success_threshold: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.success_threshold = success_threshold

class CircuitBreaker:
    """Circuit breaker implementation for external service calls"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        with self.lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise CircuitBreakerError(f"Circuit breaker {self.name} is OPEN")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            
            except self.config.expected_exception as e:
                self._on_failure()
                raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        
        return (time.time() - self.last_failure_time) >= self.config.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN

class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open"""
    pass

class ErrorTracker:
    """Track and analyze application errors"""
    
    def __init__(self):
        self.errors = deque(maxlen=1000)  # Keep last 1000 errors
        self.error_counts = defaultdict(int)
        self.lock = threading.Lock()
    
    def record_error(self, error: Exception, category: ErrorCategory, 
                    severity: ErrorSeverity, context: Dict[str, Any] = None):
        """Record an error occurrence"""
        with self.lock:
            error_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'error_type': type(error).__name__,
                'error_message': str(error),
                'category': category.value,
                'severity': severity.value,
                'context': context or {},
                'traceback': traceback.format_exc()
            }
            
            # Add request context if available
            if request:
                error_data['request'] = {
                    'method': request.method,
                    'url': request.url,
                    'endpoint': request.endpoint,
                    'client_ip': getattr(g, 'client_ip', 'unknown')
                }
            
            self.errors.append(error_data)
            self.error_counts[f"{category.value}:{type(error).__name__}"] += 1
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the specified time period"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        recent_errors = [
            error for error in self.errors
            if datetime.fromisoformat(error['timestamp']) > cutoff
        ]
        
        # Categorize errors
        by_category = defaultdict(int)
        by_severity = defaultdict(int)
        by_type = defaultdict(int)
        
        for error in recent_errors:
            by_category[error['category']] += 1
            by_severity[error['severity']] += 1
            by_type[error['error_type']] += 1
        
        return {
            'total_errors': len(recent_errors),
            'by_category': dict(by_category),
            'by_severity': dict(by_severity),
            'by_type': dict(by_type),
            'recent_errors': recent_errors[-10:] if recent_errors else []
        }

class ErrorHandler:
    """Main error handling and recovery system"""
    
    def __init__(self):
        self.circuit_breakers = {}
        self.error_tracker = ErrorTracker()
        self.fallback_handlers = {}
        self.logger = logging.getLogger(__name__)
    
    def init_app(self, app):
        """Initialize error handler with Flask app"""
        app.errorhandler(Exception)(self.handle_global_exception)
        app.errorhandler(500)(self.handle_internal_error)
        app.errorhandler(404)(self.handle_not_found)
        app.errorhandler(CircuitBreakerError)(self.handle_circuit_breaker_error)
        
        # Initialize circuit breakers for external services
        self._setup_circuit_breakers()
    
    def _setup_circuit_breakers(self):
        """Setup circuit breakers for external services"""
        # AWS Bedrock circuit breaker
        self.circuit_breakers['aws_bedrock'] = CircuitBreaker(
            'aws_bedrock',
            CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30,
                expected_exception=Exception
            )
        )
        
        # External API circuit breaker
        self.circuit_breakers['external_api'] = CircuitBreaker(
            'external_api',
            CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60,
                expected_exception=Exception
            )
        )
        
        # Database circuit breaker
        self.circuit_breakers['database'] = CircuitBreaker(
            'database',
            CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=10,
                expected_exception=Exception
            )
        )
    
    def with_circuit_breaker(self, service_name: str):
        """Decorator to protect function with circuit breaker"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if service_name not in self.circuit_breakers:
                    self.logger.warning(f"No circuit breaker configured for {service_name}")
                    return func(*args, **kwargs)
                
                circuit_breaker = self.circuit_breakers[service_name]
                return circuit_breaker.call(func, *args, **kwargs)
            
            return wrapper
        return decorator
    
    def with_fallback(self, fallback_func: Callable):
        """Decorator to provide fallback functionality"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self.logger.warning(f"Primary function failed, using fallback: {e}")
                    return fallback_func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def handle_global_exception(self, error: Exception):
        """Handle uncaught exceptions"""
        # Categorize the error
        category = self._categorize_error(error)
        severity = self._assess_severity(error, category)
        
        # Record the error
        self.error_tracker.record_error(error, category, severity)
        
        # Log the error
        self.logger.error(f"Uncaught exception: {error}", exc_info=True)
        
        # Return appropriate response
        if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            return jsonify({
                'error': 'Internal server error',
                'message': 'A serious error occurred. Please try again later.',
                'error_id': self._generate_error_id(),
                'timestamp': datetime.utcnow().isoformat()
            }), 500
        else:
            return jsonify({
                'error': 'Server error',
                'message': 'An error occurred while processing your request.',
                'timestamp': datetime.utcnow().isoformat()
            }), 500
    
    def handle_internal_error(self, error):
        """Handle 500 internal server errors"""
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred. Please try again later.',
            'timestamp': datetime.utcnow().isoformat()
        }), 500
    
    def handle_not_found(self, error):
        """Handle 404 not found errors"""
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found.',
            'timestamp': datetime.utcnow().isoformat()
        }), 404
    
    def handle_circuit_breaker_error(self, error: CircuitBreakerError):
        """Handle circuit breaker errors"""
        self.logger.warning(f"Circuit breaker triggered: {error}")
        
        return jsonify({
            'error': 'Service temporarily unavailable',
            'message': 'The requested service is experiencing issues. Please try again later.',
            'retry_after': 60,
            'timestamp': datetime.utcnow().isoformat()
        }), 503
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize error based on type and context"""
        error_type = type(error).__name__.lower()
        error_message = str(error).lower()
        
        if 'connection' in error_message or 'network' in error_message:
            return ErrorCategory.NETWORK
        elif 'database' in error_message or 'sql' in error_message:
            return ErrorCategory.DATABASE
        elif 'bedrock' in error_message or 'aws' in error_message:
            return ErrorCategory.EXTERNAL_API
        elif 'validation' in error_message or 'invalid' in error_message:
            return ErrorCategory.VALIDATION
        elif 'auth' in error_message or 'unauthorized' in error_message:
            return ErrorCategory.AUTHENTICATION
        elif 'timeout' in error_message or 'processing' in error_message:
            return ErrorCategory.PROCESSING
        elif 'system' in error_message or 'memory' in error_message:
            return ErrorCategory.SYSTEM
        else:
            return ErrorCategory.UNKNOWN
    
    def _assess_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Assess error severity"""
        error_type = type(error).__name__
        
        # Critical errors
        if error_type in ['MemoryError', 'SystemExit', 'KeyboardInterrupt']:
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        if category in [ErrorCategory.DATABASE, ErrorCategory.SYSTEM]:
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        if category in [ErrorCategory.EXTERNAL_API, ErrorCategory.PROCESSING]:
            return ErrorSeverity.MEDIUM
        
        # Low severity errors
        return ErrorSeverity.LOW
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID for tracking"""
        import hashlib
        import time
        
        timestamp = str(time.time())
        return hashlib.md5(timestamp.encode()).hexdigest()[:8]
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health based on recent errors"""
        error_summary = self.error_tracker.get_error_summary(hours=1)
        
        # Assess health based on error rates
        total_errors = error_summary['total_errors']
        critical_errors = error_summary['by_severity'].get('critical', 0)
        high_errors = error_summary['by_severity'].get('high', 0)
        
        if critical_errors > 0:
            health_status = 'critical'
            health_score = 0
        elif high_errors > 5:
            health_status = 'degraded'
            health_score = 25
        elif total_errors > 20:
            health_status = 'warning'
            health_score = 50
        elif total_errors > 5:
            health_status = 'minor_issues'
            health_score = 75
        else:
            health_status = 'healthy'
            health_score = 100
        
        return {
            'status': health_status,
            'score': health_score,
            'error_summary': error_summary,
            'circuit_breakers': {
                name: breaker.state.value
                for name, breaker in self.circuit_breakers.items()
            }
        }

# Global error handler instance
error_handler = ErrorHandler()

# Decorators for easy use
def with_circuit_breaker(service_name: str):
    """Decorator to protect function with circuit breaker"""
    return error_handler.with_circuit_breaker(service_name)

def with_fallback(fallback_func: Callable):
    """Decorator to provide fallback functionality"""
    return error_handler.with_fallback(fallback_func)

def safe_execute(func: Callable, fallback_result=None, category: ErrorCategory = ErrorCategory.UNKNOWN):
    """Safely execute a function with error handling"""
    try:
        return func()
    except Exception as e:
        error_handler.error_tracker.record_error(e, category, ErrorSeverity.MEDIUM)
        error_handler.logger.warning(f"Safe execution failed: {e}")
        return fallback_result