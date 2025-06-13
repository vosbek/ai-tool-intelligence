# config/free_apis_config.py - Configuration for free APIs and Firecrawl MCP integration

import os
import time
from typing import Optional, Dict, Any
from functools import wraps
import hashlib
import json

class FreeAPIConfig:
    """Configuration for free APIs and rate limiting"""
    
    # GitHub API (Essential - 5K requests/hour with token)
    GITHUB_TOKEN: Optional[str] = os.getenv('GITHUB_TOKEN')
    GITHUB_RATE_LIMIT = 4000  # Leave buffer from 5000 limit
    GITHUB_BASE_URL = "https://api.github.com"
    
    # Firecrawl MCP (Enhanced web scraping)
    FIRECRAWL_API_KEY: Optional[str] = os.getenv('FIRECRAWL_API_KEY')
    FIRECRAWL_RETRY_MAX_ATTEMPTS = 3
    FIRECRAWL_RETRY_INITIAL_DELAY = 1000
    FIRECRAWL_BASE_URL = "https://api.firecrawl.dev"
    
    # Alpha Vantage API (Financial data - 25 requests/day free)
    ALPHA_VANTAGE_API_KEY: Optional[str] = os.getenv('ALPHA_VANTAGE_API_KEY')
    ALPHA_VANTAGE_RATE_LIMIT = 25  # 25 requests/day
    ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
    
    # News API (Free tier - 1000 requests/month)
    NEWS_API_KEY: Optional[str] = os.getenv('NEWS_API_KEY')
    NEWS_API_RATE_LIMIT = 1000  # 1000 requests/month
    NEWS_API_BASE_URL = "https://newsapi.org/v2"
    
    # Exchange Rates API (Free tier - 1000 requests/month)
    EXCHANGE_RATE_API_KEY: Optional[str] = os.getenv('EXCHANGE_RATE_API_KEY')
    EXCHANGE_RATE_LIMIT = 1000  # 1000 requests/month
    EXCHANGE_RATE_BASE_URL = "https://api.exchangerate-api.com/v4/latest"
    
    # Nominatim OpenStreetMap (Free geocoding - 1 request/second)
    NOMINATIM_USER_AGENT = "ai-tool-intelligence/1.0"
    NOMINATIM_RATE_LIMIT = 1  # 1 request/second
    NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"
    
    # Clearbit Logo API (Free, no auth required)
    CLEARBIT_LOGO_BASE_URL = "https://logo.clearbit.com"
    
    # General settings
    ENABLE_CACHING = True
    CACHE_TTL_SECONDS = 3600  # 1 hour
    REQUEST_TIMEOUT = 30
    USER_AGENT = "Mozilla/5.0 (compatible; AI-Tool-Intelligence/1.0)"
    
    # Rate limiting storage (in-memory for now)
    _rate_limit_storage = {}
    _cache_storage = {}
    
    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """Validate which APIs are available and properly configured"""
        available_apis = {
            'github': bool(cls.GITHUB_TOKEN),
            'firecrawl': bool(cls.FIRECRAWL_API_KEY),
            'alpha_vantage': bool(cls.ALPHA_VANTAGE_API_KEY),
            'news_api': bool(cls.NEWS_API_KEY),
            'exchange_rate': bool(cls.EXCHANGE_RATE_API_KEY),
            'nominatim': True,  # No key required
            'clearbit_logo': True  # No key required
        }
        return available_apis
    
    @classmethod
    def get_api_headers(cls, api_name: str) -> Dict[str, str]:
        """Get appropriate headers for each API"""
        headers = {'User-Agent': cls.USER_AGENT}
        
        if api_name == 'github' and cls.GITHUB_TOKEN:
            headers['Authorization'] = f'token {cls.GITHUB_TOKEN}'
            headers['Accept'] = 'application/vnd.github.v3+json'
        elif api_name == 'firecrawl' and cls.FIRECRAWL_API_KEY:
            headers['Authorization'] = f'Bearer {cls.FIRECRAWL_API_KEY}'
            headers['Content-Type'] = 'application/json'
        elif api_name == 'news_api' and cls.NEWS_API_KEY:
            headers['X-API-Key'] = cls.NEWS_API_KEY
        
        return headers
    
    @classmethod
    def check_rate_limit(cls, api_name: str) -> bool:
        """Check if API is within rate limits"""
        current_time = time.time()
        
        if api_name not in cls._rate_limit_storage:
            cls._rate_limit_storage[api_name] = []
        
        # Clean old requests based on time window
        time_windows = {
            'github': 3600,  # 1 hour
            'alpha_vantage': 86400,  # 1 day
            'news_api': 2592000,  # 30 days
            'exchange_rate': 2592000,  # 30 days
            'nominatim': 1,  # 1 second
            'firecrawl': 60  # 1 minute (conservative)
        }
        
        window = time_windows.get(api_name, 3600)
        cutoff_time = current_time - window
        
        cls._rate_limit_storage[api_name] = [
            req_time for req_time in cls._rate_limit_storage[api_name] 
            if req_time > cutoff_time
        ]
        
        # Check limits
        limits = {
            'github': cls.GITHUB_RATE_LIMIT,
            'alpha_vantage': cls.ALPHA_VANTAGE_RATE_LIMIT,
            'news_api': cls.NEWS_API_RATE_LIMIT,
            'exchange_rate': cls.EXCHANGE_RATE_LIMIT,
            'nominatim': cls.NOMINATIM_RATE_LIMIT,
            'firecrawl': 100  # Conservative estimate
        }
        
        current_requests = len(cls._rate_limit_storage[api_name])
        limit = limits.get(api_name, 1000)
        
        return current_requests < limit
    
    @classmethod
    def record_api_call(cls, api_name: str):
        """Record an API call for rate limiting"""
        if api_name not in cls._rate_limit_storage:
            cls._rate_limit_storage[api_name] = []
        
        cls._rate_limit_storage[api_name].append(time.time())
    
    @classmethod
    def get_cache_key(cls, url: str, params: Dict = None) -> str:
        """Generate cache key for URL and parameters"""
        cache_data = {'url': url, 'params': params or {}}
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    @classmethod
    def get_cached_response(cls, cache_key: str) -> Optional[Any]:
        """Get cached response if available and not expired"""
        if not cls.ENABLE_CACHING or cache_key not in cls._cache_storage:
            return None
        
        cached_data = cls._cache_storage[cache_key]
        if time.time() - cached_data['timestamp'] > cls.CACHE_TTL_SECONDS:
            del cls._cache_storage[cache_key]
            return None
        
        return cached_data['data']
    
    @classmethod
    def cache_response(cls, cache_key: str, data: Any):
        """Cache response data"""
        if cls.ENABLE_CACHING:
            cls._cache_storage[cache_key] = {
                'data': data,
                'timestamp': time.time()
            }
    
    @classmethod
    def get_config_summary(cls) -> Dict[str, Any]:
        """Get configuration summary for debugging"""
        available_apis = cls.validate_config()
        
        return {
            'available_apis': available_apis,
            'total_available': sum(available_apis.values()),
            'caching_enabled': cls.ENABLE_CACHING,
            'cache_ttl_hours': cls.CACHE_TTL_SECONDS / 3600,
            'current_cache_size': len(cls._cache_storage),
            'rate_limit_tracking': {
                api: len(requests) 
                for api, requests in cls._rate_limit_storage.items()
            }
        }


def rate_limited(api_name: str):
    """Decorator to enforce rate limiting on API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not FreeAPIConfig.check_rate_limit(api_name):
                raise Exception(f"Rate limit exceeded for {api_name} API")
            
            result = func(*args, **kwargs)
            FreeAPIConfig.record_api_call(api_name)
            return result
        return wrapper
    return decorator


def cached_request(cache_enabled: bool = True):
    """Decorator to cache API responses"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not cache_enabled or not FreeAPIConfig.ENABLE_CACHING:
                return func(*args, **kwargs)
            
            # Generate cache key from function name and arguments
            cache_data = {
                'func': func.__name__,
                'args': str(args),
                'kwargs': str(sorted(kwargs.items()))
            }
            cache_key = FreeAPIConfig.get_cache_key(
                func.__name__, 
                cache_data
            )
            
            # Check cache first
            cached_result = FreeAPIConfig.get_cached_response(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            FreeAPIConfig.cache_response(cache_key, result)
            return result
        return wrapper
    return decorator