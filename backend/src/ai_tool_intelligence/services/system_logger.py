# logging_monitoring/system_logger.py - Comprehensive logging system for AI Tool Intelligence Platform

import logging
import json
import sys
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
import traceback
import psutil
import time
from threading import Lock
from pathlib import Path

# Import required modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..models.database import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text


class LogLevel(Enum):
    """Enhanced log levels"""
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    AUDIT = "AUDIT"


class LogCategory(Enum):
    """Log categories for better organization"""
    SYSTEM = "system"
    API = "api"
    DATABASE = "database"
    CURATION = "curation"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    ALERTS = "alerts"
    ADMIN = "admin"
    SECURITY = "security"
    PERFORMANCE = "performance"
    INTEGRATION = "integration"
    USER = "user"


@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: str
    level: LogLevel
    category: LogCategory
    component: str
    message: str
    details: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    trace_id: Optional[str] = None
    execution_time: Optional[float] = None
    memory_usage: Optional[int] = None
    cpu_usage: Optional[float] = None
    error_details: Optional[Dict] = None


@dataclass
class PerformanceMetrics:
    """Performance monitoring metrics"""
    component: str
    operation: str
    start_time: float
    end_time: float
    duration: float
    memory_before: int
    memory_after: int
    memory_delta: int
    cpu_percent: float
    success: bool
    error_message: Optional[str] = None


