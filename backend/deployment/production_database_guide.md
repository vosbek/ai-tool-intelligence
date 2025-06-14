# Production Database Deployment Guide

## Overview

This guide covers the transition from local SQLite development to production-ready database systems for the AI Tool Intelligence Platform.

## Database Selection Matrix

| Database | Best For | Pros | Cons | Complexity |
|----------|----------|------|------|------------|
| **PostgreSQL** | General production use | Excellent JSON support, ACID compliance, extensions | Setup complexity | Medium |
| **MySQL** | Web applications | Wide hosting support, familiar | Limited JSON features | Low |
| **SQLite** | Small deployments | Zero configuration, reliable | Single writer, no replication | Very Low |
| **DuckDB** | Analytics workloads | Fast analytics, good for reporting | Limited concurrent writes | Low |

## Recommended Production Architectures

### 1. Small to Medium Scale (< 10,000 tools)

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Frontend  │    │   Backend    │    │ PostgreSQL  │
│   (React)   │◄──►│   (Flask)    │◄──►│  Database   │
│             │    │              │    │             │
└─────────────┘    └──────────────┘    └─────────────┘
                           │
                           ▼
                   ┌──────────────┐
                   │   Redis      │
                   │   (Cache)    │
                   └──────────────┘
```

**Configuration:**
- Single PostgreSQL instance
- Redis for session storage and caching
- Connection pooling with PgBouncer
- Regular automated backups

### 2. High Availability Setup (> 10,000 tools)

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Frontend  │    │   Backend    │    │ PostgreSQL  │
│ (Load Bal.) │◄──►│ (Multiple)   │◄──►│   Primary   │
│             │    │              │    │             │
└─────────────┘    └──────────────┘    └─────────────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │ PostgreSQL  │
                                       │  Replica    │
                                       │ (Read-only) │
                                       └─────────────┘
```

**Configuration:**
- Primary/replica PostgreSQL setup
- Read replicas for analytics queries
- Connection pooling across multiple instances
- Automated failover

### 3. Microservices Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Frontend  │    │   API        │    │ PostgreSQL  │
│             │◄──►│   Gateway    │◄──►│  (Tools)    │
└─────────────┘    └──────────────┘    └─────────────┘
                           │
                           ├─────────────────────────┐
                           ▼                         ▼
                   ┌──────────────┐         ┌─────────────┐
                   │ Analytics    │         │ PostgreSQL  │
                   │ Service      │◄───────►│ (Analytics) │
                   └──────────────┘         └─────────────┘
```

## Migration Strategies

### 1. Blue-Green Deployment

**Steps:**
1. Setup new database (Green)
2. Migrate data during maintenance window
3. Test thoroughly in Green environment
4. Switch traffic to Green
5. Keep Blue as backup

**Benefits:**
- Minimal downtime
- Easy rollback
- Full testing before switch

### 2. Rolling Migration

**Steps:**
1. Setup read replica
2. Gradually move read operations
3. Migrate write operations
4. Decommission old database

**Benefits:**
- Zero downtime
- Gradual validation
- Lower risk

### 3. Parallel Run

**Steps:**
1. Setup new database
2. Write to both databases
3. Compare results
4. Switch reads to new database
5. Stop writing to old database

**Benefits:**
- Continuous validation
- High confidence
- Easy comparison

## Database-Specific Production Configurations

### PostgreSQL Production Setup

#### 1. Hardware Requirements

```bash
# Minimum Production Server
CPU: 4 cores
RAM: 16GB
Storage: 500GB SSD
Network: 1Gbps

# Recommended Production Server
CPU: 8 cores
RAM: 32GB
Storage: 1TB NVMe SSD
Network: 10Gbps
```

#### 2. PostgreSQL Configuration

```sql
-- postgresql.conf optimizations
shared_buffers = 8GB                    # 25% of total RAM
effective_cache_size = 24GB             # 75% of total RAM
maintenance_work_mem = 2GB              # For maintenance operations
work_mem = 64MB                         # Per connection working memory
max_connections = 200                   # Adjust based on needs
checkpoint_completion_target = 0.9      # Spread checkpoints
wal_buffers = 16MB                      # WAL buffer size
random_page_cost = 1.1                  # For SSD storage

