# tests/test_all_tools_integration.py - Integration tests for all enhanced tools

import pytest
from unittest.mock import patch, Mock
import json

from enhanced_strands_agent import EnhancedStrandsAgentService
from enhanced_strands_tools import enhanced_github_analyzer, enhanced_pricing_extractor
from enhanced_tools_additional import enhanced_company_lookup, enhanced_feature_extractor, enhanced_integration_detector


@pytest.mark.integration
class TestToolsIntegration:
    """Integration tests for enhanced tools working together"""
    
    def test_comprehensive_tool_analysis(self, mock_env_vars, sample_tool_data,
                                        mock_requests_response, sample_github_repo_data,
                                        sample_pricing_page_content, sample_company_page_content,
                                        sample_features_page_content):
        """Test comprehensive analysis using all tools together"""
        
        # Mock all external API calls
        def mock_request_side_effect(url, **kwargs):
            if 'api.github.com' in url:
                if 'repos/testuser/test-tool' in url:
                    return mock_requests_response(200, sample_github_repo_data)
                else:
                    return mock_requests_response(200, [])
            elif 'test-tool.example.com' in url:
                mock_resp = Mock()
                mock_resp.status_code = 200
                mock_resp.content = sample_pricing_page_content.encode()
                return mock_resp
            elif 'docs.test-tool.example.com' in url:
                mock_resp = Mock()
                mock_resp.status_code = 200
                mock_resp.content = sample_features_page_content.encode()
                return mock_resp
            else:
                return mock_requests_response(404, {"error": "Not found"})
        
        with patch('requests.get', side_effect=mock_request_side_effect):
            with patch('enhanced_strands_tools.requests.get', side_effect=mock_request_side_effect):
                with patch('enhanced_tools_additional.requests.get', side_effect=mock_request_side_effect):
                    
                    service = EnhancedStrandsAgentService()
                    result = service.analyze_tool(sample_tool_data)
        
        # Verify comprehensive analysis
        assert "error" not in result
        assert result["tool_name"] == "Test AI Tool"
        
        # Check that multiple tools were used
        tools_used = result["analysis_metadata"]["tools_used"]
        assert len(tools_used) >= 3  # Should use multiple tools
        
        # Check overall summary
        summary = result["overall_summary"]
        assert "popularity_score" in summary
        assert "activity_level" in summary
        assert "pricing_model" in summary
        assert "key_strengths" in summary
        
        # Verify data completeness
        assert result["analysis_metadata"]["total_confidence"] > 0
        assert result["analysis_metadata"]["data_completeness"] > 0
    
    def test_tool_analysis_with_partial_failures(self, mock_env_vars, sample_tool_data):
        """Test tool analysis when some tools fail"""
        
        def mock_failing_requests(*args, **kwargs):
            # Simulate network failures for some requests
            import random
            if random.choice([True, False]):
                raise Exception("Network error")
            
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.content = b"<html><body>Basic content</body></html>"
            return mock_resp
        
        with patch('requests.get', side_effect=mock_failing_requests):
            with patch('enhanced_strands_tools.requests.get', side_effect=mock_failing_requests):
                with patch('enhanced_tools_additional.requests.get', side_effect=mock_failing_requests):
                    
                    service = EnhancedStrandsAgentService()
                    result = service.analyze_tool(sample_tool_data)
        
        # Should still return results even with partial failures
        assert result["tool_name"] == "Test AI Tool"
        assert "analysis_metadata" in result
        
        # Some tools may have failed, but analysis should still complete
        tools_used = result["analysis_metadata"]["tools_used"]
        # At least one tool should have succeeded
        assert len(tools_used) >= 1
    
    def test_batch_tool_analysis(self, mock_env_vars, sample_tool_data, mock_requests_response):
        """Test analyzing multiple tools in batch"""
        
        tools_list = [
            sample_tool_data,
            {
                "name": "Another AI Tool",
                "website_url": "https://another-tool.example.com",
                "github_url": "https://github.com/another/tool",
                "company_name": "Another Company"
            }
        ]
        
        def mock_request_side_effect(url, **kwargs):
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.content = b"<html><body>Mock content</body></html>"
            return mock_resp
        
        with patch('requests.get', side_effect=mock_request_side_effect):
            with patch('enhanced_strands_tools.requests.get', side_effect=mock_request_side_effect):
                with patch('enhanced_tools_additional.requests.get', side_effect=mock_request_side_effect):
                    with patch('time.sleep'):  # Skip delays in testing
                        
                        service = EnhancedStrandsAgentService()
                        results = service.analyze_multiple_tools(tools_list)
        
        assert len(results) == 2
        assert results[0]["tool_name"] == "Test AI Tool"
        assert results[1]["tool_name"] == "Another AI Tool"
    
    @pytest.mark.slow
    def test_performance_with_large_dataset(self, mock_env_vars):
        """Test performance with many tools (performance test)"""
        import time
        
        # Create a large list of tools
        tools_list = [
            {
                "name": f"Tool {i}",
                "website_url": f"https://tool{i}.example.com",
                "github_url": f"https://github.com/user/tool{i}",
                "company_name": f"Company {i}"
            }
            for i in range(10)  # Reduced for testing
        ]
        
        def mock_fast_request(*args, **kwargs):
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.content = b"<html><body>Fast response</body></html>"
            return mock_resp
        
        with patch('requests.get', side_effect=mock_fast_request):
            with patch('enhanced_strands_tools.requests.get', side_effect=mock_fast_request):
                with patch('enhanced_tools_additional.requests.get', side_effect=mock_fast_request):
                    with patch('time.sleep'):  # Skip delays
                        
                        service = EnhancedStrandsAgentService()
                        
                        start_time = time.time()
                        results = service.analyze_multiple_tools(tools_list)
                        end_time = time.time()
        
        # Performance assertions
        assert len(results) == 10
        execution_time = end_time - start_time
        
        # Should complete reasonably quickly (adjust threshold as needed)
        assert execution_time < 30.0, f"Execution took too long: {execution_time}s"
        
        # All tools should have been processed
        successful_analyses = [r for r in results if "error" not in r]
        assert len(successful_analyses) == 10


