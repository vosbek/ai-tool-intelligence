# competitive_analysis/market_analyzer.py - Comprehensive market analysis and competitive intelligence

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import re
from collections import defaultdict, Counter

from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_, desc, func

# Import required modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ...models.database import *


class MarketPosition(Enum):
    """Market position classifications"""
    LEADER = "leader"           # Dominant player with highest metrics
    CHALLENGER = "challenger"   # Strong competitor challenging leaders
    FOLLOWER = "follower"      # Following market trends
    NICHE = "niche"            # Specialized in specific segment
    EMERGING = "emerging"      # New player with potential
    DECLINING = "declining"    # Losing market share


class TrendDirection(Enum):
    """Trend direction indicators"""
    STRONG_UP = "strong_up"       # Significant positive trend
    MODERATE_UP = "moderate_up"   # Moderate positive trend
    STABLE = "stable"             # No significant trend
    MODERATE_DOWN = "moderate_down" # Moderate negative trend
    STRONG_DOWN = "strong_down"   # Significant negative trend


@dataclass
class CompetitiveMetrics:
    """Competitive metrics for a tool"""
    tool_id: int
    tool_name: str
    category: str
    
    # Feature metrics
    total_features: int
    ai_features: int
    enterprise_features: int
    integration_count: int
    
    # Market metrics
    github_stars: int
    github_forks: int
    release_frequency: float  # releases per month
    version_count: int
    
    # Business metrics
    pricing_model: str
    starting_price: float
    free_tier_available: bool
    enterprise_available: bool
    
    # Quality metrics
    data_quality_score: float
    confidence_score: float
    last_updated: datetime
    
    # Calculated scores
    feature_score: float = 0.0
    popularity_score: float = 0.0
    innovation_score: float = 0.0
    maturity_score: float = 0.0
    overall_score: float = 0.0


@dataclass
class MarketTrendData:
    """Market trend analysis data"""
    trend_id: str
    trend_name: str
    category: str
    trend_type: str  # 'technology', 'pricing', 'features', 'adoption'
    
    # Trend metrics
    direction: TrendDirection
    strength: float  # 0-1 (strength of trend)
    velocity: float  # rate of change
    confidence: float  # confidence in trend detection
    
    # Time data
    first_detected: datetime
    last_updated: datetime
    data_points: int
    
    # Supporting data
    affected_tools: List[int]
    key_indicators: List[str]
    description: str
    implications: List[str]


@dataclass
class CompetitiveAnalysisReport:
    """Comprehensive competitive analysis report"""
    analysis_id: str
    generated_at: datetime
    category: str
    
    # Market overview
    total_tools: int
    active_tools: int
    market_segments: Dict[str, int]
    
    # Competitive landscape
    market_leaders: List[CompetitiveMetrics]
    challengers: List[CompetitiveMetrics]
    emerging_players: List[CompetitiveMetrics]
    
    # Market trends
    trending_features: List[Dict]
    pricing_trends: List[Dict]
    technology_trends: List[MarketTrendData]
    
    # Insights
    key_insights: List[str]
    opportunities: List[str]
    threats: List[str]
    recommendations: List[str]
    
    # Metadata
    analysis_depth: str  # 'basic', 'standard', 'comprehensive'
    confidence_level: float
    data_freshness: float  # how recent is the data


