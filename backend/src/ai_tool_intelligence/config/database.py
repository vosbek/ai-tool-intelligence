#!/usr/bin/env python3
"""
Database Configuration Profiles for AI Tool Intelligence Platform

Provides pre-configured database setups for different environments
and use cases with optimized settings for each database type.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool, QueuePool

@dataclass
class DatabaseProfile:
    """Database configuration profile"""
    name: str
    description: str
    url_template: str
    connection_args: Dict[str, Any]
    engine_args: Dict[str, Any]
    features: Dict[str, bool]
    recommended_for: list
    setup_instructions: str

class DatabaseProfileManager:
    """Manages database configuration profiles"""
    
    def __init__(self):
        self.profiles = self._load_profiles()
    
    def _load_profiles(self) -> Dict[str, DatabaseProfile]:
        """Load all database profiles"""
        return {
            'sqlite_dev': self._sqlite_development(),
            'sqlite_prod': self._sqlite_production(),
            'postgresql_local': self._postgresql_local(),
            'postgresql_prod': self._postgresql_production(),
            'mysql_local': self._mysql_local(),
            'mysql_prod': self._mysql_production(),
            'duckdb_analytics': self._duckdb_analytics(),
        }
    
    def _sqlite_development(self) -> DatabaseProfile:
        """SQLite configuration for development"""
        return DatabaseProfile(
            name="sqlite_dev",
            description="SQLite for local development with WAL mode",
            url_template="sqlite:///{db_path}",
            connection_args={
                'check_same_thread': False,
                'timeout': 20,
            },
            engine_args={
                'poolclass': StaticPool,
                'pool_pre_ping': True,
                'echo': False,
                'connect_args': {
                    'check_same_thread': False,
                    'timeout': 20,
                },
            },
            features={
                'json_support': True,
                'full_text_search': True,
                'concurrent_writes': False,
                'advanced_indexing': False,
                'materialized_views': False,
                'partitioning': False,
            },
            recommended_for=[
                "Local development",
                "Testing",
                "Small datasets",
                "Single-user applications"
            ],
            setup_instructions="""
1. No installation required - SQLite is built into Python
2. Configure database path in environment:
   DATABASE_URL=sqlite:///./instance/ai_tools.db
3. Enable WAL mode for better concurrency:
   PRAGMA journal_mode=WAL;
            """
        )
    
    def _sqlite_production(self) -> DatabaseProfile:
        """SQLite configuration for production (small scale)"""
        return DatabaseProfile(
            name="sqlite_prod",
            description="SQLite for production with optimizations",
            url_template="sqlite:///{db_path}",
            connection_args={
                'check_same_thread': False,
                'timeout': 30,
            },
            engine_args={
                'poolclass': StaticPool,
                'pool_pre_ping': True,
                'echo': False,
                'connect_args': {
                    'check_same_thread': False,
                    'timeout': 30,
                },
            },
            features={
                'json_support': True,
                'full_text_search': True,
                'concurrent_writes': False,
                'advanced_indexing': False,
                'materialized_views': False,
                'partitioning': False,
            },
            recommended_for=[
                "Small production deployments",
                "Single-server applications",
                "Read-heavy workloads"
            ],
            setup_instructions="""
1. Use persistent storage for database file
2. Enable WAL mode: PRAGMA journal_mode=WAL;
3. Set appropriate cache size: PRAGMA cache_size=10000;
4. Configure backup strategy for database file
5. Monitor database size and performance
            """
        )
    
    def _postgresql_local(self) -> DatabaseProfile:
        """PostgreSQL configuration for local development"""
        return DatabaseProfile(
            name="postgresql_local",
            description="PostgreSQL for local development",
            url_template="postgresql://{user}:{password}@{host}:{port}/{database}",
            connection_args={},
            engine_args={
                'poolclass': QueuePool,
                'pool_size': 10,
                'max_overflow': 20,
                'pool_pre_ping': True,
                'pool_recycle': 3600,
                'echo': False,
            },
            features={
                'json_support': True,
                'full_text_search': True,
                'concurrent_writes': True,
                'advanced_indexing': True,
                'materialized_views': True,
                'partitioning': True,
            },
            recommended_for=[
                "Local development with multiple users",
                "Development teams",
                "Complex query testing",
                "Production environment testing"
            ],
            setup_instructions="""
