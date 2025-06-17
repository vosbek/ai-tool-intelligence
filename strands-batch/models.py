"""
Database models for Strands Batch CLI
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pathlib import Path
from dataclasses import dataclass

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class AnalysisJob:
    """Analysis job model"""
    job_id: str
    tool_name: str
    tool_data: Dict
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    results: Optional[Dict] = None
    
    @classmethod
    def create(cls, tool_data: Dict) -> 'AnalysisJob':
        """Create new analysis job"""
        job_id = str(uuid.uuid4())[:8]
        tool_name = tool_data.get('name', 'Unknown')
        
        job = cls(
            job_id=job_id,
            tool_name=tool_name,
            tool_data=tool_data,
            status=JobStatus.PENDING,
            created_at=datetime.now()
        )
        
        # Insert into database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_jobs (
                job_id, tool_name, tool_data, status, created_at
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            job.job_id,
            job.tool_name,
            json.dumps(job.tool_data),
            job.status.value,
            job.created_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return job
    
    @classmethod
    def get_by_id(cls, job_id: str) -> Optional['AnalysisJob']:
        """Get job by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM analysis_jobs WHERE job_id = ?', (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_by_tool_name(cls, tool_name: str) -> Optional['AnalysisJob']:
        """Get most recent job for a tool"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM analysis_jobs 
            WHERE tool_name = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (tool_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_recent(cls, limit: int = 10) -> List['AnalysisJob']:
        """Get recent jobs"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM analysis_jobs 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def get_all(cls, status_filter: Optional[str] = None, limit: Optional[int] = None) -> List['AnalysisJob']:
        """Get all jobs with optional filters"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM analysis_jobs'
        params = []
        
        if status_filter:
            query += ' WHERE status = ?'
            params.append(status_filter)
        
        query += ' ORDER BY created_at DESC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def count_old(cls, days: int, status: Optional[str] = None) -> int:
        """Count old jobs"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        
        query = 'SELECT COUNT(*) FROM analysis_jobs WHERE created_at < ?'
        params = [cutoff_date.isoformat()]
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    @classmethod
    def get_old(cls, days: int, status: Optional[str] = None, limit: Optional[int] = None) -> List['AnalysisJob']:
        """Get old jobs"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        
        query = 'SELECT * FROM analysis_jobs WHERE created_at < ?'
        params = [cutoff_date.isoformat()]
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        query += ' ORDER BY created_at ASC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def delete_old(cls, days: int, status: Optional[str] = None) -> int:
        """Delete old jobs"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        
        query = 'DELETE FROM analysis_jobs WHERE created_at < ?'
        params = [cutoff_date.isoformat()]
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        cursor.execute(query, params)
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted
    
    def update_status(self, status: JobStatus, error_message: Optional[str] = None, results: Optional[Dict] = None):
        """Update job status"""
        self.status = status
        
        if status == JobStatus.RUNNING:
            self.started_at = datetime.now()
        elif status in [JobStatus.COMPLETED, JobStatus.ERROR]:
            self.completed_at = datetime.now()
        
        if error_message:
            self.error_message = error_message
        
        if results:
            self.results = results
        
        # Update in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE analysis_jobs 
            SET status = ?, started_at = ?, completed_at = ?, error_message = ?, results = ?
            WHERE job_id = ?
        ''', (
            self.status.value,
            self.started_at.isoformat() if self.started_at else None,
            self.completed_at.isoformat() if self.completed_at else None,
            self.error_message,
            json.dumps(self.results) if self.results else None,
            self.job_id
        ))
        
        conn.commit()
        conn.close()
    
    @classmethod
    def _from_row(cls, row: tuple) -> 'AnalysisJob':
        """Create AnalysisJob from database row"""
        return cls(
            job_id=row[0],
            tool_name=row[1],
            tool_data=json.loads(row[2]) if row[2] else {},
            status=JobStatus(row[3]),
            created_at=datetime.fromisoformat(row[4]),
            started_at=datetime.fromisoformat(row[5]) if row[5] else None,
            completed_at=datetime.fromisoformat(row[6]) if row[6] else None,
            error_message=row[7],
            results=json.loads(row[8]) if row[8] else None
        )

def get_db_connection() -> sqlite3.Connection:
    """Get database connection"""
    from config import Config
    config = Config()
    return sqlite3.connect(config.database_path)

def create_database(force: bool = False) -> bool:
    """Create database tables"""
    try:
        from config import Config
        config = Config()
        db_path = Path(config.database_path)
        
        if force and db_path.exists():
            db_path.unlink()
        
        conn = sqlite3.connect(config.database_path)
        cursor = conn.cursor()
        
        # Create analysis_jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_jobs (
                job_id TEXT PRIMARY KEY,
                tool_name TEXT NOT NULL,
                tool_data TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                error_message TEXT,
                results TEXT
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tool_name ON analysis_jobs(tool_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON analysis_jobs(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON analysis_jobs(created_at)')
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False