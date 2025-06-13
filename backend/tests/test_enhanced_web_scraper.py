# tests/test_enhanced_web_scraper.py - Unit tests for enhanced web scraper

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
import json

from utils.enhanced_web_scraper import (
    EnhancedWebScraper, 
    extract_pricing_schema, 
    extract_company_schema, 
    extract_features_schema
)
from config.free_apis_config import FreeAPIConfig


class TestEnhancedWebScraper:
    """Test suite for EnhancedWebScraper class"""
    
    def test_initialization(self, mock_env_vars):
        """Test web scraper initialization"""
        scraper = EnhancedWebScraper()
        
        assert scraper.config is not None
        assert scraper.firecrawl_available is True  # Should be True with mock env vars
        assert hasattr(scraper, 'session')
        assert scraper.session.headers['User-Agent'] == FreeAPIConfig.USER_AGENT
    
    def test_initialization_no_firecrawl(self):
        """Test initialization without Firecrawl API key"""
        with patch.dict('os.environ', {}, clear=True):
            scraper = EnhancedWebScraper()
            assert scraper.firecrawl_available is False
    
    @patch('utils.enhanced_web_scraper.requests.Session.post')
    def test_firecrawl_scrape_success(self, mock_post, mock_env_vars, mock_firecrawl_response):
        """Test successful Firecrawl scraping"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_firecrawl_response()
        mock_post.return_value = mock_response
        
        scraper = EnhancedWebScraper()
        result = scraper.scrape_url("https://example.com")
        
        assert result["success"] is True
        assert result["url"] == "https://example.com"
        assert result["method"] == "firecrawl"
        assert "content" in result
        assert "html" in result
        assert "metadata" in result
        
        # Verify API call was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0].endswith('/v0/scrape')
        assert 'url' in call_args[1]['json']
        assert call_args[1]['json']['url'] == "https://example.com"
    
    @patch('utils.enhanced_web_scraper.requests.Session.post')
    @patch('utils.enhanced_web_scraper.requests.Session.get')
    def test_firecrawl_scrape_fallback(self, mock_get, mock_post, mock_env_vars):
        """Test fallback to basic scraping when Firecrawl fails"""
        # Setup Firecrawl to fail
        mock_post.side_effect = requests.RequestException("Firecrawl failed")
        
        # Setup basic scraping to succeed
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body>Test content</body></html>"
        mock_get.return_value = mock_response
        
        scraper = EnhancedWebScraper()
        result = scraper.scrape_url("https://example.com")
        
        assert result["success"] is True
        assert result["method"] == "basic"
        assert "content" in result
    
    @patch('utils.enhanced_web_scraper.requests.Session.get')
    def test_basic_scrape_success(self, mock_get):
        """Test successful basic web scraping"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Test Content</h1>
                <a href="/about">About</a>
                <img src="/logo.png" alt="Logo">
            </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        scraper = EnhancedWebScraper()
        scraper.firecrawl_available = False  # Force basic scraping
        
        result = scraper.scrape_url("https://example.com")
        
        assert result["success"] is True
        assert result["method"] == "basic"
        assert "Test Content" in result["content"]
        assert result["metadata"]["title"] == "Test Page"
        assert len(result["links"]) > 0
        assert len(result["images"]) > 0
    
    @patch('utils.enhanced_web_scraper.requests.Session.get')
    def test_basic_scrape_failure(self, mock_get):
        """Test basic scraping failure handling"""
        mock_get.side_effect = requests.RequestException("Network error")
        
        scraper = EnhancedWebScraper()
        scraper.firecrawl_available = False
        
        result = scraper.scrape_url("https://example.com")
        
        assert result["success"] is False
        assert "error" in result
        assert result["method"] == "basic"
    
    @patch('utils.enhanced_web_scraper.requests.Session.get')
    def test_basic_scrape_http_error(self, mock_get):
        """Test basic scraping with HTTP error status"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        scraper = EnhancedWebScraper()
        scraper.firecrawl_available = False
        
        result = scraper.scrape_url("https://example.com")
        
        assert result["success"] is False
        assert "HTTP 404" in result["error"]
    
    @patch('utils.enhanced_web_scraper.requests.Session.post')
    def test_batch_scrape_firecrawl(self, mock_post, mock_env_vars):
        """Test batch scraping with Firecrawl"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"url": "https://example1.com", "content": "Content 1"},
                {"url": "https://example2.com", "content": "Content 2"}
            ]
        }
        mock_post.return_value = mock_response
        
        scraper = EnhancedWebScraper()
        urls = ["https://example1.com", "https://example2.com"]
        
        result = scraper.batch_scrape(urls)
        
        assert len(result) == 2
        assert result[0]["url"] == "https://example1.com"
        assert result[1]["url"] == "https://example2.com"
        
        # Verify batch API was called
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0].endswith('/v0/batch/scrape')
    
    def test_batch_scrape_sequential_fallback(self, mock_env_vars):
        """Test sequential scraping fallback for small batches"""
        scraper = EnhancedWebScraper()
        
        # Mock scrape_url method
        scraper.scrape_url = Mock(side_effect=[
            {"success": True, "url": "https://example1.com"},
            {"success": True, "url": "https://example2.com"}
        ])
        
        urls = ["https://example1.com", "https://example2.com"]
        result = scraper.batch_scrape(urls)
        
        assert len(result) == 2
        assert scraper.scrape_url.call_count == 2
    
    @patch('utils.enhanced_web_scraper.requests.Session.post')
    def test_extract_structured_data_firecrawl(self, mock_post, mock_env_vars):
        """Test structured data extraction with Firecrawl"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "company_name": "Test Company",
                "founded_year": "2020",
                "location": "San Francisco"
            }
        }
        mock_post.return_value = mock_response
        
        scraper = EnhancedWebScraper()
        schema = {"company_name": "string", "founded_year": "string"}
        
        result = scraper.extract_structured_data(
            "https://example.com", 
            schema, 
            "Extract company information"
        )
        
        assert result["success"] is True
        assert result["method"] == "firecrawl_ai"
        assert "extracted_data" in result
        assert result["extracted_data"]["company_name"] == "Test Company"
        
        # Verify extract API was called
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0].endswith('/v0/extract')
        assert call_args[1]['json']['schema'] == schema
    
    def test_extract_structured_data_basic_fallback(self):
        """Test basic structured data extraction fallback"""
        scraper = EnhancedWebScraper()
        scraper.firecrawl_available = False
        
        # Mock scrape_url method
        scraper.scrape_url = Mock(return_value={
            "success": True,
            "content": "Test Company was founded in 2020 in San Francisco"
        })
        
        schema = {"company_name": "string", "founded_year": "string"}
        result = scraper.extract_structured_data("https://example.com", schema)
        
        assert result["success"] is True
        assert result["method"] == "basic_pattern"
        assert "extracted_data" in result
    
    @patch('utils.enhanced_web_scraper.requests.Session.post')
    def test_search_web_firecrawl(self, mock_post, mock_env_vars):
        """Test web search with Firecrawl"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"title": "Result 1", "url": "https://example1.com"},
                {"title": "Result 2", "url": "https://example2.com"}
            ]
        }
        mock_post.return_value = mock_response
        
        scraper = EnhancedWebScraper()
        result = scraper.search_web("test query")
        
        assert result["success"] is True
        assert result["method"] == "firecrawl_search"
        assert "results" in result
        assert len(result["results"]) == 2
        
        # Verify search API was called
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0].endswith('/v0/search')
    
    def test_search_web_no_firecrawl(self):
        """Test web search without Firecrawl"""
        scraper = EnhancedWebScraper()
        scraper.firecrawl_available = False
        
        result = scraper.search_web("test query")
        
        assert result["success"] is False
        assert "requires Firecrawl API key" in result["error"]
    
    def test_get_capabilities(self, mock_env_vars):
        """Test capabilities reporting"""
        scraper = EnhancedWebScraper()
        
        capabilities = scraper.get_capabilities()
        
        expected_capabilities = {
            "firecrawl_available": True,
            "basic_scraping": True,
            "batch_scraping": True,
            "ai_extraction": True,
            "web_search": True,
            "caching_enabled": True,
            "rate_limiting": True
        }
        
        assert capabilities == expected_capabilities
    
    def test_get_capabilities_no_firecrawl(self):
        """Test capabilities without Firecrawl"""
        with patch.dict('os.environ', {}, clear=True):
            scraper = EnhancedWebScraper()
            capabilities = scraper.get_capabilities()
            
            assert capabilities["firecrawl_available"] is False
            assert capabilities["basic_scraping"] is True
            assert capabilities["batch_scraping"] is False
            assert capabilities["ai_extraction"] is False
            assert capabilities["web_search"] is False
    
    def test_extract_meta_description(self):
        """Test meta description extraction"""
        from bs4 import BeautifulSoup
        
        html = """
        <html>
            <head>
                <meta name="description" content="Test description">
                <meta property="og:description" content="OG description">
            </head>
        </html>
        """
        
        scraper = EnhancedWebScraper()
        soup = BeautifulSoup(html, 'html.parser')
        
        description = scraper._extract_meta_description(soup)
        assert description == "Test description"
    
    def test_extract_meta_description_og_fallback(self):
        """Test meta description extraction with OpenGraph fallback"""
        from bs4 import BeautifulSoup
        
        html = """
        <html>
            <head>
                <meta property="og:description" content="OG description">
            </head>
        </html>
        """
        
        scraper = EnhancedWebScraper()
        soup = BeautifulSoup(html, 'html.parser')
        
        description = scraper._extract_meta_description(soup)
        assert description == "OG description"
    
    def test_extract_meta_description_none(self):
        """Test meta description extraction when none found"""
        from bs4 import BeautifulSoup
        
        html = "<html><head></head></html>"
        
        scraper = EnhancedWebScraper()
        soup = BeautifulSoup(html, 'html.parser')
        
        description = scraper._extract_meta_description(soup)
        assert description == ""


