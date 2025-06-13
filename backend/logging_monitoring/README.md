# Comprehensive Logging and Monitoring System

This directory contains the comprehensive logging and monitoring system for the AI Tool Intelligence Platform. It provides structured logging, real-time performance monitoring, system health assessment, and operational insights.

## 🎯 Overview

The logging and monitoring system provides:

- **📝 Structured Logging**: Multi-format logging with performance tracking and audit trails
- **📊 Real-time Monitoring**: Live system health monitoring with metrics collection
- **🔍 Performance Analytics**: Resource utilization tracking and bottleneck identification
- **🚨 Health Assessment**: Automatic component status monitoring and issue detection
- **📈 Operational Insights**: Performance trends and optimization recommendations
- **🔐 Security Auditing**: Comprehensive audit logging for compliance and security

## 📁 File Structure

```
logging_monitoring/
├── system_logger.py          # Comprehensive logging system with multiple output formats
├── monitoring_dashboard.py   # Real-time monitoring dashboard with metrics collection
├── monitoring_api.py         # API endpoints for monitoring and logging access
└── README.md                 # This documentation
```

## 🔧 Core Components

### 1. SystemLogger (`system_logger.py`)

The main logging engine that provides structured logging across all platform components.

#### Key Classes:
- `SystemLogger`: Main logging engine with multiple output formats
- `LogEntry`: Structured log entry with metadata
- `PerformanceMetrics`: Performance tracking and measurement
- `PerformanceContext`: Context manager for performance monitoring

#### Logging Categories:
- **SYSTEM**: System-level operations and startup/shutdown
- **API**: API requests, responses, and authentication
- **DATABASE**: Database operations and query performance
- **CURATION**: Data curation and research operations
- **COMPETITIVE**: Competitive analysis and market intelligence
- **ADMIN**: Administrative operations and user actions
- **SECURITY**: Security events and access control

#### Log Levels:
- **DEBUG**: Detailed debugging information
- **INFO**: General information and normal operations
- **WARNING**: Warning conditions that should be monitored
- **ERROR**: Error conditions that need attention
- **CRITICAL**: Critical errors requiring immediate action

#### Output Formats:
- **JSON**: Structured JSON format for log aggregation systems
- **Console**: Human-readable format for development and debugging
- **Database**: Structured storage in database for querying and analysis
- **File**: Rotating file logs for long-term storage

### 2. MonitoringDashboard (`monitoring_dashboard.py`)

Real-time monitoring dashboard with comprehensive metrics collection and analysis.

#### Key Classes:
- `MonitoringDashboard`: Main monitoring engine with real-time metrics
- `SystemMetrics`: System resource utilization metrics
- `ComponentStatus`: Individual component health status
- `PerformanceReport`: Comprehensive performance analysis

#### Monitoring Categories:
- **System Resources**: CPU, memory, disk, and network utilization
- **Application Performance**: Response times, throughput, and error rates
- **Database Performance**: Query times, connection pools, and storage
- **Component Health**: Status of all platform components
- **User Activity**: Request patterns and usage analytics

#### Health Status Levels:
- **HEALTHY**: All systems operating normally
- **WARNING**: Minor issues detected, monitoring recommended
- **DEGRADED**: Performance issues detected, attention needed
- **CRITICAL**: Serious issues requiring immediate intervention
- **OFFLINE**: Component not responding or unavailable

### 3. MonitoringAPI (`monitoring_api.py`)

Flask blueprint providing REST API endpoints for monitoring and logging access.

#### Available Endpoints:
```bash
# System health and status
GET  /api/monitoring/health
GET  /api/monitoring/status
GET  /api/monitoring/components

# Performance metrics
GET  /api/monitoring/metrics?period=1h
GET  /api/monitoring/performance?component=api
GET  /api/monitoring/alerts

# Log access and management
GET  /api/monitoring/logs?level=ERROR&limit=100
GET  /api/monitoring/logs/download?format=json
POST /api/monitoring/logs/query

# Control operations
POST /api/monitoring/start
POST /api/monitoring/stop
POST /api/monitoring/restart
```

## 🚀 Usage Examples

### Basic Logging

