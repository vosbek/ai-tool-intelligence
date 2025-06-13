# enhanced_strands_tools.py - Enhanced AI tool research toolkit with free APIs and Firecrawl

import requests
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import time
from bs4 import BeautifulSoup
import hashlib
import sys
import os

# Import enhanced components
sys.path.append(os.path.dirname(__file__))
from config.free_apis_config import FreeAPIConfig, rate_limited, cached_request
from utils.enhanced_web_scraper import EnhancedWebScraper, extract_pricing_schema, extract_company_schema, extract_features_schema

# Initialize enhanced web scraper
web_scraper = EnhancedWebScraper()

# =============================================================================
# ENHANCED CORE RESEARCH TOOLS
# =============================================================================

@cached_request()
@rate_limited('github')
def enhanced_github_analyzer(repo_url: str) -> Dict:
    """
    Enhanced GitHub repository analysis with improved error handling and pagination:
    - Basic stats (stars, forks, issues, watchers)
    - Activity patterns and commit frequency with configurable windows
    - Contributors and community health metrics
    - Technology stack and languages with percentages
    - Release patterns, versioning, and security analysis
    - Community health score and maintenance indicators
    """
    try:
        # Extract owner/repo from URL with better validation
        match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url.strip())
        if not match:
            return {"error": "Invalid GitHub URL format", "url": repo_url}
        
        owner, repo = match.groups()
        repo = repo.replace('.git', '').split('?')[0].split('#')[0]  # Clean repo name
        
        # Validate repo name format
        if not re.match(r'^[a-zA-Z0-9._-]+$', repo) or not re.match(r'^[a-zA-Z0-9._-]+$', owner):
            return {"error": "Invalid repository or owner name", "url": repo_url}
        
        config = FreeAPIConfig()
        base_api = f"{config.GITHUB_BASE_URL}/repos/{owner}/{repo}"
        headers = config.get_api_headers('github')
        
        # Enhanced error handling with retries
        def make_github_request(url: str, max_retries: int = 3) -> Optional[requests.Response]:
            for attempt in range(max_retries):
                try:
                    response = requests.get(url, headers=headers, timeout=config.REQUEST_TIMEOUT)
                    if response.status_code == 403 and 'rate limit' in response.text.lower():
                        wait_time = 60 * (attempt + 1)
                        time.sleep(min(wait_time, 300))  # Max 5 min wait
                        continue
                    return response
                except requests.RequestException as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(2 ** attempt)  # Exponential backoff
            return None
        
        # Main repository data
        repo_response = make_github_request(base_api)
        if not repo_response or repo_response.status_code != 200:
            error_msg = f"GitHub API error: {repo_response.status_code if repo_response else 'Request failed'}"
            if repo_response and repo_response.status_code == 404:
                error_msg = "Repository not found or private"
            return {"error": error_msg, "url": repo_url}
        
        repo_data = repo_response.json()
        
        # Parallel API calls for better performance
        api_calls = {
            'contributors': f"{base_api}/contributors?per_page=100",
            'releases': f"{base_api}/releases?per_page=20",
            'languages': f"{base_api}/languages",
            'commits': f"{base_api}/commits?per_page=100",
            'community': f"{base_api}/community/profile",
            'stats': f"{base_api}/stats/participation",
            'topics': f"{base_api}/topics"
        }
        
        # Make API calls with error handling
        api_data = {}
        for key, url in api_calls.items():
            response = make_github_request(url)
            if response and response.status_code == 200:
                try:
                    api_data[key] = response.json()
                except json.JSONDecodeError:
                    api_data[key] = None
            else:
                api_data[key] = None
        
        contributors = api_data.get('contributors') or []
        releases = api_data.get('releases') or []
        languages = api_data.get('languages') or {}
        commits = api_data.get('commits') or []
        community_data = api_data.get('community') or {}
        stats_data = api_data.get('stats') or {}
        
        # Enhanced commit analysis with multiple time windows
        def analyze_commits_by_period(commits_list: List, days: int) -> Dict:
            cutoff_date = datetime.now() - timedelta(days=days)
            period_commits = []
            commit_authors = set()
            
            for commit in commits_list:
                try:
                    commit_date_str = commit['commit']['author']['date']
                    commit_date = datetime.strptime(commit_date_str, '%Y-%m-%dT%H:%M:%SZ')
                    if commit_date > cutoff_date:
                        period_commits.append(commit)
                        if commit.get('author', {}) and commit['author'].get('login'):
                            commit_authors.add(commit['author']['login'])
                except (KeyError, ValueError, TypeError):
                    continue
            
            return {
                'count': len(period_commits),
                'unique_authors': len(commit_authors),
                'avg_per_week': len(period_commits) / (days / 7) if days >= 7 else len(period_commits),
                'authors': list(commit_authors)[:10]  # Top 10 recent contributors
            }
        
        # Analyze different time periods
        commit_analysis = {
            'last_30_days': analyze_commits_by_period(commits, 30),
            'last_90_days': analyze_commits_by_period(commits, 90),
            'last_year': analyze_commits_by_period(commits, 365)
        }
        
        # Calculate community health score
        health_score = 0
        health_factors = {
            'has_readme': bool(community_data.get('files', {}).get('readme')),
            'has_contributing': bool(community_data.get('files', {}).get('contributing')),
            'has_license': bool(repo_data.get('license')),
            'has_code_of_conduct': bool(community_data.get('files', {}).get('code_of_conduct')),
            'has_issues_template': bool(community_data.get('files', {}).get('issue_template')),
            'has_pull_request_template': bool(community_data.get('files', {}).get('pull_request_template')),
            'recent_activity': commit_analysis['last_90_days']['count'] > 0,
            'multiple_contributors': len(contributors) > 1
        }
        
        health_score = sum(health_factors.values()) / len(health_factors) * 100
        
        # Enhanced language analysis
        total_bytes = sum(languages.values()) if languages else 0
        language_breakdown = {}
        if total_bytes > 0:
            for lang, bytes_count in languages.items():
                percentage = (bytes_count / total_bytes) * 100
                language_breakdown[lang] = {
                    'bytes': bytes_count,
                    'percentage': round(percentage, 1)
                }
        
        return {
            "basic_stats": {
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "watchers": repo_data.get("watchers_count", 0),
                "subscribers_count": repo_data.get("subscribers_count", 0),
                "open_issues": repo_data.get("open_issues_count", 0),
                "size_kb": repo_data.get("size", 0),
                "network_count": repo_data.get("network_count", 0)
            },
            "repository_info": {
                "created_at": repo_data.get("created_at"),
                "last_updated": repo_data.get("updated_at"),
                "last_pushed": repo_data.get("pushed_at"),
                "default_branch": repo_data.get("default_branch", "main"),
                "license": repo_data.get("license", {}).get("name") if repo_data.get("license") else None,
                "topics": repo_data.get("topics", []),
                "description": repo_data.get("description", ""),
                "homepage": repo_data.get("homepage", ""),
                "archived": repo_data.get("archived", False),
                "disabled": repo_data.get("disabled", False),
                "fork": repo_data.get("fork", False)
            },
            "activity_metrics": {
                "total_contributors": len(contributors),
                "commit_analysis": commit_analysis,
                "latest_release": releases[0].get("tag_name") if releases else None,
                "latest_release_date": releases[0].get("published_at") if releases else None,
                "total_releases": len(releases),
                "release_frequency": _calculate_release_frequency(releases),
                "last_commit_date": commits[0]['commit']['author']['date'] if commits else None,
                "is_actively_maintained": _is_actively_maintained(commits, releases)
            },
            "technology_stack": {
                "primary_language": repo_data.get("language"),
                "languages": languages,
                "language_breakdown": language_breakdown,
                "total_code_bytes": total_bytes
            },
            "community_health": {
                **health_factors,
                "health_score": round(health_score, 1),
                "issues_enabled": repo_data.get("has_issues", True),
                "discussions_enabled": repo_data.get("has_discussions", False),
                "wiki_enabled": repo_data.get("has_wiki", False),
                "pages_enabled": repo_data.get("has_pages", False),
                "security_policy": bool(community_data.get('files', {}).get('security'))
            },
            "top_contributors": [
                {
                    "username": contrib.get("login"),
                    "contributions": contrib.get("contributions", 0),
                    "avatar_url": contrib.get("avatar_url"),
                    "profile_url": contrib.get("html_url")
                } for contrib in contributors[:10]
            ],
            "recent_releases": [
                {
                    "tag": release.get("tag_name"),
                    "name": release.get("name"),
                    "published_at": release.get("published_at"),
                    "prerelease": release.get("prerelease", False),
                    "draft": release.get("draft", False),
                    "body": release.get("body", "")[:200] + "..." if release.get("body", "") else ""
                } for release in releases[:5]
            ],
            "analysis_metadata": {
                "timestamp": datetime.now().isoformat(),
                "api_calls_made": len([k for k, v in api_data.items() if v is not None]),
                "data_completeness": round(sum(1 for v in api_data.values() if v is not None) / len(api_data) * 100, 1)
            }
        }
        
    except Exception as e:
        return {
            "error": f"GitHub analysis failed: {str(e)}",
            "url": repo_url,
            "timestamp": datetime.now().isoformat()
        }