1. Install PostgreSQL:
   # Ubuntu/Debian
   sudo apt install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   
   # Windows - Download from postgresql.org

2. Create database and user:
   sudo -u postgres createdb ai_tools_dev
   sudo -u postgres createuser --interactive ai_tools_user

3. Set environment:
   DATABASE_URL=postgresql://ai_tools_user:password@localhost:5432/ai_tools_dev

4. Install Python driver:
   pip install psycopg2-binary
            """
        )
    
    def _postgresql_production(self) -> DatabaseProfile:
        """PostgreSQL configuration for production"""
        return DatabaseProfile(
            name="postgresql_prod",
            description="PostgreSQL for production with performance optimizations",
            url_template="postgresql://{user}:{password}@{host}:{port}/{database}",
            connection_args={
                'connect_timeout': 10,
                'application_name': 'ai-tool-intelligence',
            },
            engine_args={
                'poolclass': QueuePool,
                'pool_size': 20,
                'max_overflow': 40,
                'pool_pre_ping': True,
                'pool_recycle': 1800,
                'echo': False,
            },
            features={
                'json_support': True,
                'full_text_search': True,
                'concurrent_writes': True,
                'advanced_indexing': True,
                'materialized_views': True,
                'partitioning': True,
            },
            recommended_for=[
                "Production applications",
                "High-concurrency workloads",
                "Large datasets",
                "Mission-critical applications"
            ],
            setup_instructions="""
1. Use managed PostgreSQL service (AWS RDS, Google Cloud SQL, etc.)
2. Configure connection pooling (PgBouncer recommended)
3. Set up monitoring (pg_stat_statements, pgAdmin)
4. Configure automated backups
5. Optimize postgresql.conf for your workload:
   - shared_buffers = 25% of RAM
   - effective_cache_size = 75% of RAM
   - max_connections = 200
   - work_mem = 16MB
6. Enable extensions:
   - pg_trgm for fuzzy search
   - pg_stat_statements for monitoring
            """
        )
    
    def _mysql_local(self) -> DatabaseProfile:
        """MySQL configuration for local development"""
        return DatabaseProfile(
            name="mysql_local",
            description="MySQL for local development",
            url_template="mysql+pymysql://{user}:{password}@{host}:{port}/{database}",
            connection_args={
                'charset': 'utf8mb4',
                'connect_timeout': 10,
            },
            engine_args={
                'poolclass': QueuePool,
                'pool_size': 10,
                'max_overflow': 20,
                'pool_pre_ping': True,
                'pool_recycle': 3600,
                'echo': False,
            },
            features={
                'json_support': True,
                'full_text_search': True,
                'concurrent_writes': True,
                'advanced_indexing': True,
                'materialized_views': False,
                'partitioning': True,
            },
            recommended_for=[
                "Applications with existing MySQL infrastructure",
                "Teams familiar with MySQL",
                "Web hosting environments"
            ],
            setup_instructions="""
1. Install MySQL:
   # Ubuntu/Debian
   sudo apt install mysql-server
   
   # macOS
   brew install mysql
   
   # Windows - Download from mysql.com

2. Create database and user:
   CREATE DATABASE ai_tools_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'ai_tools_user'@'localhost' IDENTIFIED BY 'password';
   GRANT ALL PRIVILEGES ON ai_tools_dev.* TO 'ai_tools_user'@'localhost';

3. Set environment:
   DATABASE_URL=mysql+pymysql://ai_tools_user:password@localhost:3306/ai_tools_dev

4. Install Python driver:
   pip install PyMySQL
            """
        )
    
    def _mysql_production(self) -> DatabaseProfile:
        """MySQL configuration for production"""
        return DatabaseProfile(
            name="mysql_prod",
            description="MySQL for production with InnoDB optimizations",
            url_template="mysql+pymysql://{user}:{password}@{host}:{port}/{database}",
            connection_args={
                'charset': 'utf8mb4',
                'connect_timeout': 10,
                'read_timeout': 30,
                'write_timeout': 30,
            },
            engine_args={
                'poolclass': QueuePool,
                'pool_size': 20,
                'max_overflow': 40,
                'pool_pre_ping': True,
                'pool_recycle': 1800,
                'echo': False,
            },
            features={
                'json_support': True,
                'full_text_search': True,
                'concurrent_writes': True,
                'advanced_indexing': True,
                'materialized_views': False,
                'partitioning': True,
            },
            recommended_for=[
                "High-availability applications",
                "Read replicas setup",
                "Large-scale web applications"
            ],
            setup_instructions="""
