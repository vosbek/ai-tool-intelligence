# models/enhanced_schema.py - Complete schema for competitive monitoring and version tracking

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.sqlite import JSON
from datetime import datetime, timedelta
from enum import Enum
import json

db = SQLAlchemy()

# Enums for consistent data values
class ProcessingStatus(Enum):
    NEVER_RUN = "never_run"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"

class ChangeType(Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    VERSION_BUMP = "version_bump"
    PRICE_CHANGE = "price_change"
    FEATURE_CHANGE = "feature_change"

class DataQuality(Enum):
    HIGH = "high"        # >90% confidence, verified
    MEDIUM = "medium"    # 70-90% confidence
    LOW = "low"          # 50-70% confidence
    UNVERIFIED = "unverified"  # <50% confidence

class AnalysisType(Enum):
    INITIAL = "initial"
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    TRIGGERED = "triggered"  # By change detection


# =============================================================================
# CORE TOOL ENTITIES
# =============================================================================

class Tool(db.Model):
    """Enhanced tool model with version tracking and competitive monitoring"""
    __tablename__ = 'tools'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Core identification
    name = db.Column(db.String(200), nullable=False, index=True)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)  # URL-friendly identifier
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    
    # URLs and links
    website_url = db.Column(db.String(500), index=True)
    github_url = db.Column(db.String(500), index=True)
    documentation_url = db.Column(db.String(500))
    changelog_url = db.Column(db.String(500))
    blog_url = db.Column(db.String(500))
    
    # Current state (latest version)
    current_version = db.Column(db.String(50))
    current_version_id = db.Column(db.Integer, db.ForeignKey('tool_versions.id'))
    
    # Basic metadata
    description = db.Column(db.Text)
    is_open_source = db.Column(db.Boolean, default=False)
    license_type = db.Column(db.String(100))
    primary_language = db.Column(db.String(50))
    
    # Competitive tracking
    is_actively_monitored = db.Column(db.Boolean, default=True)
    monitoring_frequency_days = db.Column(db.Integer, default=7)  # How often to check
    priority_level = db.Column(db.Integer, default=3)  # 1=highest, 5=lowest
    
    # Processing status
    processing_status = db.Column(db.Enum(ProcessingStatus), default=ProcessingStatus.NEVER_RUN)
    last_processed_at = db.Column(db.DateTime)
    next_process_date = db.Column(db.DateTime)
    last_change_detected_at = db.Column(db.DateTime)
    
    # Data quality
    overall_data_quality = db.Column(db.Enum(DataQuality), default=DataQuality.UNVERIFIED)
    confidence_score = db.Column(db.Float, default=0.0)  # 0-100
    data_completeness = db.Column(db.Float, default=0.0)  # 0-100
    
    # Manual curation
    internal_notes = db.Column(db.Text)
    curator_notes = db.Column(db.Text)
    is_curated = db.Column(db.Boolean, default=False)
    curated_at = db.Column(db.DateTime)
    curated_by = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = db.relationship('Company', backref='tool', uselist=False, cascade='all, delete-orphan')
    versions = db.relationship('ToolVersion', backref='tool', cascade='all, delete-orphan', order_by='ToolVersion.detected_at.desc()')
    analysis_snapshots = db.relationship('AnalysisSnapshot', backref='tool', cascade='all, delete-orphan')
    changes = db.relationship('ToolChange', backref='tool', cascade='all, delete-orphan')
    competitive_analyses = db.relationship('CompetitiveAnalysis', backref='tool', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Tool {self.name} ({self.current_version})>'


class ToolVersion(db.Model):
    """Version-specific snapshots of tools"""
    __tablename__ = 'tool_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    
    # Version information
    version_number = db.Column(db.String(50), nullable=False)
    version_name = db.Column(db.String(200))  # "Codename" or marketing name
    release_date = db.Column(db.DateTime)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Version metadata
    is_stable = db.Column(db.Boolean, default=True)
    is_beta = db.Column(db.Boolean, default=False)
    is_alpha = db.Column(db.Boolean, default=False)
    is_deprecated = db.Column(db.Boolean, default=False)
    
    # Release information
    release_notes_url = db.Column(db.String(500))
    download_url = db.Column(db.String(500))
    announcement_url = db.Column(db.String(500))
    
    # Data quality for this version
    data_quality = db.Column(db.Enum(DataQuality), default=DataQuality.UNVERIFIED)
    confidence_score = db.Column(db.Float, default=0.0)
    
    # Snapshot data (JSON)
    feature_snapshot = db.Column(db.Text)  # JSON of features at this version
    pricing_snapshot = db.Column(db.Text)  # JSON of pricing at this version
    integration_snapshot = db.Column(db.Text)  # JSON of integrations
    github_metrics_snapshot = db.Column(db.Text)  # JSON of GitHub stats
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    features = db.relationship('VersionFeature', backref='version', cascade='all, delete-orphan')
    pricing_data = db.relationship('VersionPricing', backref='version', cascade='all, delete-orphan')
    integrations = db.relationship('VersionIntegration', backref='version', cascade='all, delete-orphan')
    
    __table_args__ = (
        UniqueConstraint('tool_id', 'version_number', name='unique_tool_version'),
        Index('idx_tool_version_detected', 'tool_id', 'detected_at'),
    )


# =============================================================================
# VERSION-SPECIFIC DATA
# =============================================================================

class VersionFeature(db.Model):
    """Features specific to a tool version"""
    __tablename__ = 'version_features'
    
    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.Integer, db.ForeignKey('tool_versions.id'), nullable=False)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)  # Denormalized for performance
    
    feature_category = db.Column(db.String(100), nullable=False)
    feature_name = db.Column(db.String(200), nullable=False)
    feature_description = db.Column(db.Text)
    
    is_core_feature = db.Column(db.Boolean, default=True)
    is_ai_feature = db.Column(db.Boolean, default=False)
    is_enterprise_feature = db.Column(db.Boolean, default=False)
    is_new_in_version = db.Column(db.Boolean, default=False)
    
    confidence_score = db.Column(db.Float, default=0.0)
    source_url = db.Column(db.String(500))
    extraction_method = db.Column(db.String(50))  # 'firecrawl_ai', 'basic', 'manual'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_version_feature_category', 'version_id', 'feature_category'),
    )


