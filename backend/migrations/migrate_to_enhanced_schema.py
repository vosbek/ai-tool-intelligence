#!/usr/bin/env python3
# migrations/migrate_to_enhanced_schema.py - Migration from basic to enhanced schema

import os
import sys
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.enhanced_schema import *
from app import db as old_db, Tool as OldTool, Company as OldCompany


class SchemaMigrator:
    """Handles migration from old schema to enhanced schema"""
    
    def __init__(self, database_url=None):
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
        
        print(f"Migration initialized for database: {self.database_url}")
    
    def check_current_schema(self):
        """Check what tables currently exist"""
        inspector = inspect(self.engine)
        existing_tables = inspector.get_table_names()
        
        print("Current database tables:")
        for table in sorted(existing_tables):
            print(f"  - {table}")
        
        return existing_tables
    
    def backup_existing_data(self):
        """Create backup of existing data before migration"""
        print("\nCreating backup of existing data...")
        
        session = self.Session()
        backup_data = {}
        
        try:
            # Check if old tables exist
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names()
            
            if 'tools' in existing_tables:
                # Backup tools
                tools = session.execute(text("SELECT * FROM tools")).fetchall()
                backup_data['tools'] = [dict(tool) for tool in tools]
                print(f"  Backed up {len(backup_data['tools'])} tools")
            
            if 'companies' in existing_tables:
                # Backup companies
                companies = session.execute(text("SELECT * FROM companies")).fetchall()
                backup_data['companies'] = [dict(company) for company in companies]
                print(f"  Backed up {len(backup_data['companies'])} companies")
            
            if 'categories' in existing_tables:
                # Backup categories
                categories = session.execute(text("SELECT * FROM categories")).fetchall()
                backup_data['categories'] = [dict(category) for category in categories]
                print(f"  Backed up {len(backup_data['categories'])} categories")
            
            if 'tool_features' in existing_tables:
                # Backup features
                features = session.execute(text("SELECT * FROM tool_features")).fetchall()
                backup_data['tool_features'] = [dict(feature) for feature in features]
                print(f"  Backed up {len(backup_data['tool_features'])} features")
            
            if 'tool_integrations' in existing_tables:
                # Backup integrations
                integrations = session.execute(text("SELECT * FROM tool_integrations")).fetchall()
                backup_data['tool_integrations'] = [dict(integration) for integration in integrations]
                print(f"  Backed up {len(backup_data['tool_integrations'])} integrations")
            
            # Save backup to file
            backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            print(f"  Backup saved to: {backup_file}")
            return backup_data, backup_file
            
        except Exception as e:
            print(f"Error during backup: {e}")
            return {}, None
        finally:
            session.close()
    
    def create_enhanced_schema(self):
        """Create the enhanced schema tables"""
        print("\nCreating enhanced schema tables...")
        
        try:
            # Import the enhanced models
            from models.enhanced_schema import db, create_all_tables
            
            # Create all new tables
            db.metadata.create_all(self.engine)
            
            print("  Enhanced schema tables created successfully")
            
            # List new tables
            inspector = inspect(self.engine)
            new_tables = inspector.get_table_names()
            print(f"  Total tables now: {len(new_tables)}")
            
            return True
            
        except Exception as e:
            print(f"Error creating enhanced schema: {e}")
            return False
    
    def migrate_existing_data(self, backup_data):
        """Migrate data from old schema to enhanced schema"""
        print("\nMigrating existing data to enhanced schema...")
        
        session = self.Session()
        
        try:
            # 1. Migrate Categories
            if 'categories' in backup_data:
                print("  Migrating categories...")
                for old_cat in backup_data['categories']:
                    try:
                        new_cat = Category(
                            id=old_cat['id'],
                            name=old_cat['name'],
                            slug=self._generate_slug(old_cat['name']),
                            parent_id=old_cat.get('parent_id'),
                            description=old_cat.get('description'),
                            created_at=old_cat.get('created_at', datetime.utcnow())
                        )
                        session.merge(new_cat)
                    except Exception as e:
                        print(f"    Error migrating category {old_cat.get('id')}: {e}")
                
                session.commit()
                print(f"    Migrated {len(backup_data['categories'])} categories")
            
            # 2. Migrate Tools
            if 'tools' in backup_data:
                print("  Migrating tools...")
                for old_tool in backup_data['tools']:
                    try:
                        new_tool = Tool(
                            id=old_tool['id'],
                            name=old_tool['name'],
                            slug=self._generate_slug(old_tool['name']),
                            category_id=old_tool.get('category_id'),
                            description=old_tool.get('description'),
                            website_url=old_tool.get('website_url'),
                            github_url=old_tool.get('github_url'),
                            documentation_url=old_tool.get('documentation_url'),
                            changelog_url=old_tool.get('changelog_url'),
                            blog_url=old_tool.get('blog_url'),
                            is_open_source=old_tool.get('is_open_source', False),
                            license_type=old_tool.get('license_type'),
                            primary_language=old_tool.get('primary_language'),
                            processing_status=ProcessingStatus.NEVER_RUN,
                            last_processed_at=old_tool.get('last_processed_at'),
                            next_process_date=old_tool.get('next_process_date'),
                            internal_notes=old_tool.get('internal_notes'),
                            created_at=old_tool.get('created_at', datetime.utcnow()),
                            updated_at=old_tool.get('updated_at', datetime.utcnow())
                        )
                        session.merge(new_tool)
                        
                        # Create initial version if tool has pricing or feature data
                        self._create_initial_version(session, new_tool, old_tool)
                        
                    except Exception as e:
                        print(f"    Error migrating tool {old_tool.get('id')}: {e}")
                
                session.commit()
                print(f"    Migrated {len(backup_data['tools'])} tools")
            
            # 3. Migrate Companies
            if 'companies' in backup_data:
                print("  Migrating companies...")
                for old_company in backup_data['companies']:
                    try:
                        new_company = Company(
                            id=old_company['id'],
                            tool_id=old_company['tool_id'],
                            name=old_company['name'],
                            website=old_company.get('website'),
                            founded_year=old_company.get('founded_year'),
                            headquarters=old_company.get('headquarters'),
                            stock_symbol=old_company.get('stock_symbol'),
                            is_public=old_company.get('is_public', False),
                            estimated_arr=old_company.get('estimated_arr'),
                            last_funding_round=old_company.get('last_funding_round'),
                            total_funding=old_company.get('total_funding'),
                            valuation=old_company.get('valuation'),
                            employee_count=old_company.get('employee_count'),
                            employee_count_source=old_company.get('employee_count_source'),
                            key_executives=old_company.get('key_executives'),
                            strategic_focus=old_company.get('strategic_focus'),
                            business_model=old_company.get('business_model'),
                            target_market=old_company.get('target_market'),
                            competitors=old_company.get('competitors'),
                            data_quality=DataQuality.UNVERIFIED,
                            created_at=datetime.utcnow()
                        )
                        session.merge(new_company)
                    except Exception as e:
                        print(f"    Error migrating company {old_company.get('id')}: {e}")
                
                session.commit()
                print(f"    Migrated {len(backup_data['companies'])} companies")
            
            # 4. Migrate Features to Versions
            if 'tool_features' in backup_data:
                print("  Migrating features to version-specific features...")
                self._migrate_features_to_versions(session, backup_data['tool_features'])
            
            # 5. Migrate Integrations to Versions
            if 'tool_integrations' in backup_data:
                print("  Migrating integrations to version-specific integrations...")
                self._migrate_integrations_to_versions(session, backup_data['tool_integrations'])
            
            print("  Data migration completed successfully")
            return True
            
        except Exception as e:
            print(f"Error during data migration: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def _generate_slug(self, name):
        """Generate URL-friendly slug from name"""
        import re
        slug = name.lower().strip()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        return slug[:200]  # Limit length
    
    def _create_initial_version(self, session, tool, old_tool_data):
        """Create initial version for migrated tools"""
        try:
            version = ToolVersion(
                tool_id=tool.id,
                version_number="1.0.0",  # Default initial version
                version_name="Initial Version",
                detected_at=old_tool_data.get('created_at', datetime.utcnow()),
                is_stable=True,
                data_quality=DataQuality.UNVERIFIED,
                confidence_score=50.0,  # Medium confidence for migrated data
                feature_snapshot=json.dumps({"migrated": True}),
                pricing_snapshot=json.dumps({
                    "pricing_model": old_tool_data.get('pricing_model'),
                    "free_tier_available": old_tool_data.get('free_tier_available'),
                    "starting_price": str(old_tool_data.get('starting_price', 0)),
                    "pricing_currency": old_tool_data.get('pricing_currency', 'USD')
                }),
                created_at=datetime.utcnow()
            )
            session.add(version)
            session.flush()  # Get the ID
            
            # Update tool to reference this version
            tool.current_version = "1.0.0"
            tool.current_version_id = version.id
            
        except Exception as e:
            print(f"    Error creating initial version for tool {tool.id}: {e}")
    
    def _migrate_features_to_versions(self, session, features_data):
        """Migrate old features to version-specific features"""
        try:
            # Group features by tool_id
            features_by_tool = {}
            for feature in features_data:
                tool_id = feature['tool_id']
                if tool_id not in features_by_tool:
                    features_by_tool[tool_id] = []
                features_by_tool[tool_id].append(feature)
            
            # For each tool, find its initial version and add features
            for tool_id, tool_features in features_by_tool.items():
                # Find the initial version for this tool
                initial_version = session.query(ToolVersion).filter_by(
                    tool_id=tool_id
                ).order_by(ToolVersion.detected_at.asc()).first()
                
                if initial_version:
                    for feature in tool_features:
                        version_feature = VersionFeature(
                            version_id=initial_version.id,
                            tool_id=tool_id,
                            feature_category=feature.get('feature_category', 'core'),
                            feature_name=feature['feature_name'],
                            feature_description=feature.get('feature_description'),
                            is_core_feature=feature.get('is_core_feature', True),
                            confidence_score=50.0,  # Medium confidence for migrated data
                            extraction_method='migrated',
                            created_at=datetime.utcnow()
                        )
                        session.add(version_feature)
            
            session.commit()
            print(f"    Migrated {len(features_data)} features to version-specific features")
            
        except Exception as e:
            print(f"    Error migrating features: {e}")
            session.rollback()
    
    def _migrate_integrations_to_versions(self, session, integrations_data):
        """Migrate old integrations to version-specific integrations"""
        try:
            # Group integrations by tool_id
            integrations_by_tool = {}
            for integration in integrations_data:
                tool_id = integration['tool_id']
                if tool_id not in integrations_by_tool:
                    integrations_by_tool[tool_id] = []
                integrations_by_tool[tool_id].append(integration)
            
            # For each tool, find its initial version and add integrations
            for tool_id, tool_integrations in integrations_by_tool.items():
                # Find the initial version for this tool
                initial_version = session.query(ToolVersion).filter_by(
                    tool_id=tool_id
                ).order_by(ToolVersion.detected_at.asc()).first()
                
                if initial_version:
                    for integration in tool_integrations:
                        version_integration = VersionIntegration(
                            version_id=initial_version.id,
                            tool_id=tool_id,
                            integration_category=integration.get('integration_type', 'other'),
                            integration_name=integration['integration_name'],
                            integration_type='unknown',
                            confidence_score=50.0,
                            created_at=datetime.utcnow()
                        )
                        session.add(version_integration)
            
            session.commit()
            print(f"    Migrated {len(integrations_data)} integrations to version-specific integrations")
            
        except Exception as e:
            print(f"    Error migrating integrations: {e}")
            session.rollback()
    
    def verify_migration(self):
        """Verify that migration completed successfully"""
        print("\nVerifying migration...")
        
        session = self.Session()
        
        try:
            # Count records in new tables
            tool_count = session.query(Tool).count()
            version_count = session.query(ToolVersion).count()
            category_count = session.query(Category).count()
            company_count = session.query(Company).count()
            feature_count = session.query(VersionFeature).count()
            integration_count = session.query(VersionIntegration).count()
            
            print(f"  Tools: {tool_count}")
            print(f"  Tool Versions: {version_count}")
            print(f"  Categories: {category_count}")
            print(f"  Companies: {company_count}")
            print(f"  Version Features: {feature_count}")
            print(f"  Version Integrations: {integration_count}")
            
            # Check that each tool has at least one version
            tools_without_versions = session.query(Tool).filter(
                ~Tool.id.in_(session.query(ToolVersion.tool_id))
            ).count()
            
            if tools_without_versions > 0:
                print(f"  WARNING: {tools_without_versions} tools have no versions")
            else:
                print("  ✓ All tools have at least one version")
            
            print("  Migration verification completed")
            return True
            
        except Exception as e:
            print(f"Error during verification: {e}")
            return False
        finally:
            session.close()
    
    def run_full_migration(self):
        """Run the complete migration process"""
        print("="*60)
        print("STARTING ENHANCED SCHEMA MIGRATION")
        print("="*60)
        
        # 1. Check current state
        existing_tables = self.check_current_schema()
        
        # 2. Backup existing data
        backup_data, backup_file = self.backup_existing_data()
        
        # 3. Create enhanced schema
        if not self.create_enhanced_schema():
            print("Failed to create enhanced schema. Aborting migration.")
            return False
        
        # 4. Migrate data
        if backup_data and not self.migrate_existing_data(backup_data):
            print("Failed to migrate existing data. Check backup file:", backup_file)
            return False
        
        # 5. Verify migration
        if not self.verify_migration():
            print("Migration verification failed. Check the results.")
            return False
        
        print("\n" + "="*60)
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"Backup file: {backup_file}")
        print("Enhanced schema is now ready for use.")
        
        return True


def main():
    """Main migration entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate to Enhanced Schema")
    parser.add_argument('--database-url', help='Database URL to migrate')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be migrated without actually doing it')
    parser.add_argument('--backup-only', action='store_true', help='Only create backup, don\'t migrate')
    
    args = parser.parse_args()
    
    migrator = SchemaMigrator(args.database_url)
    
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        migrator.check_current_schema()
        backup_data, _ = migrator.backup_existing_data()
        print(f"Would migrate {len(backup_data)} data sets")
        return
    
    if args.backup_only:
        migrator.backup_existing_data()
        return
    
    # Run full migration
    success = migrator.run_full_migration()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()