```python
from logging_monitoring.system_logger import get_logger, LogCategory

# Get the global logger instance
logger = get_logger()

# Log system operations
logger.info(LogCategory.SYSTEM, 'application', 'Application starting up')

# Log API requests with automatic performance tracking
logger.log_api_request('GET', '/api/tools', 200, 0.245, user_id='user123')

# Log database operations
logger.log_database_operation('SELECT', 'tools', 0.023, 150, 'get_tools_by_category')

# Log with additional context
logger.warning(
    LogCategory.CURATION, 
    'research_engine',
    'Research timeout detected',
    details={'tool_id': 123, 'timeout_seconds': 30}
)
```

### Performance Monitoring

```python
from logging_monitoring.system_logger import PerformanceContext

# Track performance of operations
with PerformanceContext('tool_curation', 'process_tool') as perf:
    # Perform expensive operation
    result = curate_tool_data(tool_id)
    perf.add_metric('tools_processed', 1)
    perf.add_metric('features_extracted', len(result.features))

# Performance metrics are automatically logged
```

### Real-time Monitoring

```python
from logging_monitoring.monitoring_dashboard import get_monitoring_dashboard

# Get the global monitoring dashboard
dashboard = get_monitoring_dashboard()

# Start monitoring with custom interval
dashboard.start_monitoring(interval_seconds=60)

# Get current system status
status = dashboard.get_system_status()
print(f"Overall Health: {status.overall_health.value}")
print(f"Active Components: {len(status.healthy_components)}")

# Get performance metrics
metrics = dashboard.get_metrics_summary(period_minutes=60)
print(f"Average CPU: {metrics.avg_cpu_percent:.1f}%")
print(f"Memory Usage: {metrics.current_memory_mb:.0f} MB")
```

### Health Monitoring

```python
# Check specific component health
component_status = dashboard.check_component_health('database')
if component_status.status != ComponentHealthStatus.HEALTHY:
    logger.warning(
        LogCategory.SYSTEM,
        'health_monitor',
        f"Component health issue detected: {component_status.component_name}",
        details={'status': component_status.status.value, 'issues': component_status.issues}
    )

# Get health assessment
health_report = dashboard.generate_health_assessment()
print(f"Health Score: {health_report.overall_health_score}/100")
print(f"Critical Issues: {len(health_report.critical_issues)}")
```

## 📊 Monitoring Features

### System Resource Monitoring

- **CPU Usage**: Real-time CPU utilization tracking
- **Memory Usage**: Memory consumption and leak detection
- **Disk Usage**: Storage utilization and I/O performance
- **Network I/O**: Network traffic and connection monitoring

### Application Performance Monitoring

- **API Performance**: Request/response times and error rates
- **Database Performance**: Query execution times and connection pooling
- **Curation Performance**: Research operation timing and success rates
- **Competitive Analysis Performance**: Analysis execution times and accuracy

### Health Assessment

- **Component Health**: Individual component status monitoring
- **Dependency Health**: External service availability and performance
- **Data Quality Health**: Data quality metrics and validation status
- **System Integration Health**: Inter-component communication status

### Alert and Notification Integration

```python
# Integration with alert system
from change_detection.alert_manager import ChangeAlertManager

# Automatic alerts for monitoring issues
if health_report.overall_health_score < 70:
    alert_manager = ChangeAlertManager()
    alert_manager.send_immediate_alert(
        title="System Health Alert",
        message=f"System health score dropped to {health_report.overall_health_score}",
        severity=AlertSeverity.HIGH
    )
```

## 📈 Performance Analytics

### Metrics Collection

The system collects comprehensive metrics:

```python
# System metrics collected every minute
system_metrics = {
    'timestamp': datetime.now(timezone.utc),
    'cpu_percent': psutil.cpu_percent(),
    'memory_percent': psutil.virtual_memory().percent,
    'memory_used_mb': psutil.virtual_memory().used / 1024 / 1024,
    'disk_usage_percent': psutil.disk_usage('/').percent,
    'network_io': psutil.net_io_counters(),
    'active_connections': len(psutil.net_connections()),
    'uptime_seconds': time.time() - start_time
}
```

### Performance Trend Analysis

```python
# Analyze performance trends
def analyze_performance_trends(self, hours: int = 24) -> Dict:
    metrics = self._get_metrics_for_period(hours)
    
    analysis = {
        'avg_response_time': np.mean([m.response_time for m in metrics]),
        'peak_cpu_usage': max([m.cpu_percent for m in metrics]),
        'memory_growth_rate': self._calculate_growth_rate([m.memory_used_mb for m in metrics]),
        'error_rate_trend': self._calculate_error_trend(metrics),
        'performance_score': self._calculate_performance_score(metrics)
    }
    
    return analysis
```