class VersionPricing(db.Model):
    """Pricing information specific to a tool version"""
    __tablename__ = 'version_pricing'
    
    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.Integer, db.ForeignKey('tool_versions.id'), nullable=False)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    
    pricing_model = db.Column(db.String(50))  # 'freemium', 'subscription', 'usage_based', etc.
    tier_name = db.Column(db.String(100))
    price_monthly = db.Column(db.Numeric(10, 2))
    price_yearly = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(3), default='USD')
    
    free_tier_available = db.Column(db.Boolean, default=False)
    trial_period_days = db.Column(db.Integer)
    enterprise_available = db.Column(db.Boolean, default=False)
    
    pricing_details = db.Column(db.Text)  # JSON with full pricing structure
    confidence_score = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class VersionIntegration(db.Model):
    """Integrations available in a specific tool version"""
    __tablename__ = 'version_integrations'
    
    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.Integer, db.ForeignKey('tool_versions.id'), nullable=False)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    
    integration_category = db.Column(db.String(50))  # 'ide', 'cicd', 'cloud', etc.
    integration_name = db.Column(db.String(200), nullable=False)
    integration_type = db.Column(db.String(50))  # 'native', 'plugin', 'api'
    
    is_verified = db.Column(db.Boolean, default=False)
    marketplace_url = db.Column(db.String(500))
    setup_complexity = db.Column(db.String(20))  # 'simple', 'moderate', 'complex'
    
    confidence_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =============================================================================
# CHANGE TRACKING
# =============================================================================

class ToolChange(db.Model):
    """Track all changes detected in tools over time"""
    __tablename__ = 'tool_changes'
    
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    
    change_type = db.Column(db.Enum(ChangeType), nullable=False)
    change_category = db.Column(db.String(50))  # 'feature', 'pricing', 'version', 'integration'
    
    # Change details
    from_version = db.Column(db.String(50))
    to_version = db.Column(db.String(50))
    
    field_name = db.Column(db.String(100))  # What field changed
    old_value = db.Column(db.Text)  # Previous value
    new_value = db.Column(db.Text)  # New value
    
    change_summary = db.Column(db.Text)  # Human-readable summary
    impact_score = db.Column(db.Integer, default=1)  # 1-5, how significant is this change
    
    # Detection metadata
    detected_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    detection_method = db.Column(db.String(50))  # 'automated', 'manual'
    confidence_score = db.Column(db.Float, default=0.0)
    
    # Review status
    is_reviewed = db.Column(db.Boolean, default=False)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.String(100))
    review_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_tool_change_detected', 'tool_id', 'detected_at'),
        Index('idx_change_type_category', 'change_type', 'change_category'),
    )


# =============================================================================
# ANALYSIS AND SNAPSHOTS
# =============================================================================

