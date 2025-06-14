# logging_monitoring/monitoring_dashboard.py - Real-time monitoring dashboard and metrics

import json
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from threading import Thread, Lock
import statistics
import psutil
import os
import sys

# Import required modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..models.database import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_, func
from .system_logger import SystemLogger, LogCategory, LogLevel


@dataclass
class SystemMetrics:
    """Real-time system metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    network_io: Dict[str, int]
    process_count: int
    thread_count: int
    file_descriptor_count: int
    uptime_seconds: float


@dataclass
class ApplicationMetrics:
    """Application-specific metrics"""
    timestamp: datetime
    active_connections: int
    api_requests_per_minute: float
    database_queries_per_minute: float
    curation_tasks_active: int
    competitive_analyses_active: int
    alert_queue_size: int
    error_rate_percent: float
    avg_response_time_ms: float
    memory_usage_mb: float
    cache_hit_rate: float


@dataclass
class BusinessMetrics:
    """Business and operational metrics"""
    timestamp: datetime
    total_tools: int
    tools_processed_today: int
    quality_score_avg: float
    alerts_sent_today: int
    competitive_analyses_today: int
    data_freshness_hours: float
    user_sessions_active: int
    api_calls_today: int
    error_count_today: int
    admin_actions_today: int


@dataclass
class HealthStatus:
    """Overall system health status"""
    timestamp: datetime
    overall_status: str  # 'healthy', 'warning', 'critical', 'down'
    component_statuses: Dict[str, str]
    alerts_active: List[Dict]
    performance_issues: List[str]
    recommendations: List[str]
    uptime_percent: float
    last_incident: Optional[datetime]


class MonitoringDashboard:
    """Real-time monitoring dashboard with metrics collection and alerting"""
    
    def __init__(self, database_url: str = None, logger: SystemLogger = None):
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
        self.logger = logger or SystemLogger()
        
        # Database connection
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # Metrics storage (in-memory time series)
        self.system_metrics = deque(maxlen=1440)  # 24 hours at 1-minute intervals
        self.app_metrics = deque(maxlen=1440)
        self.business_metrics = deque(maxlen=1440)
        
        # Real-time counters
        self.counters = {
            'api_requests': 0,
            'database_queries': 0,
            'errors': 0,
            'alerts': 0,
            'curation_tasks': 0,
            'competitive_analyses': 0
        }
        
        # Performance tracking
        self.response_times = deque(maxlen=1000)  # Last 1000 requests
        self.error_log = deque(maxlen=100)  # Last 100 errors
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread = None
        self.metrics_lock = Lock()
        
        # System process
        self.process = psutil.Process()
        self.start_time = time.time()
        
        # Component health tracking
        self.component_health = {
            'database': 'unknown',
            'api': 'unknown',
            'curation': 'unknown',
            'competitive_analysis': 'unknown',
            'alerts': 'unknown',
            'admin': 'unknown'
        }
        
        print("✅ Monitoring Dashboard initialized")
    
    def start_monitoring(self, interval_seconds: int = 60):
        """Start real-time monitoring"""
        if self.monitoring_active:
            print("Monitoring already active")
            return
        
        print(f"🔍 Starting real-time monitoring (interval: {interval_seconds}s)")
        
        self.monitoring_active = True
        self.monitoring_thread = Thread(
            target=self._monitoring_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitoring_thread.start()
        
        self.logger.info(
            LogCategory.SYSTEM, 'monitoring_dashboard',
            f"Real-time monitoring started with {interval_seconds}s interval"
        )
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        if not self.monitoring_active:
            return
        
        print("⏹️  Stopping real-time monitoring")
        self.monitoring_active = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info(
            LogCategory.SYSTEM, 'monitoring_dashboard',
            "Real-time monitoring stopped"
        )
    
    def _monitoring_loop(self, interval_seconds: int):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect metrics
                self._collect_system_metrics()
                self._collect_application_metrics()
                self._collect_business_metrics()
                
                # Update component health
                self._update_component_health()
                
                # Check for issues
                self._check_health_conditions()
                
                # Sleep until next collection
                time.sleep(interval_seconds)
                
            except Exception as e:
                self.logger.error(
                    LogCategory.SYSTEM, 'monitoring_dashboard',
                    f"Error in monitoring loop: {e}",
                    error=e
                )
                time.sleep(interval_seconds)
    
    def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            # Process info
            process_count = len(psutil.pids())
            thread_count = self.process.num_threads()
            fd_count = self.process.num_fds() if hasattr(self.process, 'num_fds') else 0
            uptime = time.time() - self.start_time
            
            # Create metrics object
            metrics = SystemMetrics(
                timestamp=datetime.now(timezone.utc),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                disk_usage_percent=disk.percent,
                network_io=network_io,
                process_count=process_count,
                thread_count=thread_count,
                file_descriptor_count=fd_count,
                uptime_seconds=uptime
            )
            
            # Store metrics
            with self.metrics_lock:
                self.system_metrics.append(metrics)
            
        except Exception as e:
            self.logger.error(
                LogCategory.PERFORMANCE, 'monitoring_dashboard',
                f"Error collecting system metrics: {e}",
                error=e
            )
    
    def _collect_application_metrics(self):
        """Collect application-specific metrics"""
        try:
            # Calculate rates from counters
            current_time = time.time()
            
            # API requests per minute
            api_rpm = self._calculate_rate('api_requests')
            db_qpm = self._calculate_rate('database_queries')
            
            # Error rate
            total_requests = max(self.counters['api_requests'], 1)
            error_rate = (self.counters['errors'] / total_requests) * 100
            
            # Average response time
            avg_response_time = (
                statistics.mean(self.response_times) * 1000 
                if self.response_times else 0
            )
            
            # Memory usage
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # Create metrics object
            metrics = ApplicationMetrics(
                timestamp=datetime.now(timezone.utc),
                active_connections=self._get_active_connections(),
                api_requests_per_minute=api_rpm,
                database_queries_per_minute=db_qpm,
                curation_tasks_active=self._get_active_curation_tasks(),
                competitive_analyses_active=self._get_active_competitive_analyses(),
                alert_queue_size=self._get_alert_queue_size(),
                error_rate_percent=error_rate,
                avg_response_time_ms=avg_response_time,
                memory_usage_mb=memory_mb,
                cache_hit_rate=self._get_cache_hit_rate()
            )
            
            # Store metrics
            with self.metrics_lock:
                self.app_metrics.append(metrics)
            
        except Exception as e:
            self.logger.error(
                LogCategory.PERFORMANCE, 'monitoring_dashboard',
                f"Error collecting application metrics: {e}",
                error=e
            )
    
    def _collect_business_metrics(self):
        """Collect business and operational metrics"""
        try:
            session = self.Session()
            
            # Tool counts
            total_tools = session.query(Tool).count()
            
            # Tools processed today
            today = datetime.now(timezone.utc).date()
            tools_today = session.query(Tool).filter(
                func.date(Tool.last_processed_at) == today
            ).count()
            
            # Average quality score
            quality_avg = session.query(func.avg(Tool.confidence_score)).scalar() or 0
            
            # Daily counts
            alerts_today = session.query(CurationTask).filter(
                and_(
                    CurationTask.task_type == 'alert',
                    func.date(CurationTask.created_at) == today
                )
            ).count()
            
            analyses_today = session.query(CompetitiveAnalysis).filter(
                func.date(CompetitiveAnalysis.analysis_date) == today
            ).count()
            
            admin_actions_today = session.query(CurationTask).filter(
                and_(
                    CurationTask.task_type == 'admin_action',
                    func.date(CurationTask.created_at) == today
                )
            ).count()
            
            # Data freshness
            latest_update = session.query(func.max(Tool.last_processed_at)).scalar()
            data_freshness = 0
            if latest_update:
                data_freshness = (datetime.now(timezone.utc) - latest_update).total_seconds() / 3600
            
            session.close()
            
            # Create metrics object
            metrics = BusinessMetrics(
                timestamp=datetime.now(timezone.utc),
                total_tools=total_tools,
                tools_processed_today=tools_today,
                quality_score_avg=float(quality_avg),
                alerts_sent_today=alerts_today,
                competitive_analyses_today=analyses_today,
                data_freshness_hours=data_freshness,
                user_sessions_active=self._get_active_user_sessions(),
                api_calls_today=self.counters['api_requests'],
                error_count_today=self.counters['errors'],
                admin_actions_today=admin_actions_today
            )
            
            # Store metrics
            with self.metrics_lock:
                self.business_metrics.append(metrics)
            
        except Exception as e:
            self.logger.error(
                LogCategory.PERFORMANCE, 'monitoring_dashboard',
                f"Error collecting business metrics: {e}",
                error=e
            )
    
    def _update_component_health(self):
        """Update health status for each system component"""
        try:
            # Database health
            self.component_health['database'] = self._check_database_health()
            
            # API health
            self.component_health['api'] = self._check_api_health()
            
            # Curation health
            self.component_health['curation'] = self._check_curation_health()
            
            # Competitive analysis health
            self.component_health['competitive_analysis'] = self._check_competitive_analysis_health()
            
            # Alert system health
            self.component_health['alerts'] = self._check_alert_system_health()
            
            # Admin interface health
            self.component_health['admin'] = self._check_admin_health()
            
        except Exception as e:
            self.logger.error(
                LogCategory.SYSTEM, 'monitoring_dashboard',
                f"Error updating component health: {e}",
                error=e
            )
    
    def _check_health_conditions(self):
        """Check for critical health conditions"""
        try:
            # Get latest metrics
            if not self.system_metrics or not self.app_metrics:
                return
            
            latest_system = self.system_metrics[-1]
            latest_app = self.app_metrics[-1]
            
            # Check critical conditions
            critical_issues = []
            warning_issues = []
            
            # High CPU usage
            if latest_system.cpu_percent > 90:
                critical_issues.append(f"Critical CPU usage: {latest_system.cpu_percent:.1f}%")
            elif latest_system.cpu_percent > 70:
                warning_issues.append(f"High CPU usage: {latest_system.cpu_percent:.1f}%")
            
            # High memory usage
            if latest_system.memory_percent > 90:
                critical_issues.append(f"Critical memory usage: {latest_system.memory_percent:.1f}%")
            elif latest_system.memory_percent > 80:
                warning_issues.append(f"High memory usage: {latest_system.memory_percent:.1f}%")
            
            # High error rate
            if latest_app.error_rate_percent > 10:
                critical_issues.append(f"Critical error rate: {latest_app.error_rate_percent:.1f}%")
            elif latest_app.error_rate_percent > 5:
                warning_issues.append(f"High error rate: {latest_app.error_rate_percent:.1f}%")
            
            # Slow response times
            if latest_app.avg_response_time_ms > 5000:
                critical_issues.append(f"Critical response time: {latest_app.avg_response_time_ms:.0f}ms")
            elif latest_app.avg_response_time_ms > 2000:
                warning_issues.append(f"Slow response time: {latest_app.avg_response_time_ms:.0f}ms")
            
            # Log issues
            for issue in critical_issues:
                self.logger.critical(
                    LogCategory.SYSTEM, 'health_monitor',
                    issue
                )
            
            for issue in warning_issues:
                self.logger.warning(
                    LogCategory.SYSTEM, 'health_monitor',
                    issue
                )
            
        except Exception as e:
            self.logger.error(
                LogCategory.SYSTEM, 'monitoring_dashboard',
                f"Error checking health conditions: {e}",
                error=e
            )
    
    def get_current_health_status(self) -> HealthStatus:
        """Get current overall health status"""
        try:
            # Determine overall status
            component_statuses = self.component_health.copy()
            
            # Count status types
            status_counts = defaultdict(int)
            for status in component_statuses.values():
                status_counts[status] += 1
            
            # Determine overall status
            if status_counts['critical'] > 0 or status_counts['down'] > 0:
                overall_status = 'critical'
            elif status_counts['warning'] > 0:
                overall_status = 'warning'
            elif status_counts['unknown'] > len(component_statuses) / 2:
                overall_status = 'warning'
            else:
                overall_status = 'healthy'
            
            # Get active alerts
            active_alerts = self._get_active_alerts()
            
            # Get performance issues
            performance_issues = self._get_performance_issues()
            
            # Generate recommendations
            recommendations = self._generate_recommendations()
            
            # Calculate uptime
            uptime_percent = self._calculate_uptime_percent()
            
            # Get last incident
            last_incident = self._get_last_incident()
            
            return HealthStatus(
                timestamp=datetime.now(timezone.utc),
                overall_status=overall_status,
                component_statuses=component_statuses,
                alerts_active=active_alerts,
                performance_issues=performance_issues,
                recommendations=recommendations,
                uptime_percent=uptime_percent,
                last_incident=last_incident
            )
            
        except Exception as e:
            self.logger.error(
                LogCategory.SYSTEM, 'monitoring_dashboard',
                f"Error getting health status: {e}",
                error=e
            )
            
            # Return degraded status on error
            return HealthStatus(
                timestamp=datetime.now(timezone.utc),
                overall_status='warning',
                component_statuses={'system': 'warning'},
                alerts_active=[],
                performance_issues=['Health check system error'],
                recommendations=['Check monitoring system'],
                uptime_percent=0.0,
                last_incident=datetime.now(timezone.utc)
            )
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            with self.metrics_lock:
                # Filter metrics by time
                recent_system = [m for m in self.system_metrics if m.timestamp >= cutoff_time]
                recent_app = [m for m in self.app_metrics if m.timestamp >= cutoff_time]
                recent_business = [m for m in self.business_metrics if m.timestamp >= cutoff_time]
            
            summary = {
                'time_range_hours': hours,
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'system_metrics': self._summarize_system_metrics(recent_system),
                'application_metrics': self._summarize_application_metrics(recent_app),
                'business_metrics': self._summarize_business_metrics(recent_business),
                'health_status': asdict(self.get_current_health_status()),
                'data_points': {
                    'system': len(recent_system),
                    'application': len(recent_app),
                    'business': len(recent_business)
                }
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(
                LogCategory.SYSTEM, 'monitoring_dashboard',
                f"Error generating metrics summary: {e}",
                error=e
            )
            return {'error': str(e)}
    
    def record_api_request(self, method: str, path: str, response_time: float, status_code: int):
        """Record API request metrics"""
        with self.metrics_lock:
            self.counters['api_requests'] += 1
            self.response_times.append(response_time)
            
            if status_code >= 400:
                self.counters['errors'] += 1
                self.error_log.append({
                    'timestamp': datetime.now(timezone.utc),
                    'method': method,
                    'path': path,
                    'status_code': status_code,
                    'response_time': response_time
                })
    
    def record_database_query(self, query_type: str, duration: float, success: bool = True):
        """Record database query metrics"""
        with self.metrics_lock:
            self.counters['database_queries'] += 1
            
            if not success:
                self.counters['errors'] += 1
    
    def record_curation_task(self, task_type: str, success: bool = True):
        """Record curation task metrics"""
        with self.metrics_lock:
            self.counters['curation_tasks'] += 1
            
            if not success:
                self.counters['errors'] += 1
    
    def record_competitive_analysis(self, analysis_type: str, success: bool = True):
        """Record competitive analysis metrics"""
        with self.metrics_lock:
            self.counters['competitive_analyses'] += 1
            
            if not success:
                self.counters['errors'] += 1
    
    def record_alert(self, alert_type: str, severity: str):
        """Record alert metrics"""
        with self.metrics_lock:
            self.counters['alerts'] += 1
    
    # Helper methods for metrics calculation
    
    def _calculate_rate(self, counter_name: str, window_minutes: int = 1) -> float:
        """Calculate rate per minute for a counter"""
        # This is a simplified rate calculation
        # In production, you'd want more sophisticated rate calculation
        return self.counters[counter_name] / max(window_minutes, 1)
    
    def _get_active_connections(self) -> int:
        """Get number of active connections"""
        try:
            connections = self.process.connections()
            return len([c for c in connections if c.status == 'ESTABLISHED'])
        except:
            return 0
    
    def _get_active_curation_tasks(self) -> int:
        """Get number of active curation tasks"""
        try:
            session = self.Session()
            count = session.query(CurationTask).filter(
                CurationTask.status.in_(['pending', 'processing'])
            ).count()
            session.close()
            return count
        except:
            return 0
    
    def _get_active_competitive_analyses(self) -> int:
        """Get number of active competitive analyses"""
        # This would track active analysis processes
        return 0
    
    def _get_alert_queue_size(self) -> int:
        """Get alert queue size"""
        # This would track pending alerts
        return 0
    
    def _get_cache_hit_rate(self) -> float:
        """Get cache hit rate"""
        # This would track cache performance
        return 0.0
    
    def _get_active_user_sessions(self) -> int:
        """Get number of active user sessions"""
        # This would track active user sessions
        return 0
    
    def _check_database_health(self) -> str:
        """Check database health"""
        try:
            session = self.Session()
            session.execute(text('SELECT 1'))
            session.close()
            return 'healthy'
        except Exception:
            return 'critical'
    
    def _check_api_health(self) -> str:
        """Check API health"""
        if not self.app_metrics:
            return 'unknown'
        
        latest = self.app_metrics[-1]
        if latest.error_rate_percent > 10:
            return 'critical'
        elif latest.error_rate_percent > 5:
            return 'warning'
        else:
            return 'healthy'
    
    def _check_curation_health(self) -> str:
        """Check curation system health"""
        try:
            session = self.Session()
            failed_tasks = session.query(CurationTask).filter(
                and_(
                    CurationTask.status == 'failed',
                    CurationTask.created_at >= datetime.now(timezone.utc) - timedelta(hours=1)
                )
            ).count()
            session.close()
            
            if failed_tasks > 10:
                return 'critical'
            elif failed_tasks > 5:
                return 'warning'
            else:
                return 'healthy'
        except:
            return 'unknown'
    
    def _check_competitive_analysis_health(self) -> str:
        """Check competitive analysis system health"""
        return 'healthy'  # Placeholder
    
    def _check_alert_system_health(self) -> str:
        """Check alert system health"""
        return 'healthy'  # Placeholder
    
    def _check_admin_health(self) -> str:
        """Check admin interface health"""
        return 'healthy'  # Placeholder
    
    def _get_active_alerts(self) -> List[Dict]:
        """Get active system alerts"""
        return []  # Placeholder
    
    def _get_performance_issues(self) -> List[str]:
        """Get current performance issues"""
        issues = []
        
        if self.system_metrics:
            latest = self.system_metrics[-1]
            if latest.cpu_percent > 80:
                issues.append(f"High CPU usage: {latest.cpu_percent:.1f}%")
            if latest.memory_percent > 80:
                issues.append(f"High memory usage: {latest.memory_percent:.1f}%")
        
        if self.app_metrics:
            latest = self.app_metrics[-1]
            if latest.avg_response_time_ms > 2000:
                issues.append(f"Slow API responses: {latest.avg_response_time_ms:.0f}ms")
            if latest.error_rate_percent > 5:
                issues.append(f"High error rate: {latest.error_rate_percent:.1f}%")
        
        return issues
    
    def _generate_recommendations(self) -> List[str]:
        """Generate system recommendations"""
        recommendations = []
        
        # Check system metrics
        if self.system_metrics:
            latest = self.system_metrics[-1]
            if latest.memory_percent > 80:
                recommendations.append("Consider increasing available memory")
            if latest.cpu_percent > 80:
                recommendations.append("Investigate high CPU usage processes")
        
        # Check application metrics
        if self.app_metrics:
            latest = self.app_metrics[-1]
            if latest.error_rate_percent > 5:
                recommendations.append("Review recent errors and fix underlying issues")
            if latest.avg_response_time_ms > 2000:
                recommendations.append("Optimize slow API endpoints")
        
        return recommendations
    
    def _calculate_uptime_percent(self) -> float:
        """Calculate system uptime percentage"""
        # This would calculate uptime based on downtime incidents
        return 99.9  # Placeholder
    
    def _get_last_incident(self) -> Optional[datetime]:
        """Get timestamp of last incident"""
        # This would track actual incidents
        return None
    
    def _summarize_system_metrics(self, metrics: List[SystemMetrics]) -> Dict:
        """Summarize system metrics"""
        if not metrics:
            return {}
        
        cpu_values = [m.cpu_percent for m in metrics]
        memory_values = [m.memory_percent for m in metrics]
        
        return {
            'cpu_usage': {
                'avg': statistics.mean(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values),
                'current': cpu_values[-1] if cpu_values else 0
            },
            'memory_usage': {
                'avg': statistics.mean(memory_values),
                'max': max(memory_values),
                'min': min(memory_values),
                'current': memory_values[-1] if memory_values else 0
            },
            'uptime_hours': metrics[-1].uptime_seconds / 3600 if metrics else 0
        }
    
    def _summarize_application_metrics(self, metrics: List[ApplicationMetrics]) -> Dict:
        """Summarize application metrics"""
        if not metrics:
            return {}
        
        response_times = [m.avg_response_time_ms for m in metrics]
        error_rates = [m.error_rate_percent for m in metrics]
        
        return {
            'api_performance': {
                'avg_response_time_ms': statistics.mean(response_times),
                'max_response_time_ms': max(response_times),
                'avg_error_rate': statistics.mean(error_rates),
                'max_error_rate': max(error_rates)
            },
            'throughput': {
                'avg_requests_per_minute': statistics.mean([m.api_requests_per_minute for m in metrics]),
                'total_requests': sum([m.api_requests_per_minute for m in metrics])
            }
        }
    
    def _summarize_business_metrics(self, metrics: List[BusinessMetrics]) -> Dict:
        """Summarize business metrics"""
        if not metrics:
            return {}
        
        latest = metrics[-1]
        
        return {
            'tools': {
                'total_tools': latest.total_tools,
                'processed_today': latest.tools_processed_today,
                'avg_quality_score': latest.quality_score_avg
            },
            'operations': {
                'alerts_today': latest.alerts_sent_today,
                'analyses_today': latest.competitive_analyses_today,
                'admin_actions_today': latest.admin_actions_today
            },
            'data_quality': {
                'freshness_hours': latest.data_freshness_hours,
                'quality_score': latest.quality_score_avg
            }
        }


# Global monitoring instance
_monitoring_dashboard = None


def get_monitoring_dashboard() -> MonitoringDashboard:
    """Get global monitoring dashboard instance"""
    global _monitoring_dashboard
    if _monitoring_dashboard is None:
        _monitoring_dashboard = MonitoringDashboard()
    return _monitoring_dashboard


# Export main classes
__all__ = [
    'MonitoringDashboard', 'SystemMetrics', 'ApplicationMetrics', 'BusinessMetrics', 
    'HealthStatus', 'get_monitoring_dashboard'
]