1. Use managed MySQL service (AWS RDS, Google Cloud SQL)
2. Configure InnoDB settings:
   - innodb_buffer_pool_size = 70-80% of RAM
   - innodb_log_file_size = 256MB
   - innodb_flush_log_at_trx_commit = 1
3. Set up monitoring and slow query log
4. Configure automated backups
5. Consider read replicas for scaling
            """
        )
    
    def _duckdb_analytics(self) -> DatabaseProfile:
        """DuckDB configuration for analytics workloads"""
        return DatabaseProfile(
            name="duckdb_analytics",
            description="DuckDB for analytical workloads and data science",
            url_template="duckdb:///{db_path}",
            connection_args={},
            engine_args={
                'poolclass': StaticPool,
                'pool_pre_ping': True,
                'echo': False,
            },
            features={
                'json_support': True,
                'full_text_search': False,
                'concurrent_writes': False,
                'advanced_indexing': True,
                'materialized_views': False,
                'partitioning': False,
            },
            recommended_for=[
                "Data analysis and reporting",
                "Analytical queries",
                "Data science workflows",
                "OLAP workloads"
            ],
            setup_instructions="""
1. Install DuckDB:
   pip install duckdb duckdb-engine

2. Set environment:
   DATABASE_URL=duckdb:///./instance/ai_tools.duckdb