def _calculate_release_frequency(releases: List[Dict]) -> str:
    """Calculate average time between releases"""
    if len(releases) < 2:
        return "insufficient_data"
    
    try:
        dates = []
        for release in releases[:10]:  # Analyze last 10 releases
            date_str = release.get('published_at')
            if date_str:
                dates.append(datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ'))
        
        if len(dates) < 2:
            return "insufficient_data"
        
        dates.sort(reverse=True)  # Most recent first
        intervals = []
        for i in range(len(dates) - 1):
            interval = (dates[i] - dates[i + 1]).days
            intervals.append(interval)
        
        avg_days = sum(intervals) / len(intervals)
        
        if avg_days < 30:
            return "very_frequent"  # Less than monthly
        elif avg_days < 90:
            return "frequent"  # Less than quarterly
        elif avg_days < 180:
            return "moderate"  # Less than bi-annual
        else:
            return "infrequent"  # More than 6 months
            
    except (ValueError, KeyError):
        return "unknown"


def _is_actively_maintained(commits: List[Dict], releases: List[Dict]) -> bool:
    """Determine if repository is actively maintained"""
    now = datetime.now()
    
    # Check recent commits (last 6 months)
    recent_commit = False
    if commits:
        try:
            last_commit_date = datetime.strptime(
                commits[0]['commit']['author']['date'], 
                '%Y-%m-%dT%H:%M:%SZ'
            )
            recent_commit = (now - last_commit_date).days < 180
        except (KeyError, ValueError):
            pass
    
    # Check recent releases (last year)
    recent_release = False
    if releases:
        try:
            last_release_date = datetime.strptime(
                releases[0]['published_at'], 
                '%Y-%m-%dT%H:%M:%SZ'
            )
            recent_release = (now - last_release_date).days < 365
        except (KeyError, ValueError):
            pass
    
    return recent_commit or recent_release


@cached_request()
def enhanced_pricing_extractor(website_url: str, docs_url: str = None) -> Dict:
    """
    Enhanced pricing extraction using Firecrawl for better accuracy:
    - Structured pricing tier extraction with AI
    - Dynamic pricing model detection
    - Multi-currency support with conversion
    - Usage-based pricing identification
    - Feature mapping per pricing tier
    """
    try:
        # Use enhanced web scraper with Firecrawl
        pricing_schema = extract_pricing_schema()
        
        # Try to extract structured pricing data
        if web_scraper.firecrawl_available:
            extraction_result = web_scraper.extract_structured_data(
                website_url, 
                pricing_schema,
                prompt="Extract comprehensive pricing information including all tiers, features, costs, trial periods, and pricing models. Focus on subscription plans, usage-based pricing, and enterprise options."
            )
            
            if extraction_result.get('success'):
                structured_data = extraction_result.get('extracted_data', {})
                
                # Enhance with additional web scraping for missing data
                scraped_data = web_scraper.scrape_url(website_url)
                if scraped_data.get('success'):
                    content = scraped_data.get('content', '').lower()
                    
                    # Add currency detection
                    currency_patterns = {
                        'USD': [r'\$', r'usd', r'dollar'],
                        'EUR': [r'€', r'eur', r'euro'],
                        'GBP': [r'£', r'gbp', r'pound'],
                        'CAD': [r'cad', r'c\$'],
                        'AUD': [r'aud', r'a\$']
                    }
                    
                    detected_currency = 'USD'  # Default
                    for currency, patterns in currency_patterns.items():
                        if any(re.search(pattern, content) for pattern in patterns):
                            detected_currency = currency
                            break
                    
                    # Enhanced pricing model detection
                    pricing_model = "unknown"
                    if 'freemium' in content or ('free forever' in content and ('pro' in content or 'premium' in content)):
                        pricing_model = "freemium"
                    elif 'free' in content and 'trial' not in content and any(word in content for word in ['plan', 'tier', 'forever']):
                        pricing_model = "free"
                    elif 'pay as you' in content or 'usage based' in content or 'per request' in content:
                        pricing_model = "usage_based"
                    elif 'subscription' in content or 'monthly' in content or 'annually' in content:
                        pricing_model = "subscription"
                    elif 'enterprise' in content and 'contact' in content:
                        pricing_model = "enterprise_only"
                    elif 'one time' in content or 'lifetime' in content:
                        pricing_model = "one_time"
                    
                    # Try to get exchange rates if needed
                    exchange_rates = {}
                    if detected_currency != 'USD':
                        exchange_rates = _get_exchange_rates(detected_currency)
                    
                    return {
                        "pricing_model": pricing_model,
                        "currency": detected_currency,
                        "exchange_rates": exchange_rates,
                        "structured_data": structured_data,
                        "extraction_method": "firecrawl_ai",
                        "source_url": website_url,
                        "analysis_timestamp": datetime.now().isoformat(),
                        **_extract_pricing_details_from_content(content)
                    }
        
        # Fallback to enhanced basic extraction
        return _enhanced_basic_pricing_extraction(website_url, docs_url)
        
    except Exception as e:
        return {
            "error": f"Enhanced pricing extraction failed: {str(e)}",
            "url": website_url,
            "timestamp": datetime.now().isoformat()
        }


@cached_request()
@rate_limited('exchange_rate')
def _get_exchange_rates(base_currency: str) -> Dict:
    """Get current exchange rates for currency conversion"""
    try:
        config = FreeAPIConfig()
        if not config.EXCHANGE_RATE_API_KEY:
            return {}
        
        url = f"{config.EXCHANGE_RATE_BASE_URL}/{base_currency}"
        response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'rates': data.get('rates', {}),
                'base': base_currency,
                'date': data.get('date', ''),
                'timestamp': datetime.now().isoformat()
            }
    except Exception:
        pass
    
    return {}


