# logging_monitoring/monitoring_api.py - API endpoints for monitoring and logging

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os
import tempfile
import csv
import io

# Import monitoring components
try:
    from .system_logger import get_logger, LogCategory, LogLevel
    from .monitoring_dashboard import get_monitoring_dashboard
except ImportError:
    print("Warning: Monitoring components not available")
    get_logger = None
    get_monitoring_dashboard = None

# Create blueprint for monitoring routes
monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')

# Initialize components
if get_logger and get_monitoring_dashboard:
    logger = get_logger()
    dashboard = get_monitoring_dashboard()
else:
    logger = None
    dashboard = None


def require_monitoring_access(f):
    """Decorator to require monitoring access"""
    def decorated_function(*args, **kwargs):
        # In production, implement proper authentication
        monitor_user = request.headers.get('X-Monitor-User')
        if not monitor_user:
            return jsonify({'error': 'Monitoring access required'}), 401
        
        request.monitor_user = monitor_user
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function


@monitoring_bp.route('/health', methods=['GET'])
def get_system_health():
    """
    Get current system health status
    
    Returns overall health, component statuses, and active alerts
    """
    if not dashboard:
        return jsonify({'error': 'Monitoring dashboard not available'}), 503
    
    try:
        health_status = dashboard.get_current_health_status()
        
        return jsonify({
            'health_status': {
                'overall_status': health_status.overall_status,
                'timestamp': health_status.timestamp.isoformat(),
                'components': health_status.component_statuses,
                'uptime_percent': health_status.uptime_percent,
                'last_incident': health_status.last_incident.isoformat() if health_status.last_incident else None
            },
            'alerts': {
                'active_count': len(health_status.alerts_active),
                'active_alerts': health_status.alerts_active
            },
            'issues': {
                'performance_issues': health_status.performance_issues,
                'recommendations': health_status.recommendations
            }
        })
        
    except Exception as e:
        if logger:
            logger.error(LogCategory.SYSTEM, 'monitoring_api', f"Health check failed: {e}", error=e)
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/metrics', methods=['GET'])
@require_monitoring_access
def get_metrics():
    """
    Get comprehensive system metrics
    
    Query parameters:
    - hours: Time range in hours (default: 24)
    - category: Metric category ('system', 'application', 'business', 'all')
    """
    if not dashboard:
        return jsonify({'error': 'Monitoring dashboard not available'}), 503
    
    try:
        hours = request.args.get('hours', 24, type=int)
        category = request.args.get('category', 'all')
        
        if hours < 1 or hours > 168:  # Max 1 week
            return jsonify({'error': 'Hours must be between 1 and 168'}), 400
        
        metrics_summary = dashboard.get_metrics_summary(hours)
        
        if 'error' in metrics_summary:
            return jsonify(metrics_summary), 500
        
        # Filter by category if specified
        if category != 'all':
            if category in ['system', 'application', 'business']:
                filtered_summary = {
                    'time_range_hours': metrics_summary['time_range_hours'],
                    'generated_at': metrics_summary['generated_at'],
                    f'{category}_metrics': metrics_summary.get(f'{category}_metrics', {}),
                    'health_status': metrics_summary['health_status']
                }
                return jsonify({'metrics': filtered_summary})
            else:
                return jsonify({'error': f'Invalid category: {category}'}), 400
        
        return jsonify({'metrics': metrics_summary})
        
    except Exception as e:
        if logger:
            logger.error(LogCategory.SYSTEM, 'monitoring_api', f"Metrics request failed: {e}", error=e)
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/metrics/realtime', methods=['GET'])
@require_monitoring_access
def get_realtime_metrics():
    """
    Get real-time metrics for live monitoring
    
    Returns current system state and recent performance data
    """
    if not dashboard:
        return jsonify({'error': 'Monitoring dashboard not available'}), 503
    
    try:
        # Get latest metrics from dashboard
        with dashboard.metrics_lock:
            latest_system = dashboard.system_metrics[-1] if dashboard.system_metrics else None
            latest_app = dashboard.app_metrics[-1] if dashboard.app_metrics else None
            latest_business = dashboard.business_metrics[-1] if dashboard.business_metrics else None
        
        # Get current counters
        current_counters = dashboard.counters.copy()
        
        # Get recent errors
        recent_errors = list(dashboard.error_log)[-10:]  # Last 10 errors
        
        realtime_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'system': {
                'cpu_percent': latest_system.cpu_percent if latest_system else 0,
                'memory_percent': latest_system.memory_percent if latest_system else 0,
                'uptime_seconds': latest_system.uptime_seconds if latest_system else 0
            } if latest_system else {},
            'application': {
                'api_requests_per_minute': latest_app.api_requests_per_minute if latest_app else 0,
                'error_rate_percent': latest_app.error_rate_percent if latest_app else 0,
                'avg_response_time_ms': latest_app.avg_response_time_ms if latest_app else 0,
                'active_connections': latest_app.active_connections if latest_app else 0
            } if latest_app else {},
            'business': {
                'total_tools': latest_business.total_tools if latest_business else 0,
                'tools_processed_today': latest_business.tools_processed_today if latest_business else 0,
                'quality_score_avg': latest_business.quality_score_avg if latest_business else 0
            } if latest_business else {},
            'counters': current_counters,
            'recent_errors': recent_errors,
            'health_status': dashboard.get_current_health_status().overall_status
        }
        
        return jsonify({'realtime_metrics': realtime_data})
        
    except Exception as e:
        if logger:
            logger.error(LogCategory.SYSTEM, 'monitoring_api', f"Realtime metrics failed: {e}", error=e)
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/logs', methods=['GET'])
@require_monitoring_access
def get_logs():
    """
    Get system logs with filtering
    
    Query parameters:
    - level: Log level filter ('debug', 'info', 'warning', 'error', 'critical')
    - category: Log category filter
    - component: Component filter
    - hours: Time range in hours (default: 24)
    - limit: Maximum number of log entries (default: 100)
    """
    if not logger:
        return jsonify({'error': 'Logging system not available'}), 503
    
    try:
        level = request.args.get('level')
        category = request.args.get('category')
        component = request.args.get('component')
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        if limit > 1000:
            return jsonify({'error': 'Limit cannot exceed 1000'}), 400
        
        # Get log files based on filters
        log_entries = _get_filtered_logs(level, category, component, hours, limit)
        
        return jsonify({
            'logs': log_entries,
            'filters_applied': {
                'level': level,
                'category': category,
                'component': component,
                'hours': hours,
                'limit': limit
            },
            'total_entries': len(log_entries)
        })
        
    except Exception as e:
        if logger:
            logger.error(LogCategory.SYSTEM, 'monitoring_api', f"Log retrieval failed: {e}", error=e)
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/logs/download', methods=['GET'])
@require_monitoring_access
def download_logs():
    """
    Download log files
    
    Query parameters:
    - log_type: Type of log ('application', 'errors', 'security', 'performance', 'audit')
    - format: Download format ('raw', 'csv', 'json')
    - hours: Time range in hours (default: 24)
    """
    if not logger:
        return jsonify({'error': 'Logging system not available'}), 503
    
    try:
        log_type = request.args.get('log_type', 'application')
        format_type = request.args.get('format', 'raw')
        hours = request.args.get('hours', 24, type=int)
        
        # Validate parameters
        valid_log_types = ['application', 'errors', 'security', 'performance', 'audit']
        if log_type not in valid_log_types:
            return jsonify({'error': f'Invalid log_type. Must be one of: {valid_log_types}'}), 400
        
        valid_formats = ['raw', 'csv', 'json']
        if format_type not in valid_formats:
            return jsonify({'error': f'Invalid format. Must be one of: {valid_formats}'}), 400
        
        # Get log file path
        log_file_path = logger.log_dir / f'{log_type}.log'
        
        if not log_file_path.exists():
            return jsonify({'error': f'Log file {log_type}.log not found'}), 404
        
        # Handle different formats
        if format_type == 'raw':
            return send_file(
                log_file_path,
                as_attachment=True,
                download_name=f'{log_type}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.log',
                mimetype='text/plain'
            )
        
        elif format_type in ['csv', 'json']:
            # Parse log file and convert format
            log_entries = _parse_log_file(log_file_path, hours)
            
            if format_type == 'csv':
                # Convert to CSV
                output = io.StringIO()
                if log_entries:
                    writer = csv.DictWriter(output, fieldnames=log_entries[0].keys())
                    writer.writeheader()
                    writer.writerows(log_entries)
                
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
                temp_file.write(output.getvalue())
                temp_file.close()
                
                return send_file(
                    temp_file.name,
                    as_attachment=True,
                    download_name=f'{log_type}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv',
                    mimetype='text/csv'
                )
            
            else:  # json
                # Create temporary JSON file
                temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
                json.dump(log_entries, temp_file, indent=2, default=str)
                temp_file.close()
                
                return send_file(
                    temp_file.name,
                    as_attachment=True,
                    download_name=f'{log_type}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json',
                    mimetype='application/json'
                )
        
    except Exception as e:
        if logger:
            logger.error(LogCategory.SYSTEM, 'monitoring_api', f"Log download failed: {e}", error=e)
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/performance', methods=['GET'])
@require_monitoring_access
def get_performance_metrics():
    """
    Get detailed performance metrics
    
    Query parameters:
    - component: Component filter
    - operation: Operation filter
    - hours: Time range in hours (default: 24)
    """
    if not dashboard:
        return jsonify({'error': 'Monitoring dashboard not available'}), 503
    
    try:
        component = request.args.get('component')
        operation = request.args.get('operation')
        hours = request.args.get('hours', 24, type=int)
        
        # Get performance metrics
        performance_metrics = dashboard.get_performance_metrics(component, hours)
        
        # Calculate statistics
        if performance_metrics:
            durations = [m.duration for m in performance_metrics]
            memory_deltas = [m.memory_delta for m in performance_metrics]
            success_rate = sum(1 for m in performance_metrics if m.success) / len(performance_metrics) * 100
            
            stats = {
                'total_operations': len(performance_metrics),
                'success_rate': success_rate,
                'duration_stats': {
                    'avg': sum(durations) / len(durations),
                    'min': min(durations),
                    'max': max(durations),
                    'p95': _calculate_percentile(durations, 95),
                    'p99': _calculate_percentile(durations, 99)
                },
                'memory_stats': {
                    'avg_delta_mb': sum(memory_deltas) / len(memory_deltas) / 1024 / 1024,
                    'max_delta_mb': max(memory_deltas) / 1024 / 1024,
                    'min_delta_mb': min(memory_deltas) / 1024 / 1024
                }
            }
        else:
            stats = {
                'total_operations': 0,
                'success_rate': 0,
                'duration_stats': {},
                'memory_stats': {}
            }
        
        # Group by component and operation
        component_stats = {}
        for metric in performance_metrics:
            comp_key = metric.component
            if comp_key not in component_stats:
                component_stats[comp_key] = {
                    'operations': {},
                    'total_operations': 0,
                    'avg_duration': 0
                }
            
            op_key = metric.operation
            if op_key not in component_stats[comp_key]['operations']:
                component_stats[comp_key]['operations'][op_key] = {
                    'count': 0,
                    'avg_duration': 0,
                    'success_rate': 0
                }
            
            component_stats[comp_key]['total_operations'] += 1
            component_stats[comp_key]['operations'][op_key]['count'] += 1
        
        # Calculate averages
        for comp, comp_data in component_stats.items():
            comp_metrics = [m for m in performance_metrics if m.component == comp]
            if comp_metrics:
                comp_data['avg_duration'] = sum(m.duration for m in comp_metrics) / len(comp_metrics)
                
                for op, op_data in comp_data['operations'].items():
                    op_metrics = [m for m in comp_metrics if m.operation == op]
                    if op_metrics:
                        op_data['avg_duration'] = sum(m.duration for m in op_metrics) / len(op_metrics)
                        op_data['success_rate'] = sum(1 for m in op_metrics if m.success) / len(op_metrics) * 100
        
        return jsonify({
            'performance_metrics': {
                'time_range_hours': hours,
                'filters': {
                    'component': component,
                    'operation': operation
                },
                'overall_stats': stats,
                'component_breakdown': component_stats
            }
        })
        
    except Exception as e:
        if logger:
            logger.error(LogCategory.SYSTEM, 'monitoring_api', f"Performance metrics failed: {e}", error=e)
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/alerts', methods=['GET'])
@require_monitoring_access
def get_system_alerts():
    """
    Get system alerts and notifications
    
    Query parameters:
    - status: Alert status filter ('active', 'resolved', 'all')
    - severity: Alert severity filter
    - hours: Time range in hours (default: 24)
    """
    try:
        status = request.args.get('status', 'active')
        severity = request.args.get('severity')
        hours = request.args.get('hours', 24, type=int)
        
        # Get alerts from various sources
        health_status = dashboard.get_current_health_status() if dashboard else None
        
        alerts_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'filters': {
                'status': status,
                'severity': severity,
                'hours': hours
            },
            'active_alerts': health_status.alerts_active if health_status else [],
            'performance_issues': health_status.performance_issues if health_status else [],
            'component_issues': [
                {'component': comp, 'status': stat}
                for comp, stat in (health_status.component_statuses.items() if health_status else [])
                if stat in ['warning', 'critical']
            ],
            'recommendations': health_status.recommendations if health_status else []
        }
        
        return jsonify({'alerts': alerts_data})
        
    except Exception as e:
        if logger:
            logger.error(LogCategory.SYSTEM, 'monitoring_api', f"Alerts request failed: {e}", error=e)
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/monitoring/start', methods=['POST'])
@require_monitoring_access
def start_monitoring():
    """
    Start real-time monitoring
    
    Expected JSON body:
    {
        "interval_seconds": 60
    }
    """
    if not dashboard:
        return jsonify({'error': 'Monitoring dashboard not available'}), 503
    
    try:
        data = request.get_json() or {}
        interval_seconds = data.get('interval_seconds', 60)
        
        if interval_seconds < 10 or interval_seconds > 300:
            return jsonify({'error': 'Interval must be between 10 and 300 seconds'}), 400
        
        dashboard.start_monitoring(interval_seconds)
        
        if logger:
            logger.info(
                LogCategory.SYSTEM, 'monitoring_api',
                f"Real-time monitoring started by {request.monitor_user}",
                details={'interval_seconds': interval_seconds}
            )
        
        return jsonify({
            'message': 'Real-time monitoring started',
            'interval_seconds': interval_seconds,
            'started_by': request.monitor_user
        })
        
    except Exception as e:
        if logger:
            logger.error(LogCategory.SYSTEM, 'monitoring_api', f"Start monitoring failed: {e}", error=e)
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/monitoring/stop', methods=['POST'])
@require_monitoring_access
def stop_monitoring():
    """
    Stop real-time monitoring
    """
    if not dashboard:
        return jsonify({'error': 'Monitoring dashboard not available'}), 503
    
    try:
        dashboard.stop_monitoring()
        
        if logger:
            logger.info(
                LogCategory.SYSTEM, 'monitoring_api',
                f"Real-time monitoring stopped by {request.monitor_user}"
            )
        
        return jsonify({
            'message': 'Real-time monitoring stopped',
            'stopped_by': request.monitor_user
        })
        
    except Exception as e:
        if logger:
            logger.error(LogCategory.SYSTEM, 'monitoring_api', f"Stop monitoring failed: {e}", error=e)
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/status', methods=['GET'])
def get_monitoring_status():
    """
    Get monitoring system status (no auth required)
    """
    try:
        status = {
            'monitoring_available': dashboard is not None,
            'logging_available': logger is not None,
            'monitoring_active': dashboard.monitoring_active if dashboard else False,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if dashboard:
            status['metrics_collected'] = {
                'system_metrics': len(dashboard.system_metrics),
                'app_metrics': len(dashboard.app_metrics),
                'business_metrics': len(dashboard.business_metrics)
            }
        
        return jsonify({'monitoring_status': status})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Helper functions

def _get_filtered_logs(level: str, category: str, component: str, hours: int, limit: int) -> List[Dict]:
    """Get filtered log entries"""
    # This would parse log files and filter entries
    # For now, return mock data
    return []


def _parse_log_file(log_file_path, hours: int) -> List[Dict]:
    """Parse log file and return structured data"""
    log_entries = []
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    try:
        with open(log_file_path, 'r') as f:
            for line in f:
                try:
                    # Try to parse JSON log entry
                    entry = json.loads(line.strip())
                    
                    # Filter by time
                    entry_time = datetime.fromisoformat(entry.get('timestamp', '').replace('Z', '+00:00'))
                    if entry_time >= cutoff_time:
                        log_entries.append(entry)
                        
                except (json.JSONDecodeError, ValueError):
                    # Handle non-JSON log lines
                    log_entries.append({
                        'timestamp': datetime.utcnow().isoformat(),
                        'level': 'INFO',
                        'message': line.strip(),
                        'raw_log': True
                    })
    except Exception:
        pass
    
    return log_entries[-1000:]  # Limit to last 1000 entries


def _calculate_percentile(values: List[float], percentile: int) -> float:
    """Calculate percentile of values"""
    if not values:
        return 0.0
    
    sorted_values = sorted(values)
    k = (len(sorted_values) - 1) * percentile / 100
    f = int(k)
    c = k - f
    
    if f + 1 < len(sorted_values):
        return sorted_values[f] * (1 - c) + sorted_values[f + 1] * c
    else:
        return sorted_values[f]


# Error handlers for monitoring blueprint
@monitoring_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'error': 'Unauthorized access to monitoring interface',
        'message': 'Valid monitoring credentials required'
    }), 401


@monitoring_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal monitoring system error',
        'message': 'An unexpected error occurred in the monitoring system'
    }), 500