# Logging
log_min_duration_statement = 1000ms     # Log slow queries
log_checkpoints = on                    # Log checkpoint activity
log_lock_waits = on                     # Log lock waits
```

#### 3. Connection Pooling with PgBouncer

```ini
# pgbouncer.ini
[databases]
ai_tools = host=localhost port=5432 dbname=ai_tools_prod

[pgbouncer]
listen_port = 6432
listen_addr = 0.0.0.0
auth_type = md5
auth_file = userlist.txt
pool_mode = transaction
max_client_conn = 200
default_pool_size = 50
```

#### 4. Monitoring Setup

```sql
-- Enable monitoring extensions
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pgstattuple;

-- Key monitoring queries
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;

SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del 
FROM pg_stat_user_tables;
```

### MySQL Production Setup

#### 1. InnoDB Configuration

```ini
# my.cnf optimizations
[mysqld]
innodb_buffer_pool_size = 20G           # 70-80% of RAM
innodb_log_file_size = 1G               # Large log files
innodb_log_buffer_size = 256M           # Log buffer
innodb_flush_log_at_trx_commit = 1      # ACID compliance
innodb_file_per_table = 1               # Separate files per table
innodb_buffer_pool_instances = 8        # Multiple buffer pools

# Query cache (if using MySQL 5.7)
query_cache_type = 1
query_cache_size = 256M

# Connection settings
max_connections = 200
max_connect_errors = 1000000
```

#### 2. Replication Setup

```sql
-- Master configuration
[mysqld]
server-id = 1
log-bin = mysql-bin
binlog-do-db = ai_tools_prod

-- Slave configuration
[mysqld]
server-id = 2
relay-log = mysql-relay-bin
read-only = 1
```

## Cloud Database Services

### AWS RDS Recommendations

#### PostgreSQL RDS Setup

```bash
# Create production PostgreSQL instance
aws rds create-db-instance \
    --db-instance-identifier ai-tools-prod \
    --db-instance-class db.r5.2xlarge \
    --engine postgres \
    --engine-version 15.4 \
    --allocated-storage 1000 \
    --storage-type gp3 \
    --storage-encrypted \
    --master-username aitools \
    --master-user-password <strong-password> \
    --backup-retention-period 7 \
    --multi-az \
    --auto-minor-version-upgrade \
    --deletion-protection
```

#### RDS Configuration

```python
# Production database URL for RDS
DATABASE_URL = (
    "postgresql://aitools:password@"
    "ai-tools-prod.cluster-xyz.us-east-1.rds.amazonaws.com:5432/"
    "ai_tools_prod"
)

# Connection pool settings
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'max_overflow': 30,
    'pool_pre_ping': True,
    'pool_recycle': 1800,
}
```

### Google Cloud SQL

```bash
# Create Cloud SQL instance
gcloud sql instances create ai-tools-prod \
    --database-version=POSTGRES_15 \
    --tier=db-custom-4-16384 \
    --region=us-central1 \
    --storage-size=1TB \
    --storage-type=SSD \
    --backup \
    --enable-bin-log \
    --deletion-protection
```

### Azure Database for PostgreSQL

```bash
# Create Azure PostgreSQL instance
az postgres server create \
    --resource-group ai-tools-rg \
    --name ai-tools-prod \
    --location eastus \
    --admin-user aitools \
    --admin-password <strong-password> \
    --sku-name GP_Gen5_4 \
    --storage-size 1024000 \
    --backup-retention 7 \
    --geo-redundant-backup Enabled
