# enhanced_strands_agent.py - Enhanced Strands Agent with all improved tools

import sys
import os
from typing import Dict, List, Optional

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

# Import configuration and enhanced tools
from config.free_apis_config import FreeAPIConfig
from enhanced_strands_tools import enhanced_github_analyzer, enhanced_pricing_extractor
from enhanced_tools_additional import enhanced_company_lookup, enhanced_feature_extractor, enhanced_integration_detector

class EnhancedStrandsAgentService:
    """Enhanced Strands Agent service with improved research tools and free APIs"""
    
    def __init__(self):
        self.config = FreeAPIConfig()
        self.available_apis = self.config.validate_config()
        
        # Initialize all enhanced tools
        self.tools = {
            'github_analyzer': enhanced_github_analyzer,
            'pricing_extractor': enhanced_pricing_extractor,
            'company_lookup': enhanced_company_lookup,
            'feature_extractor': enhanced_feature_extractor,
            'integration_detector': enhanced_integration_detector
        }
        
        print(f"Enhanced Strands Agent initialized with {len(self.tools)} tools")
        print(f"Available APIs: {sum(self.available_apis.values())}/{len(self.available_apis)}")
    
    def analyze_tool(self, tool_data: Dict) -> Dict:
        """
        Comprehensive tool analysis using all enhanced research tools
        
        Args:
            tool_data: Dict containing tool information (name, website, github_url, etc.)
        
        Returns:
            Complete analysis results from all tools
        """
        try:
            analysis_results = {
                "tool_name": tool_data.get('name', 'Unknown'),
                "analysis_timestamp": self.config.get_config_summary()['current_cache_size'],
                "github_analysis": None,
                "pricing_analysis": None,
                "company_analysis": None,
                "feature_analysis": None,
                "integration_analysis": None,
                "overall_summary": {},
                "analysis_metadata": {
                    "tools_used": [],
                    "apis_available": self.available_apis,
                    "total_confidence": 0,
                    "data_completeness": 0
                }
            }
            
            total_confidence = 0
            analyses_completed = 0
            
            # 1. GitHub Analysis (if GitHub URL provided)
            github_url = tool_data.get('github_url') or tool_data.get('repository_url')
            if github_url:
                try:
                    github_result = self.tools['github_analyzer'](github_url)
                    if not github_result.get('error'):
                        analysis_results["github_analysis"] = github_result
                        analysis_results["analysis_metadata"]["tools_used"].append("github_analyzer")
                        total_confidence += github_result.get('analysis_metadata', {}).get('data_completeness', 80)
                        analyses_completed += 1
                except Exception as e:
                    analysis_results["github_analysis"] = {"error": str(e)}
            
            # 2. Pricing Analysis (always run on website)
            website_url = tool_data.get('website_url') or tool_data.get('url')
            docs_url = tool_data.get('docs_url') or tool_data.get('documentation_url')
            
            if website_url:
                try:
                    pricing_result = self.tools['pricing_extractor'](website_url, docs_url)
                    if not pricing_result.get('error'):
                        analysis_results["pricing_analysis"] = pricing_result
                        analysis_results["analysis_metadata"]["tools_used"].append("pricing_extractor")
                        total_confidence += 75  # Standard confidence for pricing
                        analyses_completed += 1
                except Exception as e:
                    analysis_results["pricing_analysis"] = {"error": str(e)}
            
            # 3. Company Analysis
            company_name = tool_data.get('company_name') or tool_data.get('name', '').split()[0]
            if company_name:
                try:
                    company_result = self.tools['company_lookup'](company_name, website_url)
                    if not company_result.get('error'):
                        analysis_results["company_analysis"] = company_result
                        analysis_results["analysis_metadata"]["tools_used"].append("company_lookup")
                        total_confidence += company_result.get('analysis_metadata', {}).get('data_completeness', 70)
                        analyses_completed += 1
                except Exception as e:
                    analysis_results["company_analysis"] = {"error": str(e)}
            
            # 4. Feature Analysis
            if website_url:
                try:
                    feature_result = self.tools['feature_extractor'](website_url, docs_url)
                    if not feature_result.get('error'):
                        analysis_results["feature_analysis"] = feature_result
                        analysis_results["analysis_metadata"]["tools_used"].append("feature_extractor")
                        total_confidence += feature_result.get('analysis_metadata', {}).get('confidence_score', 70)
                        analyses_completed += 1
                except Exception as e:
                    analysis_results["feature_analysis"] = {"error": str(e)}
            
            # 5. Integration Analysis
            if website_url:
                try:
                    integration_result = self.tools['integration_detector'](website_url, docs_url)
                    if not integration_result.get('error'):
                        analysis_results["integration_analysis"] = integration_result
                        analysis_results["analysis_metadata"]["tools_used"].append("integration_detector")
                        total_confidence += integration_result.get('analysis_metadata', {}).get('confidence_score', 70)
                        analyses_completed += 1
                except Exception as e:
                    analysis_results["integration_analysis"] = {"error": str(e)}
            
            # Calculate overall metrics
            if analyses_completed > 0:
                analysis_results["analysis_metadata"]["total_confidence"] = round(total_confidence / analyses_completed, 1)
                analysis_results["analysis_metadata"]["data_completeness"] = round((analyses_completed / 5) * 100, 1)
            
            # Generate overall summary
            analysis_results["overall_summary"] = self._generate_overall_summary(analysis_results)
            
            return analysis_results
            
        except Exception as e:
            return {
                "error": f"Comprehensive analysis failed: {str(e)}",
                "tool_name": tool_data.get('name', 'Unknown'),
                "timestamp": self.config.get_config_summary()
            }
    
    def _generate_overall_summary(self, analysis_results: Dict) -> Dict:
        """Generate comprehensive summary from all analysis results"""
        summary = {
            "popularity_score": 0,
            "activity_level": "unknown",
            "pricing_model": "unknown",
            "target_audience": "unknown",
            "key_strengths": [],
            "integration_level": "unknown",
            "company_maturity": "unknown",
            "recommendation_score": 0
        }
        
        try:
            # Popularity score from GitHub stats
            github_data = analysis_results.get("github_analysis", {})
            if github_data and not github_data.get('error'):
                stars = github_data.get("basic_stats", {}).get("stars", 0)
                forks = github_data.get("basic_stats", {}).get("forks", 0)
                # Simple popularity calculation
                summary["popularity_score"] = min(100, (stars * 0.1 + forks * 0.2))
                
                # Activity level
                is_maintained = github_data.get("activity_metrics", {}).get("is_actively_maintained", False)
                commits_90d = github_data.get("activity_metrics", {}).get("commit_analysis", {}).get("last_90_days", {}).get("count", 0)
                
                if is_maintained and commits_90d > 50:
                    summary["activity_level"] = "very_active"
                elif is_maintained and commits_90d > 10:
                    summary["activity_level"] = "active"
                elif is_maintained:
                    summary["activity_level"] = "maintained"
                else:
                    summary["activity_level"] = "inactive"
            
            # Pricing model from pricing analysis
            pricing_data = analysis_results.get("pricing_analysis", {})
            if pricing_data and not pricing_data.get('error'):
                summary["pricing_model"] = pricing_data.get("pricing_model", "unknown")
            
            # Target audience from features and pricing
            feature_data = analysis_results.get("feature_analysis", {})
            if feature_data and not feature_data.get('error'):
                enterprise_features = len(feature_data.get("enterprise_features", []))
                developer_features = len(feature_data.get("developer_experience", []))
                ai_features = len(feature_data.get("ai_ml_features", []))
                
                if enterprise_features > 5:
                    summary["target_audience"] = "enterprise"
                elif developer_features > 5:
                    summary["target_audience"] = "developers"
                elif ai_features > 3:
                    summary["target_audience"] = "ai_researchers"
                else:
                    summary["target_audience"] = "general"
            
            # Key strengths
            strengths = []
            if github_data and github_data.get("basic_stats", {}).get("stars", 0) > 1000:
                strengths.append("Popular in community")
            if pricing_data and pricing_data.get("free_tier_available"):
                strengths.append("Free tier available")
            if feature_data and len(feature_data.get("ai_ml_features", [])) > 0:
                strengths.append("AI-powered features")
            
            integration_data = analysis_results.get("integration_analysis", {})
            if integration_data and not integration_data.get('error'):
                total_integrations = sum(len(integration_data.get(key, [])) for key in ["ide_integrations", "cicd_integrations", "cloud_integrations"])
                if total_integrations > 5:
                    strengths.append("Extensive integrations")
                    summary["integration_level"] = "extensive"
                elif total_integrations > 2:
                    summary["integration_level"] = "good"
                else:
                    summary["integration_level"] = "limited"
                
                if integration_data.get("api_available"):
                    strengths.append("API available")
            
            summary["key_strengths"] = strengths
            
            # Company maturity
            company_data = analysis_results.get("company_analysis", {})
            if company_data and not company_data.get('error'):
                founded_year = company_data.get("founded_year")
                employee_count = company_data.get("employee_count")
                
                if founded_year and founded_year < 2020:
                    summary["company_maturity"] = "established"
                elif founded_year and founded_year < 2022:
                    summary["company_maturity"] = "growing"
                else:
                    summary["company_maturity"] = "startup"
                
                if employee_count and employee_count > 100:
                    summary["company_maturity"] = "established"
            
            # Overall recommendation score (0-100)
            score_factors = [
                min(20, summary["popularity_score"] * 0.2),  # Up to 20 points for popularity
                20 if summary["activity_level"] in ["very_active", "active"] else 10 if summary["activity_level"] == "maintained" else 0,
                15 if summary["pricing_model"] in ["freemium", "free"] else 10 if summary["pricing_model"] in ["subscription"] else 5,
                15 if summary["integration_level"] == "extensive" else 10 if summary["integration_level"] == "good" else 5,
                15 if len(strengths) >= 3 else 10 if len(strengths) >= 2 else 5,
                15 if summary["company_maturity"] == "established" else 10 if summary["company_maturity"] == "growing" else 5
            ]
            
            summary["recommendation_score"] = round(sum(score_factors), 1)
            
        except Exception as e:
            summary["error"] = f"Summary generation failed: {str(e)}"
        
        return summary
    
    def get_service_status(self) -> Dict:
        """Get current service status and capabilities"""
        return {
            "service_name": "Enhanced Strands Agent",
            "available_tools": list(self.tools.keys()),
            "api_status": self.available_apis,
            "configuration": self.config.get_config_summary(),
            "capabilities": {
                "github_analysis": self.available_apis.get('github', False),
                "enhanced_web_scraping": self.available_apis.get('firecrawl', False),
                "financial_data": self.available_apis.get('alpha_vantage', False),
                "news_analysis": self.available_apis.get('news_api', False),
                "currency_conversion": self.available_apis.get('exchange_rate', False),
                "geocoding": self.available_apis.get('nominatim', True),
                "basic_web_scraping": True,
                "caching": self.config.ENABLE_CACHING,
                "rate_limiting": True
            }
        }
    
    def analyze_multiple_tools(self, tools_list: List[Dict]) -> List[Dict]:
        """Analyze multiple tools in batch"""
        results = []
        
        for i, tool_data in enumerate(tools_list):
            try:
                print(f"Analyzing tool {i+1}/{len(tools_list)}: {tool_data.get('name', 'Unknown')}")
                result = self.analyze_tool(tool_data)
                results.append(result)
                
                # Add delay between analyses to respect rate limits
                if i < len(tools_list) - 1:  # Don't delay after last item
                    import time
                    time.sleep(2)
                    
            except Exception as e:
                results.append({
                    "error": f"Failed to analyze tool: {str(e)}",
                    "tool_name": tool_data.get('name', 'Unknown')
                })
        
        return results