3. Features:
   - Excellent for analytical queries
   - Fast aggregations and window functions
   - Good JSON support
   - Parquet file integration
   - Columnar storage benefits
            """
        )
    
    def get_profile(self, profile_name: str) -> Optional[DatabaseProfile]:
        """Get database profile by name"""
        return self.profiles.get(profile_name)
    
    def list_profiles(self) -> Dict[str, str]:
        """List all available profiles"""
        return {name: profile.description for name, profile in self.profiles.items()}
    
    def get_recommended_profile(self, use_case: str) -> Optional[DatabaseProfile]:
        """Get recommended profile for use case"""
        use_case_lower = use_case.lower()
        
        for profile in self.profiles.values():
            for recommendation in profile.recommended_for:
                if use_case_lower in recommendation.lower():
                    return profile
        
        return None
    
    def create_engine_from_profile(self, profile_name: str, **url_params) -> Engine:
        """Create SQLAlchemy engine from profile"""
        profile = self.get_profile(profile_name)
        if not profile:
            raise ValueError(f"Unknown profile: {profile_name}")
        
        # Format URL template with parameters
        url = profile.url_template.format(**url_params)
        
        # Create engine with profile settings
        engine = create_engine(url, **profile.engine_args)
        
        # Add database-specific event listeners
        self._setup_engine_events(engine, profile)
        
        return engine
    
    def _setup_engine_events(self, engine: Engine, profile: DatabaseProfile):
        """Setup database-specific engine events"""
        if profile.name.startswith('sqlite'):
            @event.listens_for(engine, 'connect')
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                # Enable WAL mode for better concurrency
                cursor.execute("PRAGMA journal_mode=WAL")
                # Set cache size
                cursor.execute("PRAGMA cache_size=10000")
                # Enable foreign keys
                cursor.execute("PRAGMA foreign_keys=ON")
                # Set synchronous mode
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.close()
        
        elif profile.name.startswith('postgresql'):
            @event.listens_for(engine, 'connect')
            def set_postgresql_settings(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                # Set timezone
                cursor.execute("SET timezone TO 'UTC'")
                # Set statement timeout
                cursor.execute("SET statement_timeout = '300s'")
                cursor.close()
        
        elif profile.name.startswith('mysql'):
            @event.listens_for(engine, 'connect')
            def set_mysql_settings(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                # Set timezone
                cursor.execute("SET time_zone = '+00:00'")
                # Set SQL mode
                cursor.execute("SET sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'")
                cursor.close()


# Global profile manager instance
profile_manager = DatabaseProfileManager()

def get_database_profiles() -> Dict[str, str]:
    """Get all available database profiles"""
    return profile_manager.list_profiles()

def create_engine_from_url_or_profile(database_url: str = None, profile_name: str = None, **params) -> Engine:
    """Create engine from URL or profile name"""
    if database_url:
        # Use provided URL directly
        return create_engine(database_url)
    
    if profile_name:
        # Use profile configuration
        return profile_manager.create_engine_from_profile(profile_name, **params)
    
    # Default to SQLite development
    return profile_manager.create_engine_from_profile('sqlite_dev', db_path='./instance/ai_tools.db')

def get_migration_recommendations(current_db: str, target_use_case: str) -> Dict[str, Any]:
    """Get migration recommendations based on current setup and use case"""
    recommendations = {
        'current_database': current_db,
        'target_use_case': target_use_case,
        'recommended_profiles': [],
        'migration_complexity': 'low',
        'estimated_downtime': 'minimal',
        'data_compatibility': 'high',
        'performance_impact': 'positive',
        'considerations': []
    }
    
    # Analyze current database
    current_type = 'sqlite' if 'sqlite' in current_db.lower() else \
                  'postgresql' if 'postgresql' in current_db.lower() else \
                  'mysql' if 'mysql' in current_db.lower() else 'unknown'
    
    # Use case analysis
    if 'production' in target_use_case.lower():
        if current_type == 'sqlite':
            recommendations['recommended_profiles'] = ['postgresql_prod', 'mysql_prod']
            recommendations['migration_complexity'] = 'medium'
            recommendations['considerations'].extend([
                'Consider PostgreSQL for better JSON support and concurrent writes',
                'MySQL is good if you have existing MySQL infrastructure',
                'Plan for connection pooling in production',
                'Setup automated backups and monitoring'
            ])
        else:
            recommendations['recommended_profiles'] = [f'{current_type}_prod']
            recommendations['migration_complexity'] = 'low'
    
    elif 'analytics' in target_use_case.lower():
        recommendations['recommended_profiles'] = ['duckdb_analytics', 'postgresql_prod']
        recommendations['considerations'].extend([
            'DuckDB excellent for analytical workloads',
            'PostgreSQL good for mixed OLTP/OLAP workloads',
            'Consider data warehouse solutions for large datasets'
        ])
    
    elif 'development' in target_use_case.lower():
        recommendations['recommended_profiles'] = ['sqlite_dev', 'postgresql_local']
        recommendations['migration_complexity'] = 'low'
        recommendations['considerations'].extend([
            'SQLite perfect for single-developer scenarios',
            'PostgreSQL better for team development',
            'Consider Docker for consistent development environments'
        ])
    
    return recommendations


def main():
    """CLI for database profile management"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Database Profile Manager")
    parser.add_argument('--list', action='store_true', help='List all profiles')
    parser.add_argument('--profile', help='Show details for specific profile')
    parser.add_argument('--recommend', help='Get recommendations for use case')
    parser.add_argument('--current-db', help='Current database URL for recommendations')
    
    args = parser.parse_args()
    
    if args.list:
        profiles = get_database_profiles()
        print("Available Database Profiles:")
        print("=" * 40)
        for name, description in profiles.items():
            print(f"{name}: {description}")
    
    elif args.profile:
        profile = profile_manager.get_profile(args.profile)
        if profile:
            print(f"Profile: {profile.name}")
            print("=" * 40)
            print(f"Description: {profile.description}")
            print(f"URL Template: {profile.url_template}")
            print(f"\nFeatures:")
            for feature, supported in profile.features.items():
                status = "✅" if supported else "❌"
                print(f"  {status} {feature}")
            print(f"\nRecommended for:")
            for use_case in profile.recommended_for:
                print(f"  - {use_case}")
            print(f"\nSetup Instructions:")
            print(profile.setup_instructions)
        else:
            print(f"Profile '{args.profile}' not found")
    
    elif args.recommend:
        recommendations = get_migration_recommendations(
            args.current_db or 'sqlite:///ai_tools.db', 
            args.recommend
        )
        print("Migration Recommendations:")
        print("=" * 40)
        print(json.dumps(recommendations, indent=2))


if __name__ == '__main__':
    main()