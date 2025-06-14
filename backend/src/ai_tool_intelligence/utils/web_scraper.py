# utils/enhanced_web_scraper.py - Enhanced web scraper with Firecrawl MCP integration

import requests
import json
import time
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import sys
import os

# Add config to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config.free_apis_config import FreeAPIConfig, rate_limited, cached_request


class EnhancedWebScraper:
    """Enhanced web scraper with Firecrawl MCP integration and fallback capabilities"""
    
    def __init__(self):
        self.config = FreeAPIConfig()
        self.firecrawl_available = bool(self.config.FIRECRAWL_API_KEY)
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.USER_AGENT
        })
    
    def __del__(self):
        """Clean up session"""
        if hasattr(self, 'session'):
            self.session.close()
    
    @cached_request()
    def scrape_url(self, url: str, options: Dict = None) -> Dict:
        """
        Scrape a single URL with Firecrawl if available, fallback to basic scraping
        
        Args:
            url: URL to scrape
            options: Scraping options (format, extract_content, etc.)
        
        Returns:
            Dict with scraped content and metadata
        """
        if self.firecrawl_available:
            return self._firecrawl_scrape(url, options)
        else:
            return self._basic_scrape(url, options)
    
    @rate_limited('firecrawl')
    def _firecrawl_scrape(self, url: str, options: Dict = None) -> Dict:
        """Use Firecrawl MCP for enhanced scraping"""
        try:
            firecrawl_url = f"{self.config.FIRECRAWL_BASE_URL}/v0/scrape"
            headers = self.config.get_api_headers('firecrawl')
            
            payload = {
                "url": url,
                "formats": options.get('formats', ['markdown', 'html']) if options else ['markdown'],
                "includeTags": options.get('include_tags', []) if options else [],
                "excludeTags": options.get('exclude_tags', ['nav', 'footer', 'aside']) if options else ['nav', 'footer', 'aside'],
                "waitFor": options.get('wait_for', 3000) if options else 3000
            }
            
            response = self.session.post(
                firecrawl_url, 
                json=payload, 
                headers=headers,
                timeout=self.config.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "url": url,
                    "content": data.get('data', {}).get('markdown', ''),
                    "html": data.get('data', {}).get('html', ''),
                    "metadata": data.get('data', {}).get('metadata', {}),
                    "method": "firecrawl",
                    "links": data.get('data', {}).get('links', []),
                    "images": data.get('data', {}).get('images', [])
                }
            else:
                # Fallback on Firecrawl error
                return self._basic_scrape(url, options)
                
        except Exception as e:
            print(f"Firecrawl error: {e}, falling back to basic scraping")
            return self._basic_scrape(url, options)
    
    def _basic_scrape(self, url: str, options: Dict = None) -> Dict:
        """Basic web scraping fallback"""
        try:
            response = self.session.get(
                url, 
                timeout=self.config.REQUEST_TIMEOUT,
                headers={'User-Agent': self.config.USER_AGENT}
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove unwanted elements
                for element in soup.find_all(['nav', 'footer', 'aside', 'script', 'style']):
                    element.decompose()
                
                # Extract content
                content = soup.get_text(separator=' ', strip=True)
                
                # Extract links
                links = [
                    {
                        'href': urljoin(url, a.get('href', '')),
                        'text': a.get_text(strip=True)
                    }
                    for a in soup.find_all('a', href=True)[:50]  # Limit links
                ]
                
                # Extract images
                images = [
                    urljoin(url, img.get('src', ''))
                    for img in soup.find_all('img', src=True)[:20]  # Limit images
                ]
                
                return {
                    "success": True,
                    "url": url,
                    "content": content,
                    "html": str(soup),
                    "metadata": {
                        "title": soup.title.string if soup.title else "",
                        "description": self._extract_meta_description(soup)
                    },
                    "method": "basic",
                    "links": links,
                    "images": images
                }
            else:
                return {
                    "success": False,
                    "url": url,
                    "error": f"HTTP {response.status_code}",
                    "method": "basic"
                }
                
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": str(e),
                "method": "basic"
            }
    
    @cached_request()
    def batch_scrape(self, urls: List[str], options: Dict = None) -> List[Dict]:
        """Scrape multiple URLs efficiently"""
        if self.firecrawl_available and len(urls) > 3:
            return self._firecrawl_batch_scrape(urls, options)
        else:
            # Sequential scraping for small batches or no Firecrawl
            results = []
            for url in urls:
                result = self.scrape_url(url, options)
                results.append(result)
                time.sleep(0.5)  # Be respectful
            return results
    
    @rate_limited('firecrawl')
    def _firecrawl_batch_scrape(self, urls: List[str], options: Dict = None) -> List[Dict]:
        """Use Firecrawl batch scraping for multiple URLs"""
        try:
            firecrawl_url = f"{self.config.FIRECRAWL_BASE_URL}/v0/batch/scrape"
            headers = self.config.get_api_headers('firecrawl')
            
            payload = {
                "urls": urls[:10],  # Limit batch size
                "formats": options.get('formats', ['markdown']) if options else ['markdown'],
                "excludeTags": options.get('exclude_tags', ['nav', 'footer']) if options else ['nav', 'footer']
            }
            
            response = self.session.post(
                firecrawl_url,
                json=payload,
                headers=headers,
                timeout=self.config.REQUEST_TIMEOUT * 2  # Longer timeout for batch
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                # Fallback to sequential
                return [self.scrape_url(url, options) for url in urls]
                
        except Exception as e:
            print(f"Firecrawl batch error: {e}, falling back to sequential")
            return [self.scrape_url(url, options) for url in urls]
    
    @cached_request()
    def extract_structured_data(self, url: str, schema: Dict, prompt: str = None) -> Dict:
        """Extract structured data using AI-powered extraction"""
        if self.firecrawl_available:
            return self._firecrawl_extract(url, schema, prompt)
        else:
            return self._basic_extract(url, schema)
    
    @rate_limited('firecrawl')
    def _firecrawl_extract(self, url: str, schema: Dict, prompt: str = None) -> Dict:
        """Use Firecrawl AI-powered extraction"""
        try:
            firecrawl_url = f"{self.config.FIRECRAWL_BASE_URL}/v0/extract"
            headers = self.config.get_api_headers('firecrawl')
            
            payload = {
                "url": url,
                "schema": schema,
                "prompt": prompt or "Extract the requested information accurately"
            }
            
            response = self.session.post(
                firecrawl_url,
                json=payload,
                headers=headers,
                timeout=self.config.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "url": url,
                    "extracted_data": data.get('data', {}),
                    "method": "firecrawl_ai"
                }
            else:
                return self._basic_extract(url, schema)
                
        except Exception as e:
            print(f"Firecrawl extract error: {e}, falling back to basic extraction")
            return self._basic_extract(url, schema)
    
    def _basic_extract(self, url: str, schema: Dict) -> Dict:
        """Basic structured data extraction"""
        scraped = self.scrape_url(url)
        if not scraped.get('success'):
            return scraped
        
        # Basic pattern matching based on schema
        content = scraped.get('content', '').lower()
        extracted = {}
        
        for field, field_type in schema.items():
            if field_type == 'string':
                # Look for field-related content
                if field.lower() in content:
                    lines = content.split('\n')
                    for line in lines:
                        if field.lower() in line:
                            extracted[field] = line.strip()[:200]
                            break
            elif field_type == 'array':
                # Extract list items
                extracted[field] = []
                
        return {
            "success": True,
            "url": url,
            "extracted_data": extracted,
            "method": "basic_pattern"
        }
    
    @cached_request()
    def search_web(self, query: str, options: Dict = None) -> Dict:
        """Search the web using Firecrawl search if available"""
        if self.firecrawl_available:
            return self._firecrawl_search(query, options)
        else:
            return {
                "success": False,
                "error": "Web search requires Firecrawl API key",
                "query": query
            }
    
    @rate_limited('firecrawl')
    def _firecrawl_search(self, query: str, options: Dict = None) -> Dict:
        """Use Firecrawl search capabilities"""
        try:
            firecrawl_url = f"{self.config.FIRECRAWL_BASE_URL}/v0/search"
            headers = self.config.get_api_headers('firecrawl')
            
            payload = {
                "query": query,
                "pageOptions": {
                    "fetchPageContent": options.get('fetch_content', True) if options else True
                },
                "searchOptions": {
                    "limit": options.get('limit', 10) if options else 10
                }
            }
            
            response = self.session.post(
                firecrawl_url,
                json=payload,
                headers=headers,
                timeout=self.config.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "query": query,
                    "results": data.get('data', []),
                    "method": "firecrawl_search"
                }
            else:
                return {
                    "success": False,
                    "error": f"Search failed: HTTP {response.status_code}",
                    "query": query
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Search error: {str(e)}",
                "query": query
            }
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description from HTML"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '')
        
        meta_desc = soup.find('meta', attrs={'property': 'og:description'})
        if meta_desc:
            return meta_desc.get('content', '')
        
        return ""
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get current scraper capabilities"""
        return {
            "firecrawl_available": self.firecrawl_available,
            "basic_scraping": True,
            "batch_scraping": self.firecrawl_available,
            "ai_extraction": self.firecrawl_available,
            "web_search": self.firecrawl_available,
            "caching_enabled": self.config.ENABLE_CACHING,
            "rate_limiting": True
        }


# Utility functions for common extraction patterns
def extract_pricing_schema() -> Dict:
    """Standard schema for pricing extraction"""
    return {
        "pricing_tiers": "array",
        "free_tier_available": "boolean", 
        "enterprise_pricing": "string",
        "trial_period": "string",
        "currency": "string",
        "pricing_model": "string"
    }


def extract_company_schema() -> Dict:
    """Standard schema for company information extraction"""
    return {
        "company_name": "string",
        "founded_year": "string",
        "headquarters": "string",
        "employee_count": "string",
        "funding_info": "string",
        "leadership": "array",
        "business_model": "string"
    }


def extract_features_schema() -> Dict:
    """Standard schema for feature extraction"""
    return {
        "core_features": "array",
        "ai_features": "array", 
        "integrations": "array",
        "enterprise_features": "array",
        "api_available": "boolean"
    }