# tests/conftest.py - PyTest configuration and shared fixtures

import pytest
import os
import sys
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import tempfile
import shutil

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules under test
from config.free_apis_config import FreeAPIConfig
from utils.enhanced_web_scraper import EnhancedWebScraper


@pytest.fixture(scope="session")
def test_config():
    """Test configuration with mock API keys"""
    return {
        'GITHUB_TOKEN': 'test_github_token_123',
        'FIRECRAWL_API_KEY': 'test_firecrawl_key_456',
        'ALPHA_VANTAGE_API_KEY': 'test_alpha_vantage_789',
        'NEWS_API_KEY': 'test_news_api_012',
        'EXCHANGE_RATE_API_KEY': 'test_exchange_rate_345'
    }


@pytest.fixture(scope="session")
def mock_env_vars(test_config):
    """Mock environment variables for testing"""
    with patch.dict(os.environ, test_config):
        yield test_config


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_requests_response():
    """Mock requests response for API testing"""
    def _mock_response(status_code=200, json_data=None, text='', headers=None):
        mock_resp = Mock()
        mock_resp.status_code = status_code
        mock_resp.json.return_value = json_data or {}
        mock_resp.text = text
        mock_resp.headers = headers or {}
        mock_resp.content = text.encode() if isinstance(text, str) else text
        return mock_resp
    return _mock_response


@pytest.fixture
def sample_github_repo_data():
    """Sample GitHub repository data for testing"""
    return {
        "id": 123456789,
        "name": "test-repo",
        "full_name": "testuser/test-repo",
        "stargazers_count": 1500,
        "forks_count": 300,
        "watchers_count": 1500,
        "subscribers_count": 150,
        "open_issues_count": 25,
        "size": 5000,
        "network_count": 300,
        "created_at": "2020-01-15T10:30:00Z",
        "updated_at": "2024-01-15T15:45:00Z",
        "pushed_at": "2024-01-10T09:20:00Z",
        "default_branch": "main",
        "license": {"name": "MIT License"},
        "topics": ["ai", "python", "research"],
        "description": "Test repository for AI tool analysis",
        "homepage": "https://test-repo.example.com",
        "archived": False,
        "disabled": False,
        "fork": False,
        "language": "Python",
        "has_issues": True,
        "has_discussions": True,
        "has_wiki": True,
        "has_pages": False
    }


@pytest.fixture
def sample_github_contributors():
    """Sample GitHub contributors data"""
    return [
        {
            "login": "contributor1",
            "contributions": 150,
            "avatar_url": "https://avatars.githubusercontent.com/u/123?v=4",
            "html_url": "https://github.com/contributor1"
        },
        {
            "login": "contributor2", 
            "contributions": 75,
            "avatar_url": "https://avatars.githubusercontent.com/u/456?v=4",
            "html_url": "https://github.com/contributor2"
        }
    ]


@pytest.fixture
def sample_github_releases():
    """Sample GitHub releases data"""
    return [
        {
            "tag_name": "v2.1.0",
            "name": "Version 2.1.0",
            "published_at": "2024-01-01T12:00:00Z",
            "prerelease": False,
            "draft": False,
            "body": "Latest release with new features and bug fixes."
        },
        {
            "tag_name": "v2.0.0",
            "name": "Version 2.0.0", 
            "published_at": "2023-12-01T12:00:00Z",
            "prerelease": False,
            "draft": False,
            "body": "Major version update with breaking changes."
        }
    ]


@pytest.fixture
def sample_github_commits():
    """Sample GitHub commits data"""
    return [
        {
            "commit": {
                "author": {
                    "date": "2024-01-15T10:30:00Z"
                }
            },
            "author": {
                "login": "contributor1"
            }
        },
        {
            "commit": {
                "author": {
                    "date": "2024-01-10T15:20:00Z"
                }
            },
            "author": {
                "login": "contributor2"
            }
        }
    ]


