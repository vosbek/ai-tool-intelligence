#!/usr/bin/env python3
"""
Windows-Specific Stability Enhancements

Provides:
- Process management and lifecycle handling
- Windows path handling
- Memory management and cleanup
- Graceful shutdown procedures
- Windows service support preparation
- Performance optimization for Windows
"""

import os
import sys
import time
import signal
import threading
import platform
import psutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
import atexit
import tempfile
import shutil
import json
import logging

class WindowsStabilityManager:
    """Windows-specific stability and reliability manager"""
    
    def __init__(self):
        self.is_windows = platform.system() == 'Windows'
        self.shutdown_callbacks = []
        self.startup_checks = []
        self.cleanup_tasks = []
        self.performance_monitors = []
        self.logger = logging.getLogger(__name__)
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        # Register cleanup on exit
        atexit.register(self.cleanup_on_exit)
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        if self.is_windows:
            # Windows signal handling
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Windows-specific signals
            try:
                signal.signal(signal.SIGBREAK, self._signal_handler)
            except AttributeError:
                pass  # Not available on all Windows versions
        else:
            # Unix signal handling
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.graceful_shutdown()
    
    def register_startup_check(self, check_func: Callable[[], bool], name: str):
        """Register a startup validation check"""
        self.startup_checks.append({
            'name': name,
            'function': check_func
        })
    
    def register_shutdown_callback(self, callback_func: Callable, name: str):
        """Register a function to call during shutdown"""
        self.shutdown_callbacks.append({
            'name': name,
            'function': callback_func
        })
    
    def register_cleanup_task(self, cleanup_func: Callable, name: str):
        """Register a cleanup task"""
        self.cleanup_tasks.append({
            'name': name,
            'function': cleanup_func
        })
    
    def run_startup_checks(self) -> Dict[str, Any]:
        """Run all startup validation checks"""
        results = {
            'overall_success': True,
            'checks': [],
            'errors': []
        }
        
        self.logger.info("Running startup validation checks...")
        
        for check in self.startup_checks:
            try:
                start_time = time.time()
                success = check['function']()
                duration = time.time() - start_time
                
                check_result = {
                    'name': check['name'],
                    'success': success,
                    'duration_seconds': round(duration, 3)
                }
                
                results['checks'].append(check_result)
                
                if success:
                    self.logger.info(f"✅ {check['name']} - OK ({duration:.3f}s)")
                else:
                    self.logger.error(f"❌ {check['name']} - FAILED ({duration:.3f}s)")
                    results['overall_success'] = False
                    results['errors'].append(f"{check['name']} failed validation")
                
            except Exception as e:
                self.logger.error(f"❌ {check['name']} - ERROR: {e}")
                results['checks'].append({
                    'name': check['name'],
                    'success': False,
                    'error': str(e)
                })
                results['overall_success'] = False
                results['errors'].append(f"{check['name']} raised exception: {e}")
        
        if results['overall_success']:
            self.logger.info("🎉 All startup checks passed!")
        else:
            self.logger.warning(f"⚠️ {len(results['errors'])} startup checks failed")
        
        return results
    
    def graceful_shutdown(self):
        """Perform graceful application shutdown"""
        self.logger.info("Starting graceful shutdown...")
        
        # Run shutdown callbacks
        for callback in self.shutdown_callbacks:
            try:
                self.logger.info(f"Running shutdown callback: {callback['name']}")
                callback['function']()
            except Exception as e:
                self.logger.error(f"Error in shutdown callback {callback['name']}: {e}")
        
        # Perform cleanup
        self.cleanup_on_exit()
        
        self.logger.info("Graceful shutdown completed")
        sys.exit(0)
    
    def cleanup_on_exit(self):
        """Perform cleanup tasks on exit"""
        for task in self.cleanup_tasks:
            try:
                self.logger.debug(f"Running cleanup task: {task['name']}")
                task['function']()
            except Exception as e:
                self.logger.error(f"Error in cleanup task {task['name']}: {e}")
    
    def get_windows_system_info(self) -> Dict[str, Any]:
        """Get Windows-specific system information"""
        info = {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'platform_release': platform.release(),
            'architecture': platform.architecture(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
        }
        
        if self.is_windows:
            try:
                import winreg
                
                # Get Windows version info
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                try:
                    info['windows_product_name'] = winreg.QueryValueEx(key, "ProductName")[0]
                    info['windows_current_build'] = winreg.QueryValueEx(key, "CurrentBuild")[0]
                    info['windows_display_version'] = winreg.QueryValueEx(key, "DisplayVersion")[0]
                except FileNotFoundError:
                    pass
                finally:
                    winreg.CloseKey(key)
                    
            except ImportError:
                pass
        
        # Add system resources
        try:
            info['cpu_count'] = psutil.cpu_count()
            info['cpu_freq'] = psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            info['memory_total_gb'] = round(psutil.virtual_memory().total / (1024**3), 2)
            info['disk_total_gb'] = round(psutil.disk_usage('/').total / (1024**3), 2)
        except Exception as e:
            self.logger.warning(f"Could not get system resource info: {e}")
        
        return info
    
    def check_windows_permissions(self) -> bool:
        """Check if running with appropriate Windows permissions"""
        if not self.is_windows:
            return True
        
        try:
            # Try to write to a temp file
            test_file = Path(tempfile.gettempdir()) / 'ai_tools_permission_test.tmp'
            test_file.write_text('test')
            test_file.unlink()
            
            # Try to create a directory
            test_dir = Path(tempfile.gettempdir()) / 'ai_tools_dir_test'
            test_dir.mkdir(exist_ok=True)
            test_dir.rmdir()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Permission check failed: {e}")
            return False
    
    def optimize_for_windows(self):
        """Apply Windows-specific optimizations"""
        if not self.is_windows:
            return
        
        try:
            # Set process priority to normal (not high, to avoid system issues)
            current_process = psutil.Process()
            current_process.nice(psutil.NORMAL_PRIORITY_CLASS)
            
            # Optimize garbage collection for Windows
            import gc
            gc.set_threshold(700, 10, 10)  # More aggressive GC
            
            self.logger.info("Applied Windows-specific optimizations")
            
        except Exception as e:
            self.logger.warning(f"Could not apply Windows optimizations: {e}")
    
    def setup_windows_paths(self, app_config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup Windows-compatible paths"""
        optimized_config = app_config.copy()
        
        if self.is_windows:
            # Convert Unix-style paths to Windows paths
            path_keys = ['log_dir', 'backup_dir', 'data_dir', 'temp_dir']
            
            for key in path_keys:
                if key in optimized_config:
                    path = Path(optimized_config[key])
                    # Convert to absolute Windows path
                    optimized_config[key] = str(path.resolve())
        
        return optimized_config
    
    def monitor_memory_usage(self, threshold_mb: int = 1000) -> Dict[str, Any]:
        """Monitor memory usage and provide warnings"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            
            status = {
                'memory_mb': round(memory_mb, 2),
                'memory_percent': process.memory_percent(),
                'threshold_mb': threshold_mb,
                'above_threshold': memory_mb > threshold_mb
            }
            
            if status['above_threshold']:
                self.logger.warning(f"Memory usage ({memory_mb:.1f}MB) above threshold ({threshold_mb}MB)")
            
            return status
            
        except Exception as e:
            self.logger.error(f"Could not monitor memory usage: {e}")
            return {'error': str(e)}
    
    def check_disk_space(self, min_free_gb: float = 1.0) -> Dict[str, Any]:
        """Check available disk space"""
        try:
            disk_usage = psutil.disk_usage('.')
            free_gb = disk_usage.free / (1024**3)
            total_gb = disk_usage.total / (1024**3)
            used_percent = (disk_usage.used / disk_usage.total) * 100
            
            status = {
                'free_gb': round(free_gb, 2),
                'total_gb': round(total_gb, 2),
                'used_percent': round(used_percent, 1),
                'min_free_gb': min_free_gb,
                'sufficient_space': free_gb >= min_free_gb
            }
            
            if not status['sufficient_space']:
                self.logger.warning(f"Low disk space: {free_gb:.1f}GB free (need {min_free_gb}GB)")
            
            return status
            
        except Exception as e:
            self.logger.error(f"Could not check disk space: {e}")
            return {'error': str(e)}
    
    def create_crash_report(self, error: Exception, context: Dict[str, Any] = None) -> str:
        """Create a detailed crash report for debugging"""
        crash_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'system_info': self.get_windows_system_info(),
            'memory_status': self.monitor_memory_usage(),
            'disk_status': self.check_disk_space(),
            'context': context or {}
        }
        
        # Add stack trace
        import traceback
        crash_data['traceback'] = traceback.format_exc()
        
        # Save crash report
        try:
            reports_dir = Path('crash_reports')
            reports_dir.mkdir(exist_ok=True)
            
            crash_file = reports_dir / f"crash_{int(time.time())}.json"
            crash_file.write_text(json.dumps(crash_data, indent=2))
            
            self.logger.error(f"Crash report saved to: {crash_file}")
            return str(crash_file)
            
        except Exception as save_error:
            self.logger.error(f"Could not save crash report: {save_error}")
            return ""

class WindowsProcessManager:
    """Windows-specific process lifecycle management"""
    
    def __init__(self):
        self.child_processes = []
        self.logger = logging.getLogger(__name__)
    
    def start_background_process(self, command: List[str], name: str) -> Optional[psutil.Process]:
        """Start a background process and track it"""
        try:
            if platform.system() == 'Windows':
                # Windows-specific process creation
                import subprocess
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
                proc = subprocess.Popen(
                    command,
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                import subprocess
                proc = subprocess.Popen(command)
            
            process = psutil.Process(proc.pid)
            self.child_processes.append({
                'name': name,
                'process': process,
                'started_at': time.time()
            })
            
            self.logger.info(f"Started background process: {name} (PID: {proc.pid})")
            return process
            
        except Exception as e:
            self.logger.error(f"Failed to start background process {name}: {e}")
            return None
    
    def stop_all_processes(self):
        """Stop all tracked background processes"""
        for proc_info in self.child_processes:
            try:
                process = proc_info['process']
                name = proc_info['name']
                
                if process.is_running():
                    self.logger.info(f"Stopping process: {name}")
                    process.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=5)
                    except psutil.TimeoutExpired:
                        self.logger.warning(f"Force killing process: {name}")
                        process.kill()
                
            except Exception as e:
                self.logger.error(f"Error stopping process {proc_info['name']}: {e}")
        
        self.child_processes.clear()

# Global instances for easy access
windows_stability = WindowsStabilityManager()
process_manager = WindowsProcessManager()

def setup_windows_stability(app_config: Dict[str, Any]) -> Dict[str, Any]:
    """Setup Windows-specific stability features"""
    
    # Optimize configuration for Windows
    optimized_config = windows_stability.setup_windows_paths(app_config)
    
    # Apply Windows optimizations
    windows_stability.optimize_for_windows()
    
    # Register standard startup checks
    windows_stability.register_startup_check(
        lambda: windows_stability.check_windows_permissions(),
        "Windows Permissions"
    )
    
    windows_stability.register_startup_check(
        lambda: windows_stability.check_disk_space(min_free_gb=0.5)['sufficient_space'],
        "Disk Space"
    )
    
    # Register cleanup tasks
    windows_stability.register_cleanup_task(
        process_manager.stop_all_processes,
        "Stop Background Processes"
    )
    
    return optimized_config

def run_startup_validation() -> bool:
    """Run startup validation and return success status"""
    results = windows_stability.run_startup_checks()
    return results['overall_success']

def register_for_graceful_shutdown(func: Callable, name: str):
    """Register a function to be called during shutdown"""
    windows_stability.register_shutdown_callback(func, name)

def get_system_health() -> Dict[str, Any]:
    """Get comprehensive system health information"""
    return {
        'system_info': windows_stability.get_windows_system_info(),
        'memory_status': windows_stability.monitor_memory_usage(),
        'disk_status': windows_stability.check_disk_space(),
        'permissions_ok': windows_stability.check_windows_permissions()
    }