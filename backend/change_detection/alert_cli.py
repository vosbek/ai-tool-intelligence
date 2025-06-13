#!/usr/bin/env python3
# change_detection/alert_cli.py - CLI tool for managing alerts and testing the alert system

import argparse
import json
import sys
import os
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from change_detection.alert_manager import ChangeAlertManager, AlertSeverity, AlertChannel, AlertRule
from data_curation.curation_engine import ChangeDetection, ChangeType
from models.enhanced_schema import Tool, ToolChange
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class AlertCLI:
    """Command-line interface for alert management"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
        self.alert_manager = ChangeAlertManager(self.database_url)
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def test_alert_system(self, tool_id: int = None) -> Dict:
        """Test the alert system with sample changes"""
        session = self.Session()
        
        try:
            # Get a tool to test with
            if tool_id:
                tool = session.query(Tool).filter_by(id=tool_id).first()
            else:
                tool = session.query(Tool).first()
            
            if not tool:
                print("❌ No tools found in database. Please add some tools first.")
                return {"error": "No tools found"}
            
            print(f"🧪 Testing alert system with tool: {tool.name}")
            
            # Create sample changes for testing
            test_changes = [
                ChangeDetection(
                    change_type=ChangeType.VERSION_BUMP,
                    field_name='version',
                    old_value='1.0.0',
                    new_value='2.0.0',
                    confidence=0.95,
                    summary=f"{tool.name} released major version 2.0.0",
                    impact_score=5
                ),
                ChangeDetection(
                    change_type=ChangeType.ADDED,
                    field_name='core_features_feature',
                    old_value=None,
                    new_value='AI Code Review',
                    confidence=0.85,
                    summary="Added new AI Code Review feature",
                    impact_score=4
                ),
                ChangeDetection(
                    change_type=ChangeType.PRICE_CHANGE,
                    field_name='pricing_model',
                    old_value='freemium',
                    new_value='subscription',
                    confidence=0.90,
                    summary="Changed from freemium to subscription model",
                    impact_score=4
                )
            ]
            
            print(f"📝 Created {len(test_changes)} test changes:")
            for change in test_changes:
                print(f"  • {change.change_type.value}: {change.summary}")
            
            # Process changes through alert system
            alerts = self.alert_manager.process_change_event(tool.id, test_changes)
            
            print(f"\\n🚨 Generated {len(alerts)} alerts:")
            for alert in alerts:
                print(f"  • [{alert.severity.value.upper()}] {alert.title}")
                print(f"    Message: {alert.message}")
                print(f"    Channels: {[ch.value for ch in alert.channels]}")
                print(f"    Changes: {len(alert.changes)}")
            
            result = {
                "tool_tested": tool.name,
                "test_changes": len(test_changes),
                "alerts_generated": len(alerts),
                "alerts": [
                    {
                        "id": alert.id,
                        "severity": alert.severity.value,
                        "title": alert.title,
                        "channels": [ch.value for ch in alert.channels]
                    } for alert in alerts
                ]
            }
            
            print("\\n✅ Alert system test completed successfully!")
            return result
            
        except Exception as e:
            print(f"❌ Error testing alert system: {e}")
            return {"error": str(e)}
        finally:
            session.close()
    
    def monitor_changes(self, interval_minutes: int = 5, duration_minutes: int = 60) -> Dict:
        """Monitor for changes and send alerts"""
        print(f"🔍 Starting change monitoring...")
        print(f"Interval: {interval_minutes} minutes")
        print(f"Duration: {duration_minutes} minutes")
        print("Press Ctrl+C to stop monitoring early")
        
        try:
            # Run monitoring for specified duration
            async def run_monitoring():
                monitoring_task = asyncio.create_task(
                    self.alert_manager.monitor_continuous_changes(interval_minutes)
                )
                
                # Wait for specified duration or until stopped
                try:
                    await asyncio.wait_for(monitoring_task, timeout=duration_minutes * 60)
                except asyncio.TimeoutError:
                    monitoring_task.cancel()
                    print(f"\\n⏰ Monitoring completed after {duration_minutes} minutes")
                
                return monitoring_task.result() if monitoring_task.done() else {}
            
            # Run the monitoring
            result = asyncio.run(run_monitoring())
            
            print("\\n📊 Monitoring Results:")
            print(f"  Checks performed: {result.get('checks_performed', 0)}")
            print(f"  Tools checked: {result.get('tools_checked', 0)}")
            print(f"  Alerts generated: {result.get('alerts_generated', 0)}")
            print(f"  Errors: {len(result.get('errors', []))}")
            
            return result
            
        except KeyboardInterrupt:
            print("\\n⏹️  Monitoring stopped by user")
            return {"stopped_by_user": True}
        except Exception as e:
            print(f"❌ Error during monitoring: {e}")
            return {"error": str(e)}
    
    def create_alert_rule(self, rule_config: Dict) -> Dict:
        """Create a custom alert rule"""
        try:
            print(f"📋 Creating custom alert rule: {rule_config.get('name', 'Unnamed Rule')}")
            
            # Validate rule configuration
            required_fields = ['name', 'change_types', 'severity_threshold', 'channels']
            for field in required_fields:
                if field not in rule_config:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create the rule
            rule = self.alert_manager.create_custom_alert_rule(rule_config)
            
            print(f"✅ Created alert rule: {rule.name}")
            print(f"  Description: {rule.description}")
            print(f"  Change types: {[ct.value for ct in rule.change_types]}")
            print(f"  Severity threshold: {rule.severity_threshold.value}")
            print(f"  Channels: {[ch.value for ch in rule.channels]}")
            print(f"  Cooldown: {rule.cooldown_minutes} minutes")
            
            return {
                "rule_id": rule.rule_id,
                "name": rule.name,
                "created": True
            }
            
        except Exception as e:
            print(f"❌ Error creating alert rule: {e}")
            return {"error": str(e)}
    
    def list_alert_rules(self) -> Dict:
        """List all alert rules"""
        try:
            rules = self.alert_manager.alert_rules
            
            print(f"📋 Alert Rules ({len(rules)} total):")
            print("-" * 60)
            
            for rule in rules:
                status = "🟢 Active" if rule.is_active else "🔴 Inactive"
                print(f"{status} {rule.name} ({rule.rule_id})")
                print(f"  Description: {rule.description}")
                print(f"  Change types: {[ct.value for ct in rule.change_types]}")
                print(f"  Severity: {rule.severity_threshold.value}+")
                print(f"  Channels: {[ch.value for ch in rule.channels]}")
                print(f"  Cooldown: {rule.cooldown_minutes} min")
                
                if rule.tool_filters:
                    print(f"  Filters: {rule.tool_filters}")
                
                print()
            
            return {
                "total_rules": len(rules),
                "active_rules": sum(1 for r in rules if r.is_active),
                "rules": [
                    {
                        "rule_id": r.rule_id,
                        "name": r.name,
                        "is_active": r.is_active,
                        "change_types": [ct.value for ct in r.change_types],
                        "severity_threshold": r.severity_threshold.value,
                        "channels": [ch.value for ch in r.channels]
                    } for r in rules
                ]
            }
            
        except Exception as e:
            print(f"❌ Error listing alert rules: {e}")
            return {"error": str(e)}
    
    def get_alert_statistics(self, days: int = 30) -> Dict:
        """Get alert statistics"""
        try:
            print(f"📊 Getting alert statistics for the last {days} days...")
            
            stats = self.alert_manager.get_alert_statistics(days)
            
            print(f"\\n📈 Alert Statistics ({days} days):")
            print(f"  Total changes: {stats.get('total_changes', 0)}")
            
            if stats.get('changes_by_type'):
                print("  \\n📝 Changes by type:")
                for change_type, count in stats['changes_by_type'].items():
                    print(f"    {change_type}: {count}")
            
            if stats.get('changes_by_severity'):
                print("  \\n⚠️ Changes by severity:")
                for severity, count in stats['changes_by_severity'].items():
                    print(f"    {severity}: {count}")
            
            if stats.get('most_active_tools'):
                print("  \\n🔥 Most active tools:")
                sorted_tools = sorted(stats['most_active_tools'].items(), key=lambda x: x[1], reverse=True)
                for tool_name, count in sorted_tools[:5]:
                    print(f"    {tool_name}: {count} changes")
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting alert statistics: {e}")
            return {"error": str(e)}
    
    def test_notification_channels(self) -> Dict:
        """Test all configured notification channels"""
        print("🧪 Testing notification channels...")
        
        results = {}
        
        # Test console notification (always works)
        print("\\n📺 Testing console notifications:")
        try:
            from change_detection.alert_manager import Alert, AlertSeverity
            
            test_alert = Alert(
                id="test_alert_001",
                tool_id=1,
                tool_name="Test Tool",
                alert_type="test",
                severity=AlertSeverity.INFO,
                title="Test Alert",
                message="This is a test alert to verify notification channels",
                changes=[{
                    "change_type": "test",
                    "summary": "Test change for notification testing",
                    "impact_score": 1
                }],
                metadata={"test": True},
                created_at=datetime.utcnow(),
                channels=[AlertChannel.CONSOLE]
            )
            
            self.alert_manager._send_console_alert(test_alert)
            results["console"] = {"status": "success", "message": "Console notifications working"}
            
        except Exception as e:
            results["console"] = {"status": "error", "message": str(e)}
        
        # Test email configuration
        print("\\n📧 Testing email configuration:")
        try:
            config = self.alert_manager.channel_configs[AlertChannel.EMAIL]
            
            if config['username'] and config['to_emails'][0]:
                results["email"] = {"status": "configured", "message": f"Email configured for {len(config['to_emails'])} recipients"}
            else:
                results["email"] = {"status": "not_configured", "message": "Email credentials not set"}
            
        except Exception as e:
            results["email"] = {"status": "error", "message": str(e)}
        
        # Test Slack configuration
        print("\\n💬 Testing Slack configuration:")
        try:
            config = self.alert_manager.channel_configs[AlertChannel.SLACK]
            
            if config['webhook_url']:
                results["slack"] = {"status": "configured", "message": f"Slack webhook configured for {config['channel']}"}
            else:
                results["slack"] = {"status": "not_configured", "message": "Slack webhook URL not set"}
            
        except Exception as e:
            results["slack"] = {"status": "error", "message": str(e)}
        
        # Test webhook configuration
        print("\\n🔗 Testing webhook configuration:")
        try:
            config = self.alert_manager.channel_configs[AlertChannel.WEBHOOK]
            
            if config['webhook_urls'][0]:
                results["webhook"] = {"status": "configured", "message": f"Webhooks configured for {len(config['webhook_urls'])} endpoints"}
            else:
                results["webhook"] = {"status": "not_configured", "message": "Webhook URLs not set"}
            
        except Exception as e:
            results["webhook"] = {"status": "error", "message": str(e)}
        
        # Summary
        print("\\n📋 Channel Test Summary:")
        for channel, result in results.items():
            status_emoji = {"success": "✅", "configured": "🟡", "not_configured": "⚪", "error": "❌"}
            emoji = status_emoji.get(result["status"], "❓")
            print(f"  {emoji} {channel}: {result['message']}")
        
        return results
    
    def simulate_real_changes(self, tool_id: int, num_changes: int = 5) -> Dict:
        """Simulate realistic changes for testing"""
        session = self.Session()
        
        try:
            tool = session.query(Tool).filter_by(id=tool_id).first()
            if not tool:
                print(f"❌ Tool with ID {tool_id} not found")
                return {"error": "Tool not found"}
            
            print(f"🎭 Simulating {num_changes} realistic changes for {tool.name}...")
            
            # Create realistic change scenarios
            change_scenarios = [
                {
                    "type": ChangeType.VERSION_BUMP,
                    "field": "version",
                    "old": "1.2.3",
                    "new": "1.3.0",
                    "summary": f"{tool.name} released minor version 1.3.0 with new features",
                    "impact": 3,
                    "confidence": 0.95
                },
                {
                    "type": ChangeType.ADDED,
                    "field": "ai_features_feature",
                    "old": None,
                    "new": "Smart Code Completion",
                    "summary": "Added Smart Code Completion powered by AI",
                    "impact": 4,
                    "confidence": 0.88
                },
                {
                    "type": ChangeType.PRICE_CHANGE,
                    "field": "price_monthly",
                    "old": "29",
                    "new": "39",
                    "summary": "Monthly subscription price increased from $29 to $39",
                    "impact": 3,
                    "confidence": 0.92
                },
                {
                    "type": ChangeType.ADDED,
                    "field": "ide_integrations_integration",
                    "old": None,
                    "new": "Neovim Plugin",
                    "summary": "Added official Neovim plugin integration",
                    "impact": 2,
                    "confidence": 0.85
                },
                {
                    "type": ChangeType.MODIFIED,
                    "field": "github_stars",
                    "old": "12500",
                    "new": "15000",
                    "summary": "GitHub stars increased from 12.5K to 15K (20% growth)",
                    "impact": 1,
                    "confidence": 0.98
                },
                {
                    "type": ChangeType.REMOVED,
                    "field": "enterprise_features_feature",
                    "old": "Legacy API v1",
                    "new": None,
                    "summary": "Deprecated and removed Legacy API v1 support",
                    "impact": 3,
                    "confidence": 0.90
                }
            ]
            
            # Select random scenarios
            import random
            selected_scenarios = random.sample(change_scenarios, min(num_changes, len(change_scenarios)))
            
            # Convert to ChangeDetection objects
            changes = []
            for scenario in selected_scenarios:
                change = ChangeDetection(
                    change_type=scenario["type"],
                    field_name=scenario["field"],
                    old_value=scenario["old"],
                    new_value=scenario["new"],
                    confidence=scenario["confidence"],
                    summary=scenario["summary"],
                    impact_score=scenario["impact"]
                )
                changes.append(change)
            
            print("📝 Simulated changes:")
            for change in changes:
                print(f"  • {change.change_type.value}: {change.summary}")
            
            # Process through alert system
            alerts = self.alert_manager.process_change_event(tool.id, changes)
            
            print(f"\\n🚨 Generated {len(alerts)} alerts from simulated changes")
            
            return {
                "tool_name": tool.name,
                "simulated_changes": len(changes),
                "alerts_generated": len(alerts),
                "change_types": [c.change_type.value for c in changes],
                "alert_severities": [a.severity.value for a in alerts]
            }
            
        except Exception as e:
            print(f"❌ Error simulating changes: {e}")
            return {"error": str(e)}
        finally:
            session.close()
    
    def acknowledge_alert(self, alert_id: str, user: str) -> Dict:
        """Acknowledge an alert"""
        try:
            success = self.alert_manager.acknowledge_alert(alert_id, user)
            
            if success:
                print(f"✅ Alert {alert_id} acknowledged by {user}")
                return {"acknowledged": True, "alert_id": alert_id, "user": user}
            else:
                print(f"❌ Failed to acknowledge alert {alert_id}")
                return {"acknowledged": False, "alert_id": alert_id}
            
        except Exception as e:
            print(f"❌ Error acknowledging alert: {e}")
            return {"error": str(e)}


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Alert Management CLI")
    parser.add_argument('--database-url', help='Database URL')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Test alert system
    test_parser = subparsers.add_parser('test', help='Test the alert system')
    test_parser.add_argument('--tool-id', type=int, help='Tool ID to test with')
    
    # Monitor changes
    monitor_parser = subparsers.add_parser('monitor', help='Monitor for changes')
    monitor_parser.add_argument('--interval', type=int, default=5, help='Check interval in minutes')
    monitor_parser.add_argument('--duration', type=int, default=60, help='Monitoring duration in minutes')
    
    # Create alert rule
    rule_parser = subparsers.add_parser('create-rule', help='Create custom alert rule')
    rule_parser.add_argument('--config', required=True, help='JSON file with rule configuration')
    
    # List rules
    subparsers.add_parser('list-rules', help='List all alert rules')
    
    # Get statistics
    stats_parser = subparsers.add_parser('stats', help='Get alert statistics')
    stats_parser.add_argument('--days', type=int, default=30, help='Number of days to analyze')
    
    # Test channels
    subparsers.add_parser('test-channels', help='Test notification channels')
    
    # Simulate changes
    sim_parser = subparsers.add_parser('simulate', help='Simulate realistic changes')
    sim_parser.add_argument('tool_id', type=int, help='Tool ID to simulate changes for')
    sim_parser.add_argument('--changes', type=int, default=3, help='Number of changes to simulate')
    
    # Acknowledge alert
    ack_parser = subparsers.add_parser('acknowledge', help='Acknowledge an alert')
    ack_parser.add_argument('alert_id', help='Alert ID to acknowledge')
    ack_parser.add_argument('--user', required=True, help='User acknowledging the alert')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI
    cli = AlertCLI(args.database_url)
    
    try:
        if args.command == 'test':
            cli.test_alert_system(args.tool_id)
        
        elif args.command == 'monitor':
            cli.monitor_changes(args.interval, args.duration)
        
        elif args.command == 'create-rule':
            with open(args.config, 'r') as f:
                rule_config = json.load(f)
            cli.create_alert_rule(rule_config)
        
        elif args.command == 'list-rules':
            cli.list_alert_rules()
        
        elif args.command == 'stats':
            cli.get_alert_statistics(args.days)
        
        elif args.command == 'test-channels':
            cli.test_notification_channels()
        
        elif args.command == 'simulate':
            cli.simulate_real_changes(args.tool_id, args.changes)
        
        elif args.command == 'acknowledge':
            cli.acknowledge_alert(args.alert_id, args.user)
    
    except KeyboardInterrupt:
        print("\\n⏹️  Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()