# Create global service instance
enhanced_strands_service = EnhancedStrandsAgentService()


def create_enhanced_strands_tools():
    """Create enhanced Strands tools using the official SDK pattern"""
    try:
        from strands_tools import tool
        
        @tool
        def enhanced_github_analyzer_tool(repo_url: str) -> Dict:
            """Enhanced GitHub repository analysis with comprehensive metrics"""
            return enhanced_github_analyzer(repo_url)
        
        @tool
        def enhanced_pricing_extractor_tool(website_url: str, docs_url: str = None) -> Dict:
            """Enhanced pricing extraction with AI-powered analysis"""
            return enhanced_pricing_extractor(website_url, docs_url)
        
        @tool
        def enhanced_company_lookup_tool(company_name: str, website_url: str = None) -> Dict:
            """Enhanced company research with multiple data sources"""
            return enhanced_company_lookup(company_name, website_url)
        
        @tool
        def enhanced_feature_extractor_tool(website_url: str, docs_url: str = None) -> Dict:
            """Enhanced feature extraction with semantic analysis"""
            return enhanced_feature_extractor(website_url, docs_url)
        
        @tool
        def enhanced_integration_detector_tool(website_url: str, docs_url: str = None) -> Dict:
            """Enhanced integration detection with marketplace verification"""
            return enhanced_integration_detector(website_url, docs_url)
        
        @tool
        def comprehensive_tool_analyzer(tool_data: Dict) -> Dict:
            """Comprehensive tool analysis using all enhanced research tools"""
            return enhanced_strands_service.analyze_tool(tool_data)
        
        return [
            enhanced_github_analyzer_tool,
            enhanced_pricing_extractor_tool,
            enhanced_company_lookup_tool,
            enhanced_feature_extractor_tool,
            enhanced_integration_detector_tool,
            comprehensive_tool_analyzer
        ]
        
    except ImportError:
        print("Warning: strands_tools not available, returning empty list")
        return []