@pytest.mark.integration 
class TestCrossToolDataFlow:
    """Test data flow between different tools"""
    
    def test_github_to_company_data_correlation(self, mock_env_vars, mock_requests_response):
        """Test that GitHub data correlates with company data"""
        
        github_data = {
            "name": "test-repo",
            "owner": {"login": "testcompany"},
            "description": "Official repository for Test Company",
            "stargazers_count": 5000,
            "created_at": "2020-01-01T00:00:00Z"
        }
        
        def mock_request_side_effect(url, **kwargs):
            if 'api.github.com' in url:
                return mock_requests_response(200, github_data)
            else:
                mock_resp = Mock()
                mock_resp.status_code = 200
                mock_resp.content = b"""
                <html><body>
                <h1>About Test Company</h1>
                <p>Founded in 2020, we're the creators of the popular test-repo.</p>
                <p>Follow us on GitHub: @testcompany</p>
                </body></html>
                """
                return mock_resp
        
        with patch('requests.get', side_effect=mock_request_side_effect):
            with patch('enhanced_strands_tools.requests.get', side_effect=mock_request_side_effect):
                with patch('enhanced_tools_additional.requests.get', side_effect=mock_request_side_effect):
                    
                    # Analyze GitHub repository
                    github_result = enhanced_github_analyzer("https://github.com/testcompany/test-repo")
                    
                    # Analyze company
                    company_result = enhanced_company_lookup("Test Company", "https://testcompany.com")
        
        # Verify data correlation
        assert "error" not in github_result
        assert "error" not in company_result
        
        # GitHub data should be consistent
        assert github_result["basic_stats"]["stars"] == 5000
        
        # Company data should reference the repository
        company_content = str(company_result)
        assert "2020" in company_content  # Founded year should match
    
    def test_pricing_to_features_consistency(self, mock_env_vars):
        """Test that pricing data is consistent with features"""
        
        def mock_request_side_effect(url, **kwargs):
            if 'pricing' in url or 'plans' in url:
                content = """
                <html><body>
                <h1>Pricing</h1>
                <div class="plan">
                    <h2>Free</h2>
                    <p>$0/month</p>
                    <ul><li>Basic API access</li><li>100 requests/day</li></ul>
                </div>
                <div class="plan">
                    <h2>Pro</h2>
                    <p>$29/month</p>
                    <ul><li>Advanced API access</li><li>Unlimited requests</li><li>Premium support</li></ul>
                </div>
                </body></html>
                """
            else:
                content = """
                <html><body>
                <h1>Features</h1>
                <ul class="features">
                    <li>Powerful API for developers</li>
                    <li>Real-time processing</li>
                    <li>24/7 premium support available</li>
                    <li>Enterprise-grade security</li>
                </ul>
                </body></html>
                """
            
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.content = content.encode()
            return mock_resp
        
        with patch('requests.get', side_effect=mock_request_side_effect):
            with patch('enhanced_tools_additional.requests.get', side_effect=mock_request_side_effect):
                
                pricing_result = enhanced_pricing_extractor("https://example.com")
                features_result = enhanced_feature_extractor("https://example.com")
        
        # Verify consistency
        assert "error" not in pricing_result
        assert "error" not in features_result
        
        # Features should mention API (consistent with pricing)
        features_content = str(features_result)
        assert "api" in features_content.lower()
        
        # Premium support should be mentioned in both
        pricing_content = str(pricing_result)
        assert ("premium" in pricing_content.lower() or 
                "support" in features_content.lower())