@pytest.fixture
def sample_github_languages():
    """Sample GitHub languages data"""
    return {
        "Python": 75000,
        "JavaScript": 20000,
        "CSS": 3000,
        "HTML": 2000
    }


@pytest.fixture
def sample_pricing_page_content():
    """Sample pricing page HTML content"""
    return """
    <html>
    <head><title>Pricing - Test Tool</title></head>
    <body>
        <h1>Choose Your Plan</h1>
        <div class="pricing-tiers">
            <div class="tier">
                <h2>Free</h2>
                <p>$0/month</p>
                <ul class="features">
                    <li>Basic features</li>
                    <li>Limited usage</li>
                    <li>Community support</li>
                </ul>
            </div>
            <div class="tier">
                <h2>Pro</h2>
                <p>$29/month</p>
                <p>$290/year (save 17%)</p>
                <ul class="features">
                    <li>All basic features</li>
                    <li>Advanced analytics</li>
                    <li>Priority support</li>
                    <li>API access</li>
                </ul>
            </div>
            <div class="tier">
                <h2>Enterprise</h2>
                <p>Custom pricing</p>
                <p>Contact sales for details</p>
                <ul class="features">
                    <li>Everything in Pro</li>
                    <li>Custom integrations</li>
                    <li>Dedicated support</li>
                    <li>SLA guarantees</li>
                </ul>
            </div>
        </div>
        <p>All plans include a 14-day free trial</p>
        <p>30-day money-back guarantee</p>
    </body>
    </html>
    """


@pytest.fixture
def sample_company_page_content():
    """Sample company about page content"""
    return """
    <html>
    <head><title>About - Test Company</title></head>
    <body>
        <h1>About Test Company</h1>
        <p>Test Company was founded in 2019 and is headquartered in San Francisco, CA.</p>
        <p>We're a team of 50+ engineers and designers building the future of AI tools.</p>
        
        <h2>Leadership Team</h2>
        <div class="team">
            <div class="person">
                <h3>John Smith, CEO and Co-Founder</h3>
                <p>Former VP of Engineering at Google</p>
            </div>
            <div class="person">
                <h3>Jane Doe, CTO</h3>
                <p>Ex-Principal Engineer at Microsoft</p>
            </div>
        </div>
        
        <p>Follow us on social media:</p>
        <a href="https://twitter.com/testcompany">Twitter</a>
        <a href="https://linkedin.com/company/test-company">LinkedIn</a>
        <a href="https://github.com/testcompany">GitHub</a>
    </body>
    </html>
    """


@pytest.fixture
def sample_features_page_content():
    """Sample features page content"""
    return """
    <html>
    <head><title>Features - Test Tool</title></head>
    <body>
        <h1>Powerful Features</h1>
        
        <section class="core-features">
            <h2>Core Features</h2>
            <ul>
                <li>Real-time collaboration</li>
                <li>Advanced analytics dashboard</li>
                <li>Custom workflows</li>
                <li>Data export and import</li>
            </ul>
        </section>
        
        <section class="ai-features">
            <h2>AI-Powered Features</h2>
            <ul>
                <li>Intelligent recommendations</li>
                <li>Natural language processing</li>
                <li>Predictive analytics</li>
                <li>Smart automation</li>
            </ul>
        </section>
        
        <section class="integrations">
            <h2>Integrations</h2>
            <ul>
                <li>VS Code extension</li>
                <li>GitHub Actions integration</li>
                <li>Slack notifications</li>
                <li>REST API access</li>
            </ul>
        </section>
        
        <section class="enterprise">
            <h2>Enterprise Features</h2>
            <ul>
                <li>Single Sign-On (SSO)</li>
                <li>Role-based permissions</li>
                <li>Audit logs</li>
                <li>Priority support</li>
            </ul>
        </section>
    </body>
    </html>
    """


