# Data Validation and Quality Scoring System

This directory contains the automated data validation and quality scoring system for the AI Tool Intelligence Platform. The system provides comprehensive quality assessment, automated curation triggers, and intelligent monitoring optimization.

## 🎯 Overview

The quality scoring system addresses the critical need for maintaining high-quality data in competitive intelligence applications. It automatically evaluates data completeness, accuracy, freshness, and consistency, then triggers appropriate curation actions.

### Key Features

- **Multi-dimensional Quality Assessment**: Evaluates completeness, accuracy, freshness, and consistency
- **Automated Validation Rules**: Comprehensive field validation with configurable rules
- **Intelligent Curation Triggers**: Automatically triggers data refresh when quality drops
- **Quality-based Monitoring**: Optimizes monitoring frequency based on quality patterns
- **Alert System**: Generates alerts for tools needing immediate attention
- **Integration with Curation Engine**: Seamlessly integrates with existing data curation workflows

## 📁 File Structure

```
data_validation/
├── quality_scorer.py          # Core quality assessment engine
├── quality_integration.py     # Integration with curation systems
├── quality_cli.py            # Command-line interface for quality operations
├── test_quality_system.py    # Test suite and demonstration script
└── README.md                 # This documentation
```

## 🔧 Core Components

### 1. DataQualityScorer (`quality_scorer.py`)

The main quality assessment engine that evaluates tools, companies, and versions.

#### Key Classes:
- `DataQualityScorer`: Main scoring engine
- `QualityAssessment`: Comprehensive quality report
- `ValidationRule`: Individual validation rule configuration
- `ValidationResult`: Result of field validation

#### Quality Metrics:
- **Completeness Score (0-100)**: How much required data is present
- **Accuracy Score (0-100)**: How well data passes validation rules
- **Freshness Score (0-100)**: How recently data was updated
- **Consistency Score (0-100)**: How consistent data is internally
- **Overall Score (0-100)**: Weighted combination of all metrics

#### Quality Grades:
- `HIGH` (90-100): Excellent quality, minimal issues
- `MEDIUM` (70-89): Good quality, minor improvements needed
- `LOW` (50-69): Poor quality, significant issues
- `UNVERIFIED` (<50): Very poor quality, major problems

### 2. QualityIntegrationManager (`quality_integration.py`)

Integrates quality scoring with the curation engine and monitoring systems.

#### Key Features:
- **Integrated Quality Checks**: Combines assessment with automatic curation
- **Quality Monitoring Sweeps**: Batch processing with intelligent prioritization
- **Alert Generation**: Creates actionable alerts for quality issues
- **Schedule Optimization**: Adjusts monitoring frequency based on quality patterns

#### Quality Thresholds:
- `urgent_review`: 30.0 - Triggers immediate manual review
- `auto_refresh`: 50.0 - Triggers automatic data refresh
- `validation_alert`: 70.0 - Generates validation alerts
- `freshness_days`: 30 - Days before data is considered stale

### 3. Quality CLI (`quality_cli.py`)

Command-line interface for quality operations and reporting.

#### Available Commands:
```bash
# Assess single tool
python quality_cli.py tool <tool_id> [--verbose]

# Bulk assessment
python quality_cli.py bulk [--limit N] [--min-score X]

# Generate comprehensive report
python quality_cli.py report [--output file.json] [--format json|txt]

# Identify quality issues
python quality_cli.py issues [--min-score X]

# Track quality trends
python quality_cli.py trends [--days N]
```

## 🚀 Usage Examples

### Basic Quality Assessment

```python
from data_validation.quality_scorer import DataQualityScorer

# Initialize scorer
scorer = DataQualityScorer()

# Assess a tool
assessment = scorer.assess_tool_quality(tool_id=1, include_analysis=True)

print(f"Overall Score: {assessment.overall_score:.1f}/100")
print(f"Quality Grade: {assessment.quality_grade.value}")
print(f"Issues: {len(assessment.issues_found)}")
```

### Integrated Quality Check with Curation