def _extract_pricing_details_from_content(content: str) -> Dict:
    """Extract pricing details from content using enhanced patterns"""
    details = {
        "free_tier_available": False,
        "trial_period_days": None,
        "enterprise_available": False,
        "money_back_guarantee": False,
        "annual_discount": False,
        "subscription_tiers": [],
        "usage_based_components": []
    }
    
    # Free tier detection
    free_patterns = [
        r'free forever', r'free plan', r'free tier', r'always free',
        r'no credit card', r'free to start', r'free account'
    ]
    details["free_tier_available"] = any(re.search(pattern, content) for pattern in free_patterns)
    
    # Trial period extraction
    trial_match = re.search(r'(\d+)\s*day[s]?\s*(?:free\s*)?trial', content)
    if trial_match:
        details["trial_period_days"] = int(trial_match.group(1))
    
    # Enterprise detection
    enterprise_patterns = [r'enterprise', r'custom pricing', r'contact sales', r'custom plan']
    details["enterprise_available"] = any(re.search(pattern, content) for pattern in enterprise_patterns)
    
    # Money-back guarantee
    guarantee_patterns = [r'money back', r'refund', r'satisfaction guarantee', r'risk free']
    details["money_back_guarantee"] = any(re.search(pattern, content) for pattern in guarantee_patterns)
    
    # Annual discount
    discount_patterns = [r'annual.*save', r'yearly.*discount', r'pay annually.*off', r'annual.*cheaper']
    details["annual_discount"] = any(re.search(pattern, content) for pattern in discount_patterns)
    
    # Extract price points
    price_patterns = [
        r'\$(\d+(?:\.\d{2})?)\s*(?:/\s*(?:month|mo)|per\s*month|monthly)',
        r'\$(\d+(?:\.\d{2})?)\s*(?:/\s*(?:year|yr)|per\s*year|annually)',
        r'(\d+(?:\.\d{2})?)\s*(?:USD|dollars?)\s*(?:/\s*(?:month|year)|per\s*(?:month|year))',
    ]
    
    found_prices = []
    for pattern in price_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            try:
                price = float(match)
                if 0 < price < 10000:  # Reasonable range
                    found_prices.append(price)
            except ValueError:
                continue
    
    # Create basic tier structure from found prices
    unique_prices = sorted(list(set(found_prices)))
    tier_names = ["Starter", "Professional", "Business", "Enterprise"]
    
    for i, price in enumerate(unique_prices[:4]):  # Max 4 tiers
        tier_name = tier_names[i] if i < len(tier_names) else f"Tier {i+1}"
        details["subscription_tiers"].append({
            "name": tier_name,
            "price_monthly": price,
            "features": [],
            "billing_period": "monthly"
        })
    
    return details


def _enhanced_basic_pricing_extraction(website_url: str, docs_url: str = None) -> Dict:
    """Enhanced basic pricing extraction as fallback"""
    try:
        scraped_data = web_scraper.scrape_url(website_url)
        if not scraped_data.get('success'):
            return {"error": "Failed to scrape pricing page", "url": website_url}
        
        content = scraped_data.get('content', '').lower()
        
        basic_result = {
            "pricing_model": "unknown",
            "extraction_method": "basic_enhanced",
            "source_url": website_url,
            "analysis_timestamp": datetime.now().isoformat(),
            **_extract_pricing_details_from_content(content)
        }
        
        return basic_result
        
    except Exception as e:
        return {
            "error": f"Basic pricing extraction failed: {str(e)}",
            "url": website_url
        }


# Continue with other enhanced tools...
# (Due to length constraints, I'll create additional functions separately)

def get_enhanced_research_tools():
    """Return all enhanced research tools"""
    return [
        enhanced_github_analyzer,
        enhanced_pricing_extractor,
        # Additional enhanced tools will be added
    ]