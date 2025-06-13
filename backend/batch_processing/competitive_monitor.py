# batch_processing/competitive_monitor.py - Systematic competitive monitoring and batch processing

import asyncio
import concurrent.futures
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json
import time
import logging
from dataclasses import dataclass
from enum import Enum
import threading
import queue

# Import database and curation components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.enhanced_schema import *
from data_curation.curation_engine import DataCurationEngine, CurationResult
from sqlalchemy import create_engine, and_, or_, desc, asc
from sqlalchemy.orm import sessionmaker


class ProcessingPriority(Enum):
    """Processing priority levels"""
    URGENT = 1      # Critical tools, immediate processing
    HIGH = 2        # Important tools, process within hours
    NORMAL = 3      # Regular tools, daily processing
    LOW = 4         # Background tools, weekly processing
    MAINTENANCE = 5 # Archive/deprecated tools, monthly


@dataclass
class BatchJob:
    """Represents a batch processing job"""
    job_id: str
    tool_ids: List[int]
    priority: ProcessingPriority
    job_type: str  # 'scheduled', 'manual', 'triggered'
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = 'pending'  # 'pending', 'running', 'completed', 'failed'
    results: List[CurationResult] = None
    error_message: Optional[str] = None
    progress: float = 0.0


@dataclass
class MonitoringStats:
    """Statistics for monitoring dashboard"""
    total_tools: int
    tools_monitored: int
    tools_processed_today: int
    changes_detected_today: int
    versions_created_today: int
    average_processing_time: float
    queue_size: int
    active_jobs: int
    success_rate: float


