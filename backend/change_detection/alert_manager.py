# change_detection/alert_manager.py - Real-time change detection and alert system

import json
import asyncio
import aiohttp
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_, desc

# Import required modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.enhanced_schema import *
from data_curation.curation_engine import ChangeDetection


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"      # Major version releases, breaking changes
    HIGH = "high"             # Feature additions, pricing changes
    MEDIUM = "medium"         # Minor updates, integration changes
    LOW = "low"               # Documentation updates, small fixes
    INFO = "info"             # Regular monitoring updates


class AlertChannel(Enum):
    """Available alert channels"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    DATABASE = "database"
    CONSOLE = "console"


@dataclass
class Alert:
    """Individual alert message"""
    id: str
    tool_id: int
    tool_name: str
    alert_type: str
    severity: AlertSeverity
    title: str
    message: str
    changes: List[Dict]
    metadata: Dict[str, Any]
    created_at: datetime
    channels: List[AlertChannel]
    is_acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


@dataclass
class AlertRule:
    """Configuration for alert generation"""
    rule_id: str
    name: str
    description: str
    change_types: List[ChangeType]
    severity_threshold: AlertSeverity
    tool_filters: Dict[str, Any]  # Filter criteria for tools
    cooldown_minutes: int  # Minimum time between alerts for same tool
    channels: List[AlertChannel]
    is_active: bool = True


@dataclass
class NotificationTemplate:
    """Template for formatting notifications"""
    template_id: str
    channel: AlertChannel
    subject_template: str
    body_template: str
    format_type: str  # 'text', 'html', 'markdown', 'json'


class ChangeAlertManager:
    """Manages real-time change detection and alerting"""
    
    def __init__(self, database_url: str = None):
        from sqlalchemy import create_engine
        
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # Alert configuration
        self.alert_rules = self._load_alert_rules()
        self.notification_templates = self._load_notification_templates()
        
        # Channel configurations
        self.channel_configs = {
            AlertChannel.EMAIL: {
                'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
                'smtp_port': int(os.getenv('SMTP_PORT', '587')),
                'username': os.getenv('SMTP_USERNAME'),
                'password': os.getenv('SMTP_PASSWORD'),
                'from_email': os.getenv('ALERT_FROM_EMAIL'),
                'to_emails': os.getenv('ALERT_TO_EMAILS', '').split(',')
            },
            AlertChannel.SLACK: {
                'webhook_url': os.getenv('SLACK_WEBHOOK_URL'),
                'channel': os.getenv('SLACK_CHANNEL', '#ai-tools-alerts'),
                'username': os.getenv('SLACK_USERNAME', 'AI Tools Monitor')
            },
            AlertChannel.WEBHOOK: {
                'webhook_urls': os.getenv('WEBHOOK_URLS', '').split(','),
                'headers': json.loads(os.getenv('WEBHOOK_HEADERS', '{}'))
            }
        }
        
        # Alert tracking
        self.active_alerts = {}  # tool_id -> last_alert_time
        self.alert_history = []
        
        # Setup logging
        self.logger = self._setup_logging()
        
        print("Change Alert Manager initialized")
    
    def process_change_event(self, tool_id: int, changes: List[ChangeDetection]) -> List[Alert]:
        """
        Process detected changes and generate alerts
        
        Args:
            tool_id: ID of the tool that changed
            changes: List of detected changes
            
        Returns:
            List of alerts generated
        """
        session = self.Session()
        alerts = []
        
        try:
            # Get tool information
            tool = session.query(Tool).filter_by(id=tool_id).first()
            if not tool:
                self.logger.error(f"Tool {tool_id} not found")
                return alerts
            
            self.logger.info(f"Processing {len(changes)} changes for tool: {tool.name}")
            
            # Group changes by type and severity
            change_groups = self._group_changes_by_severity(changes)
            
            # Check each alert rule
            for rule in self.alert_rules:
                if not rule.is_active:
                    continue
                
                # Check if tool matches rule filters
                if not self._tool_matches_rule(tool, rule):
                    continue
                
                # Check if any changes match rule criteria
                matching_changes = self._get_matching_changes(changes, rule)
                if not matching_changes:
                    continue
                
                # Check cooldown period
                if not self._check_cooldown(tool_id, rule):
                    self.logger.debug(f"Skipping alert for tool {tool_id} due to cooldown")
                    continue
                
                # Generate alert
                alert = self._create_alert(tool, rule, matching_changes)
                alerts.append(alert)
                
                # Record alert time for cooldown
                self.active_alerts[f"{tool_id}_{rule.rule_id}"] = datetime.utcnow()
            
            # Send alerts through configured channels
            for alert in alerts:
                self._send_alert(alert)
                self._save_alert_to_database(session, alert)
            
            session.commit()
            
            if alerts:
                self.logger.info(f"Generated {len(alerts)} alerts for tool {tool.name}")
            
            return alerts
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error processing change event: {e}")
            return []
        finally:
            session.close()
    
    def monitor_continuous_changes(self, check_interval_minutes: int = 5) -> Dict:
        """
        Continuously monitor for changes and send alerts
        
        Args:
            check_interval_minutes: How often to check for changes
            
        Returns:
            Monitoring statistics
        """
        session = self.Session()
        monitoring_stats = {
            "monitoring_started": datetime.utcnow().isoformat(),
            "checks_performed": 0,
            "alerts_generated": 0,
            "tools_checked": 0,
            "errors": []
        }
        
        try:
            self.logger.info(f"Starting continuous change monitoring (interval: {check_interval_minutes} min)")
            
            while True:
                try:
                    # Get recent changes that haven't been alerted
                    cutoff_time = datetime.utcnow() - timedelta(minutes=check_interval_minutes)
                    
                    recent_changes = session.query(ToolChange).filter(
                        and_(
                            ToolChange.detected_at >= cutoff_time,
                            ToolChange.is_reviewed == False  # Use unreviewed changes as proxy for unalerted
                        )
                    ).all()
                    
                    monitoring_stats["checks_performed"] += 1
                    
                    # Group changes by tool
                    changes_by_tool = {}
                    for change in recent_changes:
                        if change.tool_id not in changes_by_tool:
                            changes_by_tool[change.tool_id] = []
                        
                        # Convert ToolChange to ChangeDetection for processing
                        change_detection = ChangeDetection(
                            change_type=change.change_type,
                            field_name=change.field_name,
                            old_value=change.old_value,
                            new_value=change.new_value,
                            confidence=change.confidence_score / 100.0,
                            summary=change.change_summary,
                            impact_score=change.impact_score
                        )
                        changes_by_tool[change.tool_id].append(change_detection)
                    
                    monitoring_stats["tools_checked"] += len(changes_by_tool)
                    
                    # Process changes for each tool
                    for tool_id, tool_changes in changes_by_tool.items():
                        alerts = self.process_change_event(tool_id, tool_changes)
                        monitoring_stats["alerts_generated"] += len(alerts)
                        
                        # Mark changes as reviewed (alerted)
                        for change in recent_changes:
                            if change.tool_id == tool_id:
                                change.is_reviewed = True
                    
                    session.commit()
                    
                    # Sleep until next check
                    await asyncio.sleep(check_interval_minutes * 60)
                    
                except KeyboardInterrupt:
                    self.logger.info("Monitoring stopped by user")
                    break
                except Exception as e:
                    error_info = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "error": str(e)
                    }
                    monitoring_stats["errors"].append(error_info)
                    self.logger.error(f"Error in monitoring loop: {e}")
                    
                    # Sleep before retrying
                    await asyncio.sleep(60)
            
            monitoring_stats["monitoring_ended"] = datetime.utcnow().isoformat()
            return monitoring_stats
            
        except Exception as e:
            self.logger.error(f"Fatal error in continuous monitoring: {e}")
            monitoring_stats["fatal_error"] = str(e)
            return monitoring_stats
        finally:
            session.close()
    
    def create_custom_alert_rule(self, rule_config: Dict) -> AlertRule:
        """Create a custom alert rule"""
        rule = AlertRule(
            rule_id=rule_config.get('rule_id', f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            name=rule_config['name'],
            description=rule_config.get('description', ''),
            change_types=[ChangeType(ct) for ct in rule_config.get('change_types', [])],
            severity_threshold=AlertSeverity(rule_config.get('severity_threshold', 'medium')),
            tool_filters=rule_config.get('tool_filters', {}),
            cooldown_minutes=rule_config.get('cooldown_minutes', 60),
            channels=[AlertChannel(ch) for ch in rule_config.get('channels', ['database'])],
            is_active=rule_config.get('is_active', True)
        )
        
        self.alert_rules.append(rule)
        self.logger.info(f"Created custom alert rule: {rule.name}")
        return rule
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        session = self.Session()
        
        try:
            # Find alert in database (assuming we save alerts there)
            # For now, just log the acknowledgment
            self.logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
            
            # Update alert status if stored in database
            # This would typically update an alerts table
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error acknowledging alert {alert_id}: {e}")
            return False
        finally:
            session.close()
    
    def get_alert_statistics(self, days: int = 30) -> Dict:
        """Get alert statistics for the last N days"""
        session = self.Session()
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # This would typically query an alerts table
            # For now, provide mock statistics based on changes
            recent_changes = session.query(ToolChange).filter(
                ToolChange.detected_at >= cutoff_date
            ).all()
            
            stats = {
                "period_days": days,
                "total_changes": len(recent_changes),
                "changes_by_type": {},
                "changes_by_severity": {},
                "most_active_tools": {},
                "alert_frequency": {}
            }
            
            # Analyze changes
            for change in recent_changes:
                # By type
                change_type = change.change_type.value
                stats["changes_by_type"][change_type] = stats["changes_by_type"].get(change_type, 0) + 1
                
                # By severity (based on impact score)
                if change.impact_score >= 4:
                    severity = "critical"
                elif change.impact_score >= 3:
                    severity = "high"
                elif change.impact_score >= 2:
                    severity = "medium"
                else:
                    severity = "low"
                
                stats["changes_by_severity"][severity] = stats["changes_by_severity"].get(severity, 0) + 1
                
                # Most active tools
                tool_name = f"Tool {change.tool_id}"  # Would fetch actual name
                stats["most_active_tools"][tool_name] = stats["most_active_tools"].get(tool_name, 0) + 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting alert statistics: {e}")
            return {}
        finally:
            session.close()
    
    def _group_changes_by_severity(self, changes: List[ChangeDetection]) -> Dict[AlertSeverity, List[ChangeDetection]]:
        """Group changes by their severity level"""
        groups = {severity: [] for severity in AlertSeverity}
        
        for change in changes:
            severity = self._determine_change_severity(change)
            groups[severity].append(change)
        
        return groups
    
    def _determine_change_severity(self, change: ChangeDetection) -> AlertSeverity:
        """Determine the severity of a change"""
        # Version bumps are typically high priority
        if change.change_type == ChangeType.VERSION_BUMP:
            return AlertSeverity.HIGH
        
        # Price changes are critical for business impact
        if change.change_type == ChangeType.PRICE_CHANGE:
            return AlertSeverity.CRITICAL
        
        # Feature changes depend on impact score
        if change.change_type in [ChangeType.ADDED, ChangeType.REMOVED]:
            if change.impact_score >= 4:
                return AlertSeverity.HIGH
            elif change.impact_score >= 3:
                return AlertSeverity.MEDIUM
            else:
                return AlertSeverity.LOW
        
        # Default to medium for other changes
        return AlertSeverity.MEDIUM
    
    def _tool_matches_rule(self, tool: Tool, rule: AlertRule) -> bool:
        """Check if a tool matches the rule's filter criteria"""
        filters = rule.tool_filters
        
        # Check category filter
        if 'category_ids' in filters:
            if tool.category_id not in filters['category_ids']:
                return False
        
        # Check priority filter
        if 'priority_levels' in filters:
            if tool.priority_level not in filters['priority_levels']:
                return False
        
        # Check open source filter
        if 'is_open_source' in filters:
            if tool.is_open_source != filters['is_open_source']:
                return False
        
        # Check tool name patterns
        if 'name_patterns' in filters:
            import re
            for pattern in filters['name_patterns']:
                if re.search(pattern, tool.name, re.IGNORECASE):
                    return True
            return False
        
        return True
    
    def _get_matching_changes(self, changes: List[ChangeDetection], rule: AlertRule) -> List[ChangeDetection]:
        """Get changes that match the rule criteria"""
        matching = []
        
        for change in changes:
            # Check if change type matches rule
            if rule.change_types and change.change_type not in rule.change_types:
                continue
            
            # Check if severity meets threshold
            change_severity = self._determine_change_severity(change)
            if change_severity.value not in [s.value for s in AlertSeverity if s.value <= rule.severity_threshold.value]:
                continue
            
            matching.append(change)
        
        return matching
    
    def _check_cooldown(self, tool_id: int, rule: AlertRule) -> bool:
        """Check if the cooldown period has passed for this tool/rule combination"""
        key = f"{tool_id}_{rule.rule_id}"
        
        if key not in self.active_alerts:
            return True
        
        last_alert_time = self.active_alerts[key]
        cooldown_period = timedelta(minutes=rule.cooldown_minutes)
        
        return datetime.utcnow() - last_alert_time >= cooldown_period
    
    def _create_alert(self, tool: Tool, rule: AlertRule, changes: List[ChangeDetection]) -> Alert:
        """Create an alert for the given tool and changes"""
        alert_id = f"alert_{tool.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Determine overall severity
        severities = [self._determine_change_severity(change) for change in changes]
        max_severity = max(severities, key=lambda s: list(AlertSeverity).index(s))
        
        # Create alert title and message
        if len(changes) == 1:
            change = changes[0]
            title = f"{tool.name}: {change.change_type.value.replace('_', ' ').title()}"
            message = change.summary
        else:
            title = f"{tool.name}: {len(changes)} changes detected"
            change_types = list(set(c.change_type.value for c in changes))
            message = f"Multiple changes detected: {', '.join(change_types)}"
        
        # Convert changes to dictionaries
        changes_data = []
        for change in changes:
            changes_data.append({
                "change_type": change.change_type.value,
                "field_name": change.field_name,
                "old_value": change.old_value,
                "new_value": change.new_value,
                "summary": change.summary,
                "impact_score": change.impact_score,
                "confidence": change.confidence
            })
        
        alert = Alert(
            id=alert_id,
            tool_id=tool.id,
            tool_name=tool.name,
            alert_type=rule.rule_id,
            severity=max_severity,
            title=title,
            message=message,
            changes=changes_data,
            metadata={
                "rule_name": rule.name,
                "tool_category": tool.category.name if tool.category else None,
                "tool_priority": tool.priority_level,
                "change_count": len(changes)
            },
            created_at=datetime.utcnow(),
            channels=rule.channels
        )
        
        return alert
    
    def _send_alert(self, alert: Alert):
        """Send alert through configured channels"""
        for channel in alert.channels:
            try:
                if channel == AlertChannel.EMAIL:
                    self._send_email_alert(alert)
                elif channel == AlertChannel.SLACK:
                    asyncio.create_task(self._send_slack_alert(alert))
                elif channel == AlertChannel.WEBHOOK:
                    asyncio.create_task(self._send_webhook_alert(alert))
                elif channel == AlertChannel.CONSOLE:
                    self._send_console_alert(alert)
                elif channel == AlertChannel.DATABASE:
                    # Already handled by _save_alert_to_database
                    pass
                
            except Exception as e:
                self.logger.error(f"Error sending alert via {channel.value}: {e}")
    
    def _send_email_alert(self, alert: Alert):
        """Send alert via email"""
        try:
            config = self.channel_configs[AlertChannel.EMAIL]
            
            if not config['username'] or not config['to_emails'][0]:
                self.logger.warning("Email configuration incomplete, skipping email alert")
                return
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = config['from_email'] or config['username']
            msg['To'] = ', '.join(config['to_emails'])
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
            
            # Create email body
            body = self._format_alert_message(alert, 'email')
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['username'], config['password'])
            server.sendmail(config['username'], config['to_emails'], msg.as_string())
            server.quit()
            
            self.logger.info(f"Email alert sent for {alert.tool_name}")
            
        except Exception as e:
            self.logger.error(f"Error sending email alert: {e}")
    
    async def _send_slack_alert(self, alert: Alert):
        """Send alert via Slack webhook"""
        try:
            config = self.channel_configs[AlertChannel.SLACK]
            
            if not config['webhook_url']:
                self.logger.warning("Slack webhook URL not configured, skipping Slack alert")
                return
            
            # Create Slack message
            color_map = {
                AlertSeverity.CRITICAL: "danger",
                AlertSeverity.HIGH: "warning", 
                AlertSeverity.MEDIUM: "good",
                AlertSeverity.LOW: "#439FE0",
                AlertSeverity.INFO: "#36a64f"
            }
            
            payload = {
                "channel": config['channel'],
                "username": config['username'],
                "attachments": [{
                    "color": color_map.get(alert.severity, "good"),
                    "title": alert.title,
                    "text": alert.message,
                    "fields": [
                        {"title": "Tool", "value": alert.tool_name, "short": True},
                        {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
                        {"title": "Changes", "value": str(len(alert.changes)), "short": True},
                        {"title": "Time", "value": alert.created_at.strftime("%Y-%m-%d %H:%M:%S"), "short": True}
                    ],
                    "footer": "AI Tools Monitor",
                    "ts": int(alert.created_at.timestamp())
                }]
            }
            
            # Send to Slack
            async with aiohttp.ClientSession() as session:
                async with session.post(config['webhook_url'], json=payload) as response:
                    if response.status == 200:
                        self.logger.info(f"Slack alert sent for {alert.tool_name}")
                    else:
                        self.logger.error(f"Slack alert failed with status {response.status}")
            
        except Exception as e:
            self.logger.error(f"Error sending Slack alert: {e}")
    
    async def _send_webhook_alert(self, alert: Alert):
        """Send alert via generic webhook"""
        try:
            config = self.channel_configs[AlertChannel.WEBHOOK]
            
            if not config['webhook_urls'][0]:
                self.logger.warning("Webhook URLs not configured, skipping webhook alert")
                return
            
            # Create webhook payload
            payload = asdict(alert)
            payload['created_at'] = alert.created_at.isoformat()
            payload['severity'] = alert.severity.value
            
            # Send to all configured webhooks
            async with aiohttp.ClientSession() as session:
                for webhook_url in config['webhook_urls']:
                    if not webhook_url:
                        continue
                    
                    try:
                        async with session.post(
                            webhook_url, 
                            json=payload, 
                            headers=config['headers']
                        ) as response:
                            if response.status == 200:
                                self.logger.info(f"Webhook alert sent to {webhook_url}")
                            else:
                                self.logger.error(f"Webhook alert failed for {webhook_url}: {response.status}")
                    except Exception as e:
                        self.logger.error(f"Error sending to webhook {webhook_url}: {e}")
            
        except Exception as e:
            self.logger.error(f"Error sending webhook alerts: {e}")
    
    def _send_console_alert(self, alert: Alert):
        """Send alert to console"""
        severity_emoji = {
            AlertSeverity.CRITICAL: "🚨",
            AlertSeverity.HIGH: "⚠️",
            AlertSeverity.MEDIUM: "📢",
            AlertSeverity.LOW: "ℹ️",
            AlertSeverity.INFO: "📋"
        }
        
        emoji = severity_emoji.get(alert.severity, "📢")
        print(f"\n{emoji} ALERT [{alert.severity.value.upper()}] {emoji}")
        print(f"Tool: {alert.tool_name}")
        print(f"Title: {alert.title}")
        print(f"Message: {alert.message}")
        print(f"Changes: {len(alert.changes)}")
        print(f"Time: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if alert.changes:
            print("Change Details:")
            for change in alert.changes[:3]:  # Show max 3 changes
                print(f"  • {change['change_type']}: {change['summary']}")
        
        print("-" * 50)
    
    def _save_alert_to_database(self, session, alert: Alert):
        """Save alert to database for tracking"""
        try:
            # Create a curation task for the alert (using existing model)
            task = CurationTask(
                task_type='alert_review',
                priority=self._severity_to_priority(alert.severity),
                entity_type='tool',
                entity_id=alert.tool_id,
                title=alert.title,
                description=alert.message,
                suggested_action=f"Review {len(alert.changes)} changes detected",
                status='pending'
            )
            
            session.add(task)
            self.logger.debug(f"Saved alert to database for tool {alert.tool_name}")
            
        except Exception as e:
            self.logger.error(f"Error saving alert to database: {e}")
    
    def _format_alert_message(self, alert: Alert, format_type: str) -> str:
        """Format alert message for specific channel"""
        if format_type == 'email':
            html = f"""
            <html>
            <body>
                <h2>{alert.title}</h2>
                <p><strong>Tool:</strong> {alert.tool_name}</p>
                <p><strong>Severity:</strong> {alert.severity.value.upper()}</p>
                <p><strong>Message:</strong> {alert.message}</p>
                <p><strong>Time:</strong> {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h3>Changes Detected ({len(alert.changes)}):</h3>
                <ul>
            """
            
            for change in alert.changes:
                html += f"""
                <li>
                    <strong>{change['change_type'].replace('_', ' ').title()}:</strong> 
                    {change['summary']}
                    <br><small>Impact: {change['impact_score']}/5, Confidence: {change['confidence']:.0%}</small>
                </li>
                """
            
            html += """
                </ul>
                <hr>
                <p><small>Generated by AI Tools Intelligence Platform</small></p>
            </body>
            </html>
            """
            return html
        
        # Default text format
        text = f"{alert.title}\n\n"
        text += f"Tool: {alert.tool_name}\n"
        text += f"Severity: {alert.severity.value.upper()}\n"
        text += f"Message: {alert.message}\n"
        text += f"Time: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        text += f"Changes ({len(alert.changes)}):\n"
        
        for change in alert.changes:
            text += f"• {change['change_type']}: {change['summary']}\n"
        
        return text
    
    def _severity_to_priority(self, severity: AlertSeverity) -> int:
        """Convert alert severity to curation task priority"""
        mapping = {
            AlertSeverity.CRITICAL: 1,
            AlertSeverity.HIGH: 2,
            AlertSeverity.MEDIUM: 3,
            AlertSeverity.LOW: 4,
            AlertSeverity.INFO: 5
        }
        return mapping.get(severity, 3)
    
    def _load_alert_rules(self) -> List[AlertRule]:
        """Load default alert rules"""
        return [
            # Critical version releases
            AlertRule(
                rule_id="version_releases",
                name="Version Releases",
                description="Alert on new version releases",
                change_types=[ChangeType.VERSION_BUMP],
                severity_threshold=AlertSeverity.HIGH,
                tool_filters={},
                cooldown_minutes=60,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.DATABASE]
            ),
            
            # Pricing changes
            AlertRule(
                rule_id="pricing_changes",
                name="Pricing Changes",
                description="Alert on pricing model or cost changes",
                change_types=[ChangeType.PRICE_CHANGE],
                severity_threshold=AlertSeverity.CRITICAL,
                tool_filters={},
                cooldown_minutes=30,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.DATABASE]
            ),
            
            # Major feature changes
            AlertRule(
                rule_id="major_features",
                name="Major Feature Changes",
                description="Alert on significant feature additions or removals",
                change_types=[ChangeType.ADDED, ChangeType.REMOVED],
                severity_threshold=AlertSeverity.HIGH,
                tool_filters={},
                cooldown_minutes=120,
                channels=[AlertChannel.SLACK, AlertChannel.DATABASE]
            ),
            
            # High-priority tools monitoring
            AlertRule(
                rule_id="priority_tools",
                name="Priority Tools Monitoring",
                description="Enhanced monitoring for high-priority tools",
                change_types=[ct for ct in ChangeType],
                severity_threshold=AlertSeverity.MEDIUM,
                tool_filters={"priority_levels": [1, 2]},
                cooldown_minutes=30,
                channels=[AlertChannel.EMAIL, AlertChannel.DATABASE]
            )
        ]
    
    def _load_notification_templates(self) -> Dict[str, NotificationTemplate]:
        """Load notification templates"""
        return {
            "email_default": NotificationTemplate(
                template_id="email_default",
                channel=AlertChannel.EMAIL,
                subject_template="[{severity}] {tool_name}: {title}",
                body_template="Alert for {tool_name}: {message}",
                format_type="html"
            ),
            "slack_default": NotificationTemplate(
                template_id="slack_default", 
                channel=AlertChannel.SLACK,
                subject_template="{title}",
                body_template="{message}",
                format_type="json"
            )
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the alert manager"""
        logger = logging.getLogger('change_alert_manager')
        logger.setLevel(logging.INFO)
        
        # Create file handler
        handler = logging.FileHandler('change_alerts.log')
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        
        return logger


# Export main classes
__all__ = [
    'ChangeAlertManager', 'Alert', 'AlertRule', 'AlertSeverity', 'AlertChannel'
]