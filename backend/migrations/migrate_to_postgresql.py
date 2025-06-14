#!/usr/bin/env python3
"""
PostgreSQL Migration Script for AI Tool Intelligence Platform

This script migrates from SQLite to PostgreSQL with optimizations
for competitive intelligence features.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from database_migration_toolkit import DatabaseMigrationToolkit

class PostgreSQLMigrator:
    """Specialized PostgreSQL migration with enhanced features"""
    
    def __init__(self, source_url: str, target_url: str):
        self.toolkit = DatabaseMigrationToolkit(source_url, target_url)
        self.target_url = target_url
        
    def setup_postgresql_extensions(self):
        """Setup PostgreSQL extensions for enhanced functionality"""
        extensions = [
            'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";',  # UUID generation
            'CREATE EXTENSION IF NOT EXISTS "pg_trgm";',    # Fuzzy text search
            'CREATE EXTENSION IF NOT EXISTS "btree_gin";',  # GIN indexes for btree types
            'CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";',  # Query performance
        ]
        
        print("🔧 Setting up PostgreSQL extensions...")
        
        with self.toolkit.get_target_session() as session:
            for ext in extensions:
                try:
                    session.execute(ext)
                    session.commit()
                    print(f"✅ {ext}")
                except Exception as e:
                    print(f"⚠️  Extension warning: {e}")
                    session.rollback()
    
    def create_enhanced_schema(self):
        """Create PostgreSQL-optimized schema"""
        enhanced_ddl = '''
-- Enhanced PostgreSQL schema for AI Tool Intelligence Platform

-- Tools table with PostgreSQL optimizations
CREATE TABLE IF NOT EXISTS tools (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    
    -- URLs with GIN index support
    website_url TEXT,
    github_url TEXT,
    documentation_url TEXT,
    changelog_url TEXT,
    blog_url TEXT,
    
    -- Version tracking
    current_version VARCHAR(50),
    current_version_id INTEGER,
    
    -- Enhanced metadata with JSONB
    description TEXT,
    is_open_source BOOLEAN DEFAULT FALSE,
    license_type VARCHAR(100),
    primary_language VARCHAR(50),
    
    -- Competitive tracking
    is_actively_monitored BOOLEAN DEFAULT TRUE,
    monitoring_frequency_days INTEGER DEFAULT 7,
    priority_level INTEGER DEFAULT 3,
    
    -- Processing status with enum
    processing_status processing_status_enum DEFAULT 'never_run',
    last_processed_at TIMESTAMP,
    next_process_date TIMESTAMP,
    last_change_detected_at TIMESTAMP,
    
    -- Data quality tracking
    overall_data_quality data_quality_enum DEFAULT 'unverified',
    confidence_score REAL DEFAULT 0.0,
    data_completeness REAL DEFAULT 0.0,
    
    -- Manual curation
    internal_notes TEXT,
    curator_notes TEXT,
    is_curated BOOLEAN DEFAULT FALSE,
    curated_at TIMESTAMP,
    curated_by VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Custom enum types
DO $$ BEGIN
    CREATE TYPE processing_status_enum AS ENUM (
        'never_run', 'queued', 'running', 'completed', 'failed', 'needs_review'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE data_quality_enum AS ENUM (
        'high', 'medium', 'low', 'unverified'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE change_type_enum AS ENUM (
        'added', 'removed', 'modified', 'version_bump', 'price_change', 'feature_change'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Tool versions with JSONB snapshots
CREATE TABLE IF NOT EXISTS tool_versions (
    id SERIAL PRIMARY KEY,
    tool_id INTEGER NOT NULL REFERENCES tools(id) ON DELETE CASCADE,
    
    version_number VARCHAR(50) NOT NULL,
    version_name VARCHAR(200),
    release_date TIMESTAMP,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    is_stable BOOLEAN DEFAULT TRUE,
    is_beta BOOLEAN DEFAULT FALSE,
    is_alpha BOOLEAN DEFAULT FALSE,
    is_deprecated BOOLEAN DEFAULT FALSE,
    
    release_notes_url TEXT,
    download_url TEXT,
    announcement_url TEXT,
    
    data_quality data_quality_enum DEFAULT 'unverified',
    confidence_score REAL DEFAULT 0.0,
    
    -- JSONB snapshots for efficient querying
    feature_snapshot JSONB,
    pricing_snapshot JSONB,
    integration_snapshot JSONB,
    github_metrics_snapshot JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(tool_id, version_number)
);

-- Version-specific features
CREATE TABLE IF NOT EXISTS version_features (
    id SERIAL PRIMARY KEY,
    version_id INTEGER NOT NULL REFERENCES tool_versions(id) ON DELETE CASCADE,
    tool_id INTEGER NOT NULL REFERENCES tools(id) ON DELETE CASCADE,
    
    feature_category VARCHAR(100) NOT NULL,
    feature_name VARCHAR(200) NOT NULL,
    feature_description TEXT,
    
    is_core_feature BOOLEAN DEFAULT TRUE,
    is_ai_feature BOOLEAN DEFAULT FALSE,
    is_enterprise_feature BOOLEAN DEFAULT FALSE,
    is_new_in_version BOOLEAN DEFAULT FALSE,
    
    confidence_score REAL DEFAULT 0.0,
    source_url TEXT,
    extraction_method VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tool changes tracking
CREATE TABLE IF NOT EXISTS tool_changes (
    id SERIAL PRIMARY KEY,
    tool_id INTEGER NOT NULL REFERENCES tools(id) ON DELETE CASCADE,
    
    change_type change_type_enum NOT NULL,
    change_category VARCHAR(50),
    
    from_version VARCHAR(50),
    to_version VARCHAR(50),
    
    field_name VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    
    change_summary TEXT,
    impact_score INTEGER DEFAULT 1,
    
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    detection_method VARCHAR(50),
    confidence_score REAL DEFAULT 0.0,
    
    is_reviewed BOOLEAN DEFAULT FALSE,
    reviewed_at TIMESTAMP,
    reviewed_by VARCHAR(100),
    review_notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced categories with hierarchy support
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    parent_id INTEGER REFERENCES categories(id),
    description TEXT,
    
    -- Monitoring settings
    is_monitored BOOLEAN DEFAULT TRUE,
    monitoring_priority INTEGER DEFAULT 3,
    
    -- Category metrics
    tool_count INTEGER DEFAULT 0,
    active_tool_count INTEGER DEFAULT 0,
    last_trend_analysis TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced companies with financial tracking
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    tool_id INTEGER NOT NULL REFERENCES tools(id) ON DELETE CASCADE,
    
    name VARCHAR(200) NOT NULL,
    website TEXT,
    founded_year INTEGER,
    headquarters VARCHAR(200),
    
    stock_symbol VARCHAR(10),
    is_public BOOLEAN DEFAULT FALSE,
    estimated_arr DECIMAL(15, 2),
    last_funding_round VARCHAR(50),
    total_funding DECIMAL(15, 2),
    valuation DECIMAL(15, 2),
    
    employee_count INTEGER,
    employee_count_source VARCHAR(100),
    employee_count_date TIMESTAMP,
    key_executives JSONB,
    
    strategic_focus TEXT,
    business_model VARCHAR(100),
    target_market TEXT,
    competitors JSONB,
    
    data_quality data_quality_enum DEFAULT 'unverified',
    confidence_score REAL DEFAULT 0.0,
    last_verified_at TIMESTAMP,
    data_sources JSONB,
    
    last_significant_change TIMESTAMP,
    change_frequency VARCHAR(20),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tools_monitoring 
ON tools(is_actively_monitored, next_process_date) 
WHERE is_actively_monitored = true;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tools_category_priority 
ON tools(category_id, priority_level);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tools_processing_status 
ON tools(processing_status, last_processed_at);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tool_versions_detected 
ON tool_versions(tool_id, detected_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_version_features_category 
ON version_features(feature_category, tool_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tool_changes_detected 
ON tool_changes(tool_id, detected_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_changes_unreviewed 
ON tool_changes(is_reviewed, detected_at) 
WHERE is_reviewed = false;

-- JSONB indexes for efficient querying
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_feature_snapshot_gin 
ON tool_versions USING GIN(feature_snapshot) 
WHERE feature_snapshot IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pricing_snapshot_gin 
ON tool_versions USING GIN(pricing_snapshot) 
WHERE pricing_snapshot IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_companies_executives_gin 
ON companies USING GIN(key_executives) 
WHERE key_executives IS NOT NULL;

-- Full-text search indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tools_search 
ON tools USING GIN(to_tsvector('english', name || ' ' || COALESCE(description, '')));

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_features_search 
ON version_features USING GIN(to_tsvector('english', feature_name || ' ' || COALESCE(feature_description, '')));

-- Partial indexes for active monitoring
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tools_active_monitoring 
ON tools(next_process_date) 
WHERE is_actively_monitored = true AND processing_status != 'running';

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tools_updated_at 
BEFORE UPDATE ON tools 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_categories_updated_at 
BEFORE UPDATE ON categories 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_companies_updated_at 
BEFORE UPDATE ON companies 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
'''
        
        print("🏗️  Creating enhanced PostgreSQL schema...")
        
        with self.toolkit.get_target_session() as session:
            try:
                session.execute(enhanced_ddl)
                session.commit()
                print("✅ Enhanced schema created successfully")
            except Exception as e:
                print(f"❌ Schema creation failed: {e}")
                session.rollback()
                raise
    
    def create_materialized_views(self):
        """Create materialized views for analytics"""
        views_ddl = '''
-- Materialized views for performance

-- Tool analytics summary
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_tool_analytics AS
SELECT 
    t.id,
    t.name,
    t.category_id,
    c.name as category_name,
    t.processing_status,
    t.overall_data_quality,
    t.confidence_score,
    COUNT(tv.id) as version_count,
    MAX(tv.detected_at) as latest_version_date,
    COUNT(tc.id) as change_count,
    MAX(tc.detected_at) as latest_change_date,
    COUNT(vf.id) as feature_count,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - t.last_processed_at))/86400 as days_since_processed
FROM tools t
LEFT JOIN categories c ON t.category_id = c.id
LEFT JOIN tool_versions tv ON t.id = tv.tool_id
LEFT JOIN tool_changes tc ON t.id = tc.tool_id
LEFT JOIN version_features vf ON t.id = vf.tool_id
GROUP BY t.id, t.name, t.category_id, c.name, t.processing_status, 
         t.overall_data_quality, t.confidence_score, t.last_processed_at;

-- Category analytics
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_category_analytics AS
SELECT 
    c.id,
    c.name,
    c.parent_id,
    COUNT(t.id) as tool_count,
    COUNT(CASE WHEN t.is_actively_monitored THEN 1 END) as monitored_tool_count,
    AVG(t.confidence_score) as avg_confidence_score,
    COUNT(CASE WHEN t.processing_status = 'completed' THEN 1 END) as completed_tools,
    COUNT(CASE WHEN t.processing_status = 'failed' THEN 1 END) as failed_tools,
    MAX(t.last_processed_at) as last_category_update
FROM categories c
LEFT JOIN tools t ON c.id = t.category_id
GROUP BY c.id, c.name, c.parent_id;

-- Recent changes summary
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_recent_changes AS
SELECT 
    tc.tool_id,
    t.name as tool_name,
    tc.change_type,
    tc.change_category,
    tc.detected_at,
    tc.impact_score,
    tc.is_reviewed,
    ROW_NUMBER() OVER (PARTITION BY tc.tool_id ORDER BY tc.detected_at DESC) as change_rank
FROM tool_changes tc
JOIN tools t ON tc.tool_id = t.id
WHERE tc.detected_at > CURRENT_TIMESTAMP - INTERVAL '30 days';

-- Create indexes on materialized views
CREATE INDEX IF NOT EXISTS idx_mv_tool_analytics_category 
ON mv_tool_analytics(category_id);

CREATE INDEX IF NOT EXISTS idx_mv_recent_changes_detected 
ON mv_recent_changes(detected_at DESC);

-- Refresh functions for materialized views
CREATE OR REPLACE FUNCTION refresh_analytics_views() 
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_tool_analytics;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_category_analytics;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_recent_changes;
END;
$$ LANGUAGE plpgsql;
'''
        
        print("📊 Creating materialized views...")
        
        with self.toolkit.get_target_session() as session:
            try:
                session.execute(views_ddl)
                session.commit()
                print("✅ Materialized views created successfully")
            except Exception as e:
                print(f"⚠️  Materialized views warning: {e}")
                session.rollback()
    
    def setup_maintenance_procedures(self):
        """Setup PostgreSQL maintenance procedures"""
        maintenance_ddl = '''
-- Maintenance procedures

-- Cleanup old change records
CREATE OR REPLACE FUNCTION cleanup_old_changes(retention_days INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM tool_changes 
    WHERE detected_at < CURRENT_TIMESTAMP - INTERVAL '1 day' * retention_days
    AND is_reviewed = true;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Update tool statistics
CREATE OR REPLACE FUNCTION update_tool_statistics()
RETURNS void AS $$
BEGIN
    -- Update category tool counts
    UPDATE categories SET 
        tool_count = (
            SELECT COUNT(*) FROM tools WHERE category_id = categories.id
        ),
        active_tool_count = (
            SELECT COUNT(*) FROM tools 
            WHERE category_id = categories.id AND is_actively_monitored = true
        );
    
    -- Update tool confidence scores based on recent data
    UPDATE tools SET 
        confidence_score = GREATEST(
            confidence_score * 0.95,  -- Decay factor
            (SELECT AVG(confidence_score) FROM version_features WHERE tool_id = tools.id)
        )
    WHERE last_processed_at < CURRENT_TIMESTAMP - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Schedule maintenance (requires pg_cron extension)
-- SELECT cron.schedule('cleanup-changes', '0 2 * * *', 'SELECT cleanup_old_changes();');
-- SELECT cron.schedule('update-stats', '0 3 * * *', 'SELECT update_tool_statistics();');
-- SELECT cron.schedule('refresh-views', '0 4 * * *', 'SELECT refresh_analytics_views();');
'''
        
        print("🔧 Setting up maintenance procedures...")
        
        with self.toolkit.get_target_session() as session:
            try:
                session.execute(maintenance_ddl)
                session.commit()
                print("✅ Maintenance procedures created successfully")
            except Exception as e:
                print(f"⚠️  Maintenance procedures warning: {e}")
                session.rollback()
    
    def migrate_with_enhancements(self):
        """Execute full migration with PostgreSQL enhancements"""
        print("🚀 Starting PostgreSQL migration with enhancements...")
        
        # Step 1: Setup extensions
        self.setup_postgresql_extensions()
        
        # Step 2: Create enhanced schema
        self.create_enhanced_schema()
        
        # Step 3: Migrate data
        print("\n📦 Migrating data...")
        migration_report = self.toolkit.migrate_data(batch_size=1000)
        
        print(f"Migration completed in {migration_report['duration']:.2f} seconds")
        print(f"Total rows migrated: {migration_report['total_rows']}")
        
        # Step 4: Create materialized views
        self.create_materialized_views()
        
        # Step 5: Setup maintenance
        self.setup_maintenance_procedures()
        
        # Step 6: Verify migration
        print("\n✅ Verifying migration...")
        verification = self.toolkit.verify_migration()
        
        print("\nVerification Results:")
        for table, counts in verification['table_counts'].items():
            status = "✅" if counts['match'] else "❌"
            print(f"  {status} {table}: {counts['source']} → {counts['target']}")
        
        if verification['integrity_issues']:
            print("\n⚠️  Integrity Issues:")
            for issue in verification['integrity_issues']:
                print(f"  - {issue}")
        else:
            print("\n🎉 PostgreSQL migration completed successfully!")
        
        # Performance recommendations
        print("\n📈 Performance Recommendations:")
        print("1. Run ANALYZE after initial data load")
        print("2. Consider increasing shared_buffers for better performance")
        print("3. Enable pg_stat_statements for query monitoring")
        print("4. Setup automated VACUUM and ANALYZE")
        print("5. Monitor materialized view refresh times")
        
        return migration_report


def main():
    """Main PostgreSQL migration entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PostgreSQL Migration for AI Tool Intelligence")
    parser.add_argument('--source', default='sqlite:///instance/ai_tools.db', 
                       help='Source database URL')
    parser.add_argument('--target', required=True, 
                       help='Target PostgreSQL URL (e.g., postgresql://user:pass@localhost/dbname)')
    parser.add_argument('--batch-size', type=int, default=1000, 
                       help='Batch size for data migration')
    
    args = parser.parse_args()
    
    print("🐘 PostgreSQL Migration for AI Tool Intelligence Platform")
    print("=" * 60)
    
    migrator = PostgreSQLMigrator(args.source, args.target)
    
    try:
        migrator.migrate_with_enhancements()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()