class CompetitiveMonitor:
    """Systematic competitive monitoring with batch processing and job queues"""
    
    def __init__(self, database_url: str = None, max_workers: int = 4, max_concurrent_jobs: int = 2):
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # Initialize curation engine
        self.curation_engine = DataCurationEngine(database_url)
        
        # Threading and processing configuration
        self.max_workers = max_workers
        self.max_concurrent_jobs = max_concurrent_jobs
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        
        # Job management
        self.job_queue = queue.PriorityQueue()
        self.active_jobs: Dict[str, BatchJob] = {}
        self.completed_jobs: List[BatchJob] = []
        self.job_counter = 0
        
        # Monitoring state
        self.is_running = False
        self.monitor_thread = None
        self.stats_lock = threading.Lock()
        
        # Rate limiting and API management
        self.rate_limiter = self._setup_rate_limiter()
        
        # Setup logging
        self.logger = self._setup_logging()
        
        print(f"Competitive Monitor initialized with {max_workers} workers")
    
    def start_monitoring(self):
        """Start the background monitoring process"""
        if self.is_running:
            print("Monitor is already running")
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print("Competitive monitoring started")
        self.logger.info("Competitive monitoring started")
    
    def stop_monitoring(self):
        """Stop the background monitoring process"""
        self.is_running = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=30)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        print("Competitive monitoring stopped")
        self.logger.info("Competitive monitoring stopped")
    
    def queue_tool_analysis(self, tool_ids: List[int], priority: ProcessingPriority = ProcessingPriority.NORMAL, 
                           job_type: str = 'manual') -> str:
        """Queue tools for analysis"""
        job_id = f"job_{self.job_counter}_{int(time.time())}"
        self.job_counter += 1
        
        job = BatchJob(
            job_id=job_id,
            tool_ids=tool_ids,
            priority=priority,
            job_type=job_type,
            created_at=datetime.utcnow(),
            results=[]
        )
        
        # Add to priority queue (lower priority value = higher priority)
        self.job_queue.put((priority.value, job))
        
        print(f"Queued job {job_id} with {len(tool_ids)} tools (priority: {priority.name})")
        self.logger.info(f"Queued job {job_id} with {len(tool_ids)} tools")
        
        return job_id
    
    def queue_scheduled_analysis(self) -> List[str]:
        """Queue tools that are due for scheduled analysis"""
        session = self.Session()
        job_ids = []
        
        try:
            # Find tools due for analysis
            now = datetime.utcnow()
            
            # Get tools by priority level
            priority_groups = {
                ProcessingPriority.URGENT: session.query(Tool).filter(
                    and_(
                        Tool.is_actively_monitored == True,
                        Tool.priority_level == 1,
                        or_(
                            Tool.next_process_date <= now,
                            Tool.processing_status == ProcessingStatus.FAILED
                        )
                    )
                ).all(),
                
                ProcessingPriority.HIGH: session.query(Tool).filter(
                    and_(
                        Tool.is_actively_monitored == True,
                        Tool.priority_level == 2,
                        Tool.next_process_date <= now
                    )
                ).all(),
                
                ProcessingPriority.NORMAL: session.query(Tool).filter(
                    and_(
                        Tool.is_actively_monitored == True,
                        Tool.priority_level == 3,
                        Tool.next_process_date <= now
                    )
                ).all(),
                
                ProcessingPriority.LOW: session.query(Tool).filter(
                    and_(
                        Tool.is_actively_monitored == True,
                        Tool.priority_level >= 4,
                        Tool.next_process_date <= now
                    )
                ).all()
            }
            
            # Create jobs for each priority group
            for priority, tools in priority_groups.items():
                if tools:
                    tool_ids = [tool.id for tool in tools]
                    
                    # Split into smaller batches to avoid overwhelming the system
                    batch_size = self._get_batch_size_for_priority(priority)
                    
                    for i in range(0, len(tool_ids), batch_size):
                        batch_tool_ids = tool_ids[i:i + batch_size]
                        job_id = self.queue_tool_analysis(batch_tool_ids, priority, 'scheduled')
                        job_ids.append(job_id)
            
            print(f"Queued {len(job_ids)} scheduled analysis jobs")
            self.logger.info(f"Queued {len(job_ids)} scheduled analysis jobs")
            
        except Exception as e:
            print(f"Error queuing scheduled analysis: {e}")
            self.logger.error(f"Error queuing scheduled analysis: {e}")
        finally:
            session.close()
        
        return job_ids
    
    def process_tool_list(self, tool_list: List[Dict], priority: ProcessingPriority = ProcessingPriority.NORMAL) -> str:
        """Process a list of new tools (for initial analysis)"""
        session = self.Session()
        tool_ids = []
        
        try:
            for tool_data in tool_list:
                # Create or find existing tool
                tool = self._create_or_update_tool(session, tool_data)
                tool_ids.append(tool.id)
            
            session.commit()
            
            # Queue for analysis
            job_id = self.queue_tool_analysis(tool_ids, priority, 'bulk_import')
            
            print(f"Created {len(tool_ids)} tools and queued for analysis")
            return job_id
            
        except Exception as e:
            session.rollback()
            print(f"Error processing tool list: {e}")
            self.logger.error(f"Error processing tool list: {e}")
            raise
        finally:
            session.close()
    
    def get_job_status(self, job_id: str) -> Optional[BatchJob]:
        """Get status of a specific job"""
        # Check active jobs
        if job_id in self.active_jobs:
            return self.active_jobs[job_id]
        
        # Check completed jobs
        for job in self.completed_jobs:
            if job.job_id == job_id:
                return job
        
        return None
    
    def get_monitoring_stats(self) -> MonitoringStats:
        """Get current monitoring statistics"""
        session = self.Session()
        
        try:
            today = datetime.utcnow().date()
            
            # Tool counts
            total_tools = session.query(Tool).count()
            tools_monitored = session.query(Tool).filter(Tool.is_actively_monitored == True).count()
            
            tools_processed_today = session.query(Tool).filter(
                and_(
                    Tool.last_processed_at >= datetime.combine(today, datetime.min.time()),
                    Tool.processing_status == ProcessingStatus.COMPLETED
                )
            ).count()
            
            # Change detection stats
            changes_detected_today = session.query(ToolChange).filter(
                ToolChange.detected_at >= datetime.combine(today, datetime.min.time())
            ).count()
            
            versions_created_today = session.query(ToolVersion).filter(
                ToolVersion.detected_at >= datetime.combine(today, datetime.min.time())
            ).count()
            
            # Processing time calculation
            recent_snapshots = session.query(AnalysisSnapshot).filter(
                and_(
                    AnalysisSnapshot.completed_at >= datetime.utcnow() - timedelta(days=7),
                    AnalysisSnapshot.processing_time_seconds.isnot(None)
                )
            ).all()
            
            avg_processing_time = 0.0
            if recent_snapshots:
                total_time = sum(s.processing_time_seconds for s in recent_snapshots if s.processing_time_seconds)
                avg_processing_time = total_time / len(recent_snapshots)
            
            # Job queue stats
            queue_size = self.job_queue.qsize()
            active_jobs = len(self.active_jobs)
            
            # Success rate
            recent_tools = session.query(Tool).filter(
                Tool.last_processed_at >= datetime.utcnow() - timedelta(days=7)
            ).all()
            
            success_rate = 0.0
            if recent_tools:
                successful = sum(1 for t in recent_tools if t.processing_status == ProcessingStatus.COMPLETED)
                success_rate = (successful / len(recent_tools)) * 100
            
            return MonitoringStats(
                total_tools=total_tools,
                tools_monitored=tools_monitored,
                tools_processed_today=tools_processed_today,
                changes_detected_today=changes_detected_today,
                versions_created_today=versions_created_today,
                average_processing_time=avg_processing_time,
                queue_size=queue_size,
                active_jobs=active_jobs,
                success_rate=success_rate
            )
            
        except Exception as e:
            self.logger.error(f"Error getting monitoring stats: {e}")
            return MonitoringStats(0, 0, 0, 0, 0, 0.0, 0, 0, 0.0)
        finally:
            session.close()
    
    def pause_tool_monitoring(self, tool_id: int):
        """Pause monitoring for a specific tool"""
        session = self.Session()
        
        try:
            tool = session.query(Tool).filter_by(id=tool_id).first()
            if tool:
                tool.is_actively_monitored = False
                session.commit()
                print(f"Paused monitoring for tool: {tool.name}")
                
        except Exception as e:
            session.rollback()
            print(f"Error pausing tool monitoring: {e}")
        finally:
            session.close()
    
    def resume_tool_monitoring(self, tool_id: int):
        """Resume monitoring for a specific tool"""
        session = self.Session()
        
        try:
            tool = session.query(Tool).filter_by(id=tool_id).first()
            if tool:
                tool.is_actively_monitored = True
                # Reset next process date to soon
                tool.next_process_date = datetime.utcnow() + timedelta(minutes=5)
                session.commit()
                print(f"Resumed monitoring for tool: {tool.name}")
                
        except Exception as e:
            session.rollback()
            print(f"Error resuming tool monitoring: {e}")
        finally:
            session.close()
    
    def trigger_immediate_analysis(self, tool_id: int) -> str:
        """Trigger immediate analysis for a specific tool"""
        job_id = self.queue_tool_analysis([tool_id], ProcessingPriority.URGENT, 'triggered')
        print(f"Triggered immediate analysis for tool {tool_id}")
        return job_id
    
    def _monitor_loop(self):
        """Main monitoring loop running in background thread"""
        self.logger.info("Monitor loop started")
        
        while self.is_running:
            try:
                # Queue scheduled jobs every 5 minutes
                if self._should_check_scheduled_jobs():
                    self.queue_scheduled_analysis()
                
                # Process pending jobs
                self._process_job_queue()
                
                # Clean up completed jobs (keep last 100)
                self._cleanup_completed_jobs()
                
                # Sleep before next iteration
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _should_check_scheduled_jobs(self) -> bool:
        """Check if it's time to queue scheduled jobs"""
        # Check every 5 minutes
        return int(time.time()) % 300 == 0
    
    def _process_job_queue(self):
        """Process jobs from the queue"""
        # Don't start new jobs if we're at max capacity
        if len(self.active_jobs) >= self.max_concurrent_jobs:
            return
        
        try:
            # Get next job from queue (non-blocking)
            priority, job = self.job_queue.get_nowait()
            
            # Start processing the job
            self._start_job_processing(job)
            
        except queue.Empty:
            # No jobs in queue
            pass
        except Exception as e:
            self.logger.error(f"Error processing job queue: {e}")
    
    def _start_job_processing(self, job: BatchJob):
        """Start processing a batch job"""
        job.started_at = datetime.utcnow()
        job.status = 'running'
        self.active_jobs[job.job_id] = job
        
        # Submit to thread pool
        future = self.executor.submit(self._process_batch_job, job)
        future.add_done_callback(lambda f: self._job_completed(job, f))
        
        self.logger.info(f"Started processing job {job.job_id}")
    
    def _process_batch_job(self, job: BatchJob) -> BatchJob:
        """Process a batch job (runs in thread pool)"""
        results = []
        
        try:
            total_tools = len(job.tool_ids)
            
            for i, tool_id in enumerate(job.tool_ids):
                try:
                    # Update progress
                    job.progress = (i / total_tools) * 100
                    
                    # Apply rate limiting
                    self._apply_rate_limiting(job.priority)
                    
                    # Process individual tool
                    result = self.curation_engine.curate_tool_data(tool_id)
                    results.append(result)
                    
                    self.logger.info(f"Processed tool {tool_id} in job {job.job_id}")
                    
                except Exception as e:
                    self.logger.error(f"Error processing tool {tool_id} in job {job.job_id}: {e}")
                    # Continue with other tools
                    continue
            
            job.results = results
            job.status = 'completed'
            job.progress = 100.0
            
        except Exception as e:
            job.error_message = str(e)
            job.status = 'failed'
            self.logger.error(f"Job {job.job_id} failed: {e}")
        
        job.completed_at = datetime.utcnow()
        return job
    
    def _job_completed(self, job: BatchJob, future: concurrent.futures.Future):
        """Handle job completion"""
        try:
            # Get the result (may raise exception)
            completed_job = future.result()
            
            # Move from active to completed
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]
            
            self.completed_jobs.append(completed_job)
            
            # Log completion
            if completed_job.status == 'completed':
                success_count = len([r for r in completed_job.results if r.changes_detected])
                self.logger.info(f"Job {job.job_id} completed successfully. {success_count} tools had changes.")
            else:
                self.logger.error(f"Job {job.job_id} failed: {completed_job.error_message}")
                
        except Exception as e:
            self.logger.error(f"Error handling job completion for {job.job_id}: {e}")
    
    def _cleanup_completed_jobs(self):
        """Keep only the most recent completed jobs"""
        max_completed_jobs = 100
        
        if len(self.completed_jobs) > max_completed_jobs:
            # Sort by completion time and keep most recent
            self.completed_jobs.sort(key=lambda j: j.completed_at or datetime.min, reverse=True)
            self.completed_jobs = self.completed_jobs[:max_completed_jobs]
    
    def _get_batch_size_for_priority(self, priority: ProcessingPriority) -> int:
        """Get appropriate batch size based on priority"""
        batch_sizes = {
            ProcessingPriority.URGENT: 1,      # Process immediately
            ProcessingPriority.HIGH: 5,       # Small batches
            ProcessingPriority.NORMAL: 10,    # Medium batches
            ProcessingPriority.LOW: 20,       # Larger batches
            ProcessingPriority.MAINTENANCE: 50 # Large batches
        }
        return batch_sizes.get(priority, 10)
    
    def _apply_rate_limiting(self, priority: ProcessingPriority):
        """Apply rate limiting based on priority"""
        delays = {
            ProcessingPriority.URGENT: 0,      # No delay
            ProcessingPriority.HIGH: 1,       # 1 second between tools
            ProcessingPriority.NORMAL: 2,     # 2 seconds between tools
            ProcessingPriority.LOW: 5,        # 5 seconds between tools
            ProcessingPriority.MAINTENANCE: 10 # 10 seconds between tools
        }
        
        delay = delays.get(priority, 2)
        if delay > 0:
            time.sleep(delay)
    
    def _create_or_update_tool(self, session, tool_data: Dict) -> Tool:
        """Create or update tool from data"""
        # Check if tool exists
        existing_tool = None
        
        if tool_data.get('github_url'):
            existing_tool = session.query(Tool).filter_by(github_url=tool_data['github_url']).first()
        
        if not existing_tool and tool_data.get('website_url'):
            existing_tool = session.query(Tool).filter_by(website_url=tool_data['website_url']).first()
        
        if not existing_tool and tool_data.get('name'):
            existing_tool = session.query(Tool).filter_by(name=tool_data['name']).first()
        
        if existing_tool:
            # Update existing tool
            tool = existing_tool
            tool.updated_at = datetime.utcnow()
        else:
            # Create new tool
            tool = Tool(
                name=tool_data['name'],
                slug=self._generate_slug(tool_data['name']),
                created_at=datetime.utcnow()
            )
            session.add(tool)
        
        # Update tool fields
        tool.description = tool_data.get('description', tool.description)
        tool.website_url = tool_data.get('website_url', tool.website_url)
        tool.github_url = tool_data.get('github_url', tool.github_url)
        tool.documentation_url = tool_data.get('docs_url', tool.documentation_url)
        tool.is_open_source = tool_data.get('is_open_source', tool.is_open_source)
        tool.primary_language = tool_data.get('primary_language', tool.primary_language)
        
        # Set monitoring defaults
        tool.is_actively_monitored = True
        tool.monitoring_frequency_days = tool_data.get('monitoring_frequency', 7)
        tool.priority_level = tool_data.get('priority_level', 3)
        tool.next_process_date = datetime.utcnow() + timedelta(minutes=5)  # Process soon
        
        session.flush()
        return tool
    
    def _generate_slug(self, name: str) -> str:
        """Generate URL-friendly slug"""
        import re
        slug = name.lower().strip()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        return slug[:200]
    
    def _setup_rate_limiter(self):
        """Setup rate limiting for API calls"""
        # TODO: Implement sophisticated rate limiting
        return {}
    
    def _setup_logging(self):
        """Setup logging for the monitor"""
        logger = logging.getLogger('competitive_monitor')
        logger.setLevel(logging.INFO)
        
        # Create file handler
        handler = logging.FileHandler('competitive_monitor.log')
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        
        return logger


# Utility functions for CLI and testing
def run_batch_analysis(tool_ids: List[int], database_url: str = None) -> List[CurationResult]:
    """Run batch analysis for a list of tools (utility function)"""
    monitor = CompetitiveMonitor(database_url)
    
    try:
        job_id = monitor.queue_tool_analysis(tool_ids, ProcessingPriority.HIGH, 'manual')
        
        # Wait for job to complete
        while True:
            job = monitor.get_job_status(job_id)
            if job and job.status in ['completed', 'failed']:
                return job.results or []
            
            time.sleep(2)
            
    finally:
        monitor.stop_monitoring()


def monitor_single_tool(tool_id: int, database_url: str = None) -> CurationResult:
    """Monitor a single tool (utility function)"""
    engine = DataCurationEngine(database_url)
    return engine.curate_tool_data(tool_id, force_analysis=True)


# Export main classes
__all__ = [
    'CompetitiveMonitor', 'BatchJob', 'MonitoringStats', 'ProcessingPriority',
    'run_batch_analysis', 'monitor_single_tool'
]