class TestSchemaFunctions:
    """Test suite for schema generation functions"""
    
    def test_extract_pricing_schema(self):
        """Test pricing schema generation"""
        schema = extract_pricing_schema()
        
        expected_fields = [
            "pricing_tiers", "free_tier_available", "enterprise_pricing",
            "trial_period", "currency", "pricing_model"
        ]
        
        for field in expected_fields:
            assert field in schema
        
        assert schema["pricing_tiers"] == "array"
        assert schema["free_tier_available"] == "boolean"
        assert schema["currency"] == "string"
    
    def test_extract_company_schema(self):
        """Test company schema generation"""
        schema = extract_company_schema()
        
        expected_fields = [
            "company_name", "founded_year", "headquarters",
            "employee_count", "funding_info", "leadership", "business_model"
        ]
        
        for field in expected_fields:
            assert field in schema
        
        assert schema["company_name"] == "string"
        assert schema["leadership"] == "array"
    
    def test_extract_features_schema(self):
        """Test features schema generation"""
        schema = extract_features_schema()
        
        expected_fields = [
            "core_features", "ai_features", "integrations",
            "enterprise_features", "api_available"
        ]
        
        for field in expected_fields:
            assert field in schema
        
        assert schema["core_features"] == "array"
        assert schema["api_available"] == "boolean"


