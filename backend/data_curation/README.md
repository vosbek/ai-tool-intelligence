# Data Curation and Enhancement System

This directory contains the advanced data curation and enhancement system for the AI Tool Intelligence Platform. It provides intelligent data processing, change detection, quality enhancement, and automated version management.

## 🎯 Overview

The data curation system provides:

- **🤖 Intelligent Curation**: AI-powered data analysis and enhancement using AWS Strands agents
- **🔍 Change Detection**: Sophisticated comparison and analysis of data changes over time
- **📈 Quality Enhancement**: Automatic data quality improvements and validation
- **⚡ Version Management**: Intelligent versioning and historical change tracking
- **🔄 Automated Processing**: Batch processing with priority queues and scheduling
- **🎯 Confidence Scoring**: AI-powered confidence assessment for all data changes

## 📁 File Structure

```
data_curation/
├── curation_engine.py        # Core curation engine with change detection and AI analysis
└── README.md                 # This documentation
```

## 🔧 Core Components

### 1. CurationEngine (`curation_engine.py`)

The main curation engine that provides comprehensive data processing and enhancement.

#### Key Classes:
- `CurationEngine`: Main curation processing engine
- `CurationResult`: Comprehensive curation results with change analysis
- `ChangeAnalysis`: Detailed analysis of detected changes
- `DataComparison`: Comparison results between data snapshots

#### Curation Capabilities:
- **Tool Analysis**: Comprehensive tool research and data collection
- **Change Detection**: Multi-dimensional change analysis across versions, pricing, features, and integrations
- **Quality Assessment**: Automated data quality scoring and validation
- **Version Management**: Intelligent version detection and historical tracking
- **Confidence Scoring**: AI-powered confidence assessment for data reliability

#### Change Detection Types:
- **VERSION_CHANGE**: New version releases and updates
- **PRICE_CHANGE**: Pricing model or cost modifications
- **FEATURE_CHANGE**: Added, modified, or removed features
- **INTEGRATION_CHANGE**: New or updated integrations
- **COMPANY_CHANGE**: Company information updates
- **METADATA_CHANGE**: General metadata modifications

#### Analysis Depth Levels:
- **QUICK**: Fast analysis focusing on basic updates
- **STANDARD**: Comprehensive analysis with change detection
- **DEEP**: Extensive analysis with full competitive intelligence
- **COMPARISON**: Focused comparison against existing data

## 🚀 Usage Examples

### Basic Tool Curation

```python
from data_curation.curation_engine import CurationEngine

# Initialize curation engine
engine = CurationEngine()

# Curate tool data with change detection
result = engine.curate_tool_data(tool_id=1, analysis_depth='standard')

print(f"Curation Status: {result.status}")
print(f"Changes Detected: {result.changes_detected}")
print(f"Quality Score: {result.quality_score:.2f}")
print(f"Confidence Score: {result.confidence_score:.2f}")

# Review detected changes
for change in result.change_analysis.detected_changes:
    print(f"Change Type: {change.change_type}")
    print(f"Field: {change.field_name}")
    print(f"Old Value: {change.old_value}")
    print(f"New Value: {change.new_value}")
    print(f"Confidence: {change.confidence:.2f}")
```

### Advanced Change Analysis

```python
# Perform deep analysis with competitive intelligence
result = engine.curate_tool_data(
    tool_id=1, 
    analysis_depth='deep',
    force_refresh=True,
    include_competitive_analysis=True
)

# Analyze change patterns
change_analysis = result.change_analysis
print(f"Total Changes: {len(change_analysis.detected_changes)}")
print(f"Significant Changes: {change_analysis.significant_changes_count}")
print(f"Change Categories: {change_analysis.change_categories}")

# Review change significance
for change in change_analysis.significant_changes:
    print(f"Significant Change: {change.field_name}")
    print(f"Impact Score: {change.impact_score:.2f}")
    print(f"Business Impact: {change.business_impact}")
```

### Batch Processing

```python
# Process multiple tools
tool_ids = [1, 2, 3, 4, 5]
results = []

for tool_id in tool_ids:
    result = engine.curate_tool_data(tool_id, analysis_depth='standard')
    results.append(result)
    
    if result.changes_detected:
        print(f"Tool {tool_id}: {len(result.change_analysis.detected_changes)} changes detected")

# Analyze batch results
successful_curations = [r for r in results if r.status == 'completed']
print(f"Successful Curations: {len(successful_curations)}/{len(results)}")
```