class AnalysisSnapshot(db.Model):
    """Point-in-time analysis results for tools"""
    __tablename__ = 'analysis_snapshots'
    
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    version_id = db.Column(db.Integer, db.ForeignKey('tool_versions.id'))
    
    analysis_type = db.Column(db.Enum(AnalysisType), nullable=False)
    analysis_version = db.Column(db.String(20), default='1.0')  # Schema version for analysis
    
    # Raw analysis data (JSON from strand agents)
    github_analysis = db.Column(db.Text)  # Full GitHub analysis JSON
    pricing_analysis = db.Column(db.Text)  # Full pricing analysis JSON
    company_analysis = db.Column(db.Text)  # Full company analysis JSON
    feature_analysis = db.Column(db.Text)  # Full feature analysis JSON
    integration_analysis = db.Column(db.Text)  # Full integration analysis JSON
    
    # Analysis metadata
    tools_used = db.Column(db.Text)  # JSON array of which tools were used
    api_calls_made = db.Column(db.Integer, default=0)
    total_confidence = db.Column(db.Float, default=0.0)
    data_completeness = db.Column(db.Float, default=0.0)
    
    # Processing information
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    processing_time_seconds = db.Column(db.Integer)
    
    status = db.Column(db.Enum(ProcessingStatus), default=ProcessingStatus.RUNNING)
    error_message = db.Column(db.Text)
    
    # Comparison with previous analysis
    changes_detected = db.Column(db.Integer, default=0)
    previous_snapshot_id = db.Column(db.Integer, db.ForeignKey('analysis_snapshots.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_analysis_tool_date', 'tool_id', 'started_at'),
    )


# =============================================================================
# COMPETITIVE ANALYSIS
# =============================================================================

class CompetitiveAnalysis(db.Model):
    """Cross-tool competitive analysis and market positioning"""
    __tablename__ = 'competitive_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    
    analysis_name = db.Column(db.String(200), nullable=False)
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Competitive metrics
    market_position = db.Column(db.String(50))  # 'leader', 'challenger', 'niche', 'follower'
    popularity_score = db.Column(db.Float)  # Calculated from GitHub stars, usage, etc.
    innovation_score = db.Column(db.Float)  # Based on feature velocity, uniqueness
    maturity_score = db.Column(db.Float)  # Based on stability, company age, etc.
    
    # Competitive comparisons (JSON)
    competitor_tools = db.Column(db.Text)  # JSON array of competitor tool IDs
    strength_analysis = db.Column(db.Text)  # JSON of competitive strengths
    weakness_analysis = db.Column(db.Text)  # JSON of competitive weaknesses
    market_trends = db.Column(db.Text)  # JSON of relevant market trends
    
    # Overall assessment
    recommendation = db.Column(db.Text)
    risk_level = db.Column(db.String(20))  # 'low', 'medium', 'high'
    
    confidence_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MarketTrend(db.Model):
    """Track market trends across tool categories"""
    __tablename__ = 'market_trends'
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    
    trend_name = db.Column(db.String(200), nullable=False)
    trend_type = db.Column(db.String(50))  # 'technology', 'pricing', 'features', 'adoption'
    
    trend_description = db.Column(db.Text)
    trend_data = db.Column(db.Text)  # JSON with trend metrics over time
    
    # Trend metadata
    confidence_level = db.Column(db.Enum(DataQuality))
    impact_score = db.Column(db.Integer)  # 1-5
    time_horizon = db.Column(db.String(20))  # 'short', 'medium', 'long'
    
    first_detected = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =============================================================================
# ENHANCED EXISTING MODELS
# =============================================================================