@pytest.fixture
def mock_firecrawl_response():
    """Mock Firecrawl API response"""
    def _create_response(url="https://example.com", content="Sample content", success=True):
        if success:
            return {
                "success": True,
                "data": {
                    "markdown": content,
                    "html": f"<html><body>{content}</body></html>",
                    "metadata": {
                        "title": "Test Page",
                        "description": "Test page description"
                    },
                    "links": [
                        {"href": "https://example.com/about", "text": "About"},
                        {"href": "https://example.com/pricing", "text": "Pricing"}
                    ],
                    "images": ["https://example.com/logo.png"]
                }
            }
        else:
            return {"success": False, "error": "Failed to scrape"}
    
    return _create_response


@pytest.fixture
def mock_alpha_vantage_response():
    """Mock Alpha Vantage API response"""
    return {
        "Global Quote": {
            "01. symbol": "AAPL",
            "02. open": "175.50",
            "03. high": "178.20",
            "04. low": "174.80",
            "05. price": "176.54",
            "06. volume": "45678910",
            "07. latest trading day": "2024-01-15",
            "08. previous close": "175.20",
            "09. change": "1.34",
            "10. change percent": "0.76%"
        }
    }


@pytest.fixture
def mock_news_api_response():
    """Mock News API response"""
    return {
        "status": "ok",
        "totalResults": 2,
        "articles": [
            {
                "source": {"name": "TechCrunch"},
                "author": "Test Author",
                "title": "Test Company Announces New AI Features",
                "description": "Test Company has announced new AI-powered features...",
                "url": "https://techcrunch.com/test-article",
                "publishedAt": "2024-01-15T10:00:00Z"
            },
            {
                "source": {"name": "VentureBeat"},
                "author": "Another Author", 
                "title": "Test Company Raises Series B Funding",
                "description": "Test Company has raised $50M in Series B funding...",
                "url": "https://venturebeat.com/test-article-2",
                "publishedAt": "2024-01-10T14:30:00Z"
            }
        ]
    }


@pytest.fixture
def mock_nominatim_response():
    """Mock Nominatim geocoding response"""
    return [
        {
            "lat": "37.7749",
            "lon": "-122.4194",
            "display_name": "San Francisco, California, United States",
            "address": {
                "city": "San Francisco",
                "state": "California",
                "country": "United States"
            }
        }
    ]


@pytest.fixture
def sample_tool_data():
    """Sample tool data for comprehensive testing"""
    return {
        "name": "Test AI Tool",
        "website_url": "https://test-tool.example.com",
        "github_url": "https://github.com/testuser/test-tool",
        "docs_url": "https://docs.test-tool.example.com",
        "company_name": "Test Company",
        "description": "A comprehensive AI tool for testing purposes"
    }


@pytest.fixture
def mock_web_scraper():
    """Mock enhanced web scraper for testing"""
    scraper = Mock(spec=EnhancedWebScraper)
    scraper.firecrawl_available = True
    
    def mock_scrape_url(url, options=None):
        return {
            "success": True,
            "url": url,
            "content": "Sample scraped content from " + url,
            "html": f"<html><body>Content from {url}</body></html>",
            "metadata": {"title": "Test Page"},
            "method": "firecrawl",
            "links": [],
            "images": []
        }
    
    scraper.scrape_url = mock_scrape_url
    return scraper


# Test markers for categorizing tests
def pytest_configure(config):
    """Configure custom test markers"""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test") 
    config.addinivalue_line("markers", "api: mark test as requiring API access")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "network: mark test as requiring network access")


# Auto-use fixtures for common setup
@pytest.fixture(autouse=True)
def setup_test_environment(mock_env_vars):
    """Automatically set up test environment for all tests"""
    # Clear any existing rate limiting data
    FreeAPIConfig._rate_limit_storage.clear()
    FreeAPIConfig._cache_storage.clear()
    
    # Ensure caching is enabled for tests
    FreeAPIConfig.ENABLE_CACHING = True
    
    yield
    
    # Cleanup after tests
    FreeAPIConfig._rate_limit_storage.clear()
    FreeAPIConfig._cache_storage.clear()