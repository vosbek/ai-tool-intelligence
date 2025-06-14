# enhanced_tools_additional.py - Additional enhanced tools (company lookup, features, integrations)

import requests
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import time
from bs4 import BeautifulSoup
import sys
import os

# Import enhanced components
sys.path.append(os.path.dirname(__file__))
from config.free_apis_config import FreeAPIConfig, rate_limited, cached_request
from ...utils.web_scraper import EnhancedWebScraper, extract_company_schema, extract_features_schema

# Initialize enhanced web scraper
web_scraper = EnhancedWebScraper()

@cached_request()
def enhanced_company_lookup(company_name: str, website_url: str = None) -> Dict:
    """
    Enhanced company research using multiple free sources and Firecrawl:
    - Basic company details from website and public sources
    - Geocoded location data using Nominatim
    - Social media presence analysis
    - Recent news using News API (if available)
    - Stock information using Alpha Vantage (if public company)
    - Enhanced leadership extraction using AI
    """
    try:
        config = FreeAPIConfig()
        
        company_data = {
            "company_name": company_name,
            "website": website_url,
            "founded_year": None,
            "headquarters": None,
            "headquarters_coordinates": None,
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
                "current_price": None,
                "market_cap": None
            },
            "recent_news": [],
            "social_presence": {},
            "analysis_metadata": {
                "timestamp": datetime.now().isoformat(),
                "data_sources_used": [],
                "data_completeness": 0
            }
        }
        
        data_sources_used = []
        
        # 1. Enhanced website analysis using Firecrawl
        if website_url:
            if web_scraper.firecrawl_available:
                company_schema = extract_company_schema()
                extraction_result = web_scraper.extract_structured_data(
                    website_url,
                    company_schema,
                    prompt=f"Extract comprehensive information about {company_name} including founding details, leadership team, location, employee count, business model, and company history."
                )
                
                if extraction_result.get('success'):
                    structured_data = extraction_result.get('extracted_data', {})
                    
                    # Merge structured data
                    for key, value in structured_data.items():
                        if value and key in company_data:
                            company_data[key] = value
                    
                    data_sources_used.append('firecrawl_ai_extraction')
                
            # Fallback to basic website scraping
            scraped_data = web_scraper.scrape_url(website_url)
            if scraped_data.get('success'):
                content = scraped_data.get('content', '').lower()
                company_data.update(_extract_company_details_from_content(content, company_name))
                data_sources_used.append('website_scraping')
                
                # Try to find about/team pages for more detailed info
                links = scraped_data.get('links', [])
                about_urls = [
                    link['href'] for link in links 
                    if any(keyword in link['text'].lower() for keyword in ['about', 'team', 'company', 'leadership', 'founders'])
                ][:3]  # Limit to top 3
                
                for about_url in about_urls:
                    try:
                        about_data = web_scraper.scrape_url(about_url)
                        if about_data.get('success'):
                            about_content = about_data.get('content', '')
                            leadership_info = _extract_leadership_from_content(about_content)
                            if leadership_info:
                                company_data['leadership'].extend(leadership_info)
                            data_sources_used.append('about_page_scraping')
                    except Exception:
                        continue
        
        # 2. Geocoding headquarters if location found
        if company_data.get('headquarters'):
            coordinates = _geocode_location(company_data['headquarters'])
            if coordinates:
                company_data['headquarters_coordinates'] = coordinates
                data_sources_used.append('nominatim_geocoding')
        
        # 3. Stock information lookup (if Alpha Vantage available)
        stock_symbol = _detect_stock_symbol(company_name, company_data.get('headquarters', ''))
        if stock_symbol and config.ALPHA_VANTAGE_API_KEY:
            stock_info = _get_stock_information(stock_symbol)
            if stock_info:
                company_data['stock_info'].update(stock_info)
                company_data['stock_info']['is_public'] = True
                company_data['stock_info']['stock_symbol'] = stock_symbol
                data_sources_used.append('alpha_vantage_stock')
        
        # 4. Recent news lookup (if News API available)
        if config.NEWS_API_KEY:
            news_data = _get_company_news(company_name)
            if news_data:
                company_data['recent_news'] = news_data
                data_sources_used.append('news_api')
        
        # 5. Social media presence detection
        social_presence = _detect_social_presence(company_name, website_url)
        if social_presence:
            company_data['social_presence'] = social_presence
            data_sources_used.append('social_media_detection')
        
        # 6. Calculate data completeness score
        completeness_fields = [
            'founded_year', 'headquarters', 'employee_count', 'leadership',
            'business_model', 'stock_info', 'recent_news'
        ]
        
        filled_fields = sum(1 for field in completeness_fields if company_data.get(field))
        completeness_score = (filled_fields / len(completeness_fields)) * 100
        
        company_data['analysis_metadata']['data_sources_used'] = data_sources_used
        company_data['analysis_metadata']['data_completeness'] = round(completeness_score, 1)
        
        return company_data
        
    except Exception as e:
        return {
            "error": f"Enhanced company lookup failed: {str(e)}",
            "company_name": company_name,
            "timestamp": datetime.now().isoformat()
        }


