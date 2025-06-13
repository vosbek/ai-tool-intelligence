#!/usr/bin/env python3
"""
System Health Monitoring Script
Continuously monitors the AI Tool Intelligence Platform health and performance
"""

import time
import json
import requests
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add backend to path for imports
sys.path.append('backend')

def setup_monitoring_logging():
    """Setup logging for monitoring"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / 'system_monitor.log')
        ]
    )
    return logging.getLogger('SystemMonitor')

class SystemHealthMonitor:
    """Comprehensive system health monitor"""
    
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.logger = setup_monitoring_logging()
        self.health_history = []
        self.alert_thresholds = {
            'error_rate': 0.1,  # 10% error rate
            'response_time': 5.0,  # 5 seconds
            'memory_usage': 1000,  # 1GB
            'disk_free': 1.0  # 1GB free space
        }
        
    def check_api_health(self) -> dict:
        """Check API health endpoint"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'response_time': response_time,
                    'data': response.json()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'response_time': response_time,
                    'error': f"HTTP {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'response_time': None
            }
    
    def check_system_health(self) -> dict:
        """Check detailed system health"""
        try:
            response = requests.get(f"{self.base_url}/api/system/health", timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def check_system_status(self) -> dict:
        """Check system status and components"""
        try:
            response = requests.get(f"{self.base_url}/api/system/status", timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def analyze_health_trends(self) -> dict:
        """Analyze health trends from history"""
        if len(self.health_history) < 2:
            return {'insufficient_data': True}
        
        # Calculate recent averages
        recent = self.health_history[-10:]  # Last 10 checks
        
        avg_response_time = sum(
            h.get('api_health', {}).get('response_time', 0) 
            for h in recent if h.get('api_health', {}).get('response_time')
        ) / len([h for h in recent if h.get('api_health', {}).get('response_time')])
        
        healthy_count = sum(
            1 for h in recent 
            if h.get('api_health', {}).get('status') == 'healthy'
        )
        
        return {
            'avg_response_time': avg_response_time,
            'health_rate': healthy_count / len(recent),
            'total_checks': len(self.health_history),
            'recent_checks': len(recent)
        }
    
    def check_alerts(self, health_data: dict) -> list:
        """Check for alert conditions"""
        alerts = []
        
        # Check API response time
        api_health = health_data.get('api_health', {})
        response_time = api_health.get('response_time')
        if response_time and response_time > self.alert_thresholds['response_time']:
            alerts.append({
                'type': 'performance',
                'severity': 'warning',
                'message': f"High response time: {response_time:.2f}s"
            })
        
        # Check API health status
        if api_health.get('status') != 'healthy':
            alerts.append({
                'type': 'availability',
                'severity': 'critical',
                'message': f"API unhealthy: {api_health.get('error', 'Unknown error')}"
            })
        
        # Check system health
        system_health = health_data.get('system_health', {})
        error_summary = system_health.get('error_tracking', {})
        
        if error_summary.get('status') in ['critical', 'degraded']:
            alerts.append({
                'type': 'errors',
                'severity': 'high',
                'message': f"System health: {error_summary.get('status')}"
            })
        
        # Check memory usage
        system_info = system_health.get('system_info', {})
        memory_status = system_info.get('memory_status', {})
        memory_mb = memory_status.get('memory_mb', 0)
        
        if memory_mb > self.alert_thresholds['memory_usage']:
            alerts.append({
                'type': 'resource',
                'severity': 'warning', 
                'message': f"High memory usage: {memory_mb:.1f}MB"
            })
        
        # Check disk space
        disk_status = system_info.get('disk_status', {})
        free_gb = disk_status.get('free_gb', float('inf'))
        
        if free_gb < self.alert_thresholds['disk_free']:
            alerts.append({
                'type': 'resource',
                'severity': 'warning',
                'message': f"Low disk space: {free_gb:.1f}GB free"
            })
        
        return alerts
    
    def log_health_check(self, health_data: dict, alerts: list):
        """Log health check results"""
        timestamp = datetime.now().isoformat()
        
        # Log summary
        api_status = health_data.get('api_health', {}).get('status', 'unknown')
        response_time = health_data.get('api_health', {}).get('response_time')
        
        if api_status == 'healthy':
            self.logger.info(f"✅ System healthy - Response: {response_time:.3f}s")
        else:
            error = health_data.get('api_health', {}).get('error', 'Unknown')
            self.logger.warning(f"⚠️  System unhealthy - {error}")
        
        # Log alerts
        for alert in alerts:
            severity_emoji = {
                'critical': '🚨',
                'high': '⚠️',
                'warning': '⚠️'
            }.get(alert['severity'], '📢')
            
            self.logger.warning(f"{severity_emoji} ALERT [{alert['type']}]: {alert['message']}")
        
        # Save to history
        health_data['timestamp'] = timestamp
        health_data['alerts'] = alerts
        self.health_history.append(health_data)
        
        # Keep only last 100 entries
        if len(self.health_history) > 100:
            self.health_history = self.health_history[-100:]
    
    def save_health_report(self):
        """Save detailed health report to file"""
        try:
            reports_dir = Path('logs') / 'health_reports'
            reports_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = reports_dir / f'health_report_{timestamp}.json'
            
            trends = self.analyze_health_trends()
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'summary': trends,
                'recent_history': self.health_history[-20:] if self.health_history else [],
                'thresholds': self.alert_thresholds
            }
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"📊 Health report saved: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save health report: {e}")
    
    def run_health_check(self) -> dict:
        """Run complete health check"""
        health_data = {}
        
        # Check API health
        self.logger.debug("Checking API health...")
        health_data['api_health'] = self.check_api_health()
        
        # Check system health (if API is responsive)
        if health_data['api_health']['status'] == 'healthy':
            self.logger.debug("Checking detailed system health...")
            health_data['system_health'] = self.check_system_health()
            
            self.logger.debug("Checking system status...")
            health_data['system_status'] = self.check_system_status()
        
        # Check for alerts
        alerts = self.check_alerts(health_data)
        
        # Log results
        self.log_health_check(health_data, alerts)
        
        return health_data
    
    def monitor_continuously(self, interval: int = 30, duration: int = None):
        """Monitor system continuously"""
        self.logger.info(f"🔍 Starting continuous monitoring (interval: {interval}s)")
        
        start_time = time.time()
        check_count = 0
        
        try:
            while True:
                check_count += 1
                self.logger.debug(f"Health check #{check_count}")
                
                # Run health check
                health_data = self.run_health_check()
                
                # Save periodic reports
                if check_count % 20 == 0:  # Every 20 checks
                    self.save_health_report()
                
                # Check duration limit
                if duration and (time.time() - start_time) >= duration:
                    self.logger.info(f"Monitoring duration ({duration}s) completed")
                    break
                
                # Wait for next check
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("👋 Monitoring stopped by user")
        
        except Exception as e:
            self.logger.error(f"❌ Monitoring error: {e}")
            raise
        
        finally:
            # Save final report
            self.save_health_report()
            
            # Summary
            elapsed = time.time() - start_time
            self.logger.info(f"📊 Monitoring complete: {check_count} checks in {elapsed:.1f}s")

def main():
    """Main monitoring function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Tool Intelligence Platform Health Monitor')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')
    parser.add_argument('--duration', type=int, help='Duration to monitor in seconds')
    parser.add_argument('--once', action='store_true', help='Run single health check')
    parser.add_argument('--url', default='http://localhost:5000', help='Base URL for API')
    
    args = parser.parse_args()
    
    monitor = SystemHealthMonitor(base_url=args.url)
    
    if args.once:
        print("🔍 Running single health check...")
        health_data = monitor.run_health_check()
        
        # Print summary
        api_status = health_data.get('api_health', {}).get('status', 'unknown')
        if api_status == 'healthy':
            print("✅ System is healthy")
        else:
            print("❌ System issues detected")
        
        # Print alerts
        alerts = monitor.check_alerts(health_data)
        if alerts:
            print(f"\n⚠️  {len(alerts)} alerts:")
            for alert in alerts:
                print(f"  - {alert['message']}")
        
    else:
        monitor.monitor_continuously(
            interval=args.interval,
            duration=args.duration
        )

if __name__ == '__main__':
    main()