### Quality-Driven Curation

```python
# Curation with quality thresholds
result = engine.curate_tool_data(
    tool_id=1,
    min_quality_threshold=0.8,
    min_confidence_threshold=0.7
)

if result.quality_score < 0.8:
    print("Quality threshold not met - manual review recommended")
    print(f"Quality Issues: {result.quality_issues}")

if result.confidence_score < 0.7:
    print("Confidence threshold not met - data verification needed")
    print(f"Low Confidence Areas: {result.low_confidence_fields}")
```

## 📊 Curation Workflow

### 1. Data Collection and Analysis

The curation engine collects data through multiple channels:

```python
def _collect_tool_data(self, tool_id: int) -> Dict:
    """Collect comprehensive tool data using multiple sources"""
    
    # Get current tool data
    current_data = self._get_current_tool_data(tool_id)
    
    # Perform AI-powered research using Strands agents
    research_data = self._perform_ai_research(tool_id)
    
    # Merge and validate data
    enhanced_data = self._merge_and_validate_data(current_data, research_data)
    
    return enhanced_data
```

### 2. Change Detection and Analysis

Sophisticated change detection across multiple dimensions:

```python
def _detect_changes(self, tool_id: int, new_data: Dict) -> ChangeAnalysis:
    """Detect and analyze changes in tool data"""
    
    # Get previous data snapshot
    previous_data = self._get_previous_snapshot(tool_id)
    
    if not previous_data:
        return ChangeAnalysis(is_initial_analysis=True)
    
    # Compare data structures
    changes = []
    
    # Version changes
    version_changes = self._compare_versions(previous_data, new_data)
    changes.extend(version_changes)
    
    # Pricing changes
    pricing_changes = self._compare_pricing(previous_data, new_data)
    changes.extend(pricing_changes)
    
    # Feature changes
    feature_changes = self._compare_features(previous_data, new_data)
    changes.extend(feature_changes)
    
    # Integration changes
    integration_changes = self._compare_integrations(previous_data, new_data)
    changes.extend(integration_changes)
    
    return ChangeAnalysis(detected_changes=changes)
```

### 3. Quality Assessment and Enhancement

Automated quality evaluation and improvement:

```python
def _assess_data_quality(self, data: Dict) -> float:
    """Assess the quality of curated data"""
    
    quality_metrics = {
        'completeness': self._calculate_completeness(data),
        'accuracy': self._validate_data_accuracy(data),
        'consistency': self._check_data_consistency(data),
        'freshness': self._evaluate_data_freshness(data)
    }
    
    # Weighted quality score
    quality_score = (
        quality_metrics['completeness'] * 0.3 +
        quality_metrics['accuracy'] * 0.4 +
        quality_metrics['consistency'] * 0.2 +
        quality_metrics['freshness'] * 0.1
    )
    
    return quality_score
```

### 4. Version Management

Intelligent version detection and tracking:

```python
def _manage_versions(self, tool_id: int, data: Dict, changes: ChangeAnalysis) -> None:
    """Manage tool versions based on detected changes"""
    
    # Detect if new version should be created
    if self._should_create_new_version(changes):
        version_data = self._extract_version_data(data)
        new_version = self._create_tool_version(tool_id, version_data)
        print(f"Created new version: {new_version.version_number}")
    
    # Update current data
    self._update_current_data(tool_id, data)
    
    # Store change history
    self._store_change_history(tool_id, changes)
```

## 🔍 Change Detection Features

### Multi-Dimensional Comparison

The system compares data across multiple dimensions:

#### Version Comparison
```python
def _compare_versions(self, old_data: Dict, new_data: Dict) -> List[DataChange]:
    """Compare version information"""
    changes = []
    
    # Check version number changes
    old_version = old_data.get('version', {}).get('current')
    new_version = new_data.get('version', {}).get('current')
    
    if old_version != new_version and new_version:
        changes.append(DataChange(
            change_type=ChangeType.VERSION_CHANGE,
            field_name='current_version',
            old_value=old_version,
            new_value=new_version,
            confidence=0.95,
            impact_score=0.8
        ))
    
    return changes
```

