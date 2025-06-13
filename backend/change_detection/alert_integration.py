# change_detection/alert_integration.py - Integration between alert system and curation engine

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_, desc

# Import required modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.enhanced_schema import *
from change_detection.alert_manager import ChangeAlertManager, AlertSeverity
from data_curation.curation_engine import DataCurationEngine, CurationResult
from batch_processing.competitive_monitor import CompetitiveMonitor


@dataclass
class AlertIntegrationConfig:
    """Configuration for alert integration"""
    enable_real_time_alerts: bool = True
    enable_batch_alerts: bool = True
    alert_on_curation_completion: bool = True
    alert_on_quality_issues: bool = True
    batch_alert_threshold: int = 5  # Number of changes before batching
    real_time_debounce_minutes: int = 5  # Debounce period for real-time alerts


class AlertIntegrationManager:
    """Manages integration between alert system and other components"""
    
    def __init__(self, database_url: str = None, config: AlertIntegrationConfig = None):
        from sqlalchemy import create_engine
        
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # Initialize component systems
        self.alert_manager = ChangeAlertManager(database_url)
        self.curation_engine = DataCurationEngine(database_url)
        self.competitive_monitor = CompetitiveMonitor(database_url)
        
        # Configuration
        self.config = config or AlertIntegrationConfig()
        
        # Integration state
        self.pending_alerts = {}  # tool_id -> list of changes
        self.last_alert_times = {}  # tool_id -> datetime
        
        print("Alert Integration Manager initialized")
    
    def setup_curation_hooks(self):
        """Setup hooks to trigger alerts after curation events"""
        print("🔗 Setting up curation-to-alert integration hooks...")
        
        # Monkey patch the curation engine to trigger alerts
        original_curate = self.curation_engine.curate_tool_data
        
        def curate_with_alerts(tool_id: int, force_analysis: bool = False) -> CurationResult:
            """Enhanced curation that triggers alerts"""
            # Run original curation
            result = original_curate(tool_id, force_analysis)
            
            # Trigger alerts if changes were detected
            if self.config.enable_real_time_alerts and result.changes_detected:
                try:
                    self._trigger_change_alerts(tool_id, result.changes_detected)
                except Exception as e:
                    print(f"Error triggering alerts for tool {tool_id}: {e}")
            
            return result
        
        # Replace the method
        self.curation_engine.curate_tool_data = curate_with_alerts
        print("✅ Curation hooks installed")
    
    def setup_batch_monitoring_hooks(self):
        """Setup hooks to trigger alerts from batch monitoring"""
        print("🔗 Setting up batch monitoring integration hooks...")
        
        # Monkey patch the competitive monitor
        original_process_job = self.competitive_monitor._process_batch_job
        
        def process_job_with_alerts(job):
            """Enhanced job processing that triggers alerts"""
            # Run original job processing
            result = original_process_job(job)
            
            # Trigger batch alerts if enabled
            if self.config.enable_batch_alerts and result.results:
                try:
                    self._process_batch_alerts(job, result.results)
                except Exception as e:
                    print(f"Error processing batch alerts for job {job.job_id}: {e}")
            
            return result
        
        # Replace the method
        self.competitive_monitor._process_batch_job = process_job_with_alerts
        print("✅ Batch monitoring hooks installed")
    
    def start_real_time_monitoring(self):
        """Start real-time change monitoring with alerts"""
        print("🚀 Starting real-time change monitoring with alerts...")
        
        async def monitoring_loop():
            while True:
                try:
                    # Check for recent changes
                    await self._check_recent_changes()
                    
                    # Process pending alerts
                    await self._process_pending_alerts()
                    
                    # Sleep before next check
                    await asyncio.sleep(60)  # Check every minute
                    
                except Exception as e:
                    print(f"Error in real-time monitoring: {e}")
                    await asyncio.sleep(60)
        
        # Start monitoring in background
        asyncio.create_task(monitoring_loop())
        print("✅ Real-time monitoring started")
    
    def trigger_immediate_alert(self, tool_id: int, alert_type: str, message: str, 
                              severity: AlertSeverity = AlertSeverity.HIGH) -> bool:
        """Trigger an immediate alert for a tool"""
        session = self.Session()
        
        try:
            tool = session.query(Tool).filter_by(id=tool_id).first()
            if not tool:
                print(f"Tool {tool_id} not found")
                return False
            
            # Create immediate alert
            from change_detection.alert_manager import Alert
            
            alert = Alert(
                id=f"immediate_{tool_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                tool_id=tool_id,
                tool_name=tool.name,
                alert_type=alert_type,
                severity=severity,
                title=f"{tool.name}: {alert_type.replace('_', ' ').title()}",
                message=message,
                changes=[],
                metadata={
                    "triggered_by": "manual",
                    "immediate_alert": True
                },
                created_at=datetime.utcnow(),
                channels=[ch for ch in self.alert_manager.alert_rules[0].channels]  # Use default channels
            )
            
            # Send alert
            self.alert_manager._send_alert(alert)
            self.alert_manager._save_alert_to_database(session, alert)
            
            session.commit()
            
            print(f"✅ Immediate alert sent for {tool.name}")
            return True
            
        except Exception as e:
            session.rollback()
            print(f"Error sending immediate alert: {e}")
            return False
        finally:
            session.close()
    
    def create_alert_digest(self, hours: int = 24) -> Dict:
        """Create a digest of alerts from the last N hours"""
        session = self.Session()
        
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Get recent changes (proxy for alerts)
            recent_changes = session.query(ToolChange).filter(
                ToolChange.detected_at >= cutoff_time
            ).order_by(desc(ToolChange.detected_at)).all()
            
            # Group by tool
            changes_by_tool = {}
            for change in recent_changes:
                if change.tool_id not in changes_by_tool:
                    tool = session.query(Tool).filter_by(id=change.tool_id).first()
                    changes_by_tool[change.tool_id] = {
                        "tool_name": tool.name if tool else f"Tool {change.tool_id}",
                        "changes": []
                    }
                
                changes_by_tool[change.tool_id]["changes"].append({
                    "type": change.change_type.value,
                    "summary": change.change_summary,
                    "impact_score": change.impact_score,
                    "detected_at": change.detected_at.isoformat()
                })
            
            # Create digest
            digest = {
                "period_hours": hours,
                "generated_at": datetime.utcnow().isoformat(),
                "total_changes": len(recent_changes),
                "tools_affected": len(changes_by_tool),
                "tools_with_changes": changes_by_tool,
                "summary": {
                    "high_impact_changes": len([c for c in recent_changes if c.impact_score >= 4]),
                    "version_changes": len([c for c in recent_changes if c.change_type == ChangeType.VERSION_BUMP]),
                    "pricing_changes": len([c for c in recent_changes if c.change_type == ChangeType.PRICE_CHANGE]),
                    "feature_changes": len([c for c in recent_changes if c.change_type in [ChangeType.ADDED, ChangeType.REMOVED]])
                }
            }
            
            return digest
            
        except Exception as e:
            print(f"Error creating alert digest: {e}")
            return {}
        finally:
            session.close()
    
    def send_digest_alert(self, digest: Dict, recipients: List[str] = None) -> bool:
        """Send digest as an alert"""
        try:
            # Create digest alert
            from change_detection.alert_manager import Alert, AlertChannel
            
            alert = Alert(
                id=f"digest_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                tool_id=0,  # Digest alert
                tool_name="Multiple Tools",
                alert_type="digest",
                severity=AlertSeverity.INFO,
                title=f"AI Tools Digest - {digest['total_changes']} changes in {digest['period_hours']}h",
                message=self._format_digest_message(digest),
                changes=[],
                metadata={
                    "digest": True,
                    "period_hours": digest['period_hours'],
                    "tools_affected": digest['tools_affected']
                },
                created_at=datetime.utcnow(),
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK]
            )
            
            # Send digest alert
            self.alert_manager._send_alert(alert)
            
            print(f"✅ Digest alert sent covering {digest['total_changes']} changes")
            return True
            
        except Exception as e:
            print(f"Error sending digest alert: {e}")
            return False
    
    def configure_alert_rules_for_integration(self):
        """Configure alert rules optimized for integration workflows"""
        print("⚙️ Configuring integration-optimized alert rules...")
        
        # Add integration-specific alert rules
        integration_rules = [
            {
                "rule_id": "curation_completion",
                "name": "Curation Completion Alerts",
                "description": "Alert when curation completes with significant changes",
                "change_types": ["version_bump", "price_change", "added", "removed"],
                "severity_threshold": "medium",
                "tool_filters": {"priority_levels": [1, 2, 3]},
                "cooldown_minutes": 30,
                "channels": ["slack", "database"],
                "is_active": True
            },
            {
                "rule_id": "quality_degradation",
                "name": "Data Quality Alerts",
                "description": "Alert when data quality drops significantly",
                "change_types": ["modified"],
                "severity_threshold": "high",
                "tool_filters": {},
                "cooldown_minutes": 60,
                "channels": ["email", "database"],
                "is_active": True
            },
            {
                "rule_id": "batch_summary",
                "name": "Batch Processing Summary",
                "description": "Summary alerts for batch processing results",
                "change_types": ["version_bump", "price_change"],
                "severity_threshold": "low",
                "tool_filters": {},
                "cooldown_minutes": 180,
                "channels": ["email"],
                "is_active": True
            }
        ]
        
        # Create the rules
        for rule_config in integration_rules:
            try:
                self.alert_manager.create_custom_alert_rule(rule_config)
                print(f"  ✅ Created rule: {rule_config['name']}")
            except Exception as e:
                print(f"  ❌ Error creating rule {rule_config['name']}: {e}")
        
        print("⚙️ Alert rule configuration completed")
    
    def _trigger_change_alerts(self, tool_id: int, changes):
        """Trigger alerts for detected changes"""
        if not changes:
            return
        
        # Check debounce period
        if self._should_debounce_alerts(tool_id):
            print(f"Debouncing alerts for tool {tool_id}")
            return
        
        # Convert to ChangeDetection objects if needed
        from data_curation.curation_engine import ChangeDetection
        
        change_detections = []
        for change in changes:
            if isinstance(change, ChangeDetection):
                change_detections.append(change)
            else:
                # Convert from other format if needed
                # This would depend on the actual change format
                continue
        
        if change_detections:
            # Process through alert manager
            alerts = self.alert_manager.process_change_event(tool_id, change_detections)
            
            # Update last alert time
            self.last_alert_times[tool_id] = datetime.utcnow()
            
            print(f"🚨 Triggered {len(alerts)} alerts for tool {tool_id}")
    
    def _process_batch_alerts(self, job, results: List):
        """Process alerts from batch job results"""
        if not results:
            return
        
        # Group results by significance
        significant_results = []
        for result in results:
            if hasattr(result, 'changes_detected') and result.changes_detected:
                significant_results.append(result)
        
        # If we have many significant changes, create a batch summary alert
        if len(significant_results) >= self.config.batch_alert_threshold:
            self._create_batch_summary_alert(job, significant_results)
        else:
            # Process individual alerts
            for result in significant_results:
                if hasattr(result, 'tool_id'):
                    self._trigger_change_alerts(result.tool_id, result.changes_detected)
    
    def _create_batch_summary_alert(self, job, results: List):
        """Create a summary alert for batch processing results"""
        try:
            from change_detection.alert_manager import Alert
            
            # Calculate summary statistics
            tools_affected = len(results)
            total_changes = sum(len(r.changes_detected) for r in results if hasattr(r, 'changes_detected'))
            
            alert = Alert(
                id=f"batch_{job.job_id}_{datetime.utcnow().strftime('%H%M%S')}",
                tool_id=0,  # Batch alert
                tool_name=f"{tools_affected} Tools",
                alert_type="batch_summary",
                severity=AlertSeverity.MEDIUM,
                title=f"Batch Processing Complete - {tools_affected} tools updated",
                message=f"Batch job {job.job_id} completed with {total_changes} changes across {tools_affected} tools",
                changes=[],
                metadata={
                    "job_id": job.job_id,
                    "tools_affected": tools_affected,
                    "total_changes": total_changes,
                    "job_type": job.job_type
                },
                created_at=datetime.utcnow(),
                channels=[ch for ch in self.alert_manager.alert_rules[0].channels]
            )
            
            self.alert_manager._send_alert(alert)
            print(f"📊 Sent batch summary alert for job {job.job_id}")
            
        except Exception as e:
            print(f"Error creating batch summary alert: {e}")
    
    def _should_debounce_alerts(self, tool_id: int) -> bool:
        """Check if alerts should be debounced for this tool"""
        if tool_id not in self.last_alert_times:
            return False
        
        last_alert = self.last_alert_times[tool_id]
        debounce_period = timedelta(minutes=self.config.real_time_debounce_minutes)
        
        return datetime.utcnow() - last_alert < debounce_period
    
    async def _check_recent_changes(self):
        """Check for recent changes that need alerts"""
        session = self.Session()
        
        try:
            # Get changes from the last few minutes that haven't been alerted
            cutoff_time = datetime.utcnow() - timedelta(minutes=5)
            
            unalerted_changes = session.query(ToolChange).filter(
                and_(
                    ToolChange.detected_at >= cutoff_time,
                    ToolChange.is_reviewed == False  # Using as proxy for "not alerted"
                )
            ).all()
            
            if unalerted_changes:
                print(f"🔍 Found {len(unalerted_changes)} recent changes to process")
                
                # Group by tool
                changes_by_tool = {}
                for change in unalerted_changes:
                    if change.tool_id not in changes_by_tool:
                        changes_by_tool[change.tool_id] = []
                    changes_by_tool[change.tool_id].append(change)
                
                # Process alerts for each tool
                for tool_id, tool_changes in changes_by_tool.items():
                    # Convert to ChangeDetection format
                    from data_curation.curation_engine import ChangeDetection
                    
                    change_detections = []
                    for change in tool_changes:
                        change_detection = ChangeDetection(
                            change_type=change.change_type,
                            field_name=change.field_name,
                            old_value=change.old_value,
                            new_value=change.new_value,
                            confidence=change.confidence_score / 100.0,
                            summary=change.change_summary,
                            impact_score=change.impact_score
                        )
                        change_detections.append(change_detection)
                    
                    # Process alerts
                    alerts = self.alert_manager.process_change_event(tool_id, change_detections)
                    
                    # Mark changes as reviewed (alerted)
                    for change in tool_changes:
                        change.is_reviewed = True
                
                session.commit()
            
        except Exception as e:
            session.rollback()
            print(f"Error checking recent changes: {e}")
        finally:
            session.close()
    
    async def _process_pending_alerts(self):
        """Process any pending alerts that were queued"""
        if not self.pending_alerts:
            return
        
        print(f"📤 Processing {len(self.pending_alerts)} pending alerts")
        
        for tool_id, changes in self.pending_alerts.items():
            try:
                self._trigger_change_alerts(tool_id, changes)
            except Exception as e:
                print(f"Error processing pending alerts for tool {tool_id}: {e}")
        
        # Clear pending alerts
        self.pending_alerts.clear()
    
    def _format_digest_message(self, digest: Dict) -> str:
        """Format digest data into a readable message"""
        message = f"AI Tools Activity Digest ({digest['period_hours']} hours)\\n\\n"
        
        summary = digest['summary']
        message += f"📊 Summary:\\n"
        message += f"• Total changes: {digest['total_changes']}\\n"
        message += f"• Tools affected: {digest['tools_affected']}\\n"
        message += f"• High impact changes: {summary['high_impact_changes']}\\n"
        message += f"• Version updates: {summary['version_changes']}\\n"
        message += f"• Pricing changes: {summary['pricing_changes']}\\n"
        message += f"• Feature changes: {summary['feature_changes']}\\n\\n"
        
        if digest['tools_with_changes']:
            message += "🔧 Most Active Tools:\\n"
            # Show top 5 most active tools
            sorted_tools = sorted(
                digest['tools_with_changes'].items(),
                key=lambda x: len(x[1]['changes']),
                reverse=True
            )
            
            for tool_id, tool_data in sorted_tools[:5]:
                message += f"• {tool_data['tool_name']}: {len(tool_data['changes'])} changes\\n"
        
        return message


# Export main class
__all__ = ['AlertIntegrationManager', 'AlertIntegrationConfig']