class Category(db.Model):
    """Enhanced category model with trend tracking"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    description = db.Column(db.Text)
    
    # Monitoring settings
    is_monitored = db.Column(db.Boolean, default=True)
    monitoring_priority = db.Column(db.Integer, default=3)  # 1=highest, 5=lowest
    
    # Category metrics
    tool_count = db.Column(db.Integer, default=0)
    active_tool_count = db.Column(db.Integer, default=0)
    last_trend_analysis = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))
    tools = db.relationship('Tool', backref='category')
    market_trends = db.relationship('MarketTrend', backref='category')


class Company(db.Model):
    """Enhanced company model with versioning and change tracking"""
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    
    # Basic company info
    name = db.Column(db.String(200), nullable=False)
    website = db.Column(db.String(500))
    founded_year = db.Column(db.Integer)
    headquarters = db.Column(db.String(200))
    
    # Financial data
    stock_symbol = db.Column(db.String(10))
    is_public = db.Column(db.Boolean, default=False)
    estimated_arr = db.Column(db.Numeric(15, 2))
    last_funding_round = db.Column(db.String(50))
    total_funding = db.Column(db.Numeric(15, 2))
    valuation = db.Column(db.Numeric(15, 2))
    
    # Team data
    employee_count = db.Column(db.Integer)
    employee_count_source = db.Column(db.String(100))
    employee_count_date = db.Column(db.DateTime)
    key_executives = db.Column(db.Text)  # JSON
    
    # Business intelligence
    strategic_focus = db.Column(db.Text)
    business_model = db.Column(db.String(100))
    target_market = db.Column(db.Text)
    competitors = db.Column(db.Text)  # JSON
    
    # Data quality and tracking
    data_quality = db.Column(db.Enum(DataQuality), default=DataQuality.UNVERIFIED)
    confidence_score = db.Column(db.Float, default=0.0)
    last_verified_at = db.Column(db.DateTime)
    data_sources = db.Column(db.Text)  # JSON array of data sources
    
    # Change tracking
    last_significant_change = db.Column(db.DateTime)
    change_frequency = db.Column(db.String(20))  # 'high', 'medium', 'low'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stock_prices = db.relationship('StockPrice', backref='company', cascade='all, delete-orphan')
    company_changes = db.relationship('CompanyChange', backref='company', cascade='all, delete-orphan')


class CompanyChange(db.Model):
    """Track changes in company data over time"""
    __tablename__ = 'company_changes'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    change_type = db.Column(db.String(50), nullable=False)  # 'funding', 'personnel', 'financial'
    field_changed = db.Column(db.String(100))
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    
    change_summary = db.Column(db.Text)
    significance_score = db.Column(db.Integer, default=1)  # 1-5
    
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    source = db.Column(db.String(100))
    confidence_score = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class StockPrice(db.Model):
    """Enhanced stock price tracking with analysis"""
    __tablename__ = 'stock_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    price = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    
    # Additional market data
    volume = db.Column(db.BigInteger)
    market_cap = db.Column(db.Numeric(15, 2))
    change_percent = db.Column(db.Float)
    
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    source = db.Column(db.String(50), default='alpha_vantage')
    
    __table_args__ = (
        Index('idx_stock_company_date', 'company_id', 'recorded_at'),
    )


# =============================================================================
# DATA QUALITY AND CURATION
# =============================================================================

class DataQualityReport(db.Model):
    """Track data quality across all entities"""
    __tablename__ = 'data_quality_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    
    report_date = db.Column(db.DateTime, default=datetime.utcnow)
    entity_type = db.Column(db.String(50), nullable=False)  # 'tool', 'company', 'version'
    entity_id = db.Column(db.Integer, nullable=False)
    
    # Quality metrics
    completeness_score = db.Column(db.Float, default=0.0)  # 0-100
    accuracy_score = db.Column(db.Float, default=0.0)     # 0-100
    freshness_score = db.Column(db.Float, default=0.0)    # 0-100
    consistency_score = db.Column(db.Float, default=0.0)  # 0-100
    overall_quality = db.Column(db.Enum(DataQuality))
    
    # Issues found
    issues_found = db.Column(db.Text)  # JSON array of data quality issues
    recommendations = db.Column(db.Text)  # JSON array of improvement recommendations
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_quality_entity', 'entity_type', 'entity_id'),
    )


class CurationTask(db.Model):
    """Tasks for manual data curation and review"""
    __tablename__ = 'curation_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    
    task_type = db.Column(db.String(50), nullable=False)  # 'review', 'verify', 'merge', 'update'
    priority = db.Column(db.Integer, default=3)  # 1=urgent, 5=low
    
    # Target entity
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    
    # Task details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    suggested_action = db.Column(db.Text)
    
    # Assignment and status
    assigned_to = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # 'pending', 'in_progress', 'completed', 'skipped'
    
    # Resolution
    completed_at = db.Column(db.DateTime)
    resolution_notes = db.Column(db.Text)
    action_taken = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_curation_status_priority', 'status', 'priority'),
    )


# =============================================================================
# INDEXES AND CONSTRAINTS
# =============================================================================

# Additional indexes for performance
additional_indexes = [
    Index('idx_tool_monitoring', Tool.is_actively_monitored, Tool.next_process_date),
    Index('idx_tool_priority', Tool.priority_level, Tool.last_processed_at),
    Index('idx_changes_unreviewed', ToolChange.is_reviewed, ToolChange.detected_at),
    Index('idx_snapshots_recent', AnalysisSnapshot.tool_id, AnalysisSnapshot.completed_at),
]


def create_all_tables(app):
    """Create all tables with the Flask app context"""
    with app.app_context():
        db.create_all()
        
        # Create additional indexes
        for index in additional_indexes:
            try:
                index.create(db.engine)
            except Exception as e:
                print(f"Index {index.name} already exists or failed to create: {e}")


def get_schema_version():
    """Return the current schema version for migrations"""
    return "2.0.0"


# Model exports for easy importing
__all__ = [
    'db', 'Tool', 'ToolVersion', 'VersionFeature', 'VersionPricing', 'VersionIntegration',
    'ToolChange', 'AnalysisSnapshot', 'CompetitiveAnalysis', 'MarketTrend',
    'Category', 'Company', 'CompanyChange', 'StockPrice',
    'DataQualityReport', 'CurationTask',
    'ProcessingStatus', 'ChangeType', 'DataQuality', 'AnalysisType',
    'create_all_tables', 'get_schema_version'
]