#### Pricing Comparison
```python
def _compare_pricing(self, old_data: Dict, new_data: Dict) -> List[DataChange]:
    """Compare pricing information"""
    changes = []
    
    old_pricing = old_data.get('pricing', {})
    new_pricing = new_data.get('pricing', {})
    
    # Compare pricing model
    if old_pricing.get('model') != new_pricing.get('model'):
        changes.append(DataChange(
            change_type=ChangeType.PRICE_CHANGE,
            field_name='pricing_model',
            old_value=old_pricing.get('model'),
            new_value=new_pricing.get('model'),
            confidence=0.9,
            impact_score=0.9
        ))
    
    # Compare pricing tiers
    old_tiers = set(t['name'] for t in old_pricing.get('tiers', []))
    new_tiers = set(t['name'] for t in new_pricing.get('tiers', []))
    
    # Detect new tiers
    added_tiers = new_tiers - old_tiers
    removed_tiers = old_tiers - new_tiers
    
    for tier in added_tiers:
        changes.append(DataChange(
            change_type=ChangeType.PRICE_CHANGE,
            field_name='pricing_tier_added',
            old_value=None,
            new_value=tier,
            confidence=0.85,
            impact_score=0.7
        ))
    
    return changes
```

### Change Significance Assessment

```python
def _assess_change_significance(self, change: DataChange) -> float:
    """Assess the significance of a detected change"""
    
    significance_weights = {
        ChangeType.VERSION_CHANGE: 0.8,
        ChangeType.PRICE_CHANGE: 0.9,
        ChangeType.FEATURE_CHANGE: 0.7,
        ChangeType.INTEGRATION_CHANGE: 0.6,
        ChangeType.COMPANY_CHANGE: 0.5,
        ChangeType.METADATA_CHANGE: 0.3
    }
    
    base_significance = significance_weights.get(change.change_type, 0.5)
    confidence_modifier = change.confidence
    impact_modifier = change.impact_score
    
    significance = base_significance * confidence_modifier * impact_modifier
    return min(significance, 1.0)
```

## 📈 Quality Enhancement Features

### Data Validation and Enhancement

```python
def _enhance_data_quality(self, data: Dict) -> Dict:
    """Enhance data quality through validation and enrichment"""
    
    enhanced_data = data.copy()
    
    # Standardize data formats
    enhanced_data = self._standardize_formats(enhanced_data)
    
    # Fill missing data where possible
    enhanced_data = self._fill_missing_data(enhanced_data)
    
    # Validate and correct inconsistencies
    enhanced_data = self._validate_and_correct(enhanced_data)
    
    # Enrich with additional context
    enhanced_data = self._enrich_with_context(enhanced_data)
    
    return enhanced_data
```

### Confidence Scoring

```python
def _calculate_confidence_score(self, data: Dict, research_result: Dict) -> float:
    """Calculate confidence score for curated data"""
    
    confidence_factors = {
        'source_reliability': self._assess_source_reliability(research_result),
        'data_consistency': self._check_internal_consistency(data),
        'validation_success': self._validate_against_known_patterns(data),
        'ai_confidence': research_result.get('confidence_score', 0.5)
    }
    
    # Weighted confidence calculation
    confidence_score = (
        confidence_factors['source_reliability'] * 0.3 +
        confidence_factors['data_consistency'] * 0.3 +
        confidence_factors['validation_success'] * 0.2 +
        confidence_factors['ai_confidence'] * 0.2
    )
    
    return confidence_score
```

## 🔧 Configuration

### Curation Engine Configuration

```python
curation_config = {
    'default_analysis_depth': 'standard',
    'min_quality_threshold': 0.7,
    'min_confidence_threshold': 0.6,
    'max_processing_time_minutes': 10,
    'enable_competitive_analysis': True,
    'auto_create_versions': True
}
```

### Change Detection Configuration

```python
change_detection_config = {
    'significance_threshold': 0.5,
    'confidence_threshold': 0.7,
    'max_changes_per_session': 50,
    'enable_deep_comparison': True,
    'track_minor_changes': False
}
```

### Quality Enhancement Configuration

```python
quality_config = {
    'enable_auto_enhancement': True,
    'standardize_formats': True,
    'fill_missing_data': True,
    'validate_urls': True,
    'enrich_company_data': True
}
```

## 🧪 Testing and Validation

### Curation Engine Testing