### Optimization Recommendations

```python
# Generate optimization recommendations
def generate_optimization_recommendations(self) -> List[str]:
    recommendations = []
    recent_metrics = self._get_recent_metrics(hours=1)
    
    if self._detect_memory_leak(recent_metrics):
        recommendations.append("Memory usage increasing - investigate potential memory leaks")
    
    if self._detect_slow_queries(recent_metrics):
        recommendations.append("Database queries running slowly - consider query optimization")
    
    if self._detect_high_error_rate(recent_metrics):
        recommendations.append("Error rate elevated - review recent error logs")
    
    return recommendations
```

## 🔧 Configuration

### Logger Configuration

```python
# Configure logger in system_logger.py
logger_config = {
    'log_level': LogLevel.INFO,
    'enable_console': True,
    'enable_file': True,
    'enable_database': True,
    'enable_json': False,
    'max_file_size_mb': 100,
    'backup_count': 10,
    'log_directory': 'logs'
}
```

### Monitoring Configuration

```python
# Configure monitoring in monitoring_dashboard.py
monitoring_config = {
    'collection_interval_seconds': 60,
    'metric_retention_hours': 168,  # 7 days
    'health_check_interval_seconds': 30,
    'alert_threshold_cpu': 80,
    'alert_threshold_memory': 85,
    'alert_threshold_disk': 90
}
```

### Environment Variables

```bash
# Logging configuration
LOG_LEVEL=INFO
LOG_DIR=logs
ENABLE_JSON_LOGGING=false
ENABLE_DATABASE_LOGGING=true

# Monitoring configuration
ENABLE_MONITORING=true
MONITORING_INTERVAL_SECONDS=60
METRIC_RETENTION_HOURS=168
HEALTH_CHECK_INTERVAL=30
```

## 📝 Log Format Examples

### Structured JSON Log

```json
{
    "timestamp": "2024-01-15T10:30:00.123Z",
    "level": "INFO",
    "category": "API",
    "component": "flask_app",
    "message": "API request processed successfully",
    "details": {
        "method": "GET",
        "endpoint": "/api/tools",
        "status_code": 200,
        "response_time_ms": 245,
        "user_id": "admin"
    },
    "memory_usage": 512000000,
    "cpu_usage": 15.5,
    "request_id": "req_123456"
}
```

### Console Log Format

```
2024-01-15 10:30:00.123 | INFO  | API | flask_app | API request processed successfully
  └─ GET /api/tools → 200 (245ms) [admin] {req_123456}
```

### Performance Log Entry

```json
{
    "timestamp": "2024-01-15T10:30:00.123Z",
    "level": "INFO",
    "category": "PERFORMANCE",
    "component": "curation_engine",
    "message": "Tool curation completed",
    "performance_metrics": {
        "operation": "curate_tool_data",
        "execution_time_seconds": 45.67,
        "memory_peak_mb": 256,
        "cpu_avg_percent": 25.3,
        "custom_metrics": {
            "tools_processed": 1,
            "features_extracted": 23,
            "api_calls_made": 8
        }
    }
}
```

## 🔍 Monitoring Dashboard Features

### Real-time Metrics Display

- **System Overview**: Current CPU, memory, disk, and network status
- **Component Status**: Health status of all platform components
- **Performance Graphs**: Real-time charts of key performance indicators
- **Alert Summary**: Active alerts and recent notifications

### Historical Analysis

- **Trend Charts**: Performance trends over configurable time periods
- **Comparative Analysis**: Compare performance across different time periods
- **Capacity Planning**: Resource utilization trends and growth predictions
- **Incident Analysis**: Correlation of alerts with performance metrics

### Custom Dashboards

```python
# Create custom monitoring dashboard
dashboard_config = {
    'name': 'Custom Research Dashboard',
    'metrics': [
        'research_operations_per_hour',
        'average_research_time',
        'research_success_rate',
        'data_quality_score'
    ],
    'alerts': [
        'research_failure_rate_high',
        'data_quality_degraded'
    ],
    'refresh_interval': 30
}
```