```

## Performance Optimization

### 1. Index Strategy

```sql
-- PostgreSQL indexes for AI Tool Intelligence
CREATE INDEX CONCURRENTLY idx_tools_monitoring_active 
ON tools(next_process_date, priority_level) 
WHERE is_actively_monitored = true;

CREATE INDEX CONCURRENTLY idx_tool_changes_recent 
ON tool_changes(detected_at DESC, tool_id) 
WHERE detected_at > CURRENT_TIMESTAMP - INTERVAL '30 days';

CREATE INDEX CONCURRENTLY idx_version_features_search 
ON version_features USING GIN(to_tsvector('english', feature_name || ' ' || feature_description));

-- JSONB indexes for competitive intelligence
CREATE INDEX CONCURRENTLY idx_pricing_snapshot_gin 
ON tool_versions USING GIN(pricing_snapshot) 
WHERE pricing_snapshot IS NOT NULL;
```

### 2. Query Optimization

```sql
-- Optimized query for tool monitoring dashboard
WITH tool_stats AS (
    SELECT 
        t.id,
        t.name,
        t.processing_status,
        COUNT(tc.id) as change_count,
        MAX(tc.detected_at) as last_change
    FROM tools t
    LEFT JOIN tool_changes tc ON t.id = tc.tool_id 
        AND tc.detected_at > CURRENT_TIMESTAMP - INTERVAL '7 days'
    WHERE t.is_actively_monitored = true
    GROUP BY t.id, t.name, t.processing_status
)
SELECT * FROM tool_stats 
ORDER BY change_count DESC, last_change DESC
LIMIT 50;
```

### 3. Maintenance Procedures

```sql
-- Automated maintenance function
CREATE OR REPLACE FUNCTION perform_daily_maintenance()
RETURNS void AS $$
BEGIN
    -- Update statistics
    ANALYZE;
    
    -- Clean old change records
    DELETE FROM tool_changes 
    WHERE detected_at < CURRENT_TIMESTAMP - INTERVAL '90 days'
    AND is_reviewed = true;
    
    -- Refresh materialized views
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_tool_analytics;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_category_analytics;
    
    -- Log maintenance completion
    INSERT INTO maintenance_log (operation, completed_at) 
    VALUES ('daily_maintenance', CURRENT_TIMESTAMP);
END;
$$ LANGUAGE plpgsql;

-- Schedule with pg_cron (if available)
SELECT cron.schedule('daily-maintenance', '0 2 * * *', 'SELECT perform_daily_maintenance();');
```

## Security Considerations

### 1. Database Security

```sql
-- Create application-specific user
CREATE USER ai_tools_app WITH PASSWORD 'strong-random-password';

-- Grant minimal required permissions
GRANT CONNECT ON DATABASE ai_tools_prod TO ai_tools_app;
GRANT USAGE ON SCHEMA public TO ai_tools_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ai_tools_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ai_tools_app;

-- Create read-only user for analytics
CREATE USER ai_tools_readonly WITH PASSWORD 'another-strong-password';
GRANT CONNECT ON DATABASE ai_tools_prod TO ai_tools_readonly;
GRANT USAGE ON SCHEMA public TO ai_tools_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ai_tools_readonly;
```

### 2. Connection Security

```python
# SSL configuration for production
DATABASE_URL = (
    "postgresql://user:password@host:5432/database"
    "?sslmode=require&sslcert=client-cert.pem&sslkey=client-key.pem&sslrootcert=ca-cert.pem"
)

# Environment-based configuration
import os
from urllib.parse import quote_plus

DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT', 5432),
    'database': os.getenv('DB_NAME'),
    'username': os.getenv('DB_USER'),
    'password': quote_plus(os.getenv('DB_PASSWORD')),
    'sslmode': os.getenv('DB_SSL_MODE', 'require')
}

