# Change Detection and Alert System

This directory contains the real-time change detection and alert system for the AI Tool Intelligence Platform. The system automatically monitors for changes in AI developer tools and sends configurable alerts through multiple notification channels.

## 🎯 Overview

The change detection and alert system provides:

- **Real-time change monitoring** with configurable alert rules
- **Multiple notification channels** (Email, Slack, Webhooks, Console)
- **Intelligent alert routing** based on change severity and tool priority
- **Alert management** with acknowledgments and cooldown periods
- **Integration** with the existing curation and monitoring systems
- **Comprehensive testing** and configuration management

## 📁 File Structure

```
change_detection/
├── alert_manager.py           # Core alert system with notification channels
├── alert_integration.py       # Integration with curation and monitoring systems
├── alert_cli.py              # Command-line interface for alert management
├── test_alert_system.py      # Comprehensive test suite
├── example_alert_rule.json   # Example alert rule configuration
├── .env.example              # Environment configuration template
└── README.md                 # This documentation
```

## 🔧 Core Components

### 1. ChangeAlertManager (`alert_manager.py`)

The main alert processing engine that handles:

- **Alert Rule Processing**: Configurable rules for different change types
- **Severity Classification**: Automatic severity determination (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- **Multi-channel Notifications**: Email, Slack, webhooks, console, and database
- **Cooldown Management**: Prevents alert spam with configurable cooldown periods
- **Alert Tracking**: Maintains history and statistics

#### Key Classes:
- `ChangeAlertManager`: Main alert processing engine
- `Alert`: Individual alert message with metadata
- `AlertRule`: Configurable rule for alert generation
- `AlertSeverity`: Severity levels for alerts
- `AlertChannel`: Available notification channels

### 2. AlertIntegrationManager (`alert_integration.py`)

Integrates the alert system with existing components:

- **Curation Integration**: Automatic alerts when curation detects changes
- **Batch Processing Integration**: Summary alerts for batch processing results
- **Real-time Monitoring**: Continuous monitoring for new changes
- **Alert Digests**: Periodic summaries of activity
- **Quality Integration**: Alerts for data quality issues

### 3. Alert CLI (`alert_cli.py`)

Command-line tools for alert management:

- **System Testing**: Test alert generation and notification channels
- **Rule Management**: Create and manage custom alert rules
- **Monitoring**: Real-time change monitoring with alerts
- **Statistics**: Alert statistics and reporting
- **Simulation**: Simulate changes for testing

## 🚀 Quick Start

### 1. Configuration

Copy the environment template and configure your notification channels:

```bash
cp change_detection/.env.example .env
# Edit .env with your notification settings
```

### 2. Test the System

Run the comprehensive test suite:

```bash
python change_detection/test_alert_system.py
```

### 3. Test Alert Channels

Check notification channel configuration:

```bash
python change_detection/alert_cli.py test-channels
```

### 4. Simulate Alerts

Test with realistic change scenarios:

```bash
python change_detection/alert_cli.py simulate 1 --changes 5
```

### 5. Monitor Changes

Start real-time monitoring:

```bash
python change_detection/alert_cli.py monitor --interval 5 --duration 60
```

## 📊 Alert Types and Severity

### Severity Levels

| Severity | Description | Use Cases |
|----------|-------------|-----------|
| `CRITICAL` | Urgent attention required | Price changes, breaking changes |
| `HIGH` | Important changes | Version releases, major features |
| `MEDIUM` | Notable changes | Minor features, integrations |
| `LOW` | Minor changes | Documentation, small updates |
| `INFO` | Informational | Regular monitoring updates |

### Change Types

| Change Type | Typical Severity | Description |
|-------------|------------------|-------------|
| `VERSION_BUMP` | HIGH | New version releases |
| `PRICE_CHANGE` | CRITICAL | Pricing model or cost changes |
| `ADDED` | MEDIUM/HIGH | New features or capabilities |
| `REMOVED` | HIGH | Removed features or capabilities |
| `MODIFIED` | LOW/MEDIUM | Modified existing features |

## 🔧 Configuration

### Environment Variables

```bash
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ALERT_FROM_EMAIL=alerts@yourcompany.com
ALERT_TO_EMAILS=admin@yourcompany.com,team@yourcompany.com

# Slack Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
SLACK_CHANNEL=#ai-tools-alerts
SLACK_USERNAME=AI Tools Monitor

# Webhook Configuration
WEBHOOK_URLS=https://your-endpoint.com/alerts
WEBHOOK_HEADERS={"Authorization": "Bearer token"}

# System Settings
ALERT_DEBOUNCE_MINUTES=5
ALERT_BATCH_THRESHOLD=3
ENABLE_REAL_TIME_ALERTS=true
```

### Alert Rules

Create custom alert rules with JSON configuration:

```json
{
  "rule_id": "custom_rule",
  "name": "Custom Alert Rule",
  "description": "Description of when this rule triggers",
  "change_types": ["version_bump", "price_change"],
  "severity_threshold": "medium",
  "tool_filters": {
    "priority_levels": [1, 2],
    "category_ids": [1, 2, 3],
    "is_open_source": false
  },
  "cooldown_minutes": 30,
  "channels": ["email", "slack", "database"],
  "is_active": true
}
```

#### Tool Filters

Filter alerts by tool characteristics:

- `priority_levels`: Array of priority levels (1=highest, 5=lowest)
- `category_ids`: Array of category IDs to monitor
- `is_open_source`: Boolean to filter by open source status
- `name_patterns`: Array of regex patterns to match tool names

## 📧 Notification Channels

### 1. Email Notifications

- **HTML formatted** alerts with change details
- **Configurable recipients** with multiple email support
- **SMTP configuration** for various email providers
- **Template customization** for different alert types

### 2. Slack Notifications

- **Rich formatting** with colors based on severity
- **Structured attachments** with change details
- **Channel configuration** for different alert types
- **Bot integration** with custom usernames and icons

### 3. Webhook Notifications

- **JSON payload** with complete alert data
- **Multiple endpoints** support
- **Custom headers** for authentication
- **Retry logic** for failed deliveries

### 4. Console Notifications

- **Real-time display** in terminal
- **Severity-based emojis** for visual distinction
- **Formatted output** with change summaries
- **Development testing** friendly

### 5. Database Storage

- **Persistent alert history** in CurationTask table
- **Alert tracking** and management
- **Integration** with admin interfaces
- **Statistical analysis** of alert patterns

## 🔄 Integration with Existing Systems

### Curation Engine Integration

```python
from change_detection.alert_integration import AlertIntegrationManager

# Initialize integration
integration = AlertIntegrationManager()

# Setup automatic alerts after curation
integration.setup_curation_hooks()

# Now curation will automatically trigger alerts
result = curation_engine.curate_tool_data(tool_id)
```

### Batch Processing Integration

```python
# Setup batch monitoring alerts
integration.setup_batch_monitoring_hooks()

# Batch processing will now send summary alerts
monitor = CompetitiveMonitor()
monitor.run_quality_monitoring_sweep()
```

### Real-time Monitoring

```python
# Start continuous monitoring
integration.start_real_time_monitoring()

# Monitor will check for changes every minute and send alerts
```

## 📈 Usage Examples

### 1. Basic Alert Testing

```bash
# Test alert system with sample tool
python change_detection/alert_cli.py test --tool-id 1

# Test all notification channels
python change_detection/alert_cli.py test-channels
```

### 2. Custom Alert Rules

```bash
# Create custom rule from JSON
python change_detection/alert_cli.py create-rule --config example_alert_rule.json

# List all alert rules
python change_detection/alert_cli.py list-rules
```

### 3. Real-time Monitoring

```bash
# Monitor for 1 hour, checking every 5 minutes
python change_detection/alert_cli.py monitor --interval 5 --duration 60

# Monitor indefinitely (until Ctrl+C)
python change_detection/alert_cli.py monitor --interval 10 --duration 0
```

### 4. Alert Statistics

```bash
# Get alert statistics for last 30 days
python change_detection/alert_cli.py stats --days 30

# Get statistics for last week
python change_detection/alert_cli.py stats --days 7
```

### 5. Change Simulation

```bash
# Simulate 3 realistic changes for tool ID 1
python change_detection/alert_cli.py simulate 1 --changes 3

# Simulate changes for multiple tools
for i in {1..5}; do
  python change_detection/alert_cli.py simulate $i --changes 2
done
```

## 🧪 Testing

### Comprehensive Test Suite

Run the full test suite:

```bash
python change_detection/test_alert_system.py
```

The test suite includes:

- **Basic Functionality**: Alert manager initialization and configuration
- **Alert Rules**: Custom rule creation and matching logic
- **Notification Channels**: Channel configuration and message formatting
- **Change Processing**: End-to-end change detection and alert generation
- **Integration**: Integration with curation and monitoring systems
- **Performance**: Multi-alert processing and memory usage
- **Error Handling**: Edge cases and error recovery

### Test Results

Tests generate detailed results in JSON format:

```json
{
  "started_at": "2025-12-06T10:30:00",
  "completed_at": "2025-12-06T10:32:15",
  "tests_run": 25,
  "tests_passed": 24,
  "tests_failed": 1,
  "success_rate": 96.0,
  "overall_success": false,
  "test_results": {
    "Basic Alert Manager": {"tests_passed": 3, "tests_failed": 0},
    "Alert Rules": {"tests_passed": 2, "tests_failed": 0},
    "Notification Channels": {"tests_passed": 3, "tests_failed": 0},
    "Change Processing": {"tests_passed": 3, "tests_failed": 0},
    "Alert Integration": {"tests_passed": 3, "tests_failed": 0},
    "Performance": {"tests_passed": 2, "tests_failed": 0},
    "Error Handling": {"tests_passed": 2, "tests_failed": 1}
  }
}
```

## 🚨 Alert Management

### Alert Acknowledgment

```bash
# Acknowledge a specific alert
python change_detection/alert_cli.py acknowledge alert_123 --user john.doe
```

### Alert Digests

```python
from change_detection.alert_integration import AlertIntegrationManager

integration = AlertIntegrationManager()

# Create daily digest
digest = integration.create_alert_digest(hours=24)

# Send digest alert
integration.send_digest_alert(digest)
```

### Immediate Alerts

```python
# Trigger immediate alert
integration.trigger_immediate_alert(
    tool_id=1,
    alert_type="manual_review_needed",
    message="Tool requires immediate manual review",
    severity=AlertSeverity.HIGH
)
```

## 🔧 Customization

### Custom Alert Rules

Create domain-specific alert rules:

```python
from change_detection.alert_manager import ChangeAlertManager, AlertRule, AlertSeverity, AlertChannel, ChangeType

alert_manager = ChangeAlertManager()

# Create rule for enterprise tools
enterprise_rule = {
    "rule_id": "enterprise_focus",
    "name": "Enterprise Tool Focus",
    "description": "Enhanced monitoring for enterprise AI tools",
    "change_types": [ChangeType.VERSION_BUMP, ChangeType.PRICE_CHANGE],
    "severity_threshold": AlertSeverity.MEDIUM,
    "tool_filters": {
        "name_patterns": [".*[Ee]nterprise.*", ".*[Bb]usiness.*"],
        "priority_levels": [1, 2]
    },
    "cooldown_minutes": 15,
    "channels": [AlertChannel.EMAIL, AlertChannel.SLACK],
    "is_active": True
}

alert_manager.create_custom_alert_rule(enterprise_rule)
```

### Custom Notification Templates

Extend message formatting:

```python
def custom_email_formatter(alert):
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #d73502;">{alert.title}</h2>
        <p><strong>Tool:</strong> {alert.tool_name}</p>
        <p><strong>Severity:</strong> {alert.severity.value.upper()}</p>
        <p><strong>Message:</strong> {alert.message}</p>
        <!-- Custom styling and content -->
    </body>
    </html>
    """

# Replace the default formatter
alert_manager._format_alert_message = custom_email_formatter
```

## 📊 Monitoring and Analytics

### Alert Statistics

The system automatically tracks:

- **Alert frequency** by tool and severity
- **Change patterns** over time
- **Notification delivery** success rates
- **Response times** and acknowledgments

### Integration with Dashboards

Export alert data for visualization:

```python
# Get alert statistics
stats = alert_manager.get_alert_statistics(days=30)

# Create digest for dashboard
digest = integration.create_alert_digest(hours=24)

# Export to external systems via webhooks
```

## 🚀 Production Deployment

### Environment Setup

1. **Configure notification channels** in production environment
2. **Set up proper SMTP** for email alerts
3. **Configure Slack webhooks** for team notifications
4. **Set up monitoring webhooks** for integration with other systems

### Scaling Considerations

- **Rate limiting**: Configure cooldown periods to prevent alert spam
- **Batch processing**: Use batch alerts for high-volume changes
- **Queue management**: Consider message queues for high-throughput environments
- **Database performance**: Monitor alert storage and cleanup old records

### Security

- **Secure credentials**: Use environment variables or secrets management
- **Webhook security**: Implement proper authentication for webhook endpoints
- **Access control**: Restrict alert management to authorized users
- **Audit logging**: Track alert rule changes and management actions

## 🔧 Troubleshooting

### Common Issues

1. **Alerts not being sent**
   - Check notification channel configuration
   - Verify environment variables
   - Test channels with `alert_cli.py test-channels`

2. **Too many alerts**
   - Adjust cooldown periods in alert rules
   - Increase severity thresholds
   - Use batch alert mode

3. **Missing alerts**
   - Check alert rule filters
   - Verify tool priority levels
   - Review change detection thresholds

4. **Email delivery issues**
   - Verify SMTP configuration
   - Check email credentials
   - Test with simple SMTP client

5. **Slack notifications not working**
   - Verify webhook URL is active
   - Check Slack app permissions
   - Test webhook with curl

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run alert system with debug output
alert_manager = ChangeAlertManager()
```

### Testing Tools

Use CLI tools for debugging:

```bash
# Test specific functionality
python change_detection/alert_cli.py test --tool-id 1
python change_detection/alert_cli.py test-channels
python change_detection/alert_cli.py simulate 1 --changes 1

# Check system status
python change_detection/alert_cli.py stats --days 1
python change_detection/alert_cli.py list-rules
```

---

This change detection and alert system provides a comprehensive foundation for real-time monitoring of AI tool changes with flexible notification and integration capabilities. It seamlessly integrates with the existing competitive intelligence platform to provide immediate awareness of important changes in the AI tools landscape.