## 🧪 Testing and Validation

### Log Testing

```python
# Test logging functionality
def test_logging_system():
    logger = get_logger()
    
    # Test all log levels
    logger.debug(LogCategory.SYSTEM, 'test', 'Debug message')
    logger.info(LogCategory.API, 'test', 'Info message')
    logger.warning(LogCategory.DATABASE, 'test', 'Warning message')
    logger.error(LogCategory.CURATION, 'test', 'Error message')
    logger.critical(LogCategory.SECURITY, 'test', 'Critical message')
    
    # Verify log entries
    recent_logs = logger.get_recent_logs(minutes=1)
    assert len(recent_logs) == 5
    print("✅ Logging system test passed")
```

### Monitoring Testing

```python
# Test monitoring system
def test_monitoring_system():
    dashboard = get_monitoring_dashboard()
    
    # Test metrics collection
    dashboard.collect_system_metrics()
    metrics = dashboard.get_current_metrics()
    assert metrics.cpu_percent >= 0
    assert metrics.memory_used_mb > 0
    
    # Test health assessment
    health = dashboard.assess_system_health()
    assert health.overall_health in [h.value for h in ComponentHealthStatus]
    
    print("✅ Monitoring system test passed")
```

## 🚀 Integration with Main Platform

### Automatic Initialization

The logging and monitoring systems are automatically initialized when the main application starts:

```python
# In app.py
if get_logger and get_monitoring_dashboard:
    try:
        print("🔄 Initializing comprehensive logging and monitoring...")
        
        # Initialize global logger
        logger = get_logger()
        logger.info(LogCategory.SYSTEM, 'application', "AI Tool Intelligence Platform starting up")
        
        # Initialize monitoring dashboard
        dashboard = get_monitoring_dashboard()
        
        # Start monitoring if enabled
        if os.getenv('ENABLE_MONITORING', 'true').lower() == 'true':
            monitoring_interval = int(os.getenv('MONITORING_INTERVAL_SECONDS', '60'))
            dashboard.start_monitoring(monitoring_interval)
            print(f"📊 Real-time monitoring started (interval: {monitoring_interval}s)")
        
        print("✅ Logging and monitoring system initialized")
        
    except Exception as e:
        print(f"⚠️  Warning: Logging and monitoring initialization failed: {e}")
```

### API Integration

All monitoring endpoints are automatically available through the main Flask application:

```python
# Monitoring endpoints accessible at:
# http://localhost:5000/api/monitoring/*
```

### Cross-Component Integration

```python
# Other components can use the logger
from logging_monitoring.system_logger import get_logger, LogCategory

logger = get_logger()
logger.info(LogCategory.COMPETITIVE, 'market_analyzer', 'Competitive analysis completed')
```

## 🔧 Maintenance and Optimization

### Log Rotation and Cleanup

```python
# Automatic log rotation
def setup_log_rotation():
    handler = RotatingFileHandler(
        filename='logs/application.log',
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=10,
        encoding='utf-8'
    )
    return handler
```

### Performance Optimization

```python
# Optimize monitoring performance
def optimize_monitoring_performance():
    # Use efficient data structures
    self.system_metrics = deque(maxlen=10080)  # 7 days at 1-minute intervals
    
    # Batch database operations
    self._batch_log_entries()
    
    # Use background threads for collection
    self._start_background_collection()
```

### Database Maintenance

```sql
-- Clean old log entries (keep last 30 days)
DELETE FROM system_logs WHERE log_timestamp < datetime('now', '-30 days');

-- Clean old performance metrics (keep last 7 days)
DELETE FROM performance_metrics WHERE collected_at < datetime('now', '-7 days');

-- Optimize log tables
VACUUM system_logs;
ANALYZE system_logs;
```

## 🚀 Future Enhancements

1. **Distributed Logging**: Support for centralized logging in multi-instance deployments
2. **Advanced Analytics**: Machine learning-based anomaly detection
3. **Custom Alerting**: User-defined alert rules and notification channels
4. **Performance Profiling**: Detailed code-level performance analysis
5. **Log Aggregation**: Integration with ELK stack or similar log aggregation systems

---

This comprehensive logging and monitoring system provides enterprise-grade observability for the AI Tool Intelligence Platform, ensuring optimal performance, reliability, and operational insights across all platform components.