DATABASE_URL = (
    f"postgresql://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}"
    f"@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}"
    f"/{DATABASE_CONFIG['database']}?sslmode={DATABASE_CONFIG['sslmode']}"
)
```

## Backup and Recovery

### 1. Backup Strategy

```bash
#!/bin/bash
# Production backup script for PostgreSQL

BACKUP_DIR="/backups/postgresql"
DB_NAME="ai_tools_prod"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Full database backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --format=custom --compress=9 \
    --file="$BACKUP_DIR/full_backup_$TIMESTAMP.dump"

# Schema-only backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --schema-only --format=custom \
    --file="$BACKUP_DIR/schema_backup_$TIMESTAMP.dump"

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.dump" -mtime +30 -delete

# Upload to cloud storage
aws s3 cp "$BACKUP_DIR/full_backup_$TIMESTAMP.dump" \
    s3://ai-tools-backups/postgresql/
```

### 2. Recovery Procedures

```bash
# Point-in-time recovery setup
# In postgresql.conf:
# wal_level = replica
# archive_mode = on
# archive_command = 'cp %p /archive/%f'

# Recovery from backup
pg_restore -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --clean --if-exists \
    /backups/postgresql/full_backup_20240101_120000.dump
```

## Monitoring and Alerting

### 1. Key Metrics to Monitor

```yaml
# Prometheus monitoring configuration
- name: database_health
  rules:
    - alert: DatabaseConnectionsHigh
      expr: pg_stat_activity_count > 180
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High number of database connections"
    
    - alert: DatabaseSlowQueries
      expr: pg_stat_statements_mean_time_ms > 1000
      for: 2m
      labels:
        severity: critical
      annotations:
        summary: "Slow database queries detected"
    
    - alert: DatabaseDiskSpace
      expr: pg_database_size_bytes / pg_filesystem_size_bytes > 0.8
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Database disk space running low"
```

### 2. Application-Level Monitoring

```python
# Database performance monitoring in Flask
import time
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Query performance tracking
@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    if total > 1.0:  # Log slow queries
        logger.warning(f"Slow query: {total:.2f}s - {statement[:100]}...")
```

## Migration Checklist

### Pre-Migration
- [ ] Backup current SQLite database
- [ ] Setup target database infrastructure
- [ ] Test migration process on copy of data
- [ ] Plan maintenance window
- [ ] Prepare rollback procedures
- [ ] Update application configuration
- [ ] Test application with new database

### During Migration
- [ ] Put application in maintenance mode
- [ ] Run final backup
- [ ] Execute migration scripts
- [ ] Verify data integrity
- [ ] Update DNS/load balancer configuration
- [ ] Test critical application functions
- [ ] Monitor system performance

### Post-Migration
- [ ] Monitor application logs
- [ ] Check database performance metrics
- [ ] Verify all features working
- [ ] Update documentation
- [ ] Schedule regular maintenance
- [ ] Setup monitoring and alerting
- [ ] Plan capacity scaling

## Troubleshooting Common Issues

### Connection Pool Exhaustion
```python
# Symptoms: "QueuePool limit of size X overflow Y reached"
# Solutions:
1. Increase pool_size and max_overflow
2. Check for connection leaks
3. Implement connection timeouts
4. Use connection pooling middleware (PgBouncer)
```

### Slow Query Performance
```sql
-- Identify slow queries
SELECT query, calls, total_time, mean_time, rows
FROM pg_stat_statements 
WHERE mean_time > 100  -- queries taking >100ms
ORDER BY total_time DESC;

-- Check missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public' AND n_distinct > 100;
```

### High CPU Usage
```sql
-- Check for sequential scans
SELECT schemaname, tablename, seq_scan, seq_tup_read, idx_scan, idx_tup_fetch
FROM pg_stat_user_tables
WHERE seq_scan > idx_scan;

-- Optimize frequent queries
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM tools WHERE processing_status = 'queued';
```

This comprehensive guide provides the foundation for successfully deploying the AI Tool Intelligence Platform with production-ready database systems.