@pytest.mark.integration
class TestServiceStatusAndMonitoring:
    """Test service status and monitoring capabilities"""
    
    def test_service_status_reporting(self, mock_env_vars):
        """Test comprehensive service status reporting"""
        service = EnhancedStrandsAgentService()
        status = service.get_service_status()
        
        # Verify status structure
        assert "service_name" in status
        assert "available_tools" in status
        assert "api_status" in status
        assert "configuration" in status
        assert "capabilities" in status
        
        # Check available tools
        expected_tools = [
            'github_analyzer', 'pricing_extractor', 'company_lookup',
            'feature_extractor', 'integration_detector'
        ]
        
        for tool in expected_tools:
            assert tool in status["available_tools"]
        
        # Check API availability
        api_status = status["api_status"]
        assert isinstance(api_status, dict)
        assert len(api_status) > 0
        
        # Check capabilities
        capabilities = status["capabilities"]
        assert "github_analysis" in capabilities
        assert "enhanced_web_scraping" in capabilities
        assert "basic_web_scraping" in capabilities
        assert "caching" in capabilities
        assert "rate_limiting" in capabilities
    
    def test_configuration_validation(self, mock_env_vars):
        """Test configuration validation across all components"""
        from config.free_apis_config import FreeAPIConfig
        
        # Test configuration validation
        config = FreeAPIConfig()
        available_apis = config.validate_config()
        
        # Should have multiple APIs available in test environment
        assert available_apis["github"] is True
        assert available_apis["firecrawl"] is True
        assert available_apis["nominatim"] is True
        
        # Test configuration summary
        summary = config.get_config_summary()
        assert summary["total_available"] >= 3
        assert summary["caching_enabled"] is True
    
    def test_error_recovery_mechanisms(self, mock_env_vars):
        """Test that tools recover gracefully from errors"""
        
        def mock_failing_then_succeeding(*args, **kwargs):
            # Fail first, then succeed
            if not hasattr(mock_failing_then_succeeding, 'call_count'):
                mock_failing_then_succeeding.call_count = 0
            
            mock_failing_then_succeeding.call_count += 1
            
            if mock_failing_then_succeeding.call_count <= 2:
                raise Exception("Network error")
            
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.content = b"<html><body>Success after retry</body></html>"
            return mock_resp
        
        service = EnhancedStrandsAgentService()
        
        # Test that service can handle failures gracefully
        tool_data = {
            "name": "Test Tool",
            "website_url": "https://failing-then-working.com"
        }
        
        with patch('requests.get', side_effect=mock_failing_then_succeeding):
            with patch('enhanced_tools_additional.requests.get', side_effect=mock_failing_then_succeeding):
                
                result = service.analyze_tool(tool_data)
        
        # Should complete even with initial failures
        assert result["tool_name"] == "Test Tool"
        assert "analysis_metadata" in result