def create_enhanced_strands_agent():
    """Create enhanced Strands Agent with all research tools"""
    try:
        from strands import Agent
        
        enhanced_tools = create_enhanced_strands_tools()
        
        agent = Agent(
            tools=enhanced_tools,
            system_prompt="""You are an advanced AI tool research specialist with access to comprehensive, enhanced research tools powered by free APIs and Firecrawl MCP.

Your enhanced capabilities include:

1. **GitHub Analysis**: Deep repository metrics, community health, activity patterns, and maintenance status
2. **Pricing Intelligence**: AI-powered pricing extraction, multi-currency support, and business model analysis  
3. **Company Research**: Multi-source company data including leadership, funding, location, and recent news
4. **Feature Analysis**: Semantic feature extraction, categorization, and technical capability assessment
5. **Integration Mapping**: Marketplace verification, modern tool detection, and setup complexity analysis

When researching tools, systematically use these enhanced tools:
- enhanced_github_analyzer_tool: For repository analysis (if GitHub URL available)
- enhanced_pricing_extractor_tool: For comprehensive pricing and business model analysis
- enhanced_company_lookup_tool: For company background, leadership, and market presence
- enhanced_feature_extractor_tool: For detailed feature categorization and capabilities
- enhanced_integration_detector_tool: For ecosystem analysis and integration verification
- comprehensive_tool_analyzer: For complete analysis using all tools together

Always provide structured, detailed reports with confidence scores, data completeness metrics, and actionable insights. Cite sources and provide context for your findings."""
        )
        
        return agent
        
    except ImportError as e:
        print(f"Warning: Could not create enhanced Strands agent - {e}")
        return None


if __name__ == "__main__":
    # Test the enhanced service
    service = EnhancedStrandsAgentService()
    status = service.get_service_status()
    
    print("Enhanced Strands Agent Service Status:")
    print(f"Available Tools: {len(status['available_tools'])}")
    print(f"API Availability: {status['api_status']}")
    print(f"Total Capabilities: {sum(status['capabilities'].values())}/{len(status['capabilities'])}")
    
    # Test with sample tool data
    sample_tool = {
        "name": "GitHub Copilot",
        "website_url": "https://github.com/features/copilot",
        "github_url": "https://github.com/github/copilot-docs",
        "company_name": "GitHub"
    }
    
    print("\nTesting with sample tool...")
    result = service.analyze_tool(sample_tool)
    print(f"Analysis completed. Tools used: {result.get('analysis_metadata', {}).get('tools_used', [])}")
    print(f"Overall confidence: {result.get('analysis_metadata', {}).get('total_confidence', 0)}")