class MarketAnalyzer:
    """Comprehensive market analysis and competitive intelligence engine"""
    
    def __init__(self, database_url: str = None):
        from sqlalchemy import create_engine
        
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # Analysis configuration
        self.scoring_weights = {
            'feature_score': 0.25,
            'popularity_score': 0.25,
            'innovation_score': 0.25,
            'maturity_score': 0.25
        }
        
        # Trend detection parameters
        self.trend_config = {
            'min_data_points': 3,
            'trend_threshold': 0.15,  # 15% change to be considered a trend
            'strong_trend_threshold': 0.30,  # 30% change for strong trend
            'confidence_threshold': 0.70  # 70% confidence minimum
        }
        
        print("Market Analyzer initialized")
    
    def analyze_category_competition(self, category_id: int, depth: str = 'standard') -> CompetitiveAnalysisReport:
        """
        Perform comprehensive competitive analysis for a category
        
        Args:
            category_id: Category to analyze
            depth: Analysis depth ('basic', 'standard', 'comprehensive')
            
        Returns:
            CompetitiveAnalysisReport with detailed analysis
        """
        session = self.Session()
        
        try:
            # Get category information
            category = session.query(Category).filter_by(id=category_id).first()
            if not category:
                raise ValueError(f"Category {category_id} not found")
            
            print(f"Analyzing competitive landscape for: {category.name}")
            
            # Get all tools in category
            tools = session.query(Tool).filter_by(category_id=category_id).all()
            
            if not tools:
                print(f"No tools found in category {category.name}")
                return self._create_empty_report(category)
            
            # Calculate competitive metrics for each tool
            competitive_metrics = []
            for tool in tools:
                metrics = self._calculate_tool_metrics(session, tool)
                competitive_metrics.append(metrics)
            
            # Analyze market positioning
            market_positions = self._analyze_market_positioning(competitive_metrics)
            
            # Detect trends
            trends = self._detect_market_trends(session, category_id, depth)
            
            # Generate insights
            insights = self._generate_market_insights(competitive_metrics, trends, market_positions)
            
            # Create comprehensive report
            report = CompetitiveAnalysisReport(
                analysis_id=f"analysis_{category_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                generated_at=datetime.utcnow(),
                category=category.name,
                total_tools=len(tools),
                active_tools=len([t for t in tools if t.is_actively_monitored]),
                market_segments=self._identify_market_segments(competitive_metrics),
                market_leaders=market_positions['leaders'],
                challengers=market_positions['challengers'],
                emerging_players=market_positions['emerging'],
                trending_features=trends['features'],
                pricing_trends=trends['pricing'],
                technology_trends=trends['technology'],
                key_insights=insights['key_insights'],
                opportunities=insights['opportunities'],
                threats=insights['threats'],
                recommendations=insights['recommendations'],
                analysis_depth=depth,
                confidence_level=self._calculate_analysis_confidence(competitive_metrics),
                data_freshness=self._calculate_data_freshness(tools)
            )
            
            # Save analysis to database
            self._save_competitive_analysis(session, report)
            
            session.commit()
            
            print(f"Competitive analysis completed for {category.name}")
            print(f"  Leaders: {len(report.market_leaders)}")
            print(f"  Challengers: {len(report.challengers)}")
            print(f"  Emerging: {len(report.emerging_players)}")
            print(f"  Trends detected: {len(report.technology_trends)}")
            
            return report
            
        except Exception as e:
            session.rollback()
            print(f"Error in competitive analysis: {e}")
            raise
        finally:
            session.close()
    
    def compare_tools(self, tool_ids: List[int], comparison_type: str = 'comprehensive') -> Dict:
        """
        Perform detailed comparison between specific tools
        
        Args:
            tool_ids: List of tool IDs to compare
            comparison_type: Type of comparison ('features', 'pricing', 'comprehensive')
            
        Returns:
            Detailed comparison analysis
        """
        session = self.Session()
        
        try:
            # Get tools
            tools = session.query(Tool).filter(Tool.id.in_(tool_ids)).all()
            
            if len(tools) < 2:
                raise ValueError("At least 2 tools required for comparison")
            
            print(f"Comparing {len(tools)} tools: {[t.name for t in tools]}")
            
            # Calculate metrics for each tool
            tool_metrics = {}
            for tool in tools:
                metrics = self._calculate_tool_metrics(session, tool)
                tool_metrics[tool.id] = metrics
            
            # Perform comparison based on type
            if comparison_type == 'features':
                comparison = self._compare_features(session, tools)
            elif comparison_type == 'pricing':
                comparison = self._compare_pricing(session, tools)
            else:  # comprehensive
                comparison = self._comprehensive_comparison(session, tools, tool_metrics)
            
            comparison['comparison_date'] = datetime.utcnow().isoformat()
            comparison['tools_compared'] = len(tools)
            comparison['comparison_type'] = comparison_type
            
            return comparison
            
        except Exception as e:
            print(f"Error in tool comparison: {e}")
            raise
        finally:
            session.close()
    
    def detect_market_opportunities(self, category_id: int = None) -> Dict:
        """
        Identify market opportunities and gaps
        
        Args:
            category_id: Specific category to analyze (None for all)
            
        Returns:
            Market opportunity analysis
        """
        session = self.Session()
        
        try:
            print("Detecting market opportunities...")
            
            # Get tools to analyze
            if category_id:
                tools = session.query(Tool).filter_by(category_id=category_id).all()
                category = session.query(Category).filter_by(id=category_id).first()
                scope = category.name if category else "Unknown Category"
            else:
                tools = session.query(Tool).all()
                scope = "All Categories"
            
            # Analyze feature gaps
            feature_gaps = self._identify_feature_gaps(session, tools)
            
            # Analyze pricing gaps
            pricing_gaps = self._identify_pricing_gaps(session, tools)
            
            # Analyze market segments
            underserved_segments = self._identify_underserved_segments(session, tools)
            
            # Analyze technology trends
            emerging_technologies = self._identify_emerging_technologies(session, tools)
            
            # Calculate opportunity scores
            opportunities = self._score_opportunities(feature_gaps, pricing_gaps, underserved_segments, emerging_technologies)
            
            opportunity_analysis = {
                "analysis_date": datetime.utcnow().isoformat(),
                "scope": scope,
                "tools_analyzed": len(tools),
                "feature_gaps": feature_gaps,
                "pricing_gaps": pricing_gaps,
                "underserved_segments": underserved_segments,
                "emerging_technologies": emerging_technologies,
                "top_opportunities": opportunities[:10],  # Top 10 opportunities
                "opportunity_summary": self._summarize_opportunities(opportunities)
            }
            
            print(f"Identified {len(opportunities)} market opportunities")
            return opportunity_analysis
            
        except Exception as e:
            print(f"Error detecting market opportunities: {e}")
            raise
        finally:
            session.close()
    
    def track_competitive_trends(self, days: int = 90) -> Dict:
        """
        Track competitive trends over time
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Trend tracking analysis
        """
        session = self.Session()
        
        try:
            print(f"Tracking competitive trends over {days} days...")
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get changes over time period
            changes = session.query(ToolChange).filter(
                ToolChange.detected_at >= cutoff_date
            ).order_by(ToolChange.detected_at).all()
            
            # Analyze change patterns
            change_patterns = self._analyze_change_patterns(changes)
            
            # Track feature evolution
            feature_trends = self._track_feature_trends(session, cutoff_date)
            
            # Track pricing evolution
            pricing_trends = self._track_pricing_trends(session, cutoff_date)
            
            # Track market share shifts
            market_shifts = self._track_market_shifts(session, cutoff_date)
            
            # Predict future trends
            predictions = self._predict_future_trends(changes, feature_trends, pricing_trends)
            
            trend_analysis = {
                "analysis_period": f"{days} days",
                "analysis_date": datetime.utcnow().isoformat(),
                "total_changes": len(changes),
                "change_patterns": change_patterns,
                "feature_trends": feature_trends,
                "pricing_trends": pricing_trends,
                "market_shifts": market_shifts,
                "trend_predictions": predictions,
                "trend_summary": self._summarize_trends(change_patterns, feature_trends, pricing_trends)
            }
            
            print(f"Analyzed {len(changes)} changes across {days} days")
            return trend_analysis
            
        except Exception as e:
            print(f"Error tracking competitive trends: {e}")
            raise
        finally:
            session.close()
    
    def generate_competitive_intelligence_report(self, category_id: int = None, 
                                               include_predictions: bool = True) -> Dict:
        """
        Generate comprehensive competitive intelligence report
        
        Args:
            category_id: Category to focus on (None for all)
            include_predictions: Whether to include trend predictions
            
        Returns:
            Comprehensive intelligence report
        """
        session = self.Session()
        
        try:
            print("Generating comprehensive competitive intelligence report...")
            
            # Get scope
            if category_id:
                category = session.query(Category).filter_by(id=category_id).first()
                scope = category.name if category else "Unknown Category"
            else:
                scope = "AI Developer Tools Market"
            
            # Perform competitive analysis
            if category_id:
                competitive_analysis = self.analyze_category_competition(category_id, 'comprehensive')
            else:
                # Analyze all categories
                categories = session.query(Category).all()
                competitive_analysis = {}
                for cat in categories:
                    try:
                        cat_analysis = self.analyze_category_competition(cat.id, 'standard')
                        competitive_analysis[cat.name] = cat_analysis
                    except:
                        continue
            
            # Detect market opportunities
            opportunities = self.detect_market_opportunities(category_id)
            
            # Track trends
            trends = self.track_competitive_trends(90)
            
            # Generate executive summary
            executive_summary = self._generate_executive_summary(competitive_analysis, opportunities, trends)
            
            # Compile comprehensive report
            intelligence_report = {
                "report_id": f"intelligence_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.utcnow().isoformat(),
                "scope": scope,
                "executive_summary": executive_summary,
                "competitive_analysis": competitive_analysis,
                "market_opportunities": opportunities,
                "trend_analysis": trends,
                "key_metrics": self._calculate_key_market_metrics(session, category_id),
                "strategic_recommendations": self._generate_strategic_recommendations(
                    competitive_analysis, opportunities, trends
                ),
                "methodology": self._document_methodology(),
                "data_sources": self._document_data_sources(session)
            }
            
            print("Competitive intelligence report generated successfully")
            return intelligence_report
            
        except Exception as e:
            print(f"Error generating intelligence report: {e}")
            raise
        finally:
            session.close()
    
    def _calculate_tool_metrics(self, session, tool: Tool) -> CompetitiveMetrics:
        """Calculate comprehensive metrics for a tool"""
        try:
            # Get latest version
            latest_version = session.query(ToolVersion).filter_by(
                tool_id=tool.id
            ).order_by(desc(ToolVersion.detected_at)).first()
            
            # Feature metrics
            total_features = 0
            ai_features = 0
            enterprise_features = 0
            integration_count = 0
            
            if latest_version:
                # Count features from latest version
                features = session.query(VersionFeature).filter_by(version_id=latest_version.id).all()
                total_features = len(features)
                ai_features = len([f for f in features if f.is_ai_feature])
                enterprise_features = len([f for f in features if f.is_enterprise_feature])
                
                # Count integrations
                integrations = session.query(VersionIntegration).filter_by(version_id=latest_version.id).all()
                integration_count = len(integrations)
            
            # GitHub metrics
            github_stars = 0
            github_forks = 0
            if latest_version and latest_version.github_metrics_snapshot:
                try:
                    github_data = json.loads(latest_version.github_metrics_snapshot)
                    basic_stats = github_data.get('basic_stats', {})
                    github_stars = basic_stats.get('stars', 0)
                    github_forks = basic_stats.get('forks', 0)
                except:
                    pass
            
            # Release frequency
            version_count = session.query(ToolVersion).filter_by(tool_id=tool.id).count()
            
            # Calculate release frequency (releases per month)
            release_frequency = 0.0
            if version_count > 1:
                first_version = session.query(ToolVersion).filter_by(
                    tool_id=tool.id
                ).order_by(ToolVersion.detected_at.asc()).first()
                
                if first_version:
                    days_active = (datetime.utcnow() - first_version.detected_at).days
                    if days_active > 0:
                        release_frequency = (version_count / days_active) * 30  # per month
            
            # Pricing metrics
            starting_price = 0.0
            pricing_model = "unknown"
            free_tier_available = False
            enterprise_available = False
            
            if latest_version and latest_version.pricing_snapshot:
                try:
                    pricing_data = json.loads(latest_version.pricing_snapshot)
                    pricing_model = pricing_data.get('pricing_model', 'unknown')
                    free_tier_available = pricing_data.get('free_tier_available', False)
                    enterprise_available = pricing_data.get('enterprise_available', False)
                    
                    # Find starting price
                    if pricing_data.get('subscription_tiers'):
                        prices = []
                        for tier in pricing_data['subscription_tiers']:
                            if tier.get('price_monthly') and tier['price_monthly'] > 0:
                                prices.append(float(tier['price_monthly']))
                        if prices:
                            starting_price = min(prices)
                except:
                    pass
            
            # Quality metrics
            data_quality_score = tool.confidence_score or 0.0
            confidence_score = tool.confidence_score or 0.0
            last_updated = tool.last_processed_at or tool.updated_at
            
            # Create metrics object
            metrics = CompetitiveMetrics(
                tool_id=tool.id,
                tool_name=tool.name,
                category=tool.category.name if tool.category else "Uncategorized",
                total_features=total_features,
                ai_features=ai_features,
                enterprise_features=enterprise_features,
                integration_count=integration_count,
                github_stars=github_stars,
                github_forks=github_forks,
                release_frequency=release_frequency,
                version_count=version_count,
                pricing_model=pricing_model,
                starting_price=starting_price,
                free_tier_available=free_tier_available,
                enterprise_available=enterprise_available,
                data_quality_score=data_quality_score,
                confidence_score=confidence_score,
                last_updated=last_updated
            )
            
            # Calculate derived scores
            metrics.feature_score = self._calculate_feature_score(metrics)
            metrics.popularity_score = self._calculate_popularity_score(metrics)
            metrics.innovation_score = self._calculate_innovation_score(metrics)
            metrics.maturity_score = self._calculate_maturity_score(metrics)
            metrics.overall_score = self._calculate_overall_score(metrics)
            
            return metrics
            
        except Exception as e:
            print(f"Error calculating metrics for tool {tool.name}: {e}")
            # Return minimal metrics
            return CompetitiveMetrics(
                tool_id=tool.id,
                tool_name=tool.name,
                category=tool.category.name if tool.category else "Uncategorized",
                total_features=0, ai_features=0, enterprise_features=0, integration_count=0,
                github_stars=0, github_forks=0, release_frequency=0.0, version_count=0,
                pricing_model="unknown", starting_price=0.0, free_tier_available=False, enterprise_available=False,
                data_quality_score=0.0, confidence_score=0.0, last_updated=datetime.utcnow()
            )
    
    def _calculate_feature_score(self, metrics: CompetitiveMetrics) -> float:
        """Calculate feature completeness score (0-100)"""
        # Base score from total features
        feature_base = min(metrics.total_features / 20.0, 1.0) * 40  # Up to 40 points
        
        # Bonus for AI features
        ai_bonus = min(metrics.ai_features / 10.0, 1.0) * 25  # Up to 25 points
        
        # Bonus for enterprise features
        enterprise_bonus = min(metrics.enterprise_features / 5.0, 1.0) * 20  # Up to 20 points
        
        # Bonus for integrations
        integration_bonus = min(metrics.integration_count / 15.0, 1.0) * 15  # Up to 15 points
        
        return min(feature_base + ai_bonus + enterprise_bonus + integration_bonus, 100.0)
    
    def _calculate_popularity_score(self, metrics: CompetitiveMetrics) -> float:
        """Calculate popularity score (0-100)"""
        # GitHub stars (logarithmic scale)
        stars_score = 0.0
        if metrics.github_stars > 0:
            stars_score = min(np.log10(metrics.github_stars + 1) / np.log10(50000) * 60, 60)  # Up to 60 points
        
        # GitHub forks
        forks_score = 0.0
        if metrics.github_forks > 0:
            forks_score = min(np.log10(metrics.github_forks + 1) / np.log10(5000) * 25, 25)  # Up to 25 points
        
        # Free tier availability (accessibility bonus)
        accessibility_bonus = 15 if metrics.free_tier_available else 0  # Up to 15 points
        
        return min(stars_score + forks_score + accessibility_bonus, 100.0)
    
    def _calculate_innovation_score(self, metrics: CompetitiveMetrics) -> float:
        """Calculate innovation score (0-100)"""
        # Release frequency (active development)
        release_score = min(metrics.release_frequency / 2.0, 1.0) * 40  # Up to 40 points for 2+ releases/month
        
        # AI feature ratio
        ai_ratio = metrics.ai_features / max(metrics.total_features, 1)
        ai_innovation = ai_ratio * 35  # Up to 35 points
        
        # Recent activity (data freshness)
        freshness_score = 0.0
        if metrics.last_updated:
            days_since_update = (datetime.utcnow() - metrics.last_updated).days
            freshness_score = max(0, (30 - days_since_update) / 30 * 25)  # Up to 25 points
        
        return min(release_score + ai_innovation + freshness_score, 100.0)
    
    def _calculate_maturity_score(self, metrics: CompetitiveMetrics) -> float:
        """Calculate maturity score (0-100)"""
        # Version count (stability through iterations)
        version_score = min(metrics.version_count / 10.0, 1.0) * 30  # Up to 30 points
        
        # Enterprise features (business maturity)
        enterprise_score = min(metrics.enterprise_features / 5.0, 1.0) * 25  # Up to 25 points
        
        # Pricing model maturity
        pricing_maturity = 0
        if metrics.pricing_model in ['subscription', 'enterprise']:
            pricing_maturity = 20
        elif metrics.pricing_model in ['freemium', 'usage_based']:
            pricing_maturity = 15
        elif metrics.pricing_model == 'free':
            pricing_maturity = 10
        
        # Data quality (indicates mature processes)
        quality_score = metrics.data_quality_score / 100 * 25  # Up to 25 points
        
        return min(version_score + enterprise_score + pricing_maturity + quality_score, 100.0)
    
    def _calculate_overall_score(self, metrics: CompetitiveMetrics) -> float:
        """Calculate weighted overall competitive score"""
        return (
            metrics.feature_score * self.scoring_weights['feature_score'] +
            metrics.popularity_score * self.scoring_weights['popularity_score'] +
            metrics.innovation_score * self.scoring_weights['innovation_score'] +
            metrics.maturity_score * self.scoring_weights['maturity_score']
        )
    
    def _analyze_market_positioning(self, metrics_list: List[CompetitiveMetrics]) -> Dict:
        """Analyze market positioning of tools"""
        if not metrics_list:
            return {"leaders": [], "challengers": [], "followers": [], "niche": [], "emerging": []}
        
        # Sort by overall score
        sorted_metrics = sorted(metrics_list, key=lambda m: m.overall_score, reverse=True)
        
        total_tools = len(sorted_metrics)
        
        # Define thresholds based on distribution
        if total_tools >= 10:
            leader_count = max(1, total_tools // 10)  # Top 10%
            challenger_count = max(1, total_tools // 5)  # Next 20%
        else:
            leader_count = 1
            challenger_count = min(2, total_tools - 1)
        
        leaders = sorted_metrics[:leader_count]
        challengers = sorted_metrics[leader_count:leader_count + challenger_count]
        
        # Identify emerging players (high innovation, lower overall)
        emerging = []
        followers = []
        niche = []
        
        remaining = sorted_metrics[leader_count + challenger_count:]
        
        for metric in remaining:
            if metric.innovation_score > 70 and metric.overall_score < 60:
                emerging.append(metric)
            elif metric.feature_score > 80 and metric.total_features < 10:  # Specialized
                niche.append(metric)
            else:
                followers.append(metric)
        
        return {
            "leaders": leaders,
            "challengers": challengers,
            "followers": followers,
            "niche": niche,
            "emerging": emerging
        }
    
    def _detect_market_trends(self, session, category_id: int, depth: str) -> Dict:
        """Detect various market trends"""
        trends = {
            "features": [],
            "pricing": [],
            "technology": []
        }
        
        try:
            # Feature trends
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            
            # Get recent changes in the category
            category_tools = session.query(Tool).filter_by(category_id=category_id).all()
            tool_ids = [t.id for t in category_tools]
            
            if tool_ids:
                changes = session.query(ToolChange).filter(
                    and_(
                        ToolChange.tool_id.in_(tool_ids),
                        ToolChange.detected_at >= cutoff_date
                    )
                ).all()
                
                # Analyze feature trends
                feature_changes = [c for c in changes if 'feature' in c.field_name.lower()]
                feature_trends = self._analyze_feature_trends(feature_changes)
                trends["features"] = feature_trends
                
                # Analyze pricing trends
                pricing_changes = [c for c in changes if c.change_type == ChangeType.PRICE_CHANGE]
                pricing_trends = self._analyze_pricing_trends(pricing_changes)
                trends["pricing"] = pricing_trends
                
                # Analyze technology trends (if comprehensive)
                if depth == 'comprehensive':
                    tech_trends = self._analyze_technology_trends(session, tool_ids, cutoff_date)
                    trends["technology"] = tech_trends
        
        except Exception as e:
            print(f"Error detecting trends: {e}")
        
        return trends
    
    def _analyze_feature_trends(self, feature_changes: List[ToolChange]) -> List[Dict]:
        """Analyze trending features"""
        if not feature_changes:
            return []
        
        # Count feature additions
        added_features = defaultdict(int)
        for change in feature_changes:
            if change.change_type == ChangeType.ADDED and change.new_value:
                feature_name = change.new_value.lower()
                # Extract common feature keywords
                keywords = re.findall(r'\b\w+\b', feature_name)
                for keyword in keywords:
                    if len(keyword) > 3:  # Ignore short words
                        added_features[keyword] += 1
        
        # Find trending features (mentioned multiple times)
        trending_features = []
        for feature, count in added_features.items():
            if count >= 2:  # At least 2 mentions
                trending_features.append({
                    "feature": feature,
                    "mention_count": count,
                    "trend_strength": min(count / 5.0, 1.0),  # Normalize to 0-1
                    "trend_type": "feature_addition"
                })
        
        return sorted(trending_features, key=lambda x: x["mention_count"], reverse=True)[:10]
    
    def _analyze_pricing_trends(self, pricing_changes: List[ToolChange]) -> List[Dict]:
        """Analyze pricing trends"""
        if not pricing_changes:
            return []
        
        price_movements = {"increases": 0, "decreases": 0}
        model_changes = defaultdict(int)
        
        for change in pricing_changes:
            # Analyze price movements
            if "price" in change.field_name.lower():
                try:
                    old_val = float(change.old_value or 0)
                    new_val = float(change.new_value or 0)
                    if new_val > old_val:
                        price_movements["increases"] += 1
                    elif new_val < old_val:
                        price_movements["decreases"] += 1
                except ValueError:
                    pass
            
            # Analyze model changes
            if "model" in change.field_name.lower() and change.new_value:
                model_changes[change.new_value] += 1
        
        trends = []
        
        # Price movement trends
        total_price_changes = price_movements["increases"] + price_movements["decreases"]
        if total_price_changes > 0:
            increase_ratio = price_movements["increases"] / total_price_changes
            if increase_ratio > 0.7:
                trends.append({
                    "trend": "price_increases",
                    "description": "Market showing upward pricing pressure",
                    "strength": increase_ratio,
                    "data_points": total_price_changes
                })
            elif increase_ratio < 0.3:
                trends.append({
                    "trend": "price_decreases", 
                    "description": "Market showing downward pricing pressure",
                    "strength": 1 - increase_ratio,
                    "data_points": total_price_changes
                })
        
        # Model trends
        for model, count in model_changes.items():
            if count >= 2:
                trends.append({
                    "trend": f"adoption_of_{model}",
                    "description": f"Increasing adoption of {model} pricing model",
                    "strength": min(count / 5.0, 1.0),
                    "data_points": count
                })
        
        return trends
    
    def _analyze_technology_trends(self, session, tool_ids: List[int], cutoff_date: datetime) -> List[MarketTrendData]:
        """Analyze technology trends (comprehensive analysis)"""
        trends = []
        
        try:
            # Analyze integration trends
            recent_integrations = session.query(VersionIntegration).join(ToolVersion).filter(
                and_(
                    ToolVersion.tool_id.in_(tool_ids),
                    ToolVersion.detected_at >= cutoff_date
                )
            ).all()
            
            integration_types = Counter([i.integration_category for i in recent_integrations])
            
            for int_type, count in integration_types.items():
                if count >= 3:  # Minimum threshold
                    trend = MarketTrendData(
                        trend_id=f"integration_{int_type}_{datetime.utcnow().strftime('%Y%m%d')}",
                        trend_name=f"Rising {int_type} Integration",
                        category="technology",
                        trend_type="integration",
                        direction=TrendDirection.MODERATE_UP,
                        strength=min(count / 10.0, 1.0),
                        velocity=count / 90,  # per day
                        confidence=0.8,
                        first_detected=cutoff_date,
                        last_updated=datetime.utcnow(),
                        data_points=count,
                        affected_tools=tool_ids,
                        key_indicators=[f"{count} new {int_type} integrations"],
                        description=f"Increasing adoption of {int_type} integrations",
                        implications=[f"Tools focusing on {int_type} connectivity", "Market convergence"]
                    )
                    trends.append(trend)
        
        except Exception as e:
            print(f"Error analyzing technology trends: {e}")
        
        return trends
    
    def _generate_market_insights(self, metrics: List[CompetitiveMetrics], trends: Dict, positions: Dict) -> Dict:
        """Generate market insights from analysis"""
        insights = {
            "key_insights": [],
            "opportunities": [],
            "threats": [],
            "recommendations": []
        }
        
        if not metrics:
            return insights
        
        # Key insights
        avg_overall_score = statistics.mean([m.overall_score for m in metrics])
        avg_feature_score = statistics.mean([m.feature_score for m in metrics])
        avg_innovation_score = statistics.mean([m.innovation_score for m in metrics])
        
        insights["key_insights"].extend([
            f"Market average competitive score: {avg_overall_score:.1f}/100",
            f"Feature completeness average: {avg_feature_score:.1f}/100",
            f"Innovation level average: {avg_innovation_score:.1f}/100",
            f"Market leaders: {len(positions['leaders'])} tools",
            f"Emerging players: {len(positions['emerging'])} tools"
        ])
        
        # Opportunities
        low_innovation_tools = [m for m in metrics if m.innovation_score < 50]
        if len(low_innovation_tools) > len(metrics) / 2:
            insights["opportunities"].append("Market has low innovation scores - opportunity for disruptive entry")
        
        high_price_tools = [m for m in metrics if m.starting_price > 50]
        if len(high_price_tools) > len(metrics) / 3:
            insights["opportunities"].append("High pricing levels suggest opportunity for affordable alternatives")
        
        # Feature gaps
        avg_ai_features = statistics.mean([m.ai_features for m in metrics])
        if avg_ai_features < 3:
            insights["opportunities"].append("Limited AI features across market - opportunity for AI-first tools")
        
        # Threats
        high_innovation_leaders = [m for m in positions['leaders'] if m.innovation_score > 80]
        if high_innovation_leaders:
            insights["threats"].append("Market leaders showing high innovation - competitive pressure increasing")
        
        emerging_with_features = [m for m in positions['emerging'] if m.feature_score > 70]
        if emerging_with_features:
            insights["threats"].append("Emerging players with strong feature sets - market disruption possible")
        
        # Recommendations
        if avg_innovation_score < 60:
            insights["recommendations"].append("Focus on innovation and unique feature development")
        
        if len(positions['leaders']) < 3:
            insights["recommendations"].append("Market consolidation opportunity - consider M&A strategies")
        
        if trends["features"]:
            top_trend = trends["features"][0]
            insights["recommendations"].append(f"Consider adopting '{top_trend['feature']}' features - trending in market")
        
        return insights
    
    def _identify_market_segments(self, metrics: List[CompetitiveMetrics]) -> Dict[str, int]:
        """Identify market segments based on pricing and features"""
        segments = {
            "enterprise": 0,
            "professional": 0, 
            "small_business": 0,
            "individual": 0,
            "open_source": 0
        }
        
        for metric in metrics:
            if metric.enterprise_available and metric.starting_price > 100:
                segments["enterprise"] += 1
            elif metric.starting_price > 50:
                segments["professional"] += 1
            elif metric.starting_price > 10:
                segments["small_business"] += 1
            elif metric.free_tier_available:
                segments["individual"] += 1
            elif metric.pricing_model == "free":
                segments["open_source"] += 1
        
        return segments
    
    def _calculate_analysis_confidence(self, metrics: List[CompetitiveMetrics]) -> float:
        """Calculate confidence level of analysis"""
        if not metrics:
            return 0.0
        
        # Base confidence on data quality
        avg_confidence = statistics.mean([m.confidence_score for m in metrics])
        
        # Adjust for data completeness
        complete_metrics = len([m for m in metrics if m.total_features > 0 and m.data_quality_score > 50])
        completeness_ratio = complete_metrics / len(metrics)
        
        # Adjust for recency
        recent_metrics = len([m for m in metrics if m.last_updated and 
                            (datetime.utcnow() - m.last_updated).days < 30])
        recency_ratio = recent_metrics / len(metrics)
        
        return min((avg_confidence * 0.5 + completeness_ratio * 30 + recency_ratio * 20), 100.0)
    
    def _calculate_data_freshness(self, tools: List[Tool]) -> float:
        """Calculate data freshness score"""
        if not tools:
            return 0.0
        
        recent_tools = len([t for t in tools if t.last_processed_at and 
                          (datetime.utcnow() - t.last_processed_at).days < 7])
        
        return (recent_tools / len(tools)) * 100
    
    def _save_competitive_analysis(self, session, report: CompetitiveAnalysisReport):
        """Save competitive analysis to database"""
        try:
            # Create CompetitiveAnalysis record
            analysis = CompetitiveAnalysis(
                tool_id=0,  # Category-level analysis
                analysis_name=f"Category Analysis: {report.category}",
                analysis_date=report.generated_at,
                market_position="analysis",
                popularity_score=report.confidence_level,
                innovation_score=report.data_freshness,
                maturity_score=float(report.total_tools),
                competitor_tools=json.dumps([m.tool_id for m in report.market_leaders]),
                strength_analysis=json.dumps({
                    "leaders": len(report.market_leaders),
                    "challengers": len(report.challengers),
                    "emerging": len(report.emerging_players)
                }),
                weakness_analysis=json.dumps(report.threats),
                market_trends=json.dumps(report.key_insights),
                recommendation="; ".join(report.recommendations[:3]),
                risk_level="medium",
                confidence_score=report.confidence_level,
                created_at=datetime.utcnow()
            )
            
            session.add(analysis)
            
        except Exception as e:
            print(f"Error saving competitive analysis: {e}")
    
    def _create_empty_report(self, category: Category) -> CompetitiveAnalysisReport:
        """Create empty report for categories with no tools"""
        return CompetitiveAnalysisReport(
            analysis_id=f"empty_{category.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            generated_at=datetime.utcnow(),
            category=category.name,
            total_tools=0,
            active_tools=0,
            market_segments={},
            market_leaders=[],
            challengers=[],
            emerging_players=[],
            trending_features=[],
            pricing_trends=[],
            technology_trends=[],
            key_insights=[f"No tools found in {category.name} category"],
            opportunities=["Opportunity for first-mover advantage"],
            threats=[],
            recommendations=["Consider entering this market segment"],
            analysis_depth="basic",
            confidence_level=0.0,
            data_freshness=0.0
        )
    
    # Additional methods for comprehensive comparison, opportunity detection, etc.
    # These would be implemented following similar patterns...
    
    def _comprehensive_comparison(self, session, tools: List[Tool], metrics: Dict) -> Dict:
        """Perform comprehensive tool comparison"""
        comparison = {
            "comparison_matrix": {},
            "feature_comparison": {},
            "pricing_comparison": {},
            "performance_metrics": {},
            "recommendations": {}
        }
        
        # This would implement detailed comparison logic...
        # For brevity, returning basic structure
        
        return comparison
    
    def _identify_feature_gaps(self, session, tools: List[Tool]) -> List[Dict]:
        """Identify feature gaps in the market"""
        # Implementation would analyze feature coverage gaps
        return []
    
    def _identify_pricing_gaps(self, session, tools: List[Tool]) -> List[Dict]:
        """Identify pricing gaps in the market"""
        # Implementation would analyze pricing strategy gaps
        return []
    
    def _identify_underserved_segments(self, session, tools: List[Tool]) -> List[Dict]:
        """Identify underserved market segments"""
        # Implementation would analyze market segment coverage
        return []
    
    def _identify_emerging_technologies(self, session, tools: List[Tool]) -> List[Dict]:
        """Identify emerging technology trends"""
        # Implementation would analyze technology adoption patterns
        return []
    
    def _score_opportunities(self, feature_gaps, pricing_gaps, segments, technologies) -> List[Dict]:
        """Score and rank market opportunities"""
        # Implementation would score opportunities
        return []
    
    def _summarize_opportunities(self, opportunities: List[Dict]) -> Dict:
        """Summarize opportunity analysis"""
        return {"total_opportunities": len(opportunities)}


# Export main classes
__all__ = [
    'MarketAnalyzer', 'CompetitiveMetrics', 'MarketTrendData', 'CompetitiveAnalysisReport',
    'MarketPosition', 'TrendDirection'
]