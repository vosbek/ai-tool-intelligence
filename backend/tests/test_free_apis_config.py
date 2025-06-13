# tests/test_free_apis_config.py - Unit tests for free APIs configuration

import pytest
import os
import time
from unittest.mock import patch, Mock
import json
import hashlib

from config.free_apis_config import FreeAPIConfig, rate_limited, cached_request


class TestFreeAPIConfig:
    """Test suite for FreeAPIConfig class"""
    
    def test_config_initialization(self, mock_env_vars):
        """Test that configuration initializes with correct values"""
        config = FreeAPIConfig()
        
        assert config.GITHUB_TOKEN == 'test_github_token_123'
        assert config.FIRECRAWL_API_KEY == 'test_firecrawl_key_456'
        assert config.ALPHA_VANTAGE_API_KEY == 'test_alpha_vantage_789'
        assert config.REQUEST_TIMEOUT == 30
        assert config.ENABLE_CACHING is True
    
    def test_validate_config(self, mock_env_vars):
        """Test API configuration validation"""
        available_apis = FreeAPIConfig.validate_config()
        
        expected_apis = {
            'github': True,
            'firecrawl': True,
            'alpha_vantage': True,
            'news_api': True,
            'exchange_rate': True,
            'nominatim': True,
            'clearbit_logo': True
        }
        
        assert available_apis == expected_apis
    
    def test_validate_config_missing_keys(self):
        """Test validation with missing API keys"""
        with patch.dict(os.environ, {}, clear=True):
            available_apis = FreeAPIConfig.validate_config()
            
            expected_apis = {
                'github': False,
                'firecrawl': False,
                'alpha_vantage': False,
                'news_api': False,
                'exchange_rate': False,
                'nominatim': True,  # No key required
                'clearbit_logo': True  # No key required
            }
            
            assert available_apis == expected_apis
    
    def test_get_api_headers_github(self, mock_env_vars):
        """Test GitHub API headers generation"""
        headers = FreeAPIConfig.get_api_headers('github')
        
        expected_headers = {
            'User-Agent': FreeAPIConfig.USER_AGENT,
            'Authorization': 'token test_github_token_123',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        assert headers == expected_headers
    
    def test_get_api_headers_firecrawl(self, mock_env_vars):
        """Test Firecrawl API headers generation"""
        headers = FreeAPIConfig.get_api_headers('firecrawl')
        
        expected_headers = {
            'User-Agent': FreeAPIConfig.USER_AGENT,
            'Authorization': 'Bearer test_firecrawl_key_456',
            'Content-Type': 'application/json'
        }
        
        assert headers == expected_headers
    
    def test_get_api_headers_news_api(self, mock_env_vars):
        """Test News API headers generation"""
        headers = FreeAPIConfig.get_api_headers('news_api')
        
        expected_headers = {
            'User-Agent': FreeAPIConfig.USER_AGENT,
            'X-API-Key': 'test_news_api_012'
        }
        
        assert headers == expected_headers
    
    def test_get_api_headers_unknown_api(self, mock_env_vars):
        """Test headers for unknown API"""
        headers = FreeAPIConfig.get_api_headers('unknown_api')
        
        expected_headers = {
            'User-Agent': FreeAPIConfig.USER_AGENT
        }
        
        assert headers == expected_headers
    
    def test_rate_limiting_github(self):
        """Test GitHub rate limiting"""
        # Clear existing data
        FreeAPIConfig._rate_limit_storage.clear()
        
        # Should allow requests initially
        assert FreeAPIConfig.check_rate_limit('github') is True
        
        # Record many requests to hit limit
        for _ in range(FreeAPIConfig.GITHUB_RATE_LIMIT + 1):
            FreeAPIConfig.record_api_call('github')
        
        # Should now be rate limited
        assert FreeAPIConfig.check_rate_limit('github') is False
    
    def test_rate_limiting_cleanup(self):
        """Test rate limiting cleanup of old requests"""
        FreeAPIConfig._rate_limit_storage.clear()
        
        # Add old request (should be cleaned up)
        old_time = time.time() - 7200  # 2 hours ago
        FreeAPIConfig._rate_limit_storage['github'] = [old_time]
        
        # Check rate limit (should clean up old request)
        assert FreeAPIConfig.check_rate_limit('github') is True
        
        # Verify old request was removed
        assert len(FreeAPIConfig._rate_limit_storage['github']) == 0
    
    def test_cache_operations(self):
        """Test caching functionality"""
        FreeAPIConfig._cache_storage.clear()
        
        # Test cache miss
        cache_key = FreeAPIConfig.get_cache_key('test_url', {'param': 'value'})
        assert FreeAPIConfig.get_cached_response(cache_key) is None
        
        # Test cache store and retrieve
        test_data = {'result': 'test_data'}
        FreeAPIConfig.cache_response(cache_key, test_data)
        
        cached_result = FreeAPIConfig.get_cached_response(cache_key)
        assert cached_result == test_data
    
    def test_cache_expiration(self):
        """Test cache expiration"""
        FreeAPIConfig._cache_storage.clear()
        
        cache_key = 'test_key'
        test_data = {'result': 'test_data'}
        
        # Store with fake old timestamp
        FreeAPIConfig._cache_storage[cache_key] = {
            'data': test_data,
            'timestamp': time.time() - FreeAPIConfig.CACHE_TTL_SECONDS - 1
        }
        
        # Should return None for expired cache
        assert FreeAPIConfig.get_cached_response(cache_key) is None
        
        # Should remove expired entry
        assert cache_key not in FreeAPIConfig._cache_storage
    
    def test_cache_key_generation(self):
        """Test cache key generation consistency"""
        url1 = 'https://example.com'
        params1 = {'key': 'value', 'other': 'param'}
        
        # Same inputs should generate same key
        key1 = FreeAPIConfig.get_cache_key(url1, params1)
        key2 = FreeAPIConfig.get_cache_key(url1, params1)
        assert key1 == key2
        
        # Different inputs should generate different keys
        url2 = 'https://different.com'
        key3 = FreeAPIConfig.get_cache_key(url2, params1)
        assert key1 != key3
        
        # Parameter order shouldn't matter
        params2 = {'other': 'param', 'key': 'value'}
        key4 = FreeAPIConfig.get_cache_key(url1, params2)
        assert key1 == key4
    
    def test_get_config_summary(self, mock_env_vars):
        """Test configuration summary generation"""
        FreeAPIConfig._cache_storage.clear()
        FreeAPIConfig._rate_limit_storage.clear()
        
        # Add some test data
        FreeAPIConfig.cache_response('test_key', {'data': 'test'})
        FreeAPIConfig.record_api_call('github')
        
        summary = FreeAPIConfig.get_config_summary()
        
        assert 'available_apis' in summary
        assert 'total_available' in summary
        assert 'caching_enabled' in summary
        assert 'cache_ttl_hours' in summary
        assert 'current_cache_size' in summary
        assert 'rate_limit_tracking' in summary
        
        assert summary['total_available'] == 7  # All APIs should be available in test
        assert summary['caching_enabled'] is True
        assert summary['current_cache_size'] == 1
        assert summary['rate_limit_tracking']['github'] == 1


class TestRateLimitedDecorator:
    """Test suite for rate_limited decorator"""
    
    def test_rate_limited_decorator_allows_calls(self):
        """Test rate limited decorator allows calls within limit"""
        FreeAPIConfig._rate_limit_storage.clear()
        
        @rate_limited('test_api')
        def test_function():
            return "success"
        
        # Should allow call
        result = test_function()
        assert result == "success"
    
    def test_rate_limited_decorator_blocks_calls(self):
        """Test rate limited decorator blocks calls over limit"""
        FreeAPIConfig._rate_limit_storage.clear()
        
        # Mock rate limit check to return False
        with patch.object(FreeAPIConfig, 'check_rate_limit', return_value=False):
            @rate_limited('test_api')
            def test_function():
                return "success"
            
            # Should raise exception
            with pytest.raises(Exception, match="Rate limit exceeded"):
                test_function()
    
    def test_rate_limited_decorator_records_calls(self):
        """Test rate limited decorator records API calls"""
        FreeAPIConfig._rate_limit_storage.clear()
        
        @rate_limited('test_api')
        def test_function():
            return "success"
        
        # Call function
        test_function()
        
        # Should have recorded the call
        assert 'test_api' in FreeAPIConfig._rate_limit_storage
        assert len(FreeAPIConfig._rate_limit_storage['test_api']) == 1


class TestCachedRequestDecorator:
    """Test suite for cached_request decorator"""
    
    def test_cached_request_decorator_caches_results(self):
        """Test cached_request decorator caches function results"""
        FreeAPIConfig._cache_storage.clear()
        call_count = 0
        
        @cached_request()
        def test_function(param):
            nonlocal call_count
            call_count += 1
            return f"result_{param}_{call_count}"
        
        # First call
        result1 = test_function("test")
        assert result1 == "result_test_1"
        assert call_count == 1
        
        # Second call with same params should use cache
        result2 = test_function("test")
        assert result2 == "result_test_1"  # Same result
        assert call_count == 1  # Function not called again
        
        # Different params should call function again
        result3 = test_function("different")
        assert result3 == "result_different_2"
        assert call_count == 2
    
    def test_cached_request_decorator_disabled_caching(self):
        """Test cached_request decorator with caching disabled"""
        FreeAPIConfig._cache_storage.clear()
        call_count = 0
        
        @cached_request(cache_enabled=False)
        def test_function(param):
            nonlocal call_count
            call_count += 1
            return f"result_{param}_{call_count}"
        
        # Multiple calls should not use cache
        result1 = test_function("test")
        result2 = test_function("test")
        
        assert result1 == "result_test_1"
        assert result2 == "result_test_2"
        assert call_count == 2
    
    def test_cached_request_with_global_caching_disabled(self):
        """Test cached_request when global caching is disabled"""
        FreeAPIConfig._cache_storage.clear()
        call_count = 0
        
        # Temporarily disable global caching
        original_caching = FreeAPIConfig.ENABLE_CACHING
        FreeAPIConfig.ENABLE_CACHING = False
        
        try:
            @cached_request()
            def test_function(param):
                nonlocal call_count
                call_count += 1
                return f"result_{param}_{call_count}"
            
            # Multiple calls should not use cache
            result1 = test_function("test")
            result2 = test_function("test")
            
            assert result1 == "result_test_1"
            assert result2 == "result_test_2"
            assert call_count == 2
            
        finally:
            # Restore original setting
            FreeAPIConfig.ENABLE_CACHING = original_caching


class TestConfigurationEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_empty_environment(self):
        """Test configuration with completely empty environment"""
        with patch.dict(os.environ, {}, clear=True):
            config = FreeAPIConfig()
            
            assert config.GITHUB_TOKEN is None
            assert config.FIRECRAWL_API_KEY is None
            assert config.ALPHA_VANTAGE_API_KEY is None
            
            # Default values should still be set
            assert config.REQUEST_TIMEOUT == 30
            assert config.ENABLE_CACHING is True
            assert config.USER_AGENT == "Mozilla/5.0 (compatible; AI-Tool-Intelligence/1.0)"
    
    def test_rate_limiting_unknown_api(self):
        """Test rate limiting for unknown API"""
        FreeAPIConfig._rate_limit_storage.clear()
        
        # Should default to allowing requests
        assert FreeAPIConfig.check_rate_limit('unknown_api') is True
        
        # Record call
        FreeAPIConfig.record_api_call('unknown_api')
        
        # Should be recorded
        assert 'unknown_api' in FreeAPIConfig._rate_limit_storage
        assert len(FreeAPIConfig._rate_limit_storage['unknown_api']) == 1
    
    def test_cache_with_none_values(self):
        """Test caching with None values"""
        FreeAPIConfig._cache_storage.clear()
        
        cache_key = 'test_none'
        FreeAPIConfig.cache_response(cache_key, None)
        
        # Should be able to cache and retrieve None
        result = FreeAPIConfig.get_cached_response(cache_key)
        assert result is None
        
        # But key should exist in cache
        assert cache_key in FreeAPIConfig._cache_storage
    
    def test_concurrent_rate_limiting(self):
        """Test rate limiting under concurrent access"""
        FreeAPIConfig._rate_limit_storage.clear()
        
        import threading
        results = []
        
        def make_requests():
            for _ in range(10):
                allowed = FreeAPIConfig.check_rate_limit('test_concurrent')
                if allowed:
                    FreeAPIConfig.record_api_call('test_concurrent')
                results.append(allowed)
        
        # Create multiple threads
        threads = [threading.Thread(target=make_requests) for _ in range(5)]
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Should have some True results (allowed requests)
        assert any(results)
        
        # Should have recorded requests
        assert 'test_concurrent' in FreeAPIConfig._rate_limit_storage