def _extract_company_details_from_content(content: str, company_name: str) -> Dict:
    """Extract company details from web content using enhanced patterns"""
    details = {}
    
    # Founded year patterns
    founded_patterns = [
        rf'{re.escape(company_name.lower())}.*?(?:founded|established|started|launched).*?(\d{{4}})',
        r'(?:founded|established|started|launched).*?(?:in\s+)?(\d{4})',
        r'since\s+(\d{4})',
        r'(\d{4}).*?(?:founded|established|started)'
    ]
    
    for pattern in founded_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            year = int(match.group(1))
            if 1950 <= year <= datetime.now().year:
                details['founded_year'] = year
                break
    
    # Location patterns
    location_patterns = [
        r'(?:based|located|headquartered)\s+(?:in\s+)?([^,\n.]{5,50})',
        r'headquarters[:\s]+([^,\n.]{5,50})',
        r'(?:from|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2,})',  # City, State/Country
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            if 5 <= len(location) <= 50:  # Reasonable location length
                details['headquarters'] = location
                break
    
    # Employee count patterns
    employee_patterns = [
        r'(\d+(?:,\d+)*)\s+(?:employees?|team members?|people)',
        r'(?:team of|staff of|over)\s+(\d+(?:,\d+)*)',
        r'(\d+(?:,\d+)*)\+?\s+(?:strong|member) team'
    ]
    
    for pattern in employee_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            count_str = match.group(1).replace(',', '')
            try:
                count = int(count_str)
                if 1 <= count <= 1000000:  # Reasonable range
                    details['employee_count'] = count
                    details['employee_count_source'] = 'website'
                    break
            except ValueError:
                continue
    
    # Business model detection
    business_model_keywords = {
        'SaaS': ['software as a service', 'saas', 'subscription', 'cloud-based'],
        'B2B': ['business to business', 'b2b', 'enterprise', 'corporate'],
        'B2C': ['business to consumer', 'b2c', 'consumer', 'individual'],
        'Marketplace': ['marketplace', 'platform', 'connect buyers', 'connect sellers'],
        'API': ['api', 'application programming interface', 'developers'],
        'Open Source': ['open source', 'opensource', 'free software', 'github'],
        'Freemium': ['freemium', 'free tier', 'free plan', 'upgrade to premium']
    }
    
    for model, keywords in business_model_keywords.items():
        if any(keyword in content for keyword in keywords):
            details['business_model'] = model
            break
    
    return details


def _extract_leadership_from_content(content: str) -> List[Dict]:
    """Extract leadership information from content"""
    leadership = []
    
    # Enhanced leadership patterns
    patterns = [
        r'((?:CEO|Chief Executive Officer|Founder|Co-?Founder|CTO|Chief Technology Officer|CPO|Chief Product Officer|COO|Chief Operating Officer|CFO|Chief Financial Officer)[:\s,]+)([A-Z][a-zA-Z\s\-\']{2,40})',
        r'([A-Z][a-zA-Z\s\-\']{2,40})[,\s]+((?:CEO|Chief Executive Officer|Founder|Co-?Founder|CTO|Chief Technology Officer|CPO|Chief Product Officer|COO|Chief Operating Officer|CFO|Chief Financial Officer))',
        r'([A-Z][a-zA-Z\s\-\']{2,40})\s*-\s*((?:CEO|Founder|CTO|CPO|COO|CFO))',
    ]
    
    found_people = set()  # Avoid duplicates
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            if len(match) == 2:
                # Determine which is name and which is title
                part1, part2 = match
                
                title_keywords = ['ceo', 'cto', 'cfo', 'coo', 'cpo', 'founder', 'chief']
                if any(keyword in part1.lower() for keyword in title_keywords):
                    title, name = part1, part2
                else:
                    name, title = part1, part2
                
                name = name.strip()
                title = title.strip()
                
                # Validate name (should be reasonable length and format)
                if (2 < len(name) < 40 and 
                    len(name.split()) >= 2 and 
                    name not in found_people and
                    not any(char.isdigit() for char in name)):
                    
                    leadership.append({
                        "name": name,
                        "title": title,
                        "source": "website_content"
                    })
                    found_people.add(name)
    
    return leadership[:10]  # Limit to 10 people


@cached_request()
@rate_limited('nominatim')
def _geocode_location(location: str) -> Optional[Dict]:
    """Geocode location using Nominatim (free OpenStreetMap service)"""
    try:
        config = FreeAPIConfig()
        url = f"{config.NOMINATIM_BASE_URL}/search"
        
        params = {
            'q': location,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1
        }
        
        headers = {'User-Agent': config.NOMINATIM_USER_AGENT}
        
        response = requests.get(url, params=params, headers=headers, timeout=config.REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                result = data[0]
                return {
                    'latitude': float(result.get('lat', 0)),
                    'longitude': float(result.get('lon', 0)),
                    'display_name': result.get('display_name', ''),
                    'country': result.get('address', {}).get('country', ''),
                    'city': result.get('address', {}).get('city', ''),
                    'state': result.get('address', {}).get('state', '')
                }
    except Exception:
        pass
    
    return None


def _detect_stock_symbol(company_name: str, headquarters: str = '') -> Optional[str]:
    """Detect potential stock symbol for public companies"""
    # Common patterns for stock symbols
    # This is a simplified detection - in practice, you'd use a financial data API
    
    known_symbols = {
        'microsoft': 'MSFT',
        'apple': 'AAPL',
        'google': 'GOOGL',
        'alphabet': 'GOOGL',
        'amazon': 'AMZN',
        'meta': 'META',
        'facebook': 'META',
        'tesla': 'TSLA',
        'netflix': 'NFLX',
        'adobe': 'ADBE',
        'salesforce': 'CRM',
        'nvidia': 'NVDA',
        'intel': 'INTC',
        'oracle': 'ORCL',
        'ibm': 'IBM',
        'cisco': 'CSCO'
    }
    
    company_lower = company_name.lower()
    for company, symbol in known_symbols.items():
        if company in company_lower:
            return symbol
    
    return None


@cached_request()
@rate_limited('alpha_vantage')
def _get_stock_information(symbol: str) -> Optional[Dict]:
    """Get stock information using Alpha Vantage free API"""
    try:
        config = FreeAPIConfig()
        if not config.ALPHA_VANTAGE_API_KEY:
            return None
        
        url = config.ALPHA_VANTAGE_BASE_URL
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': config.ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            quote = data.get('Global Quote', {})
            
            if quote:
                return {
                    'current_price': float(quote.get('05. price', 0)),
                    'change': quote.get('09. change', ''),
                    'change_percent': quote.get('10. change percent', ''),
                    'volume': quote.get('06. volume', ''),
                    'latest_trading_day': quote.get('07. latest trading day', ''),
                    'previous_close': float(quote.get('08. previous close', 0)),
                    'open': float(quote.get('02. open', 0)),
                    'high': float(quote.get('03. high', 0)),
                    'low': float(quote.get('04. low', 0))
                }
    except Exception:
        pass
    
    return None


@cached_request()
@rate_limited('news_api')
def _get_company_news(company_name: str) -> List[Dict]:
    """Get recent company news using News API free tier"""
    try:
        config = FreeAPIConfig()
        if not config.NEWS_API_KEY:
            return []
        
        url = f"{config.NEWS_API_BASE_URL}/everything"
        params = {
            'q': f'"{company_name}"',
            'sortBy': 'publishedAt',
            'pageSize': 5,
            'language': 'en'
        }
        
        headers = config.get_api_headers('news_api')
        
        response = requests.get(url, params=params, headers=headers, timeout=config.REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            return [
                {
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'published_at': article.get('publishedAt', ''),
                    'author': article.get('author', '')
                }
                for article in articles[:5]
            ]
    except Exception:
        pass
    
    return []


def _detect_social_presence(company_name: str, website_url: str = None) -> Dict:
    """Detect social media presence"""
    social_presence = {}
    
    if website_url:
        try:
            scraped_data = web_scraper.scrape_url(website_url)
            if scraped_data.get('success'):
                links = scraped_data.get('links', [])
                content = scraped_data.get('content', '').lower()
                
                # Look for social media links
                social_patterns = {
                    'twitter': [r'twitter\.com/(\w+)', r'x\.com/(\w+)'],
                    'linkedin': [r'linkedin\.com/company/([^/\s]+)'],
                    'github': [r'github\.com/([^/\s]+)'],
                    'youtube': [r'youtube\.com/(?:c/|channel/|user/)([^/\s]+)'],
                    'facebook': [r'facebook\.com/([^/\s]+)'],
                    'instagram': [r'instagram\.com/([^/\s]+)']
                }
                
                # Check links for social media URLs
                for link in links:
                    href = link.get('href', '')
                    for platform, patterns in social_patterns.items():
                        for pattern in patterns:
                            match = re.search(pattern, href, re.IGNORECASE)
                            if match:
                                social_presence[platform] = {
                                    'url': href,
                                    'handle': match.group(1),
                                    'found_via': 'website_links'
                                }
                
                # Also check content for mentions
                for platform, patterns in social_patterns.items():
                    if platform not in social_presence:
                        for pattern in patterns:
                            match = re.search(pattern, content, re.IGNORECASE)
                            if match:
                                social_presence[platform] = {
                                    'handle': match.group(1),
                                    'found_via': 'website_content'
                                }
                                break
        except Exception:
            pass
    
    return social_presence


@cached_request()
def enhanced_feature_extractor(website_url: str, docs_url: str = None) -> Dict:
    """
    Enhanced feature extraction using Firecrawl AI and semantic analysis:
    - AI-powered feature categorization
    - Technical capability detection
    - Integration feature mapping
    - Feature relationship analysis
    - Confidence scoring for each feature
    """
    try:
        # Use Firecrawl for AI-powered extraction if available
        if web_scraper.firecrawl_available:
            features_schema = extract_features_schema()
            
            urls_to_analyze = [website_url]
            if docs_url:
                urls_to_analyze.append(docs_url)
            
            all_features = {
                "core_features": [],
                "ai_ml_features": [],
                "developer_experience": [],
                "integration_features": [],
                "enterprise_features": [],
                "technical_capabilities": [],
                "api_features": [],
                "security_features": [],
                "analysis_metadata": {
                    "extraction_method": "firecrawl_ai",
                    "urls_analyzed": urls_to_analyze,
                    "timestamp": datetime.now().isoformat(),
                    "confidence_score": 0
                }
            }
            
            total_confidence = 0
            urls_processed = 0
            
            for url in urls_to_analyze:
                try:
                    # AI-powered structured extraction
                    extraction_result = web_scraper.extract_structured_data(
                        url,
                        features_schema,
                        prompt=f"Extract comprehensive feature information including core functionality, AI/ML capabilities, developer tools, integrations, enterprise features, security features, and technical specifications. Categorize each feature and provide brief descriptions."
                    )
                    
                    if extraction_result.get('success'):
                        structured_features = extraction_result.get('extracted_data', {})
                        
                        # Merge features from this URL
                        for category, features in structured_features.items():
                            if category in all_features and isinstance(features, list):
                                all_features[category].extend(features)
                        
                        urls_processed += 1
                        total_confidence += 85  # High confidence for AI extraction
                    
                    # Also do traditional scraping for additional context
                    scraped_data = web_scraper.scrape_url(url)
                    if scraped_data.get('success'):
                        content = scraped_data.get('content', '')
                        traditional_features = _extract_features_from_content(content)
                        
                        # Merge traditional features
                        for category, features in traditional_features.items():
                            if category in all_features:
                                # Add features that weren't found by AI
                                existing_feature_names = {f.get('feature_name', '').lower() for f in all_features[category]}
                                for feature in features:
                                    if feature.get('feature_name', '').lower() not in existing_feature_names:
                                        all_features[category].append(feature)
                        
                        total_confidence += 60  # Lower confidence for traditional extraction
                        
                except Exception as e:
                    print(f"Error processing {url}: {e}")
                    continue
            
            # Calculate overall confidence
            if urls_processed > 0:
                all_features["analysis_metadata"]["confidence_score"] = round(total_confidence / (urls_processed * 2), 1)
            
            # Deduplicate and enhance features
            all_features = _deduplicate_and_enhance_features(all_features)
            
            return all_features
        
        else:
            # Fallback to enhanced traditional extraction
            return _enhanced_traditional_feature_extraction(website_url, docs_url)
            
    except Exception as e:
        return {
            "error": f"Enhanced feature extraction failed: {str(e)}",
            "url": website_url,
            "timestamp": datetime.now().isoformat()
        }


def _extract_features_from_content(content: str) -> Dict:
    """Extract features from content using enhanced pattern matching"""
    features = {
        "core_features": [],
        "ai_ml_features": [],
        "developer_experience": [],
        "integration_features": [],
        "enterprise_features": [],
        "technical_capabilities": [],
        "api_features": [],
        "security_features": []
    }
    
    # Enhanced feature patterns with confidence scoring
    feature_patterns = {
        "ai_ml_features": {
            "keywords": ["ai-powered", "artificial intelligence", "machine learning", "ml", "neural network", "deep learning", "natural language", "computer vision", "predictive", "intelligent", "smart suggestions", "auto-complete", "recommendation"],
            "confidence": 90
        },
        "developer_experience": {
            "keywords": ["user-friendly", "easy to use", "intuitive", "simple setup", "quick start", "drag and drop", "visual", "no-code", "low-code", "user interface", "dashboard"],
            "confidence": 75
        },
        "integration_features": {
            "keywords": ["api", "webhook", "integration", "plugin", "extension", "connects to", "works with", "compatible", "import", "export", "sync", "embed"],
            "confidence": 85
        },
        "enterprise_features": {
            "keywords": ["enterprise", "team collaboration", "role-based", "permissions", "audit", "compliance", "sso", "single sign-on", "ldap", "saml", "admin", "governance"],
            "confidence": 80
        },
        "technical_capabilities": {
            "keywords": ["scalable", "high performance", "real-time", "batch processing", "cloud native", "microservices", "kubernetes", "docker", "serverless", "edge computing"],
            "confidence": 85
        },
        "api_features": {
            "keywords": ["rest api", "graphql", "api endpoint", "sdk", "api key", "rate limiting", "api documentation", "webhook", "api gateway", "api versioning"],
            "confidence": 90
        },
        "security_features": {
            "keywords": ["encryption", "secure", "privacy", "gdpr", "hipaa", "compliance", "two-factor", "2fa", "oauth", "security", "ssl", "tls", "authentication"],
            "confidence": 85
        }
    }
    
    content_lower = content.lower()
    
    # Find feature lists in HTML structure
    soup = BeautifulSoup(content, 'html.parser')
    feature_lists = soup.find_all(['ul', 'ol'], class_=re.compile(r'feature|benefit|capability|service', re.I))
    
    found_features = []
    for feature_list in feature_lists:
        items = feature_list.find_all('li')
        for item in items[:20]:  # Limit to avoid noise
            item_text = item.get_text().strip()
            if 10 < len(item_text) < 200:  # Reasonable feature description length
                found_features.append(item_text)
    
    # Categorize found features
    for feature_text in found_features:
        feature_lower = feature_text.lower()
        categorized = False
        
        for category, pattern_info in feature_patterns.items():
            keywords = pattern_info["keywords"]
            confidence = pattern_info["confidence"]
            
            if any(keyword in feature_lower for keyword in keywords):
                features[category].append({
                    "feature_name": feature_text,
                    "feature_description": feature_text,
                    "confidence_score": confidence,
                    "extraction_method": "pattern_matching"
                })
                categorized = True
                break
        
        if not categorized:
            features["core_features"].append({
                "feature_name": feature_text,
                "feature_description": feature_text,
                "confidence_score": 60,
                "extraction_method": "pattern_matching"
            })
    
    return features


def _deduplicate_and_enhance_features(features_dict: Dict) -> Dict:
    """Remove duplicates and enhance feature information"""
    for category in features_dict:
        if category == "analysis_metadata":
            continue
            
        if isinstance(features_dict[category], list):
            # Remove duplicates based on feature name similarity
            unique_features = []
            seen_names = set()
            
            for feature in features_dict[category]:
                if isinstance(feature, dict):
                    name = feature.get('feature_name', '').lower().strip()
                    if name and name not in seen_names:
                        seen_names.add(name)
                        unique_features.append(feature)
                elif isinstance(feature, str):
                    # Convert string features to dict format
                    name = feature.lower().strip()
                    if name and name not in seen_names:
                        seen_names.add(name)
                        unique_features.append({
                            "feature_name": feature,
                            "feature_description": feature,
                            "confidence_score": 70,
                            "extraction_method": "basic"
                        })
            
            features_dict[category] = unique_features[:15]  # Limit to top 15 per category
    
    return features_dict


def _enhanced_traditional_feature_extraction(website_url: str, docs_url: str = None) -> Dict:
    """Enhanced traditional feature extraction as fallback"""
    try:
        urls_to_check = [website_url]
        if docs_url:
            urls_to_check.append(docs_url)
        
        all_features = {
            "core_features": [],
            "ai_ml_features": [],
            "developer_experience": [],
            "integration_features": [],
            "enterprise_features": [],
            "technical_capabilities": [],
            "api_features": [],
            "security_features": [],
            "analysis_metadata": {
                "extraction_method": "traditional_enhanced",
                "urls_analyzed": urls_to_check,
                "timestamp": datetime.now().isoformat(),
                "confidence_score": 65
            }
        }
        
        for url in urls_to_check:
            scraped_data = web_scraper.scrape_url(url)
            if scraped_data.get('success'):
                content = scraped_data.get('content', '')
                url_features = _extract_features_from_content(content)
                
                # Merge features
                for category, features in url_features.items():
                    if category in all_features:
                        all_features[category].extend(features)
        
        # Deduplicate
        all_features = _deduplicate_and_enhance_features(all_features)
        
        return all_features
        
    except Exception as e:
        return {
            "error": f"Traditional feature extraction failed: {str(e)}",
            "url": website_url
        }


@cached_request()
def enhanced_integration_detector(website_url: str, docs_url: str = None) -> Dict:
    """
    Enhanced integration detection with marketplace verification:
    - Dynamic integration discovery from documentation
    - Marketplace verification (VS Code, Chrome Web Store, etc.)
    - Modern AI tool integration detection
    - Integration complexity assessment
    - Setup requirement analysis
    """
    try:
        integrations = {
            "ide_integrations": [],
            "cicd_integrations": [],
            "cloud_integrations": [],
            "development_tools": [],
            "ai_assistant_integrations": [],
            "marketplace_verified": [],
            "api_available": False,
            "webhook_support": False,
            "integration_complexity": "unknown",
            "setup_requirements": [],
            "analysis_metadata": {
                "extraction_method": "enhanced",
                "timestamp": datetime.now().isoformat(),
                "verification_attempted": [],
                "confidence_score": 0
            }
        }
        
        urls_to_check = [website_url]
        if docs_url:
            urls_to_check.append(docs_url)
        
        # Enhanced integration patterns including modern tools
        integration_patterns = {
            "ide_integrations": [
                "vs code", "visual studio code", "intellij", "pycharm", "webstorm", 
                "sublime text", "atom", "vim", "emacs", "eclipse", "xcode"
            ],
            "cicd_integrations": [
                "github actions", "gitlab ci", "jenkins", "circleci", "travis ci",
                "azure devops", "teamcity", "bamboo", "drone", "buildkite"
            ],
            "cloud_integrations": [
                "aws", "azure", "google cloud", "gcp", "vercel", "netlify",
                "heroku", "digitalocean", "cloudflare", "railway", "render"
            ],
            "development_tools": [
                "docker", "kubernetes", "git", "npm", "yarn", "webpack",
                "eslint", "prettier", "jest", "cypress", "postman"
            ],
            "ai_assistant_integrations": [
                "github copilot", "copilot", "claude", "chatgpt", "tabnine", 
                "codewhisperer", "kite", "intellicode", "cursor"
            ]
        }
        
        total_confidence = 0
        urls_processed = 0
        
        for url in urls_to_check:
            try:
                scraped_data = web_scraper.scrape_url(url)
                if not scraped_data.get('success'):
                    continue
                
                content = scraped_data.get('content', '').lower()
                links = scraped_data.get('links', [])
                
                # Check for API availability
                api_indicators = ['api', 'rest', 'graphql', 'endpoint', 'developer']
                integrations["api_available"] = any(indicator in content for indicator in api_indicators)
                
                # Check for webhook support
                webhook_indicators = ['webhook', 'callback', 'notification', 'event']
                integrations["webhook_support"] = any(indicator in content for indicator in webhook_indicators)
                
                # Detect integrations using patterns
                for category, keywords in integration_patterns.items():
                    for keyword in keywords:
                        if keyword in content:
                            # Check if it's just a mention or actual integration
                            context_indicators = ['integrate', 'plugin', 'extension', 'connect', 'install', 'setup']
                            is_integration = any(indicator in content[max(0, content.find(keyword)-100):content.find(keyword)+100] for indicator in context_indicators)
                            
                            if is_integration:
                                integrations[category].append({
                                    "integration_name": keyword.title(),
                                    "integration_type": "unknown",
                                    "verification_status": "found_in_content",
                                    "confidence_score": 70
                                })
                
                # Look for marketplace links
                marketplace_patterns = {
                    "vs_code_marketplace": r'marketplace\.visualstudio\.com',
                    "chrome_web_store": r'chrome\.google\.com/webstore',
                    "firefox_addons": r'addons\.mozilla\.org',
                    "github_marketplace": r'github\.com/marketplace',
                    "atlassian_marketplace": r'marketplace\.atlassian\.com'
                }
                
                for link in links:
                    href = link.get('href', '')
                    for marketplace, pattern in marketplace_patterns.items():
                        if re.search(pattern, href, re.IGNORECASE):
                            integrations["marketplace_verified"].append({
                                "marketplace": marketplace,
                                "url": href,
                                "verification_status": "link_found"
                            })
                
                # Assess integration complexity
                complexity_indicators = {
                    "simple": ["one-click", "easy setup", "no configuration", "instant"],
                    "moderate": ["configuration", "setup required", "api key", "authentication"],
                    "complex": ["custom implementation", "webhook setup", "advanced configuration", "developer required"]
                }
                
                for complexity, indicators in complexity_indicators.items():
                    if any(indicator in content for indicator in indicators):
                        integrations["integration_complexity"] = complexity
                        break
                
                # Extract setup requirements
                setup_patterns = [
                    r'(?:requires?|need[s]?|must have)\s+([^.]{10,100})',
                    r'(?:prerequisite|requirement)[s]?:\s*([^.]{10,100})',
                    r'before.*?(?:install|setup|configure)\s+([^.]{10,100})'
                ]
                
                for pattern in setup_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches[:5]:  # Limit requirements
                        if len(match.strip()) > 10:
                            integrations["setup_requirements"].append(match.strip())
                
                total_confidence += 75
                urls_processed += 1
                
            except Exception as e:
                print(f"Error processing {url}: {e}")
                continue
        
        # Try to verify marketplace integrations
        verified_count = 0
        for marketplace_item in integrations["marketplace_verified"]:
            try:
                # Simple verification - check if URL is accessible
                response = requests.head(marketplace_item["url"], timeout=5)
                if response.status_code == 200:
                    marketplace_item["verification_status"] = "verified"
                    verified_count += 1
                    total_confidence += 10
            except:
                marketplace_item["verification_status"] = "verification_failed"
        
        # Calculate confidence score
        if urls_processed > 0:
            base_confidence = total_confidence / urls_processed
            verification_bonus = (verified_count * 5) if integrations["marketplace_verified"] else 0
            integrations["analysis_metadata"]["confidence_score"] = min(100, round(base_confidence + verification_bonus, 1))
        
        integrations["analysis_metadata"]["verification_attempted"] = [item["marketplace"] for item in integrations["marketplace_verified"]]
        
        # Remove duplicates
        for category in ["ide_integrations", "cicd_integrations", "cloud_integrations", "development_tools", "ai_assistant_integrations"]:
            seen = set()
            unique_items = []
            for item in integrations[category]:
                name = item["integration_name"].lower()
                if name not in seen:
                    seen.add(name)
                    unique_items.append(item)
            integrations[category] = unique_items
        
        return integrations
        
    except Exception as e:
        return {
            "error": f"Enhanced integration detection failed: {str(e)}",
            "url": website_url,
            "timestamp": datetime.now().isoformat()
        }


# Export enhanced tools
def get_all_enhanced_tools():
    """Return all enhanced research tools"""
    return [
        enhanced_company_lookup,
        enhanced_feature_extractor,
        enhanced_integration_detector
    ]