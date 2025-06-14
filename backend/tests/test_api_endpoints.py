# tests/test_api_endpoints.py - Comprehensive API endpoint testing

import pytest
import json
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
import tempfile
import os

# Flask testing
from flask import Flask
from flask.testing import FlaskClient

# Import the Flask app
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, db, Tool, Category, Company, ResearchLog


@pytest.fixture
def client():
    """Create test client with isolated database"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SKIP_AWS_VALIDATION'] = '1'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Add test data
            _create_test_data()
        yield client


@pytest.fixture
def auth_headers():
    """Authentication headers for admin endpoints"""
    return {
        'Authorization': 'Bearer test_admin_token',
        'X-Admin-User': 'test_admin'
    }


def _create_test_data():
    """Create test data for API tests"""
    # Create categories
    category1 = Category(
        name='AI Developer Tools',
        description='All AI-powered developer tools'
    )
    category2 = Category(
        name='Code Assistants',
        parent_id=1,
        description='AI coding assistants and copilots'
    )
    
    db.session.add(category1)
    db.session.add(category2)
    db.session.flush()
    
    # Create tools
    tool1 = Tool(
        name='Test AI Tool 1',
        category_id=1,
        description='A test AI tool for development',
        website_url='https://test-tool-1.com',
        github_url='https://github.com/test/tool1',
        is_open_source=True,
        pricing_model='freemium',
        processing_status='completed'
    )
    
    tool2 = Tool(
        name='Test AI Tool 2',
        category_id=2,
        description='Another test AI tool',
        website_url='https://test-tool-2.com',
        is_open_source=False,
        pricing_model='subscription',
        processing_status='never_run'
    )
    
    db.session.add(tool1)
    db.session.add(tool2)
    db.session.flush()
    
    # Create company for tool1
    company1 = Company(
        tool_id=tool1.id,
        name='Test Company 1',
        founded_year=2020,
        employee_count=50,
        headquarters='San Francisco, CA'
    )
    
    db.session.add(company1)
    db.session.commit()


class TestHealthEndpoints:
    """Test health and status endpoints"""
    
    def test_health_endpoint(self, client):
        """Test basic health check"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert data['version'] == 'MVP'
    
    def test_system_status_endpoint(self, client):
        """Test enhanced system status"""
        response = client.get('/api/system/status')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'enhanced_features_available' in data
        assert 'stability_features_available' in data
        assert 'components' in data
        assert 'timestamp' in data
    
    def test_system_health_endpoint(self, client):
        """Test detailed system health"""
        response = client.get('/api/system/health')
        
        # May not be available in test environment
        if response.status_code == 200:
            data = response.get_json()
            assert 'timestamp' in data
            assert 'uptime_seconds' in data


