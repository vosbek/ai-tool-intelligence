#!/usr/bin/env python3
"""
Database Migration Toolkit for AI Tool Intelligence Platform

Provides database-agnostic migration utilities for moving between
SQLite, PostgreSQL, MySQL, and other supported databases.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy import create_engine, text, inspect, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from contextlib import contextmanager
import pandas as pd

class DatabaseMigrationToolkit:
    """Comprehensive database migration toolkit"""
    
    def __init__(self, source_url: str, target_url: str):
        self.source_url = source_url
        self.target_url = target_url
        self.source_engine = create_engine(source_url)
        self.target_engine = create_engine(target_url)
        self.logger = logging.getLogger(__name__)
        
        # Database type detection
        self.source_type = self._detect_db_type(source_url)
        self.target_type = self._detect_db_type(target_url)
        
        print(f"Migration: {self.source_type} → {self.target_type}")
    
    def _detect_db_type(self, url: str) -> str:
        """Detect database type from URL"""
        if url.startswith('sqlite'):
            return 'sqlite'
        elif url.startswith('postgresql'):
            return 'postgresql'
        elif url.startswith('mysql'):
            return 'mysql'
        elif url.startswith('duckdb'):
            return 'duckdb'
        else:
            return 'unknown'
    
    @contextmanager
    def get_source_session(self):
        """Get source database session"""
        Session = sessionmaker(bind=self.source_engine)
        session = Session()
        try:
            yield session
        finally:
            session.close()
    
    @contextmanager
    def get_target_session(self):
        """Get target database session"""
        Session = sessionmaker(bind=self.target_engine)
        session = Session()
        try:
            yield session
        finally:
            session.close()
    
    def analyze_source_schema(self) -> Dict[str, Any]:
        """Analyze source database schema"""
        inspector = inspect(self.source_engine)
        
        schema_info = {
            'tables': {},
            'indexes': {},
            'foreign_keys': {},
            'data_counts': {}
        }
        
        # Get table information
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            schema_info['tables'][table_name] = {
                'columns': columns,
                'primary_keys': inspector.get_pk_constraint(table_name),
                'foreign_keys': inspector.get_foreign_keys(table_name),
                'indexes': inspector.get_indexes(table_name)
            }
            
            # Get row count
            with self.get_source_session() as session:
                count = session.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                schema_info['data_counts'][table_name] = count
        
        return schema_info
    
    def generate_target_schema(self, source_schema: Dict[str, Any]) -> str:
        """Generate target database schema with database-specific optimizations"""
        ddl_statements = []
        
        # Table creation order (respecting foreign keys)
        table_order = self._determine_table_order(source_schema)
        
        for table_name in table_order:
            table_info = source_schema['tables'][table_name]
            ddl = self._generate_table_ddl(table_name, table_info)
            ddl_statements.append(ddl)
        
        return '\n\n'.join(ddl_statements)
    
    def _determine_table_order(self, schema: Dict[str, Any]) -> List[str]:
        """Determine table creation order based on dependencies"""
        tables = list(schema['tables'].keys())
        ordered = []
        remaining = tables.copy()
        
        # Simple dependency resolution
        while remaining:
            for table in remaining[:]:
                fks = schema['tables'][table]['foreign_keys']
                dependencies = [fk['referred_table'] for fk in fks]
                
                if all(dep in ordered or dep == table for dep in dependencies):
                    ordered.append(table)
                    remaining.remove(table)
                    break
            else:
                # If we can't resolve dependencies, add remaining tables
                ordered.extend(remaining)
                break
        
        return ordered
    
    def _generate_table_ddl(self, table_name: str, table_info: Dict[str, Any]) -> str:
        """Generate database-specific DDL for table"""
        columns = table_info['columns']
        pk = table_info['primary_keys']
        
        column_defs = []
        for col in columns:
            col_def = self._convert_column_type(col, self.target_type)
            column_defs.append(col_def)
        
        # Primary key
        if pk and pk['constrained_columns']:
            pk_cols = ', '.join(pk['constrained_columns'])
            column_defs.append(f"PRIMARY KEY ({pk_cols})")
        
        ddl = f"CREATE TABLE {table_name} (\n"
        ddl += ',\n'.join(f"  {col_def}" for col_def in column_defs)
        ddl += "\n);"
        
        # Add database-specific optimizations
        if self.target_type == 'postgresql':
            # Add JSONB indexes for PostgreSQL
            if any('json' in col['type'].lower() for col in columns):
                ddl += f"\n-- Add JSONB indexes for {table_name}"
        
        return ddl
    
    def _convert_column_type(self, column: Dict[str, Any], target_db: str) -> str:
        """Convert column type between databases"""
        col_name = column['name']
        col_type = str(column['type']).upper()
        nullable = "" if column['nullable'] else " NOT NULL"
        
        # Type mapping based on target database
        type_mappings = {
            'postgresql': {
                'INTEGER': 'INTEGER',
                'VARCHAR': 'VARCHAR',
                'TEXT': 'TEXT',
                'DATETIME': 'TIMESTAMP',
                'BOOLEAN': 'BOOLEAN',
                'NUMERIC': 'DECIMAL',
                'JSON': 'JSONB',  # Use JSONB for better performance
                'FLOAT': 'REAL'
            },
            'mysql': {
                'INTEGER': 'INT',
                'VARCHAR': 'VARCHAR',
                'TEXT': 'TEXT',
                'DATETIME': 'DATETIME',
                'BOOLEAN': 'BOOLEAN',
                'NUMERIC': 'DECIMAL',
                'JSON': 'JSON',
                'FLOAT': 'FLOAT'
            },
            'sqlite': {
                'INTEGER': 'INTEGER',
                'VARCHAR': 'TEXT',
                'TEXT': 'TEXT',
                'DATETIME': 'TEXT',
                'BOOLEAN': 'INTEGER',
                'NUMERIC': 'REAL',
                'JSON': 'TEXT',
                'FLOAT': 'REAL'
            }
        }
        
        # Extract base type
        base_type = col_type.split('(')[0]
        type_map = type_mappings.get(target_db, {})
        converted_type = type_map.get(base_type, col_type)
        
        # Handle size specifiers
        if '(' in col_type and converted_type in ['VARCHAR', 'DECIMAL']:
            size_spec = col_type[col_type.find('('):col_type.find(')')+1]
            converted_type += size_spec
        
        return f"{col_name} {converted_type}{nullable}"
    
    def migrate_data(self, batch_size: int = 1000) -> Dict[str, Any]:
        """Migrate data from source to target database"""
        migration_report = {
            'start_time': datetime.now(),
            'tables_migrated': [],
            'total_rows': 0,
            'errors': []
        }
        
        # Get source schema
        source_schema = self.analyze_source_schema()
        table_order = self._determine_table_order(source_schema)
        
        for table_name in table_order:
            try:
                rows_migrated = self._migrate_table_data(table_name, batch_size)
                migration_report['tables_migrated'].append({
                    'table': table_name,
                    'rows': rows_migrated
                })
                migration_report['total_rows'] += rows_migrated
                
                print(f"✅ Migrated {table_name}: {rows_migrated} rows")
                
            except Exception as e:
                error_msg = f"Failed to migrate {table_name}: {str(e)}"
                migration_report['errors'].append(error_msg)
                print(f"❌ {error_msg}")
                continue
        
        migration_report['end_time'] = datetime.now()
        migration_report['duration'] = (
            migration_report['end_time'] - migration_report['start_time']
        ).total_seconds()
        
        return migration_report
    
    def _migrate_table_data(self, table_name: str, batch_size: int) -> int:
        """Migrate data for a specific table"""
        # Read data from source
        with self.get_source_session() as source_session:
            # Get column names
            result = source_session.execute(text(f"SELECT * FROM {table_name} LIMIT 1"))
            columns = list(result.keys()) if result.rowcount > 0 else []
            
            if not columns:
                return 0
            
            # Read all data
            df = pd.read_sql_table(table_name, self.source_engine)
            
            if df.empty:
                return 0
            
            # Data transformations for target database
            df = self._transform_data_for_target(df, table_name)
        
        # Write data to target in batches
        total_rows = len(df)
        rows_written = 0
        
        for start_idx in range(0, total_rows, batch_size):
            end_idx = min(start_idx + batch_size, total_rows)
            batch_df = df.iloc[start_idx:end_idx]
            
            # Write batch to target
            batch_df.to_sql(
                table_name, 
                self.target_engine, 
                if_exists='append', 
                index=False,
                method=self._get_insert_method()
            )
            
            rows_written += len(batch_df)
            
            if rows_written % 5000 == 0:
                print(f"  Progress: {rows_written}/{total_rows} rows")
        
        return rows_written
    
    def _transform_data_for_target(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Transform data for target database compatibility"""
        # Handle JSON columns
        if self.target_type == 'postgresql':
            # Convert JSON text to proper JSON for PostgreSQL
            json_columns = ['pricing_details', 'key_executives', 'competitors', 
                          'feature_snapshot', 'pricing_snapshot']
            
            for col in json_columns:
                if col in df.columns:
                    df[col] = df[col].apply(self._ensure_valid_json)
        
        # Handle datetime columns
        datetime_columns = df.select_dtypes(include=['datetime64']).columns
        for col in datetime_columns:
            if self.target_type == 'mysql':
                # MySQL has stricter datetime validation
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Handle boolean columns for SQLite target
        if self.target_type == 'sqlite':
            bool_columns = df.select_dtypes(include=['bool']).columns
            for col in bool_columns:
                df[col] = df[col].astype(int)
        
        return df
    
    def _ensure_valid_json(self, value):
        """Ensure value is valid JSON"""
        if pd.isna(value) or value is None:
            return None
        
        if isinstance(value, str):
            try:
                # Test if it's valid JSON
                json.loads(value)
                return value
            except json.JSONDecodeError:
                # If not valid JSON, wrap in quotes
                return json.dumps(value)
        
        return json.dumps(value)
    
    def _get_insert_method(self):
        """Get database-specific insert method for pandas"""
        if self.target_type == 'postgresql':
            return 'multi'  # Use executemany for PostgreSQL
        elif self.target_type == 'mysql':
            return 'multi'
        else:
            return None  # Use default for SQLite
    
    def create_indexes(self, schema_info: Dict[str, Any]):
        """Create indexes on target database"""
        print("Creating indexes...")
        
        with self.get_target_session() as session:
            # Create custom indexes based on usage patterns
            index_ddl = []
            
            if self.target_type == 'postgresql':
                # PostgreSQL-specific indexes
                index_ddl.extend([
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tools_processing_status ON tools(processing_status);",
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tools_category_id ON tools(category_id);",
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tools_is_monitored ON tools(is_actively_monitored) WHERE is_actively_monitored = true;",
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pricing_details_gin ON tools USING GIN(pricing_details) WHERE pricing_details IS NOT NULL;",
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tool_changes_detected_at ON tool_changes(detected_at DESC);",
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_version_features_category ON version_features(feature_category);",
                ])
            
            elif self.target_type == 'mysql':
                # MySQL-specific indexes
                index_ddl.extend([
                    "CREATE INDEX idx_tools_processing_status ON tools(processing_status);",
                    "CREATE INDEX idx_tools_category_id ON tools(category_id);",
                    "CREATE INDEX idx_tools_website_url ON tools(website_url(255));",
                    "CREATE INDEX idx_tool_changes_detected_at ON tool_changes(detected_at DESC);",
                ])
            
            # Execute index creation
            for ddl in index_ddl:
                try:
                    session.execute(text(ddl))
                    session.commit()
                    print(f"✅ Created index: {ddl.split()[2]}")
                except Exception as e:
                    print(f"⚠️  Index creation warning: {e}")
                    session.rollback()
    
    def verify_migration(self) -> Dict[str, Any]:
        """Verify migration completeness and data integrity"""
        verification_report = {
            'table_counts': {},
            'sample_data_check': {},
            'integrity_issues': []
        }
        
        # Compare row counts
        source_schema = self.analyze_source_schema()
        
        with self.get_target_session() as target_session:
            for table_name in source_schema['tables'].keys():
                source_count = source_schema['data_counts'][table_name]
                
                try:
                    target_count = target_session.execute(
                        text(f"SELECT COUNT(*) FROM {table_name}")
                    ).scalar()
                    
                    verification_report['table_counts'][table_name] = {
                        'source': source_count,
                        'target': target_count,
                        'match': source_count == target_count
                    }
                    
                    if source_count != target_count:
                        verification_report['integrity_issues'].append(
                            f"Row count mismatch in {table_name}: {source_count} vs {target_count}"
                        )
                
                except Exception as e:
                    verification_report['integrity_issues'].append(
                        f"Could not verify {table_name}: {e}"
                    )
        
        return verification_report
    
    def generate_migration_script(self, output_file: str = "migration_script.py"):
        """Generate a complete migration script"""
        script_content = f'''#!/usr/bin/env python3
"""
Generated migration script for AI Tool Intelligence Platform
From: {self.source_type} to {self.target_type}
Generated: {datetime.now().isoformat()}
"""

import os
import sys
from database_migration_toolkit import DatabaseMigrationToolkit

def main():
    """Execute database migration"""
    source_url = "{self.source_url}"
    target_url = "{self.target_url}"
    
    print("🔄 Starting database migration...")
    print(f"Source: {{source_url}}")
    print(f"Target: {{target_url}}")
    
    # Create migration toolkit
    migrator = DatabaseMigrationToolkit(source_url, target_url)
    
    # Step 1: Analyze source
    print("\\n📊 Analyzing source database...")
    source_schema = migrator.analyze_source_schema()
    print(f"Found {{len(source_schema['tables'])}} tables")
    
    # Step 2: Generate target schema
    print("\\n🏗️  Generating target schema...")
    schema_ddl = migrator.generate_target_schema(source_schema)
    
    with open("target_schema.sql", "w") as f:
        f.write(schema_ddl)
    print("Schema DDL saved to target_schema.sql")
    
    # Step 3: Create target tables (manual step)
    print("\\n⚠️  Please execute target_schema.sql on your target database before continuing")
    input("Press Enter when target schema is ready...")
    
    # Step 4: Migrate data
    print("\\n📦 Migrating data...")
    migration_report = migrator.migrate_data(batch_size=1000)
    
    print(f"Migration completed in {{migration_report['duration']:.2f}} seconds")
    print(f"Total rows migrated: {{migration_report['total_rows']}}")
    
    if migration_report['errors']:
        print("\\n❌ Errors encountered:")
        for error in migration_report['errors']:
            print(f"  - {{error}}")
    
    # Step 5: Create indexes
    print("\\n🗂️  Creating indexes...")
    migrator.create_indexes(source_schema)
    
    # Step 6: Verify migration
    print("\\n✅ Verifying migration...")
    verification = migrator.verify_migration()
    
    print("\\nVerification Results:")
    for table, counts in verification['table_counts'].items():
        status = "✅" if counts['match'] else "❌"
        print(f"  {{status}} {{table}}: {{counts['source']}} → {{counts['target']}}")
    
    if verification['integrity_issues']:
        print("\\n⚠️  Integrity Issues:")
        for issue in verification['integrity_issues']:
            print(f"  - {{issue}}")
    else:
        print("\\n🎉 Migration completed successfully!")

if __name__ == '__main__':
    main()
'''
        
        with open(output_file, 'w') as f:
            f.write(script_content)
        
        print(f"Migration script generated: {output_file}")
        return output_file


