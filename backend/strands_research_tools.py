# strands_research_tools.py - Complete toolkit for AI tool research

from strands import tool
import requests
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import time
from bs4 import BeautifulSoup
import hashlib

# =============================================================================
# CORE RESEARCH TOOLS
# =============================================================================

@tool
def github_analyzer(repo_url: str) -> Dict:
    """
    Analyze GitHub repository for comprehensive metrics including:
    - Basic stats (stars, forks, issues)
    - Activity patterns and commit frequency
    - Contributors and community health
    - Technology stack and languages
    - Release patterns and versioning
    """
    try:
        # Extract owner/repo from URL
        match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
        if not match:
            return {"error": "Invalid GitHub URL format"}
        
        owner, repo = match.groups()
        repo = repo.replace('.git', '').split('?')[0]  # Clean repo name
        
        base_api = f"https://api.github.com/repos/{owner}/{repo}"
        headers = {"Accept": "application/vnd.github.v3+json"}
        
        # Add GitHub token if available for higher rate limits
        import os
        if os.getenv('GITHUB_TOKEN'):
            headers["Authorization"] = f"token {os.getenv('GITHUB_TOKEN')}"
        
        # Main repository data
        repo_response = requests.get(base_api, headers=headers)
        if repo_response.status_code != 200:
            return {"error": f"GitHub API error: {repo_response.status_code}"}
        
        repo_data = repo_response.json()
        
        # Contributors data
        contributors_response = requests.get(f"{base_api}/contributors", headers=headers)
        contributors = contributors_response.json() if contributors_response.status_code == 200 else []
        
        # Recent releases
        releases_response = requests.get(f"{base_api}/releases", headers=headers)
        releases = releases_response.json() if releases_response.status_code == 200 else []
        
        # Languages
        languages_response = requests.get(f"{base_api}/languages", headers=headers)
        languages = languages_response.json() if languages_response.status_code == 200 else {}
        
        # Recent commits (activity)
        commits_response = requests.get(f"{base_api}/commits?per_page=100", headers=headers)
        commits = commits_response.json() if commits_response.status_code == 200 else []
        
        # Analyze commit frequency (last 3 months)
        recent_commits = []
        cutoff_date = datetime.now() - timedelta(days=90)
        for commit in commits:
            try:
                commit_date = datetime.strptime(commit['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ')
                if commit_date > cutoff_date:
                    recent_commits.append(commit)
            except:
                continue
        
        return {
            "basic_stats": {
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "watchers": repo_data.get("watchers_count", 0),
                "open_issues": repo_data.get("open_issues_count", 0),
                "size_kb": repo_data.get("size", 0)
            },
            "repository_info": {
                "created_at": repo_data.get("created_at"),
                "last_updated": repo_data.get("updated_at"),
                "default_branch": repo_data.get("default_branch", "main"),
                "license": repo_data.get("license", {}).get("name") if repo_data.get("license") else None,
                "topics": repo_data.get("topics", []),
                "has_wiki": repo_data.get("has_wiki", False),
                "has_pages": repo_data.get("has_pages", False),
                "archived": repo_data.get("archived", False)
            },
            "activity_metrics": {
                "total_contributors": len(contributors),
                "commits_last_90_days": len(recent_commits),
                "avg_commits_per_week": len(recent_commits) / 13 if recent_commits else 0,
                "latest_release": releases[0].get("tag_name") if releases else None,
                "latest_release_date": releases[0].get("published_at") if releases else None,
                "total_releases": len(releases)
            },
            "technology_stack": {
                "primary_language": repo_data.get("language"),
                "languages": languages,
                "language_percentages": {lang: round((bytes_count / sum(languages.values())) * 100, 1) 
                                       for lang, bytes_count in languages.items()} if languages else {}
            },
            "community_health": {
                "has_readme": True,  # GitHub API doesn't directly provide this
                "has_contributing": repo_data.get("has_downloads", False),
                "has_code_of_conduct": False,  # Would need additional API call
                "issues_enabled": repo_data.get("has_issues", True),
                "discussions_enabled": repo_data.get("has_discussions", False)
            },
            "top_contributors": [
                {
                    "username": contrib.get("login"),
                    "contributions": contrib.get("contributions", 0),
                    "avatar_url": contrib.get("avatar_url")
                } for contrib in contributors[:10]
            ],
            "recent_releases": [
                {
                    "tag": release.get("tag_name"),
                    "name": release.get("name"),
                    "published_at": release.get("published_at"),
                    "prerelease": release.get("prerelease", False)
                } for release in releases[:5]
            ]
        }
        
    except Exception as e:
        return {"error": f"GitHub analysis failed: {str(e)}"}

@tool
def pricing_extractor(website_url: str) -> Dict:
    """
    Extract comprehensive pricing information from tool websites including:
    - Pricing tiers and monthly/annual costs
    - Free tier limitations and features
    - Enterprise pricing indicators
    - Trial periods and money-back guarantees
    - Usage-based pricing components
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Common pricing page paths to try
        pricing_paths = ['/pricing', '/price', '/plans', '/pricing-plans', '/cost', '/subscription']
        pricing_urls = [website_url.rstrip('/') + path for path in pricing_paths]
        pricing_urls.insert(0, website_url)  # Try main page first
        
        pricing_data = {
            "pricing_model": "unknown",
            "free_tier_available": False,
            "subscription_tiers": [],
            "enterprise_available": False,
            "trial_period_days": None,
            "pricing_currency": "USD",
            "usage_based_components": [],
            "money_back_guarantee": False,
            "annual_discount": False,
            "source_url": None
        }
        
        for url in pricing_urls:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    text_content = soup.get_text().lower()
                    
                    # Check if this looks like a pricing page
                    pricing_indicators = ['pricing', 'plans', 'price', '$', '€', '£', 'free', 'pro', 'enterprise', 'subscription']
                    if any(indicator in text_content for indicator in pricing_indicators):
                        pricing_data["source_url"] = url
                        
                        # Extract pricing model
                        if 'freemium' in text_content or ('free' in text_content and ('pro' in text_content or 'paid' in text_content)):
                            pricing_data["pricing_model"] = "freemium"
                        elif 'free' in text_content and 'trial' not in text_content:
                            pricing_data["pricing_model"] = "free"
                        elif 'subscription' in text_content or 'monthly' in text_content:
                            pricing_data["pricing_model"] = "subscription"
                        elif 'enterprise' in text_content and 'contact' in text_content:
                            pricing_data["pricing_model"] = "enterprise"
                        
                        # Check for free tier
                        if 'free forever' in text_content or 'free plan' in text_content or 'free tier' in text_content:
                            pricing_data["free_tier_available"] = True
                        
                        # Extract trial period
                        trial_match = re.search(r'(\d+)\s*day[s]?\s*(?:free\s*)?trial', text_content)
                        if trial_match:
                            pricing_data["trial_period_days"] = int(trial_match.group(1))
                        
                        # Check for enterprise tier
                        if 'enterprise' in text_content or 'custom pricing' in text_content:
                            pricing_data["enterprise_available"] = True
                        
                        # Check for money-back guarantee
                        if 'money back' in text_content or 'refund' in text_content:
                            pricing_data["money_back_guarantee"] = True
                        
                        # Check for annual discount
                        if 'annual' in text_content and ('discount' in text_content or 'save' in text_content):
                            pricing_data["annual_discount"] = True
                        
                        # Extract specific prices (basic regex patterns)
                        price_patterns = [
                            r'\$(\d+(?:\.\d{2})?)\s*(?:/\s*month|per\s*month|monthly)',
                            r'\$(\d+(?:\.\d{2})?)\s*(?:/\s*year|per\s*year|annually)',
                            r'(\d+(?:\.\d{2})?)\s*(?:USD|dollars?)\s*(?:/\s*month|per\s*month)',
                        ]
                        
                        prices_found = []
                        for pattern in price_patterns:
                            matches = re.findall(pattern, text_content, re.IGNORECASE)
                            for match in matches:
                                try:
                                    price = float(match)
                                    if 0 < price < 10000:  # Reasonable price range
                                        prices_found.append(price)
                                except:
                                    continue
                        
                        # Look for common tier structures
                        if prices_found:
                            unique_prices = sorted(list(set(prices_found)))
                            for i, price in enumerate(unique_prices):
                                tier_name = f"Tier {i+1}" if i > 0 else "Basic"
                                pricing_data["subscription_tiers"].append({
                                    "name": tier_name,
                                    "price_monthly": price,
                                    "features": [],
                                    "billing_period": "monthly"
                                })
                        
                        break  # Found pricing info, stop searching other URLs
                        
            except requests.RequestException:
                continue
        
        return pricing_data
        
    except Exception as e:
        return {"error": f"Pricing extraction failed: {str(e)}"}

@tool
def company_lookup(company_name: str, website_url: str = None) -> Dict:
    """
    Research comprehensive company information from multiple sources:
    - Basic company details (founding, location, size)
    - Funding history and financial data
    - Leadership team and key personnel
    - Business model and strategic focus
    - Recent news and developments
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        company_data = {
            "company_name": company_name,
            "website": website_url,
            "founded_year": None,
            "headquarters": None,
            "employee_count": None,
            "employee_count_source": None,
            "funding_info": {
                "total_funding": None,
                "latest_round": None,
                "funding_stage": None,
                "investors": []
            },
            "leadership": [],
            "business_model": None,
            "industry": "Software/AI",
            "stock_info": {
                "is_public": False,
                "stock_symbol": None,
                "market_cap": None
            },
            "recent_news": [],
            "social_presence": {}
        }
        
        # Try to get info from company website first
        if website_url:
            try:
                response = requests.get(website_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    text_content = soup.get_text().lower()
                    
                    # Look for founding year
                    founded_patterns = [
                        r'founded in (\d{4})',
                        r'established (\d{4})',
                        r'since (\d{4})',
                        r'started in (\d{4})'
                    ]
                    for pattern in founded_patterns:
                        match = re.search(pattern, text_content)
                        if match:
                            year = int(match.group(1))
                            if 1990 <= year <= datetime.now().year:
                                company_data["founded_year"] = year
                                break
                    
                    # Look for location info
                    location_patterns = [
                        r'based in ([^,\n\.]+)',
                        r'headquartered in ([^,\n\.]+)',
                        r'located in ([^,\n\.]+)'
                    ]
                    for pattern in location_patterns:
                        match = re.search(pattern, text_content)
                        if match:
                            location = match.group(1).strip()
                            if len(location) < 50:  # Reasonable location length
                                company_data["headquarters"] = location.title()
                                break
                    
                    # Try to find about/team pages
                    about_links = soup.find_all('a', href=re.compile(r'/(about|team|company|leadership)', re.I))
                    for link in about_links[:3]:  # Check first few about/team links
                        try:
                            about_url = urljoin(website_url, link.get('href'))
                            about_response = requests.get(about_url, headers=headers, timeout=5)
                            if about_response.status_code == 200:
                                about_soup = BeautifulSoup(about_response.content, 'html.parser')
                                about_text = about_soup.get_text()
                                
                                # Extract leadership info
                                leadership_patterns = [
                                    r'(CEO|Chief Executive Officer|Founder|Co-Founder|CTO|Chief Technology Officer)[:\s]+([A-Z][a-zA-Z\s]+)',
                                    r'([A-Z][a-zA-Z\s]+),?\s+(CEO|Chief Executive Officer|Founder|Co-Founder|CTO)'
                                ]
                                for pattern in leadership_patterns:
                                    matches = re.findall(pattern, about_text, re.MULTILINE)
                                    for match in matches:
                                        if len(match) == 2:
                                            title, name = match if len(match[0]) < len(match[1]) else (match[1], match[0])
                                            if len(name.strip()) > 2 and len(name.strip()) < 50:
                                                company_data["leadership"].append({
                                                    "name": name.strip(),
                                                    "title": title.strip(),
                                                    "source": "company_website"
                                                })
                                break
                        except:
                            continue
            except:
                pass
        
        return company_data
        
    except Exception as e:
        return {"error": f"Company lookup failed: {str(e)}"}

# Additional simplified tools for MVP
@tool  
def feature_extractor(website_url: str, docs_url: str = None) -> Dict:
    """Extract and categorize tool features"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; AI Research Bot)'}
        
        urls_to_check = [website_url]
        if docs_url:
            urls_to_check.append(docs_url)
        
        features = {
            "core_features": [],
            "ai_ml_features": [],
            "developer_experience": [],
            "integration_features": [],
            "enterprise_features": []
        }
        
        # Feature detection patterns
        feature_patterns = {
            "ai_ml_features": ["ai-powered", "machine learning", "artificial intelligence", "smart", "intelligent"],
            "developer_experience": ["user-friendly", "easy", "simple", "intuitive", "fast"],
            "integration_features": ["api", "integration", "plugin", "extension", "connects"],
            "enterprise_features": ["enterprise", "team", "collaboration", "security", "compliance"]
        }
        
        for url in urls_to_check:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    text_content = soup.get_text().lower()
                    
                    # Look for feature lists
                    feature_lists = soup.find_all(['ul', 'ol'], class_=re.compile(r'feature|benefit|capability', re.I))
                    for feature_list in feature_lists:
                        list_items = feature_list.find_all('li')
                        for item in list_items[:10]:  # Limit to avoid noise
                            item_text = item.get_text().strip()
                            if 10 < len(item_text) < 100:
                                # Categorize feature
                                categorized = False
                                for category, keywords in feature_patterns.items():
                                    if any(keyword in item_text.lower() for keyword in keywords):
                                        features[category].append({
                                            "feature_name": item_text,
                                            "feature_description": item_text,
                                            "is_core_feature": True
                                        })
                                        categorized = True
                                        break
                                
                                if not categorized:
                                    features["core_features"].append({
                                        "feature_name": item_text,
                                        "feature_description": item_text,
                                        "is_core_feature": True
                                    })
                    break
            except:
                continue
        
        return features
        
    except Exception as e:
        return {"error": f"Feature extraction failed: {str(e)}"}

@tool
def integration_detector(website_url: str, docs_url: str = None) -> Dict:
    """Detect tool integrations and ecosystem connections"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; AI Research Bot)'}
        
        integrations = {
            "ide_integrations": [],
            "cicd_integrations": [],
            "cloud_integrations": [],
            "development_tools": [],
            "api_available": False
        }
        
        urls_to_check = [website_url]
        if docs_url:
            urls_to_check.append(docs_url)
        
        # Integration patterns
        integration_patterns = {
            "ide_integrations": ["vs code", "visual studio", "intellij", "pycharm", "webstorm"],
            "cicd_integrations": ["github actions", "gitlab ci", "jenkins", "circleci"],
            "cloud_integrations": ["aws", "azure", "google cloud", "vercel", "netlify"],
            "development_tools": ["docker", "kubernetes", "git", "npm"]
        }
        
        for url in urls_to_check:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    text_content = soup.get_text().lower()
                    
                    # Check for API availability
                    if 'api' in text_content or 'rest' in text_content:
                        integrations["api_available"] = True
                    
                    # Detect integrations
                    for category, keywords in integration_patterns.items():
                        for keyword in keywords:
                            if keyword in text_content:
                                integrations[category].append({
                                    "integration_name": keyword.title(),
                                    "integration_type": "native" if "native" in text_content else "plugin"
                                })
                    break
            except:
                continue
        
        return integrations
        
    except Exception as e:
        return {"error": f"Integration detection failed: {str(e)}"}

# Utility function to get all research tools
def get_all_research_tools():
    """Return all available research tools for the Strands Agent"""
    return [
        github_analyzer,
        pricing_extractor, 
        company_lookup,
        feature_extractor,
        integration_detector
    ]

def create_comprehensive_research_agent():
    """Create a Strands Agent with all research tools"""
    from strands import Agent
    from strands.models import BedrockModel
    from strands_tools import http_request, python
    
    model = BedrockModel(
        model_id="us.anthropic.claude-3-7-sonnet-20241109-v1:0",
        temperature=0.1
    )
    
    all_tools = [http_request, python] + get_all_research_tools()
    
    agent = Agent(
        model=model,
        tools=all_tools,
        system_prompt="""You are a comprehensive AI tool research specialist with access to specialized research tools.
        
        When researching a tool, systematically use the available tools:
        1. github_analyzer - for repository metrics and activity (if GitHub URL available)
        2. pricing_extractor - for pricing and subscription information  
        3. company_lookup - for company background and team info
        4. feature_extractor - for comprehensive feature analysis
        5. integration_detector - for ecosystem and integration analysis
        
        Always provide structured, comprehensive reports with confidence scores and cite sources when possible."""
    )
    
    return agent
