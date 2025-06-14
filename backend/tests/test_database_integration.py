# backend/tests/test_database_integration.py - Database integration tests

import pytest
import tempfile
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.models.database import db, Tool, Category, ResearchResult
from backend.app import app

class TestDatabaseIntegration:
    """Integration tests for database operations"""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        temp_db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db_file.close()
        
        db_url = f'sqlite:///{temp_db_file.name}'
        engine = create_engine(db_url)
        
        # Configure app for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        
        with app.app_context():
            db.create_all()
            
        yield db_url, engine
        
        # Cleanup
        os.unlink(temp_db_file.name)
    
    def test_database_connection(self, temp_db):
        """Test basic database connection"""
        db_url, engine = temp_db
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
    
    def test_table_creation(self, temp_db):
        """Test that all tables are created properly"""
        db_url, engine = temp_db
        
        with engine.connect() as conn:
            # Check that main tables exist
            tables = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)).fetchall()
            
            table_names = [table[0] for table in tables]
            
            # Verify core tables exist
            assert 'category' in table_names
            assert 'tool' in table_names
            assert 'research_result' in table_names
    
    def test_foreign_key_constraints(self, temp_db):
        """Test foreign key relationships"""
        db_url, engine = temp_db
        
        with app.app_context():
            # Create a category
            category = Category(
                name='Test Category',
                description='Test category for integration testing'
            )
            db.session.add(category)
            db.session.commit()
            
            # Create a tool with the category
            tool = Tool(
                name='Test Tool',
                category_id=category.id,
                description='Test tool for integration testing',
                website_url='https://test.com',
                status='pending'
            )
            db.session.add(tool)
            db.session.commit()
            
            # Verify the relationship
            assert tool.category.name == 'Test Category'
            assert category.tools[0].name == 'Test Tool'
    
    def test_data_persistence(self, temp_db):
        """Test that data persists across sessions"""
        db_url, engine = temp_db
        
        # Create data in first session
        with app.app_context():
            category = Category(
                name='Persistent Category',
                description='Test persistence'
            )
            db.session.add(category)
            db.session.commit()
            category_id = category.id
        
        # Verify data exists in new session
        with app.app_context():
            retrieved_category = Category.query.get(category_id)
            assert retrieved_category is not None
            assert retrieved_category.name == 'Persistent Category'
    
    def test_transaction_rollback(self, temp_db):
        """Test transaction rollback functionality"""
        db_url, engine = temp_db
        
        with app.app_context():
            # Start a transaction that will fail
            try:
                category = Category(
                    name='Test Category',
                    description='Test'
                )
                db.session.add(category)
                db.session.flush()  # Force the insert
                
                # Try to insert duplicate (should fail if unique constraint exists)
                duplicate_category = Category(
                    name='Test Category',  # Same name
                    description='Duplicate'
                )
                db.session.add(duplicate_category)
                db.session.commit()
                
            except Exception:
                db.session.rollback()
                
            # Verify rollback worked
            categories = Category.query.filter_by(name='Test Category').all()
            # Should have 0 or 1 category, not 2
            assert len(categories) <= 1
    
    def test_bulk_operations(self, temp_db):
        """Test bulk database operations"""
        db_url, engine = temp_db
        
        with app.app_context():
            # Create category for tools
            category = Category(
                name='Bulk Test Category',
                description='For bulk testing'
            )
            db.session.add(category)
            db.session.commit()
            
            # Bulk insert tools
            tools = []
            for i in range(100):
                tool = Tool(
                    name=f'Bulk Tool {i}',
                    category_id=category.id,
                    description=f'Bulk test tool {i}',
                    website_url=f'https://bulk-tool-{i}.com',
                    status='pending'
                )
                tools.append(tool)
            
            db.session.bulk_save_objects(tools)
            db.session.commit()
            
            # Verify bulk insert worked
            tool_count = Tool.query.filter(Tool.name.like('Bulk Tool%')).count()
            assert tool_count == 100
    
    def test_complex_queries(self, temp_db):
        """Test complex database queries"""
        db_url, engine = temp_db
        
        with app.app_context():
            # Create test data
            category1 = Category(name='Category 1', description='First category')
            category2 = Category(name='Category 2', description='Second category')
            db.session.add_all([category1, category2])
            db.session.commit()
            
            # Create tools in different categories with different statuses
            tools = [
                Tool(name='Tool A', category_id=category1.id, status='completed', description='Tool A', website_url='https://a.com'),
                Tool(name='Tool B', category_id=category1.id, status='pending', description='Tool B', website_url='https://b.com'),
                Tool(name='Tool C', category_id=category2.id, status='completed', description='Tool C', website_url='https://c.com'),
                Tool(name='Tool D', category_id=category2.id, status='failed', description='Tool D', website_url='https://d.com'),
            ]
            db.session.add_all(tools)
            db.session.commit()
            
            # Test complex query: completed tools in category 1
            completed_cat1 = db.session.query(Tool).join(Category).filter(
                Category.name == 'Category 1',
                Tool.status == 'completed'
            ).all()
            
            assert len(completed_cat1) == 1
            assert completed_cat1[0].name == 'Tool A'
            
            # Test aggregation query
            status_counts = db.session.query(
                Tool.status,
                db.func.count(Tool.id).label('count')
            ).group_by(Tool.status).all()
            
            status_dict = {status: count for status, count in status_counts}
            assert status_dict['completed'] == 2
            assert status_dict['pending'] == 1
            assert status_dict['failed'] == 1
    
    def test_database_indexes(self, temp_db):
        """Test database indexes for performance"""
        db_url, engine = temp_db
        
        with engine.connect() as conn:
            # Check if indexes exist (SQLite specific)
            indexes = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND tbl_name='tool'
            """)).fetchall()
            
            # Should have at least some indexes
            assert len(indexes) > 0
    
    def test_data_validation(self, temp_db):
        """Test database-level data validation"""
        db_url, engine = temp_db
        
        with app.app_context():
            # Test required field validation
            with pytest.raises(Exception):
                tool = Tool(
                    # Missing required name field
                    description='Test tool without name',
                    website_url='https://test.com',
                    status='pending'
                )
                db.session.add(tool)
                db.session.commit()
    
    def test_concurrent_access(self, temp_db):
        """Test concurrent database access"""
        db_url, engine = temp_db
        
        # Create multiple sessions to simulate concurrent access
        Session = sessionmaker(bind=engine)
        
        session1 = Session()
        session2 = Session()
        
        try:
            with app.app_context():
                # Create category in session 1
                category = Category(name='Concurrent Test', description='Test concurrent access')
                session1.add(category)
                session1.commit()
                
                # Read from session 2
                category_from_s2 = session2.query(Category).filter_by(name='Concurrent Test').first()
                assert category_from_s2 is not None
                assert category_from_s2.name == 'Concurrent Test'
                
        finally:
            session1.close()
            session2.close()
    
    def test_backup_and_restore(self, temp_db):
        """Test database backup and restore functionality"""
        db_url, engine = temp_db
        
        with app.app_context():  
            # Create test data
            category = Category(name='Backup Test', description='For backup testing')
            db.session.add(category)
            db.session.commit()
            
            # Create backup (simple approach for SQLite)
            backup_file = tempfile.NamedTemporaryFile(delete=False, suffix='.backup.db')
            backup_file.close()
            
            # SQLite backup using SQL
            with engine.connect() as conn:
                conn.execute(text(f"VACUUM INTO '{backup_file.name}'"))
            
            # Verify backup exists and has data
            backup_engine = create_engine(f'sqlite:///{backup_file.name}')
            with backup_engine.connect() as backup_conn:
                result = backup_conn.execute(text("SELECT COUNT(*) FROM category")).fetchone()
                assert result[0] > 0
            
            # Cleanup
            os.unlink(backup_file.name)
    
    def test_migration_simulation(self, temp_db):
        """Test database migration scenarios"""
        db_url, engine = temp_db
        
        with app.app_context():
            # Create initial data
            category = Category(name='Migration Test', description='Test migration')
            db.session.add(category)
            db.session.commit()
            
            # Simulate adding a new column (SQLite limitations make this tricky)
            # Instead, test that we can add new data with updated schema expectations
            tool = Tool(
                name='Migration Tool',
                category_id=category.id,
                description='Tool for migration testing',
                website_url='https://migration-test.com',
                status='pending'
            )
            db.session.add(tool)
            db.session.commit()
            
            # Verify data integrity after "migration"
            assert Tool.query.filter_by(name='Migration Tool').first() is not None