```python
def test_curation_engine():
    engine = CurationEngine()
    
    # Test basic curation
    result = engine.curate_tool_data(1, analysis_depth='quick')
    assert result.status in ['completed', 'partial', 'failed']
    assert 0 <= result.quality_score <= 1
    assert 0 <= result.confidence_score <= 1
    
    # Test change detection
    if result.changes_detected:
        assert len(result.change_analysis.detected_changes) > 0
        for change in result.change_analysis.detected_changes:
            assert change.confidence > 0
            assert change.change_type in [ct.value for ct in ChangeType]
    
    print("✅ Curation engine test passed")
```

### Change Detection Testing

```python
def test_change_detection():
    engine = CurationEngine()
    
    # Create test data with known changes
    old_data = {'version': {'current': '1.0.0'}, 'pricing': {'model': 'free'}}
    new_data = {'version': {'current': '1.1.0'}, 'pricing': {'model': 'freemium'}}
    
    # Detect changes
    changes = engine._detect_changes_in_data(old_data, new_data)
    
    # Validate change detection
    assert len(changes.detected_changes) >= 2  # Version and pricing changes
    version_change = next((c for c in changes.detected_changes if c.field_name == 'current_version'), None)
    assert version_change is not None
    assert version_change.old_value == '1.0.0'
    assert version_change.new_value == '1.1.0'
    
    print("✅ Change detection test passed")
```

## 🚀 Integration with Main Platform

### Automatic Integration

The curation engine is automatically integrated into the main application:

```python
# Enhanced curation endpoint in app.py
@app.route('/api/tools/<int:tool_id>/curate', methods=['POST'])
def curate_tool_data(tool_id):
    """Enhanced curation with competitive analysis"""
    enhanced_system = EnhancedSystemManager()
    
    if not enhanced_system.available:
        # Fallback to basic research
        return research_tool(tool_id)
    
    try:
        result = enhanced_system.curate_tool_data(tool_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Real-time Integration

```python
# Integration with competitive analysis
def curate_tool_data(self, tool_id: int) -> Dict:
    """Curate tool data with competitive analysis"""
    if not self.available:
        return {"error": "Enhanced features not available"}
    
    try:
        # Run curation
        result = self.curation_engine.curate_tool_data(tool_id)
        
        # Trigger competitive analysis if significant changes
        if result.get('changes_detected'):
            self.competitive_integration.trigger_immediate_analysis(tool_id, 'standard')
        
        return result
        
    except Exception as e:
        return {"error": str(e)}
```

## 🔄 Maintenance and Optimization

### Performance Optimization

```python
# Optimize curation performance
def optimize_curation_performance():
    # Cache frequently accessed data
    self._setup_data_cache()
    
    # Use connection pooling for database operations
    self._setup_connection_pool()
    
    # Optimize AI research calls
    self._batch_ai_requests()
    
    # Implement intelligent scheduling
    self._setup_priority_queues()
```

### Data Cleanup

```sql
-- Clean old curation results (keep last 90 days)
DELETE FROM curation_results WHERE created_at < datetime('now', '-90 days');

-- Clean old change history (keep last 180 days)
DELETE FROM tool_changes WHERE detected_at < datetime('now', '-180 days');

-- Optimize curation tables
VACUUM curation_results;
ANALYZE tool_changes;
```

### Error Handling and Recovery

```python
def handle_curation_error(self, tool_id: int, error: Exception) -> Dict:
    """Handle curation errors with graceful degradation"""
    
    error_result = {
        'status': 'failed',
        'error_type': type(error).__name__,
        'error_message': str(error),
        'fallback_attempted': False
    }
    
    # Attempt fallback to basic research
    try:
        fallback_result = self._fallback_to_basic_research(tool_id)
        error_result['fallback_attempted'] = True
        error_result['fallback_result'] = fallback_result
    except Exception as fallback_error:
        error_result['fallback_error'] = str(fallback_error)
    
    return error_result
```

## 🚀 Future Enhancements

1. **Machine Learning Integration**: ML-powered change prediction and data enhancement
2. **Real-time Streaming**: Continuous data monitoring and instant change detection
3. **Advanced Analytics**: Predictive analytics for data quality and change patterns
4. **Multi-source Integration**: Integration with additional data sources and APIs
5. **Automated Workflows**: Self-healing data pipelines with automatic error recovery

---

This data curation and enhancement system provides intelligent, automated data processing capabilities that ensure the AI Tool Intelligence Platform maintains high-quality, up-to-date information about AI developer tools with comprehensive change tracking and quality assessment.