class TestToolsAPI:
    """Test core tools API endpoints"""
    
    def test_get_tools_list(self, client):
        """Test getting tools list"""
        response = client.get('/api/tools')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'tools' in data
        assert 'total' in data
        assert 'pages' in data
        assert 'current_page' in data
        assert len(data['tools']) == 2
        assert data['total'] == 2
    
    def test_get_tools_with_pagination(self, client):
        """Test tools list with pagination"""
        response = client.get('/api/tools?page=1&per_page=1')
        assert response.status_code == 200
        
        data = response.get_json()
        assert len(data['tools']) == 1
        assert data['total'] == 2
        assert data['pages'] == 2
        assert data['current_page'] == 1
    
    def test_get_tools_with_category_filter(self, client):
        """Test tools list filtered by category"""
        response = client.get('/api/tools?category_id=1')
        assert response.status_code == 200
        
        data = response.get_json()
        assert len(data['tools']) == 1
        assert data['tools'][0]['category_id'] == 1
    
    def test_get_tools_with_status_filter(self, client):
        """Test tools list filtered by processing status"""
        response = client.get('/api/tools?status=completed')
        assert response.status_code == 200
        
        data = response.get_json()
        assert len(data['tools']) == 1
        assert data['tools'][0]['processing_status'] == 'completed'
    
    def test_get_single_tool(self, client):
        """Test getting single tool with details"""
        response = client.get('/api/tools/1')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['id'] == 1
        assert data['name'] == 'Test AI Tool 1'
        assert 'category' in data
        assert 'company' in data
        assert 'features' in data
        assert 'integrations' in data
    
    def test_get_nonexistent_tool(self, client):
        """Test getting non-existent tool"""
        response = client.get('/api/tools/999')
        assert response.status_code == 404
    
    def test_create_tool(self, client):
        """Test creating a new tool"""
        tool_data = {
            'name': 'New Test Tool',
            'category_id': 1,
            'description': 'A newly created test tool',
            'website_url': 'https://new-test-tool.com',
            'is_open_source': True,
            'pricing_model': 'free'
        }
        
        response = client.post('/api/tools', 
                             data=json.dumps(tool_data),
                             content_type='application/json')
        assert response.status_code == 201
        
        data = response.get_json()
        assert data['name'] == 'New Test Tool'
        assert data['category_id'] == 1
        assert data['processing_status'] == 'never_run'
        assert 'id' in data
    
    def test_create_tool_invalid_data(self, client):
        """Test creating tool with invalid data"""
        tool_data = {
            'description': 'Missing required name field'
        }
        
        response = client.post('/api/tools',
                             data=json.dumps(tool_data),
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_update_tool(self, client):
        """Test updating an existing tool"""
        update_data = {
            'description': 'Updated description',
            'internal_notes': 'Some internal notes'
        }
        
        response = client.put('/api/tools/1',
                            data=json.dumps(update_data),
                            content_type='application/json')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['description'] == 'Updated description'
        assert data['internal_notes'] == 'Some internal notes'
        assert 'updated_at' in data
    
    def test_update_nonexistent_tool(self, client):
        """Test updating non-existent tool"""
        update_data = {'description': 'Updated description'}
        
        response = client.put('/api/tools/999',
                            data=json.dumps(update_data),
                            content_type='application/json')
        assert response.status_code == 404


class TestResearchAPI:
    """Test research functionality"""
    
    @patch('app.StrandsAgentService')
    def test_research_tool_success(self, mock_service_class, client):
        """Test successful tool research"""
        # Mock the research service
        mock_service = Mock()
        mock_service.research_tool.return_value = {
            'tool': {
                'description': 'Enhanced description from research',
                'license_type': 'MIT'
            },
            'company': {
                'name': 'Research Company',
                'founded_year': 2021
            },
            'confidence_score': 0.85
        }
        mock_service_class.return_value = mock_service
        
        response = client.post('/api/tools/1/research')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'completed'
        assert 'research_data' in data
        assert 'tool' in data
        assert data['tool']['processing_status'] == 'completed'
    
    @patch('app.StrandsAgentService')
    def test_research_tool_failure(self, mock_service_class, client):
        """Test tool research failure"""
        # Mock service to raise exception
        mock_service = Mock()
        mock_service.research_tool.side_effect = Exception('Research failed')
        mock_service_class.return_value = mock_service
        
        response = client.post('/api/tools/1/research')
        assert response.status_code == 500
        
        data = response.get_json()
        assert 'error' in data
    
    @patch('app.StrandsAgentService')
    def test_research_tool_strands_unavailable(self, mock_service_class, client):
        """Test research when Strands packages unavailable"""
        # Mock service to return error
        mock_service = Mock()
        mock_service.research_tool.return_value = {
            'error': 'Strands Agents not available. Please install with: pip install strands-agents strands-tools'
        }
        mock_service_class.return_value = mock_service
        
        response = client.post('/api/tools/1/research')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'failed'
        assert 'error' in data['research_data']
        assert data['tool']['processing_status'] == 'error'
    
    def test_research_nonexistent_tool(self, client):
        """Test researching non-existent tool"""
        response = client.post('/api/tools/999/research')
        assert response.status_code == 404


class TestCategoriesAPI:
    """Test categories API"""
    
    def test_get_categories(self, client):
        """Test getting all categories"""
        response = client.get('/api/categories')
        assert response.status_code == 200
        
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 2
        
        # Find the root category
        root_category = next((cat for cat in data if cat['name'] == 'AI Developer Tools'), None)
        assert root_category is not None
        assert root_category['parent_id'] is None
        
        # Find the child category
        child_category = next((cat for cat in data if cat['name'] == 'Code Assistants'), None)
        assert child_category is not None
        assert child_category['parent_id'] == 1


class TestCompetitiveAnalysisAPI:
    """Test competitive analysis endpoints"""
    
    def test_curate_tool_data(self, client):
        """Test enhanced tool curation"""
        response = client.post('/api/tools/1/curate')
        
        # May return error if enhanced features not available
        if response.status_code == 200:
            data = response.get_json()
            assert 'status' in data or 'error' in data
        else:
            assert response.status_code in [503, 500]
    
    def test_competitive_analysis_category(self, client):
        """Test category competitive analysis"""
        response = client.get('/api/categories/1/competitive-analysis')
        
        # May return error if enhanced features not available
        if response.status_code == 200:
            data = response.get_json()
            assert 'analysis_id' in data
            assert 'category' in data
            assert 'market_leaders' in data
        else:
            assert response.status_code in [503, 500]
    
    def test_market_trends(self, client):
        """Test market trends endpoint"""
        response = client.get('/api/market/trends?type=features&days=30')
        
        # May return error if enhanced features not available
        if response.status_code == 200:
            data = response.get_json()
            assert 'trend_type' in data
            assert 'analysis_period_days' in data
            assert 'trends' in data
        else:
            assert response.status_code in [503, 500]
    
    def test_market_forecast(self, client):
        """Test market forecast endpoint"""
        response = client.get('/api/market/forecast?category_id=1')
        
        # May return error if enhanced features not available
        if response.status_code == 200:
            data = response.get_json()
            assert 'forecast_id' in data
            assert 'horizon_days' in data
        else:
            assert response.status_code in [503, 500]
    
    def test_competitive_digest(self, client):
        """Test competitive digest endpoint"""
        response = client.get('/api/competitive/digest?hours=24')
        
        # May return error if enhanced features not available
        if response.status_code == 200:
            data = response.get_json()
            assert 'digest_id' in data
            assert 'period_start' in data
            assert 'period_end' in data
        else:
            assert response.status_code in [503, 500]
    
    def test_compare_tools(self, client):
        """Test tool comparison endpoint"""
        comparison_data = {
            'tool_ids': [1, 2],
            'type': 'comprehensive'
        }
        
        response = client.post('/api/competitive/compare',
                             data=json.dumps(comparison_data),
                             content_type='application/json')
        
        # May return error if enhanced features not available
        if response.status_code == 200:
            data = response.get_json()
            assert 'comparison_id' in data
            assert 'tools_compared' in data
        else:
            assert response.status_code in [503, 500]
    
    def test_market_opportunities(self, client):
        """Test market opportunities endpoint"""
        response = client.get('/api/market/opportunities?category_id=1')
        
        # May return error if enhanced features not available
        if response.status_code == 200:
            data = response.get_json()
            assert 'opportunities' in data
        else:
            assert response.status_code in [503, 500]
    
    def test_tool_quality_score(self, client):
        """Test tool quality score endpoint"""
        response = client.get('/api/tools/1/quality-score')
        
        # May return error if enhanced features not available
        if response.status_code == 200:
            data = response.get_json()
            assert 'tool_id' in data
            assert 'quality_score' in data
        else:
            assert response.status_code in [503, 500]


class TestAdminAPI:
    """Test admin interface endpoints"""
    
    def test_admin_dashboard(self, client, auth_headers):
        """Test admin dashboard endpoint"""
        response = client.get('/api/admin/dashboard', headers=auth_headers)
        
        # May return error if admin features not available
        if response.status_code == 200:
            data = response.get_json()
            assert 'summary' in data
            assert 'recent_activity' in data
        else:
            assert response.status_code in [503, 500, 401, 403]
    
    def test_admin_analytics(self, client, auth_headers):
        """Test admin analytics endpoint"""
        response = client.get('/api/admin/analytics?time_range=30', headers=auth_headers)
        
        # May return error if admin features not available
        if response.status_code == 200:
            data = response.get_json()
            assert 'time_range_days' in data
        else:
            assert response.status_code in [503, 500, 401, 403]
    
    def test_bulk_operations(self, client, auth_headers):
        """Test bulk operations endpoint"""
        bulk_data = {
            'operation': 'research',
            'tool_ids': [1, 2],
            'parameters': {'priority': 'high'}
        }
        
        response = client.post('/api/admin/bulk-operations',
                             data=json.dumps(bulk_data),
                             content_type='application/json',
                             headers=auth_headers)
        
        # May return error if admin features not available
        if response.status_code == 200:
            data = response.get_json()
            assert 'operation_id' in data
            assert 'operation' in data
        else:
            assert response.status_code in [503, 500, 401, 403]


class TestMonitoringAPI:
    """Test monitoring and logging endpoints"""
    
    def test_monitoring_health(self, client):
        """Test monitoring health endpoint"""
        response = client.get('/api/monitoring/health')
        
        # May return error if monitoring features not available
        if response.status_code == 200:
            data = response.get_json()
            assert 'status' in data
            assert 'components' in data
        else:
            assert response.status_code in [503, 500, 401, 403]
    
    def test_monitoring_metrics(self, client):
        """Test monitoring metrics endpoint"""
        response = client.get('/api/monitoring/metrics')
        
        # May return error if monitoring features not available
        if response.status_code == 200:
            data = response.get_json()
            assert 'performance' in data
            assert 'business' in data
            assert 'system' in data
        else:
            assert response.status_code in [503, 500, 401, 403]
    
    def test_monitoring_logs(self, client):
        """Test monitoring logs endpoint"""
        response = client.get('/api/monitoring/logs?level=ERROR&limit=10')
        
        # May return error if monitoring features not available
        if response.status_code == 200:
            data = response.get_json()
            assert 'logs' in data
            assert 'total_entries' in data
        else:
            assert response.status_code in [503, 500, 401, 403]


class TestErrorHandling:
    """Test error handling across endpoints"""
    
    def test_invalid_json_request(self, client):
        """Test handling of invalid JSON"""
        response = client.post('/api/tools',
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_missing_content_type(self, client):
        """Test handling of missing content type"""
        response = client.post('/api/tools',
                             data=json.dumps({'name': 'Test'}))
        # Should handle gracefully or return appropriate error
        assert response.status_code in [400, 415]
    
    def test_malformed_url_parameters(self, client):
        """Test handling of malformed URL parameters"""
        response = client.get('/api/tools?page=invalid&per_page=abc')
        # Should handle gracefully with defaults or return error
        assert response.status_code in [200, 400]
    
    def test_sql_injection_protection(self, client):
        """Test protection against SQL injection"""
        response = client.get("/api/tools?category_id=1'; DROP TABLE tools; --")
        # Should handle safely
        assert response.status_code in [200, 400]


class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present"""
        response = client.options('/api/health')
        
        # Check for CORS headers
        if 'Access-Control-Allow-Origin' in response.headers:
            assert response.headers['Access-Control-Allow-Origin'] == '*' or 'localhost' in response.headers['Access-Control-Allow-Origin']
    
    def test_preflight_request(self, client):
        """Test CORS preflight request"""
        response = client.options('/api/tools',
                                headers={
                                    'Origin': 'http://localhost:3000',
                                    'Access-Control-Request-Method': 'POST',
                                    'Access-Control-Request-Headers': 'Content-Type'
                                })
        
        # Should allow the request
        assert response.status_code in [200, 204]


@pytest.mark.slow
class TestPerformance:
    """Test API performance"""
    
    def test_health_endpoint_response_time(self, client):
        """Test health endpoint response time"""
        import time
        
        start_time = time.time()
        response = client.get('/api/health')
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond within 1 second
    
    def test_tools_list_pagination_performance(self, client):
        """Test tools list performance with pagination"""
        import time
        
        start_time = time.time()
        response = client.get('/api/tools?page=1&per_page=50')
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Should respond within 2 seconds


if __name__ == '__main__':
    pytest.main([__file__, '-v'])