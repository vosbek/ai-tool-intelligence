"""
Strands Batch Agent - Core agent implementation using official Strands SDK
"""

import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import existing enhanced tools
from backend.src.ai_tool_intelligence.core.research.strands_tools import (
    enhanced_github_analyzer,
    enhanced_pricing_extractor
)
from backend.src.ai_tool_intelligence.core.research.additional_tools import (
    enhanced_company_lookup,
    enhanced_feature_extractor, 
    enhanced_integration_detector
)

try:
    from strands import Agent, tool
    from strands.models import BedrockModel, OpenAIModel
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False
    print("Warning: Strands SDK not available. Install with: pip install strands-agents strands-agents-tools")

from config import Config

class StrandsBatchAgent:
    """Enhanced Strands Agent for batch processing using official SDK"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.agent = None
        
        if STRANDS_AVAILABLE:
            self._initialize_agent()
        else:
            print("Warning: Running without Strands SDK - using fallback mode")
    
    def _initialize_agent(self):
        """Initialize the Strands agent with enhanced tools"""
        try:
            # Create enhanced tools using Strands SDK
            strands_tools = self._create_strands_tools()
            
            # Configure model based on config
            model = self._get_model()
            
            # Create agent with system prompt
            system_prompt = self._get_system_prompt()
            
            self.agent = Agent(
                tools=strands_tools,
                model=model,
                system_prompt=system_prompt
            )
            
            print(f"✅ Strands Agent initialized with {len(strands_tools)} tools")
            
        except Exception as e:
            print(f"❌ Failed to initialize Strands agent: {e}")
            self.agent = None
    
    def _create_strands_tools(self) -> List:
        """Create Strands-compatible tools from existing enhanced functions"""
        
        @tool
        def github_analyzer(repo_url: str) -> Dict:
            """Enhanced GitHub repository analysis with comprehensive metrics"""
            return enhanced_github_analyzer(repo_url)
        
        @tool
        def pricing_extractor(website_url: str, docs_url: str = None) -> Dict:
            """Enhanced pricing extraction with AI-powered analysis"""
            return enhanced_pricing_extractor(website_url, docs_url)
        
        @tool
        def company_lookup(company_name: str, website_url: str = None) -> Dict:
            """Enhanced company research with multiple data sources"""
            return enhanced_company_lookup(company_name, website_url)
        
        @tool
        def feature_extractor(website_url: str, docs_url: str = None) -> Dict:
            """Enhanced feature extraction with semantic analysis"""
            return enhanced_feature_extractor(website_url, docs_url)
        
        @tool
        def integration_detector(website_url: str, docs_url: str = None) -> Dict:
            """Enhanced integration detection with marketplace verification"""
            return enhanced_integration_detector(website_url, docs_url)
        
        @tool
        def comprehensive_analyzer(tool_data: Dict) -> Dict:
            """Run comprehensive analysis using all available tools"""
            return self._run_comprehensive_analysis(tool_data)
        
        return [
            github_analyzer,
            pricing_extractor,
            company_lookup,
            feature_extractor,
            integration_detector,
            comprehensive_analyzer
        ]
    
    def _get_model(self):
        """Get configured model for Strands agent"""
        model_config = self.config.get_model_config()
        
        if model_config.get('provider') == 'bedrock':
            return BedrockModel(
                model_id=model_config.get('model_id', 'us.amazon.nova-pro-v1:0'),
                temperature=model_config.get('temperature', 0.3),
                streaming=model_config.get('streaming', True)
            )
        elif model_config.get('provider') == 'openai':
            return OpenAIModel(
                model=model_config.get('model_id', 'gpt-4'),
                temperature=model_config.get('temperature', 0.3)
            )
        else:
            # Default to Bedrock if available
            return BedrockModel(
                model_id='us.amazon.nova-pro-v1:0',
                temperature=0.3,
                streaming=True
            )
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the agent"""
        return """You are an advanced AI tool research specialist with access to comprehensive, enhanced research tools.

Your enhanced capabilities include:

1. **GitHub Analysis**: Deep repository metrics, community health, activity patterns, and maintenance status
2. **Pricing Intelligence**: AI-powered pricing extraction, multi-currency support, and business model analysis  
3. **Company Research**: Multi-source company data including leadership, funding, location, and recent news
4. **Feature Analysis**: Semantic feature extraction, categorization, and technical capability assessment
5. **Integration Mapping**: Marketplace verification, modern tool detection, and setup complexity analysis

When researching tools, you should:
- Use the comprehensive_analyzer tool for complete analysis
- Or use individual tools for specific aspects
- Always provide structured, detailed reports with confidence scores
- Include data completeness metrics and actionable insights
- Cite sources and provide context for your findings

Focus on providing accurate, comprehensive analysis that helps users make informed decisions about AI development tools."""
    
    def analyze_tool(self, tool_data: Dict) -> Dict:
        """Analyze a tool using the Strands agent or fallback to direct analysis"""
        
        if self.agent:
            return self._analyze_with_strands(tool_data)
        else:
            return self._analyze_fallback(tool_data)
    
    def _analyze_with_strands(self, tool_data: Dict) -> Dict:
        """Analyze tool using Strands agent"""
        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt(tool_data)
            
            # Run analysis through Strands agent
            response = self.agent(prompt)
            
            # Parse response and structure results
            return self._parse_agent_response(response, tool_data)
            
        except Exception as e:
            print(f"❌ Strands analysis failed: {e}")
            return self._analyze_fallback(tool_data)
    
    def _analyze_fallback(self, tool_data: Dict) -> Dict:
        """Fallback analysis using direct tool calls"""
        return self._run_comprehensive_analysis(tool_data)
    
    def _create_analysis_prompt(self, tool_data: Dict) -> str:
        """Create analysis prompt for the agent"""
        tool_name = tool_data.get('name', 'Unknown Tool')
        website_url = tool_data.get('website_url', '')
        github_url = tool_data.get('github_url', '')
        docs_url = tool_data.get('docs_url', '')
        company_name = tool_data.get('company_name', '')
        
        prompt = f"""Please analyze the AI development tool: {tool_name}

Tool Information:
- Website: {website_url}
- GitHub: {github_url}
- Documentation: {docs_url}  
- Company: {company_name}

Please use the comprehensive_analyzer tool to perform a complete analysis including:
1. GitHub repository analysis (if available)
2. Pricing and business model analysis
3. Company background research
4. Feature extraction and categorization
5. Integration ecosystem analysis

Provide a structured report with confidence scores and actionable insights."""
        
        return prompt
    
    def _parse_agent_response(self, response: str, tool_data: Dict) -> Dict:
        """Parse agent response and extract structured data"""
        try:
            # For now, run comprehensive analysis directly
            # TODO: Implement proper response parsing from agent
            return self._run_comprehensive_analysis(tool_data)
            
        except Exception as e:
            return {
                "error": f"Failed to parse agent response: {str(e)}",
                "tool_name": tool_data.get('name', 'Unknown'),
                "raw_response": response
            }
    
    def _run_comprehensive_analysis(self, tool_data: Dict) -> Dict:
        """Run comprehensive analysis using all enhanced tools"""
        try:
            analysis_results = {
                "tool_name": tool_data.get('name', 'Unknown'),
                "analysis_timestamp": datetime.now().isoformat(),
                "github_analysis": None,
                "pricing_analysis": None,
                "company_analysis": None,
                "feature_analysis": None,
                "integration_analysis": None,
                "overall_summary": {},
                "analysis_metadata": {
                    "tools_used": [],
                    "apis_available": self.config.get_api_status(),
                    "total_confidence": 0,
                    "data_completeness": 0
                }
            }
            
            total_confidence = 0
            analyses_completed = 0
            
            # 1. GitHub Analysis
            github_url = tool_data.get('github_url') or tool_data.get('repository_url')
            if github_url:
                try:
                    github_result = enhanced_github_analyzer(github_url)
                    if not github_result.get('error'):
                        analysis_results["github_analysis"] = github_result
                        analysis_results["analysis_metadata"]["tools_used"].append("github_analyzer")
                        total_confidence += github_result.get('analysis_metadata', {}).get('data_completeness', 80)
                        analyses_completed += 1
                except Exception as e:
                    analysis_results["github_analysis"] = {"error": str(e)}
            
            # 2. Pricing Analysis
            website_url = tool_data.get('website_url') or tool_data.get('url')
            docs_url = tool_data.get('docs_url') or tool_data.get('documentation_url')
            
            if website_url:
                try:
                    pricing_result = enhanced_pricing_extractor(website_url, docs_url)
                    if not pricing_result.get('error'):
                        analysis_results["pricing_analysis"] = pricing_result
                        analysis_results["analysis_metadata"]["tools_used"].append("pricing_extractor")
                        total_confidence += 75
                        analyses_completed += 1
                except Exception as e:
                    analysis_results["pricing_analysis"] = {"error": str(e)}
            
            # 3. Company Analysis
            company_name = tool_data.get('company_name') or tool_data.get('name', '').split()[0]
            if company_name:
                try:
                    company_result = enhanced_company_lookup(company_name, website_url)
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
                    feature_result = enhanced_feature_extractor(website_url, docs_url)
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
                    integration_result = enhanced_integration_detector(website_url, docs_url)
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
                "timestamp": datetime.now().isoformat()
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
            
            # Key strengths
            strengths = []
            if github_data and github_data.get("basic_stats", {}).get("stars", 0) > 1000:
                strengths.append("Popular in community")
            if pricing_data and pricing_data.get("free_tier_available"):
                strengths.append("Free tier available")
            
            feature_data = analysis_results.get("feature_analysis", {})
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
            
            summary["key_strengths"] = strengths
            
            # Overall recommendation score
            score_factors = [
                min(20, summary["popularity_score"] * 0.2),
                20 if summary["activity_level"] in ["very_active", "active"] else 10 if summary["activity_level"] == "maintained" else 0,
                15 if summary["pricing_model"] in ["freemium", "free"] else 10 if summary["pricing_model"] in ["subscription"] else 5,
                15 if summary["integration_level"] == "extensive" else 10 if summary["integration_level"] == "good" else 5,
                15 if len(strengths) >= 3 else 10 if len(strengths) >= 2 else 5
            ]
            
            summary["recommendation_score"] = round(sum(score_factors), 1)
            
        except Exception as e:
            summary["error"] = f"Summary generation failed: {str(e)}"
        
        return summary
    
    def get_status(self) -> Dict:
        """Get agent status and capabilities"""
        return {
            "strands_available": STRANDS_AVAILABLE,
            "agent_initialized": self.agent is not None,
            "config_valid": self.config.validate(),
            "api_status": self.config.get_api_status(),
            "model_config": self.config.get_model_config(),
            "tools_available": [
                "github_analyzer",
                "pricing_extractor", 
                "company_lookup",
                "feature_extractor",
                "integration_detector",
                "comprehensive_analyzer"
            ]
        }