class SystemLogger:
    """Comprehensive logging system with monitoring capabilities"""
    
    def __init__(self, database_url: str = None, log_dir: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
        self.log_dir = Path(log_dir or os.getenv('LOG_DIR', 'logs'))
        self.log_dir.mkdir(exist_ok=True)
        
        # Thread safety
        self._lock = Lock()
        
        # Database connection
        try:
            self.engine = create_engine(self.database_url)
            self.Session = sessionmaker(bind=self.engine)
            self.db_available = True
        except Exception as e:
            self.db_available = False
            print(f"Warning: Database logging unavailable: {e}")
        
        # Configure structured logging
        self._setup_logging()
        
        # Performance tracking
        self.performance_metrics = []
        self.active_operations = {}
        
        # System monitoring
        self.process = psutil.Process()
        
        print("✅ System Logger initialized")
    
    def _setup_logging(self):
        """Setup comprehensive logging configuration"""
        # Create formatters
        json_formatter = JsonFormatter()
        console_formatter = ConsoleFormatter()
        
        # Setup root logger
        self.logger = logging.getLogger('ai_tools')
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handlers for different log levels
        self._setup_file_handlers(json_formatter)
        
        # Database handler if available
        if self.db_available:
            db_handler = DatabaseLogHandler(self.Session)
            db_handler.setLevel(logging.INFO)
            self.logger.addHandler(db_handler)
    
    def _setup_file_handlers(self, formatter):
        """Setup file handlers for different log categories"""
        # Main application log
        app_handler = logging.FileHandler(self.log_dir / 'application.log')
        app_handler.setLevel(logging.DEBUG)
        app_handler.setFormatter(formatter)
        self.logger.addHandler(app_handler)
        
        # Error log
        error_handler = logging.FileHandler(self.log_dir / 'errors.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
        
        # Security log
        security_handler = logging.FileHandler(self.log_dir / 'security.log')
        security_handler.setLevel(logging.WARNING)
        security_handler.addFilter(SecurityLogFilter())
        security_handler.setFormatter(formatter)
        self.logger.addHandler(security_handler)
        
        # Performance log
        performance_handler = logging.FileHandler(self.log_dir / 'performance.log')
        performance_handler.setLevel(logging.INFO)
        performance_handler.addFilter(PerformanceLogFilter())
        performance_handler.setFormatter(formatter)
        self.logger.addHandler(performance_handler)
        
        # Audit log
        audit_handler = logging.FileHandler(self.log_dir / 'audit.log')
        audit_handler.setLevel(logging.INFO)
        audit_handler.addFilter(AuditLogFilter())
        audit_handler.setFormatter(formatter)
        self.logger.addHandler(audit_handler)
    
    def log(self, level: LogLevel, category: LogCategory, component: str, 
           message: str, details: Dict[str, Any] = None, **kwargs):
        """Main logging method with structured data"""
        try:
            with self._lock:
                # Get system metrics
                memory_info = self.process.memory_info()
                cpu_percent = self.process.cpu_percent()
                
                # Create log entry
                log_entry = LogEntry(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    level=level,
                    category=category,
                    component=component,
                    message=message,
                    details=details or {},
                    user_id=kwargs.get('user_id'),
                    session_id=kwargs.get('session_id'),
                    trace_id=kwargs.get('trace_id'),
                    execution_time=kwargs.get('execution_time'),
                    memory_usage=memory_info.rss,
                    cpu_usage=cpu_percent,
                    error_details=kwargs.get('error_details')
                )
                
                # Convert to logging level
                log_level = self._convert_log_level(level)
                
                # Create extra data for structured logging
                extra = {
                    'log_entry': asdict(log_entry),
                    'category': category.value,
                    'component': component
                }
                
                # Log the message
                self.logger.log(log_level, message, extra=extra)
                
        except Exception as e:
            # Fallback logging to prevent logging failures from breaking the system
            print(f"Logging error: {e}")
    
    def info(self, category: LogCategory, component: str, message: str, **kwargs):
        """Log info level message"""
        self.log(LogLevel.INFO, category, component, message, **kwargs)
    
    def debug(self, category: LogCategory, component: str, message: str, **kwargs):
        """Log debug level message"""
        self.log(LogLevel.DEBUG, category, component, message, **kwargs)
    
    def warning(self, category: LogCategory, component: str, message: str, **kwargs):
        """Log warning level message"""
        self.log(LogLevel.WARN, category, component, message, **kwargs)
    
    def error(self, category: LogCategory, component: str, message: str, 
             error: Exception = None, **kwargs):
        """Log error level message with exception details"""
        error_details = None
        if error:
            error_details = {
                'exception_type': type(error).__name__,
                'exception_message': str(error),
                'traceback': traceback.format_exc()
            }
        
        self.log(LogLevel.ERROR, category, component, message, 
                error_details=error_details, **kwargs)
    
    def critical(self, category: LogCategory, component: str, message: str, 
                error: Exception = None, **kwargs):
        """Log critical level message"""
        error_details = None
        if error:
            error_details = {
                'exception_type': type(error).__name__,
                'exception_message': str(error),
                'traceback': traceback.format_exc()
            }
        
        self.log(LogLevel.CRITICAL, category, component, message,
                error_details=error_details, **kwargs)
    
    def security(self, component: str, message: str, **kwargs):
        """Log security-related events"""
        self.log(LogLevel.SECURITY, LogCategory.SECURITY, component, message, **kwargs)
    
    def audit(self, component: str, action: str, user_id: str = None, 
             details: Dict[str, Any] = None, **kwargs):
        """Log audit events for compliance"""
        audit_details = details or {}
        audit_details.update({
            'action': action,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        self.log(LogLevel.AUDIT, LogCategory.ADMIN, component, 
                f"Audit: {action}", details=audit_details, user_id=user_id, **kwargs)
    
    def start_performance_tracking(self, component: str, operation: str) -> str:
        """Start tracking performance for an operation"""
        operation_id = f"{component}_{operation}_{int(time.time() * 1000)}"
        
        self.active_operations[operation_id] = {
            'component': component,
            'operation': operation,
            'start_time': time.time(),
            'memory_before': self.process.memory_info().rss,
            'cpu_start': time.time()
        }
        
        return operation_id
    
    def end_performance_tracking(self, operation_id: str, success: bool = True, 
                               error_message: str = None):
        """End performance tracking and log metrics"""
        if operation_id not in self.active_operations:
            return
        
        operation = self.active_operations.pop(operation_id)
        end_time = time.time()
        
        # Calculate metrics
        duration = end_time - operation['start_time']
        memory_after = self.process.memory_info().rss
        memory_delta = memory_after - operation['memory_before']
        cpu_percent = self.process.cpu_percent()
        
        # Create performance metrics
        metrics = PerformanceMetrics(
            component=operation['component'],
            operation=operation['operation'],
            start_time=operation['start_time'],
            end_time=end_time,
            duration=duration,
            memory_before=operation['memory_before'],
            memory_after=memory_after,
            memory_delta=memory_delta,
            cpu_percent=cpu_percent,
            success=success,
            error_message=error_message
        )
        
        # Store metrics
        with self._lock:
            self.performance_metrics.append(metrics)
            
            # Keep only recent metrics (last 1000)
            if len(self.performance_metrics) > 1000:
                self.performance_metrics = self.performance_metrics[-1000:]
        
        # Log performance
        self.log(LogLevel.PERFORMANCE, LogCategory.PERFORMANCE, 
                operation['component'], 
                f"Operation {operation['operation']} completed",
                details=asdict(metrics),
                execution_time=duration)
    
    def performance_context(self, component: str, operation: str):
        """Context manager for performance tracking"""
        return PerformanceContext(self, component, operation)
    
    def get_performance_metrics(self, component: str = None, hours: int = 24) -> List[PerformanceMetrics]:
        """Get performance metrics for analysis"""
        cutoff_time = time.time() - (hours * 3600)
        
        with self._lock:
            metrics = [
                m for m in self.performance_metrics 
                if m.end_time >= cutoff_time
            ]
            
            if component:
                metrics = [m for m in metrics if m.component == component]
            
            return metrics
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health metrics"""
        memory_info = self.process.memory_info()
        cpu_percent = self.process.cpu_percent(interval=1)
        
        # Get performance statistics
        recent_metrics = self.get_performance_metrics(hours=1)
        
        error_count = sum(1 for m in recent_metrics if not m.success)
        avg_duration = sum(m.duration for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
        
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'system_metrics': {
                'memory_usage_mb': memory_info.rss / 1024 / 1024,
                'memory_percent': self.process.memory_percent(),
                'cpu_percent': cpu_percent,
                'num_threads': self.process.num_threads(),
                'num_file_descriptors': self.process.num_fds() if hasattr(self.process, 'num_fds') else None
            },
            'performance_metrics': {
                'operations_last_hour': len(recent_metrics),
                'error_count_last_hour': error_count,
                'error_rate': (error_count / len(recent_metrics)) if recent_metrics else 0,
                'avg_operation_duration': avg_duration
            },
            'log_statistics': self._get_log_statistics(),
            'health_status': self._assess_health_status(cpu_percent, memory_info.rss, error_count)
        }
    
    def _get_log_statistics(self) -> Dict[str, int]:
        """Get log file statistics"""
        stats = {}
        
        for log_file in self.log_dir.glob('*.log'):
            try:
                stats[log_file.name] = {
                    'size_mb': log_file.stat().st_size / 1024 / 1024,
                    'modified': datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
                }
            except Exception:
                continue
        
        return stats
    
    def _assess_health_status(self, cpu_percent: float, memory_bytes: int, error_count: int) -> str:
        """Assess overall system health"""
        memory_mb = memory_bytes / 1024 / 1024
        
        if cpu_percent > 90 or memory_mb > 1000 or error_count > 10:
            return 'critical'
        elif cpu_percent > 70 or memory_mb > 500 or error_count > 5:
            return 'warning'
        else:
            return 'healthy'
    
    def _convert_log_level(self, level: LogLevel) -> int:
        """Convert custom log level to Python logging level"""
        mapping = {
            LogLevel.TRACE: logging.DEBUG,
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARN: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
            LogLevel.SECURITY: logging.WARNING,
            LogLevel.PERFORMANCE: logging.INFO,
            LogLevel.AUDIT: logging.INFO
        }
        return mapping.get(level, logging.INFO)


class PerformanceContext:
    """Context manager for performance tracking"""
    
    def __init__(self, logger: SystemLogger, component: str, operation: str):
        self.logger = logger
        self.component = component
        self.operation = operation
        self.operation_id = None
    
    def __enter__(self):
        self.operation_id = self.logger.start_performance_tracking(self.component, self.operation)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        success = exc_type is None
        error_message = str(exc_val) if exc_val else None
        self.logger.end_performance_tracking(self.operation_id, success, error_message)


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add structured data if available
        if hasattr(record, 'log_entry'):
            log_data.update(record.log_entry)
        
        # Add exception info if available
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, default=str)


class ConsoleFormatter(logging.Formatter):
    """Console formatter with colors and emojis"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m'   # Magenta
    }
    
    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨'
    }
    
    RESET = '\033[0m'
    
    def format(self, record):
        # Get color and emoji for level
        color = self.COLORS.get(record.levelname, '')
        emoji = self.EMOJIS.get(record.levelname, '')
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Get component info
        component = getattr(record, 'component', record.module)
        category = getattr(record, 'category', 'general')
        
        # Format message
        formatted = f"{color}{emoji} {timestamp} [{record.levelname:8}] {category}:{component} - {record.getMessage()}{self.RESET}"
        
        # Add exception if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


class DatabaseLogHandler(logging.Handler):
    """Handler that writes logs to database"""
    
    def __init__(self, session_factory):
        super().__init__()
        self.Session = session_factory
    
    def emit(self, record):
        try:
            # Only log important messages to database
            if record.levelno < logging.INFO:
                return
            
            session = self.Session()
            
            # Create log record in database using CurationTask table
            log_record = CurationTask(
                tool_id=None,  # System log
                task_type='system_log',
                priority='low',
                status='completed',
                description=record.getMessage(),
                created_at=datetime.fromtimestamp(record.created, tz=timezone.utc),
                updated_at=datetime.fromtimestamp(record.created, tz=timezone.utc),
                metadata=json.dumps({
                    'level': record.levelname,
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno,
                    'category': getattr(record, 'category', 'general'),
                    'component': getattr(record, 'component', record.module)
                })
            )
            
            session.add(log_record)
            session.commit()
            session.close()
            
        except Exception:
            # Don't let database logging errors break the application
            pass


class SecurityLogFilter(logging.Filter):
    """Filter for security-related logs"""
    
    def filter(self, record):
        return (
            hasattr(record, 'category') and 
            record.category == LogCategory.SECURITY.value
        ) or (
            'security' in record.getMessage().lower() or
            'auth' in record.getMessage().lower() or
            'login' in record.getMessage().lower()
        )


class PerformanceLogFilter(logging.Filter):
    """Filter for performance-related logs"""
    
    def filter(self, record):
        return (
            hasattr(record, 'category') and 
            record.category == LogCategory.PERFORMANCE.value
        ) or (
            'performance' in record.getMessage().lower() or
            'duration' in record.getMessage().lower() or
            'slow' in record.getMessage().lower()
        )


class AuditLogFilter(logging.Filter):
    """Filter for audit-related logs"""
    
    def filter(self, record):
        return (
            hasattr(record, 'category') and 
            record.category == LogCategory.ADMIN.value
        ) or (
            'audit' in record.getMessage().lower() or
            'admin' in record.getMessage().lower() or
            'action' in record.getMessage().lower()
        )


# Global logger instance
_system_logger = None


def get_logger() -> SystemLogger:
    """Get global system logger instance"""
    global _system_logger
    if _system_logger is None:
        _system_logger = SystemLogger()
    return _system_logger


def log_api_request(method: str, path: str, user_id: str = None, **kwargs):
    """Log API request"""
    get_logger().info(
        LogCategory.API, 'api_handler', 
        f"{method} {path}",
        details={'method': method, 'path': path},
        user_id=user_id,
        **kwargs
    )


def log_database_operation(operation: str, table: str, duration: float = None, **kwargs):
    """Log database operation"""
    get_logger().info(
        LogCategory.DATABASE, 'database', 
        f"Database {operation} on {table}",
        details={'operation': operation, 'table': table},
        execution_time=duration,
        **kwargs
    )


def log_curation_event(tool_id: int, event: str, details: Dict = None, **kwargs):
    """Log curation event"""
    get_logger().info(
        LogCategory.CURATION, 'curation_engine',
        f"Curation {event} for tool {tool_id}",
        details={'tool_id': tool_id, 'event': event, **(details or {})},
        **kwargs
    )


def log_competitive_analysis(category_id: int, analysis_type: str, duration: float = None, **kwargs):
    """Log competitive analysis event"""
    get_logger().info(
        LogCategory.COMPETITIVE_ANALYSIS, 'market_analyzer',
        f"Competitive analysis {analysis_type} for category {category_id}",
        details={'category_id': category_id, 'analysis_type': analysis_type},
        execution_time=duration,
        **kwargs
    )


def log_alert_event(alert_type: str, severity: str, details: Dict = None, **kwargs):
    """Log alert event"""
    get_logger().info(
        LogCategory.ALERTS, 'alert_manager',
        f"Alert {alert_type} with severity {severity}",
        details={'alert_type': alert_type, 'severity': severity, **(details or {})},
        **kwargs
    )


def log_admin_action(user_id: str, action: str, target: str = None, details: Dict = None, **kwargs):
    """Log admin action for audit trail"""
    get_logger().audit(
        'admin_interface', action,
        user_id=user_id,
        details={'target': target, **(details or {})},
        **kwargs
    )


# Export main classes and functions
__all__ = [
    'SystemLogger', 'LogLevel', 'LogCategory', 'LogEntry', 'PerformanceMetrics',
    'get_logger', 'log_api_request', 'log_database_operation', 'log_curation_event',
    'log_competitive_analysis', 'log_alert_event', 'log_admin_action'
]