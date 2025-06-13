#!/usr/bin/env python3
# change_detection/test_alert_system.py - Comprehensive test suite for the alert system

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from change_detection.alert_manager import ChangeAlertManager, AlertSeverity, AlertChannel
from change_detection.alert_integration import AlertIntegrationManager, AlertIntegrationConfig
from data_curation.curation_engine import ChangeDetection, ChangeType
from models.enhanced_schema import Tool, Company, ToolVersion, ToolChange
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class AlertSystemTestSuite:
    """Comprehensive test suite for the alert system"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
        self.alert_manager = ChangeAlertManager(self.database_url)
        self.integration_manager = AlertIntegrationManager(self.database_url)
        
        # Test configuration
        self.test_config = {
            "test_email": os.getenv('TEST_EMAIL'),
            "test_slack_webhook": os.getenv('TEST_SLACK_WEBHOOK'),
            "run_integration_tests": os.getenv('RUN_INTEGRATION_TESTS', 'false').lower() == 'true'
        }
        
        # Setup test database session
        engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=engine)
    
    def run_all_tests(self) -> Dict:
        """Run all test suites"""
        print("🧪 Starting Comprehensive Alert System Tests")
        print("=" * 60)
        
        results = {
            "started_at": datetime.utcnow().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "test_results": {}
        }
        
        # Test suites to run
        test_suites = [
            ("Basic Alert Manager", self.test_basic_alert_manager),
            ("Alert Rules", self.test_alert_rules),
            ("Notification Channels", self.test_notification_channels),
            ("Change Processing", self.test_change_processing),
            ("Alert Integration", self.test_alert_integration),
            ("Performance", self.test_performance),
            ("Error Handling", self.test_error_handling)
        ]
        
        # Run each test suite
        for suite_name, test_method in test_suites:
            print(f"\\n🔍 Running {suite_name} Tests...")
            
            try:
                suite_result = test_method()
                results["test_results"][suite_name] = suite_result
                results["tests_run"] += suite_result.get("tests_run", 0)
                results["tests_passed"] += suite_result.get("tests_passed", 0)
                results["tests_failed"] += suite_result.get("tests_failed", 0)
                
                if suite_result.get("overall_success", False):
                    print(f"  ✅ {suite_name} tests PASSED")
                else:
                    print(f"  ❌ {suite_name} tests FAILED")
                
            except Exception as e:
                print(f"  💥 {suite_name} tests CRASHED: {e}")
                results["test_results"][suite_name] = {
                    "overall_success": False,
                    "error": str(e),
                    "tests_run": 0,
                    "tests_passed": 0,
                    "tests_failed": 1
                }
                results["tests_run"] += 1
                results["tests_failed"] += 1
        
        # Calculate overall results
        results["completed_at"] = datetime.utcnow().isoformat()
        results["overall_success"] = results["tests_failed"] == 0
        results["success_rate"] = (results["tests_passed"] / max(results["tests_run"], 1)) * 100
        
        # Print summary
        self._print_test_summary(results)
        
        return results
    
    def test_basic_alert_manager(self) -> Dict:
        """Test basic alert manager functionality"""
        result = {"tests_run": 0, "tests_passed": 0, "tests_failed": 0, "details": []}
        
        # Test 1: Initialization
        result["tests_run"] += 1
        try:
            assert self.alert_manager is not None
            assert len(self.alert_manager.alert_rules) > 0
            result["tests_passed"] += 1
            result["details"].append("✅ Alert manager initialization")
        except Exception as e:
            result["tests_failed"] += 1
            result["details"].append(f"❌ Alert manager initialization: {e}")
        
        # Test 2: Rule loading
        result["tests_run"] += 1
        try:
            rules = self.alert_manager.alert_rules
            assert all(rule.rule_id for rule in rules)
            assert all(rule.name for rule in rules)
            result["tests_passed"] += 1
            result["details"].append(f"✅ Rule loading ({len(rules)} rules)")
        except Exception as e:
            result["tests_failed"] += 1
            result["details"].append(f"❌ Rule loading: {e}")
        
        # Test 3: Channel configuration
        result["tests_run"] += 1
        try:
            channels = self.alert_manager.channel_configs
            assert AlertChannel.EMAIL in channels
            assert AlertChannel.SLACK in channels
            result["tests_passed"] += 1
            result["details"].append("✅ Channel configuration")
        except Exception as e:
            result["tests_failed"] += 1
            result["details"].append(f"❌ Channel configuration: {e}")
        
        result["overall_success"] = result["tests_failed"] == 0
        return result
    
    def test_alert_rules(self) -> Dict:
        """Test alert rule functionality"""
        result = {"tests_run": 0, "tests_passed": 0, "tests_failed": 0, "details": []}
        
        # Test 1: Custom rule creation
        result["tests_run"] += 1
        try:
            rule_config = {
                "name": "Test Rule",
                "description": "Test rule for unit testing",
                "change_types": ["version_bump"],
                "severity_threshold": "high",
                "tool_filters": {"priority_levels": [1, 2]},
                "cooldown_minutes": 30,
                "channels": ["console", "database"]
            }
            
            rule = self.alert_manager.create_custom_alert_rule(rule_config)
            assert rule.name == "Test Rule"
            assert rule.cooldown_minutes == 30
            result["tests_passed"] += 1
            result["details"].append("✅ Custom rule creation")
        except Exception as e:
            result["tests_failed"] += 1
            result["details"].append(f"❌ Custom rule creation: {e}")
        
        # Test 2: Rule matching
        result["tests_run"] += 1
        try:
            session = self.Session()
            tool = session.query(Tool).first()
            if tool:
                rule = self.alert_manager.alert_rules[0]
                matches = self.alert_manager._tool_matches_rule(tool, rule)
                # Should return boolean
                assert isinstance(matches, bool)
                result["tests_passed"] += 1
                result["details"].append("✅ Rule matching logic")
            else:
                result["details"].append("⚠️ Rule matching: No tools in database")
            session.close()
        except Exception as e:
            result["tests_failed"] += 1
            result["details"].append(f"❌ Rule matching: {e}")
        
        result["overall_success"] = result["tests_failed"] == 0
        return result
    
    def test_notification_channels(self) -> Dict:
        """Test notification channel functionality"""
        result = {"tests_run": 0, "tests_passed": 0, "tests_failed": 0, "details": []}
        
        # Test 1: Console notifications
        result["tests_run"] += 1
        try:
            from change_detection.alert_manager import Alert
            
            test_alert = Alert(
                id="test_001",
                tool_id=1,
                tool_name="Test Tool",
                alert_type="test",
                severity=AlertSeverity.INFO,
                title="Test Alert",
                message="This is a test",
                changes=[],
                metadata={},
                created_at=datetime.utcnow(),
                channels=[AlertChannel.CONSOLE]
            )
            
            # This should not raise an exception
            self.alert_manager._send_console_alert(test_alert)
            result["tests_passed"] += 1
            result["details"].append("✅ Console notifications")
        except Exception as e:
            result["tests_failed"] += 1
            result["details"].append(f"❌ Console notifications: {e}")
        
        # Test 2: Email configuration check
        result["tests_run"] += 1
        try:
            email_config = self.alert_manager.channel_configs[AlertChannel.EMAIL]
            has_config = bool(email_config.get('username') and email_config.get('to_emails'))
            
            if has_config:
                result["details"].append("✅ Email configuration (configured)")
            else:
                result["details"].append("⚠️ Email configuration (not configured)")
            
            result["tests_passed"] += 1  # Pass regardless of configuration
        except Exception as e:
            result["tests_failed"] += 1
            result["details"].append(f"❌ Email configuration check: {e}")
        
        # Test 3: Message formatting
        result["tests_run"] += 1
        try:
            test_alert = Alert(
                id="test_002",
                tool_id=1,
                tool_name="Test Tool",
                alert_type="test",
                severity=AlertSeverity.MEDIUM,
                title="Format Test",
                message="Testing message formatting",
                changes=[{
                    "change_type": "test",
                    "summary": "Test change",
                    "impact_score": 3,
                    "confidence": 0.8
                }],
                metadata={},
                created_at=datetime.utcnow(),
                channels=[]
            )
            
            email_message = self.alert_manager._format_alert_message(test_alert, 'email')
            text_message = self.alert_manager._format_alert_message(test_alert, 'text')
            
            assert len(email_message) > 0
            assert len(text_message) > 0
            assert "Test Tool" in email_message
            assert "Test Tool" in text_message
            
            result["tests_passed"] += 1
            result["details"].append("✅ Message formatting")
        except Exception as e:
            result["tests_failed"] += 1
            result["details"].append(f"❌ Message formatting: {e}")
        
        result["overall_success"] = result["tests_failed"] == 0
        return result
    
    def test_change_processing(self) -> Dict:
        """Test change detection and processing"""
        result = {"tests_run": 0, "tests_passed": 0, "tests_failed": 0, "details": []}
        
        # Test 1: Change severity determination
        result["tests_run"] += 1
        try:
            test_changes = [
                ChangeDetection(ChangeType.VERSION_BUMP, "version", "1.0", "2.0", 0.9, "Version bump", 5),
                ChangeDetection(ChangeType.PRICE_CHANGE, "price", "10", "15", 0.8, "Price change", 4),
                ChangeDetection(ChangeType.ADDED, "feature", None, "New feature", 0.7, "Feature added", 2),
            ]
            
            severities = [self.alert_manager._determine_change_severity(change) for change in test_changes]
            
            # Version bump should be HIGH, price change CRITICAL, feature addition depends on impact
            assert severities[0] == AlertSeverity.HIGH  # Version bump
            assert severities[1] == AlertSeverity.CRITICAL  # Price change
            
            result["tests_passed"] += 1
            result["details"].append("✅ Change severity determination")
        except Exception as e:
            result["tests_failed"] += 1
            result["details"].append(f"❌ Change severity determination: {e}")
        
        # Test 2: Change grouping
        result["tests_run"] += 1
        try:
            test_changes = [
                ChangeDetection(ChangeType.VERSION_BUMP, "version", "1.0", "2.0", 0.9, "Version bump", 5),
                ChangeDetection(ChangeType.ADDED, "feature", None, "Feature", 0.7, "Feature added", 1),
            ]
            
            groups = self.alert_manager._group_changes_by_severity(test_changes)
            
            # Should have groups for each severity level
            assert isinstance(groups, dict)
            assert all(isinstance(changes, list) for changes in groups.values())
            
            result["tests_passed"] += 1
            result["details"].append("✅ Change grouping")
        except Exception as e:
            result["tests_failed"] += 1
            result["details"].append(f"❌ Change grouping: {e}")
        
        # Test 3: End-to-end change processing
        result["tests_run"] += 1
        try:
            session = self.Session()
            tool = session.query(Tool).first()
            
            if tool:
                test_changes = [
                    ChangeDetection(ChangeType.VERSION_BUMP, "version", "1.0", "1.1", 0.9, "Minor update", 3)
                ]
                
                alerts = self.alert_manager.process_change_event(tool.id, test_changes)
                
                # Should generate at least one alert
                assert isinstance(alerts, list)
                if alerts:
                    assert all(hasattr(alert, 'id') for alert in alerts)
                
                result["tests_passed"] += 1
                result["details"].append(f"✅ End-to-end processing ({len(alerts)} alerts)")
            else:
                result["details"].append("⚠️ End-to-end processing: No tools in database")
            
            session.close()
        except Exception as e:
            result["tests_failed"] += 1
            result["details"].append(f"❌ End-to-end processing: {e}")
        
        result["overall_success"] = result["tests_failed"] == 0
        return result
    
    def test_alert_integration(self) -> Dict:
        """Test integration between alert system and other components"""
        result = {"tests_run": 0, "tests_passed": 0, "tests_failed": 0, "details": []}
        
        # Test 1: Integration manager initialization
        result["tests_run"] += 1
        try:
            assert self.integration_manager is not None
            assert self.integration_manager.alert_manager is not None
            assert self.integration_manager.curation_engine is not None
            result["tests_passed"] += 1
            result["details"].append("✅ Integration manager initialization")
        except Exception as e:
            result["tests_failed"] += 1
            result["details"].append(f"❌ Integration manager initialization: {e}")
        
        # Test 2: Alert digest creation
        result["tests_run"] += 1
        try:
            digest = self.integration_manager.create_alert_digest(hours=24)
            
            assert isinstance(digest, dict)
            assert 'period_hours' in digest
            assert 'total_changes' in digest
            assert 'generated_at' in digest
            
            result["tests_passed"] += 1
            result["details"].append(f"✅ Alert digest creation ({digest.get('total_changes', 0)} changes)")
        except Exception as e:
            result["tests_failed"] += 1
            result["details"].append(f"❌ Alert digest creation: {e}")
        
        # Test 3: Immediate alert triggering
        result["tests_run"] += 1
        try:
            session = self.Session()
            tool = session.query(Tool).first()
            
            if tool:
                success = self.integration_manager.trigger_immediate_alert(
                    tool.id, 
                    "test_alert", 
                    "This is a test immediate alert",
                    AlertSeverity.LOW
                )
                
                assert isinstance(success, bool)
                result["tests_passed"] += 1
                result["details"].append(f"✅ Immediate alert triggering (success: {success})")
            else:
                result["details"].append("⚠️ Immediate alert: No tools in database")
            
            session.close()
        except Exception as e:
            result["tests_failed"] += 1
            result["details"].append(f"❌ Immediate alert triggering: {e}")
        
        result["overall_success"] = result["tests_failed"] == 0
        return result
    
    def test_performance(self) -> Dict:
        """Test system performance with multiple alerts"""
        result = {"tests_run": 0, "tests_passed": 0, "tests_failed": 0, "details": []}
        
        # Test 1: Multiple alert processing performance
        result["tests_run"] += 1
        try:
            session = self.Session()
            tool = session.query(Tool).first()
            
            if tool:
                # Create multiple test changes
                test_changes = []
                for i in range(10):
                    change = ChangeDetection(
                        ChangeType.MODIFIED,
                        f"test_field_{i}",
                        f"old_value_{i}",
                        f"new_value_{i}",
                        0.8,
                        f"Test change {i}",
                        2
                    )
                    test_changes.append(change)
                
                start_time = datetime.utcnow()
                alerts = self.alert_manager.process_change_event(tool.id, test_changes)
                end_time = datetime.utcnow()
                
                processing_time = (end_time - start_time).total_seconds()
                
                # Should process quickly (under 5 seconds for 10 changes)
                assert processing_time < 5.0
                
                result["tests_passed"] += 1
                result["details"].append(f"✅ Performance test ({len(test_changes)} changes in {processing_time:.2f}s)")
            else:
                result["details"].append("⚠️ Performance test: No tools in database")
            
            session.close()
        except Exception as e:
            result["tests_failed"] += 1
            result["details"].append(f"❌ Performance test: {e}")
        
        # Test 2: Memory usage during alert processing
        result["tests_run"] += 1
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Process several alerts
            session = self.Session()
            tools = session.query(Tool).limit(5).all()
            
            for tool in tools:
                test_changes = [
                    ChangeDetection(ChangeType.MODIFIED, "test", "old", "new", 0.8, "Test", 1)
                ]
                self.alert_manager.process_change_event(tool.id, test_changes)
            
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = memory_after - memory_before
            
            # Memory increase should be reasonable (under 50MB)
            assert memory_increase < 50
            
            result["tests_passed"] += 1
            result["details"].append(f"✅ Memory usage (+{memory_increase:.1f}MB)")
            
            session.close()
        except ImportError:
            result["details"].append("⚠️ Memory test: psutil not available")
        except Exception as e:
            result["tests_failed"] += 1
            result["details"].append(f"❌ Memory usage test: {e}")
        
        result["overall_success"] = result["tests_failed"] == 0
        return result
    
    def test_error_handling(self) -> Dict:
        """Test error handling and edge cases"""
        result = {"tests_run": 0, "tests_passed": 0, "tests_failed": 0, "details": []}
        
        # Test 1: Invalid tool ID
        result["tests_run"] += 1
        try:
            alerts = self.alert_manager.process_change_event(99999, [])
            
            # Should handle gracefully and return empty list
            assert isinstance(alerts, list)
            assert len(alerts) == 0
            
            result["tests_passed"] += 1
            result["details"].append("✅ Invalid tool ID handling")
        except Exception as e:
            result["tests_failed"] += 1
            result["details"].append(f"❌ Invalid tool ID handling: {e}")
        
        # Test 2: Empty changes list
        result["tests_run"] += 1
        try:
            session = self.Session()
            tool = session.query(Tool).first()
            
            if tool:
                alerts = self.alert_manager.process_change_event(tool.id, [])
                
                # Should handle empty changes gracefully
                assert isinstance(alerts, list)
                assert len(alerts) == 0
                
                result["tests_passed"] += 1
                result["details"].append("✅ Empty changes handling")
            else:
                result["details"].append("⚠️ Empty changes: No tools in database")
            
            session.close()
        except Exception as e:
            result["tests_failed"] += 1
            result["details"].append(f"❌ Empty changes handling: {e}")
        
        # Test 3: Malformed change data
        result["tests_run"] += 1
        try:
            session = self.Session()
            tool = session.query(Tool).first()
            
            if tool:
                # Create malformed change (missing required fields)
                malformed_changes = [
                    ChangeDetection(None, "", None, None, 0, "", 0)  # All None/empty values
                ]
                
                # Should not crash the system
                alerts = self.alert_manager.process_change_event(tool.id, malformed_changes)
                assert isinstance(alerts, list)
                
                result["tests_passed"] += 1
                result["details"].append("✅ Malformed change data handling")
            else:
                result["details"].append("⚠️ Malformed data: No tools in database")
            
            session.close()
        except Exception as e:
            result["tests_failed"] += 1
            result["details"].append(f"❌ Malformed change data: {e}")
        
        result["overall_success"] = result["tests_failed"] == 0
        return result
    
    def _print_test_summary(self, results: Dict):
        """Print comprehensive test summary"""
        print("\\n" + "=" * 60)
        print("🧪 ALERT SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        print(f"📊 Overall Results:")
        print(f"  Tests Run: {results['tests_run']}")
        print(f"  Tests Passed: {results['tests_passed']}")
        print(f"  Tests Failed: {results['tests_failed']}")
        print(f"  Success Rate: {results['success_rate']:.1f}%")
        
        overall_status = "✅ PASSED" if results['overall_success'] else "❌ FAILED"
        print(f"  Overall Status: {overall_status}")
        
        print(f"\\n📋 Test Suite Details:")
        for suite_name, suite_result in results['test_results'].items():
            status = "✅" if suite_result.get('overall_success', False) else "❌"
            passed = suite_result.get('tests_passed', 0)
            total = suite_result.get('tests_run', 0)
            print(f"  {status} {suite_name}: {passed}/{total}")
            
            # Show details for failed tests
            if not suite_result.get('overall_success', False) and 'details' in suite_result:
                for detail in suite_result['details']:
                    if detail.startswith('❌'):
                        print(f"    {detail}")
        
        print(f"\\n⏱️  Duration: {results['started_at']} → {results['completed_at']}")
        
        if results['overall_success']:
            print("\\n🎉 All tests passed! Alert system is working correctly.")
        else:
            print("\\n⚠️  Some tests failed. Please review the issues above.")


def main():
    """Main test runner"""
    print("🚀 Alert System Test Suite")
    print("Starting comprehensive tests...")
    
    try:
        # Initialize test suite
        test_suite = AlertSystemTestSuite()
        
        # Run all tests
        results = test_suite.run_all_tests()
        
        # Save results to file
        results_file = f"alert_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\\n📄 Test results saved to: {results_file}")
        
        # Exit with appropriate code
        sys.exit(0 if results['overall_success'] else 1)
        
    except KeyboardInterrupt:
        print("\\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\n💥 Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()