```python
from data_validation.quality_integration import QualityIntegrationManager

# Initialize integration manager
manager = QualityIntegrationManager()

# Run integrated check (includes automatic curation if needed)
result = manager.run_integrated_quality_check(tool_id=1)

print(f"Curation triggered: {result['curation_triggered']}")
print(f"Tasks created: {len(result['triggered_tasks'])}")
```

### Quality Monitoring Sweep

```python
# Run quality monitoring on all tools
sweep_result = manager.run_quality_monitoring_sweep(max_tools=50)

print(f"Tools processed: {sweep_result['total_tools_processed']}")
print(f"Issues found: {sweep_result['urgent_issues_found']}")
```

### Generate Quality Alerts

```python
# Get tools needing attention
alerts = manager.create_quality_alerts(min_score=70.0)

for alert in alerts:
    print(f"Tool: {alert['tool_name']}")
    print(f"Score: {alert['overall_score']:.1f}")
    print(f"Alert Level: {alert['alert_level']}")
```

## 📊 Validation Rules

### Tool Validation Rules

| Field | Rule Type | Weight | Description |
|-------|-----------|--------|-------------|
| name | required | 0.2 | Tool name must be present |
| description | min_length | 0.15 | Description should be at least 10 characters |
| website_url | url_format | 0.1 | Website URL should be valid |
| github_url | github_url | 0.1 | GitHub URL should be valid repository |
| category_id | required | 0.1 | Tool category is required |
| current_version | version_format | 0.05 | Version should follow semantic versioning |
| confidence_score | range | 0.1 | Confidence score should be 0-100 |

### Company Validation Rules

| Field | Rule Type | Weight | Description |
|-------|-----------|--------|-------------|
| name | required | 0.2 | Company name must be present |
| website | url_format | 0.1 | Company website should be valid |
| founded_year | year_range | 0.1 | Founded year should be reasonable |
| employee_count | positive_number | 0.1 | Employee count should be positive |
| headquarters | location_format | 0.05 | Headquarters should be in "City, Country" format |

### Version Validation Rules

| Field | Rule Type | Weight | Description |
|-------|-----------|--------|-------------|
| version_number | required | 0.3 | Version number is required |
| version_number | version_format | 0.2 | Version should follow semantic versioning |
| detected_at | required | 0.1 | Detection date is required |
| feature_snapshot | valid_json | 0.1 | Feature snapshot should be valid JSON |
| pricing_snapshot | valid_json | 0.1 | Pricing snapshot should be valid JSON |

## 🔄 Quality Workflow

### 1. Automated Quality Monitoring

The system runs continuous quality monitoring with the following schedule:

- **Daily Quality Sweeps**: Process all tools due for monitoring
- **Real-time Assessment**: Assess quality after each curation run
- **Weekly Schedule Optimization**: Adjust monitoring frequencies
- **Alert Generation**: Create alerts for quality issues every 6 hours

### 2. Quality-Triggered Actions

Based on quality scores, the system automatically:

| Score Range | Action | Description |
|-------------|--------|-------------|
| < 30 | Urgent Review | Manual review required immediately |
| 30-50 | Auto Refresh | Trigger automatic data curation |
| 50-70 | Validation Alert | Generate alert for validation issues |
| 70-90 | Minor Issues | Schedule routine review |
| > 90 | High Quality | Reduce monitoring frequency |

### 3. Curation Integration

The quality system integrates with the curation engine to:

- **Trigger Fresh Analysis**: When data is stale or inaccurate
- **Create Manual Tasks**: For issues requiring human intervention
- **Update Quality Metadata**: Store quality scores in tool records
- **Optimize Processing**: Focus resources on low-quality tools

## 📈 Quality Metrics

### Component Score Calculation

#### Completeness Score
```python
# Required fields weight: 70%, Optional fields weight: 30%
completeness = (required_filled * 0.7 + optional_filled * 0.3) / total_weighted_fields * 100
```

#### Accuracy Score
```python
# Weighted average of validation results
accuracy = sum(result.score * rule.weight) / total_weight * 100
```

#### Freshness Score
```python
# Based on days since last update
if days <= 1: return 100.0
elif days <= 7: return 90.0
elif days <= 30: return 75.0
elif days <= 90: return 50.0
else: return 25.0
```