def main():
    """CLI interface for database migration toolkit"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Migration Toolkit")
    parser.add_argument('--source', required=True, help='Source database URL')
    parser.add_argument('--target', required=True, help='Target database URL')
    parser.add_argument('--action', choices=['analyze', 'migrate', 'verify', 'script'], 
                       default='migrate', help='Action to perform')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for data migration')
    
    args = parser.parse_args()
    
    migrator = DatabaseMigrationToolkit(args.source, args.target)
    
    if args.action == 'analyze':
        schema = migrator.analyze_source_schema()
        print(json.dumps(schema, indent=2, default=str))
    
    elif args.action == 'migrate':
        # Full migration
        schema = migrator.analyze_source_schema()
        ddl = migrator.generate_target_schema(schema)
        
        print("Generated DDL:")
        print(ddl)
        
        if input("Proceed with migration? (y/N): ").lower() == 'y':
            report = migrator.migrate_data(args.batch_size)
            print("Migration report:", json.dumps(report, indent=2, default=str))
    
    elif args.action == 'verify':
        report = migrator.verify_migration()
        print(json.dumps(report, indent=2))
    
    elif args.action == 'script':
        script_file = migrator.generate_migration_script()
        print(f"Generated migration script: {script_file}")


if __name__ == '__main__':
    main()