class TestWebScrapingEdgeCases:
    """Test edge cases and error conditions"""
    
    @patch('utils.enhanced_web_scraper.requests.Session.get')
    def test_scrape_url_with_timeout(self, mock_get):
        """Test scraping with timeout"""
        mock_get.side_effect = requests.Timeout("Request timed out")
        
        scraper = EnhancedWebScraper()
        scraper.firecrawl_available = False
        
        result = scraper.scrape_url("https://example.com")
        
        assert result["success"] is False
        assert "error" in result
    
    @patch('utils.enhanced_web_scraper.requests.Session.get')
    def test_scrape_url_with_invalid_html(self, mock_get):
        """Test scraping with malformed HTML"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body><p>Unclosed tag<div>More content"
        mock_get.return_value = mock_response
        
        scraper = EnhancedWebScraper()
        scraper.firecrawl_available = False
        
        result = scraper.scrape_url("https://example.com")
        
        # Should still succeed, BeautifulSoup handles malformed HTML
        assert result["success"] is True
        assert "content" in result
    
    def test_scrape_url_empty_url(self):
        """Test scraping with empty URL"""
        scraper = EnhancedWebScraper()
        
        result = scraper.scrape_url("")
        
        assert result["success"] is False
        assert "error" in result
    
    @patch('utils.enhanced_web_scraper.requests.Session.post')
    def test_firecrawl_rate_limit_error(self, mock_post, mock_env_vars):
        """Test Firecrawl rate limit handling"""
        mock_response = Mock()
        mock_response.status_code = 429  # Rate limit
        mock_response.text = "Rate limit exceeded"
        mock_post.return_value = mock_response
        
        scraper = EnhancedWebScraper()
        
        # Mock the fallback basic scraping
        with patch.object(scraper, '_basic_scrape') as mock_basic:
            mock_basic.return_value = {"success": True, "method": "basic"}
            
            result = scraper.scrape_url("https://example.com")
            
            # Should fall back to basic scraping
            assert result["method"] == "basic"
            mock_basic.assert_called_once()
    
    def test_batch_scrape_empty_list(self):
        """Test batch scraping with empty URL list"""
        scraper = EnhancedWebScraper()
        
        result = scraper.batch_scrape([])
        
        assert result == []
    
    def test_batch_scrape_large_list(self, mock_env_vars):
        """Test batch scraping with large URL list"""
        scraper = EnhancedWebScraper()
        
        # Mock the Firecrawl batch method
        with patch.object(scraper, '_firecrawl_batch_scrape') as mock_batch:
            mock_batch.return_value = [{"success": True} for _ in range(15)]
            
            # Create list larger than batch limit
            urls = [f"https://example{i}.com" for i in range(15)]
            result = scraper.batch_scrape(urls)
            
            # Should use Firecrawl batch method
            mock_batch.assert_called_once()
    
    @patch('utils.enhanced_web_scraper.requests.Session.get')
    def test_scrape_url_connection_error(self, mock_get):
        """Test scraping with connection error"""
        mock_get.side_effect = requests.ConnectionError("Connection failed")
        
        scraper = EnhancedWebScraper()
        scraper.firecrawl_available = False
        
        result = scraper.scrape_url("https://example.com")
        
        assert result["success"] is False
        assert "Connection failed" in result["error"]
    
    def test_session_cleanup(self):
        """Test that session is properly cleaned up"""
        scraper = EnhancedWebScraper()
        session = scraper.session
        
        # Simulate cleanup
        scraper.__del__()
        
        # Session should be closed (we can't easily test this directly,
        # but we ensure the __del__ method doesn't raise exceptions)
        assert True  # If we get here, cleanup worked