#### Consistency Score
```python
# Based on internal data consistency checks
consistency = (passed_checks / total_checks) * 100
```

#### Overall Score
```python
# Weighted combination
overall = (completeness * 0.3 + accuracy * 0.4 + freshness * 0.2 + consistency * 0.1)
```

## 🧪 Testing

### Run the Test Suite

```bash
# Run comprehensive tests
python data_validation/test_quality_system.py

# Test specific components
python -c "from data_validation.test_quality_system import test_quality_scorer; test_quality_scorer()"
```

### CLI Testing

```bash
# Test single tool assessment
python data_validation/quality_cli.py tool 1 --verbose

# Test bulk assessment
python data_validation/quality_cli.py bulk --limit 5

# Generate test report
python data_validation/quality_cli.py report --output test_report.json
```

## 📝 Configuration

### Environment Variables

```bash
# Database connection
DATABASE_URL=sqlite:///ai_tools.db

# Quality thresholds (optional, defaults provided)
QUALITY_URGENT_THRESHOLD=30.0
QUALITY_REFRESH_THRESHOLD=50.0
QUALITY_ALERT_THRESHOLD=70.0
```

### Customizing Validation Rules

```python
# Extend validation rules in quality_scorer.py
custom_rules = {
    'tool': [
        ValidationRule('custom_field', 'custom_rule', {'param': 'value'}, 0.1, 'Custom validation'),
        # Add more rules...
    ]
}
```

## 🚀 Integration with Main Application

### Add to Curation Pipeline

```python
# In your curation workflow
from data_validation.quality_integration import QualityIntegrationManager

manager = QualityIntegrationManager()

# Run integrated quality check after each tool analysis
result = manager.run_integrated_quality_check(tool_id)

# Handle results
if result['curation_triggered']:
    print("Quality issues triggered automatic curation")

if result['triggered_tasks']:
    print(f"Created {len(result['triggered_tasks'])} improvement tasks")
```

### Monitoring Dashboard Integration

```python
# Get quality alerts for dashboard
alerts = manager.create_quality_alerts(min_score=70.0)

# Get quality trends
trends = manager.track_quality_trends(days=30)

# Display in your monitoring interface
for alert in alerts:
    display_alert(alert['tool_name'], alert['overall_score'], alert['alert_level'])
```

## 🔧 Maintenance

### Database Cleanup

The system creates quality reports that should be periodically cleaned:

```sql
-- Clean old quality reports (keep last 90 days)
DELETE FROM data_quality_reports 
WHERE report_date < datetime('now', '-90 days');

-- Clean completed curation tasks (keep last 30 days)
DELETE FROM curation_tasks 
WHERE status = 'completed' AND completed_at < datetime('now', '-30 days');
```

### Performance Optimization

For large datasets:

1. **Batch Processing**: Use bulk assessment with limits
2. **Caching**: Enable URL accessibility caching
3. **Indexing**: Ensure proper database indexes
4. **Parallel Processing**: Consider async processing for large sweeps

## 🆘 Troubleshooting

### Common Issues

1. **ValidationError: Tool not found**
   - Ensure tool exists in database
   - Check tool_id parameter

2. **ImportError: Module not found**
   - Verify Python path includes parent directory
   - Check all dependencies are installed

3. **Low Quality Scores**
   - Review validation rules
   - Check data completeness
   - Verify URL accessibility

4. **Performance Issues**
   - Reduce batch sizes
   - Enable caching
   - Use limits in bulk operations

### Debug Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with error handling
try:
    assessment = scorer.assess_tool_quality(tool_id)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
```

## 📋 Future Enhancements

1. **Machine Learning Integration**: Use ML for quality prediction
2. **Real-time Monitoring**: WebSocket-based live quality updates
3. **Advanced Analytics**: Quality trend prediction and forecasting
4. **API Integration**: RESTful API for external quality checks
5. **Custom Dashboards**: Interactive quality visualization tools

---

This data validation and quality scoring system provides a comprehensive foundation for maintaining high-quality competitive intelligence data. It automatically identifies issues, triggers appropriate actions, and optimizes monitoring resources for maximum efficiency.