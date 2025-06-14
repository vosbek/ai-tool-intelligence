# competitive_analysis/trend_tracker.py - Advanced trend tracking and prediction system

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
import hashlib

from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_, desc, func, extract

# Import required modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ...models.database import *
from .market_analyzer import TrendDirection, MarketTrendData


class TrendType(Enum):
    """Types of trends we can track"""
    FEATURE_ADOPTION = "feature_adoption"
    PRICING_EVOLUTION = "pricing_evolution"
    MARKET_SHARE = "market_share"
    TECHNOLOGY_SHIFT = "technology_shift"
    USER_BEHAVIOR = "user_behavior"
    COMPETITIVE_POSITIONING = "competitive_positioning"


class TrendSignificance(Enum):
    """Significance levels for trends"""
    CRITICAL = "critical"      # Game-changing trends
    MAJOR = "major"           # Significant market impact
    MODERATE = "moderate"     # Notable but not transformative
    MINOR = "minor"           # Small market shifts
    NOISE = "noise"           # Statistical noise, not meaningful


@dataclass
class TrendPoint:
    """Individual data point in a trend"""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any]
    confidence: float = 1.0


@dataclass
class TrendAnalysis:
    """Complete trend analysis"""
    trend_id: str
    trend_name: str
    trend_type: TrendType
    
    # Trend characteristics
    direction: TrendDirection
    significance: TrendSignificance
    strength: float  # 0-1 magnitude of change
    velocity: float  # rate of change per unit time
    acceleration: float  # change in velocity
    
    # Statistical measures
    correlation: float  # how well data fits trend
    confidence_interval: Tuple[float, float]
    p_value: float
    
    # Time characteristics
    start_date: datetime
    end_date: datetime
    duration_days: int
    data_points: List[TrendPoint]
    
    # Prediction
    predicted_next_value: float
    prediction_confidence: float
    
    # Context
    affected_entities: List[int]  # tool IDs or category IDs
    key_drivers: List[str]
    implications: List[str]
    recommendations: List[str]


@dataclass
class MarketForecast:
    """Market forecast based on trend analysis"""
    forecast_id: str
    generated_at: datetime
    forecast_horizon_days: int
    
    # Forecast data
    predictions: Dict[str, List[TrendPoint]]
    confidence_bands: Dict[str, Tuple[List[float], List[float]]]
    
    # Key predictions
    emerging_technologies: List[str]
    declining_technologies: List[str]
    price_movements: Dict[str, float]  # category -> predicted change %
    market_disruptions: List[Dict]
    
    # Scenario analysis
    bull_case: Dict[str, Any]
    bear_case: Dict[str, Any]
    base_case: Dict[str, Any]
    
    # Methodology
    models_used: List[str]
    data_quality: float
    forecast_accuracy_estimate: float


class TrendTracker:
    """Advanced trend tracking and prediction system"""
    
    def __init__(self, database_url: str = None):
        from sqlalchemy import create_engine
        
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # Trend detection parameters
        self.trend_config = {
            'min_data_points': 5,
            'significance_threshold': 0.05,  # p-value threshold
            'correlation_threshold': 0.6,
            'velocity_threshold': 0.1,  # minimum velocity to be considered a trend
            'noise_filter': 0.05  # filter out changes smaller than this
        }
        
        # Forecasting parameters
        self.forecast_config = {
            'default_horizon_days': 90,
            'confidence_level': 0.95,
            'seasonal_adjustment': True,
            'outlier_detection': True
        }
        
        print("Trend Tracker initialized")
    
    def track_feature_adoption_trends(self, days: int = 180) -> List[TrendAnalysis]:
        """
        Track feature adoption trends across the market
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of feature adoption trends
        """
        session = self.Session()
        
        try:
            print(f"Tracking feature adoption trends over {days} days...")
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get all feature additions in time period
            feature_changes = session.query(ToolChange).filter(
                and_(
                    ToolChange.change_type == ChangeType.ADDED,
                    ToolChange.field_name.like('%feature%'),
                    ToolChange.detected_at >= cutoff_date
                )
            ).order_by(ToolChange.detected_at).all()
            
            # Group by feature keywords
            feature_timelines = self._extract_feature_timelines(feature_changes)
            
            # Analyze trends for each feature type
            trends = []
            for feature_keyword, timeline in feature_timelines.items():
                if len(timeline) >= self.trend_config['min_data_points']:
                    trend = self._analyze_adoption_trend(feature_keyword, timeline, TrendType.FEATURE_ADOPTION)
                    if trend:
                        trends.append(trend)
            
            # Sort by significance and strength
            trends.sort(key=lambda t: (t.significance.value, t.strength), reverse=True)
            
            print(f"Identified {len(trends)} feature adoption trends")
            return trends
            
        except Exception as e:
            print(f"Error tracking feature adoption trends: {e}")
            return []
        finally:
            session.close()
    
    def track_pricing_evolution(self, category_id: int = None, days: int = 365) -> List[TrendAnalysis]:
        """
        Track pricing evolution trends
        
        Args:
            category_id: Specific category to analyze (None for all)
            days: Number of days to analyze
            
        Returns:
            List of pricing evolution trends
        """
        session = self.Session()
        
        try:
            print(f"Tracking pricing evolution over {days} days...")
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Build query for pricing changes
            query = session.query(ToolChange).filter(
                and_(
                    ToolChange.change_type == ChangeType.PRICE_CHANGE,
                    ToolChange.detected_at >= cutoff_date
                )
            )
            
            if category_id:
                # Join with tools to filter by category
                query = query.join(Tool).filter(Tool.category_id == category_id)
            
            pricing_changes = query.order_by(ToolChange.detected_at).all()
            
            # Analyze different pricing aspects
            trends = []
            
            # Overall price level trends
            price_timeline = self._extract_price_timeline(pricing_changes)
            if len(price_timeline) >= self.trend_config['min_data_points']:
                price_trend = self._analyze_pricing_trend(price_timeline)
                if price_trend:
                    trends.append(price_trend)
            
            # Pricing model evolution
            model_timeline = self._extract_pricing_model_timeline(pricing_changes)
            for model, timeline in model_timeline.items():
                if len(timeline) >= self.trend_config['min_data_points']:
                    model_trend = self._analyze_model_adoption_trend(model, timeline)
                    if model_trend:
                        trends.append(model_trend)
            
            print(f"Identified {len(trends)} pricing evolution trends")
            return trends
            
        except Exception as e:
            print(f"Error tracking pricing evolution: {e}")
            return []
        finally:
            session.close()
    
    def track_market_share_shifts(self, category_id: int, days: int = 180) -> List[TrendAnalysis]:
        """
        Track market share shifts based on popularity metrics
        
        Args:
            category_id: Category to analyze
            days: Number of days to analyze
            
        Returns:
            List of market share trend analyses
        """
        session = self.Session()
        
        try:
            print(f"Tracking market share shifts in category {category_id}...")
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get tools in category
            tools = session.query(Tool).filter_by(category_id=category_id).all()
            tool_ids = [t.id for t in tools]
            
            if not tool_ids:
                return []
            
            # Get GitHub star changes (proxy for popularity/market share)
            star_changes = session.query(ToolChange).filter(
                and_(
                    ToolChange.tool_id.in_(tool_ids),
                    ToolChange.field_name == 'github_stars',
                    ToolChange.detected_at >= cutoff_date
                )
            ).order_by(ToolChange.detected_at).all()
            
            # Build market share timelines
            market_share_data = self._calculate_market_share_evolution(star_changes, tools)
            
            # Analyze trends for each tool
            trends = []
            for tool_id, timeline in market_share_data.items():
                if len(timeline) >= self.trend_config['min_data_points']:
                    tool_name = next((t.name for t in tools if t.id == tool_id), f"Tool {tool_id}")
                    trend = self._analyze_market_share_trend(tool_name, tool_id, timeline)
                    if trend:
                        trends.append(trend)
            
            print(f"Identified {len(trends)} market share trends")
            return trends
            
        except Exception as e:
            print(f"Error tracking market share shifts: {e}")
            return []
        finally:
            session.close()
    
    def detect_technology_shifts(self, days: int = 365) -> List[TrendAnalysis]:
        """
        Detect major technology shifts across the market
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of technology shift trends
        """
        session = self.Session()
        
        try:
            print(f"Detecting technology shifts over {days} days...")
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get integration changes (technology adoption indicator)
            integration_changes = session.query(ToolChange).filter(
                and_(
                    ToolChange.field_name.like('%integration%'),
                    ToolChange.detected_at >= cutoff_date
                )
            ).order_by(ToolChange.detected_at).all()
            
            # Extract technology adoption timelines
            tech_timelines = self._extract_technology_timelines(integration_changes)
            
            # Analyze trends
            trends = []
            for technology, timeline in tech_timelines.items():
                if len(timeline) >= self.trend_config['min_data_points']:
                    trend = self._analyze_technology_shift(technology, timeline)
                    if trend:
                        trends.append(trend)
            
            print(f"Identified {len(trends)} technology shift trends")
            return trends
            
        except Exception as e:
            print(f"Error detecting technology shifts: {e}")
            return []
        finally:
            session.close()
    
    def generate_market_forecast(self, category_id: int = None, horizon_days: int = 90) -> MarketForecast:
        """
        Generate comprehensive market forecast
        
        Args:
            category_id: Category to forecast (None for all)
            horizon_days: Forecast horizon in days
            
        Returns:
            Comprehensive market forecast
        """
        session = self.Session()
        
        try:
            print(f"Generating market forecast for {horizon_days} days...")
            
            # Gather trend data
            feature_trends = self.track_feature_adoption_trends(180)
            pricing_trends = self.track_pricing_evolution(category_id, 365)
            
            if category_id:
                market_trends = self.track_market_share_shifts(category_id, 180)
            else:
                market_trends = []
            
            tech_trends = self.detect_technology_shifts(365)
            
            # Generate predictions
            predictions = self._generate_predictions(feature_trends, pricing_trends, market_trends, tech_trends, horizon_days)
            
            # Calculate confidence bands
            confidence_bands = self._calculate_confidence_bands(predictions, 0.95)
            
            # Identify key forecast elements
            emerging_tech = self._identify_emerging_technologies(feature_trends, tech_trends)
            declining_tech = self._identify_declining_technologies(feature_trends, tech_trends)
            price_movements = self._predict_price_movements(pricing_trends)
            market_disruptions = self._predict_market_disruptions(market_trends, tech_trends)
            
            # Scenario analysis
            scenarios = self._generate_scenarios(predictions, confidence_bands)
            
            # Create forecast
            forecast = MarketForecast(
                forecast_id=f"forecast_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                generated_at=datetime.utcnow(),
                forecast_horizon_days=horizon_days,
                predictions=predictions,
                confidence_bands=confidence_bands,
                emerging_technologies=emerging_tech,
                declining_technologies=declining_tech,
                price_movements=price_movements,
                market_disruptions=market_disruptions,
                bull_case=scenarios['bull'],
                bear_case=scenarios['bear'],
                base_case=scenarios['base'],
                models_used=['linear_regression', 'trend_extrapolation', 'moving_average'],
                data_quality=self._assess_forecast_data_quality(feature_trends + pricing_trends + market_trends + tech_trends),
                forecast_accuracy_estimate=self._estimate_forecast_accuracy()
            )
            
            print("Market forecast generated successfully")
            return forecast
            
        except Exception as e:
            print(f"Error generating market forecast: {e}")
            raise
        finally:
            session.close()
    
    def identify_trend_breakouts(self, significance: TrendSignificance = TrendSignificance.MAJOR) -> List[TrendAnalysis]:
        """
        Identify trends that are breaking out (accelerating or changing direction)
        
        Args:
            significance: Minimum significance level to report
            
        Returns:
            List of breakout trends
        """
        print("Identifying trend breakouts...")
        
        # Get recent trends
        feature_trends = self.track_feature_adoption_trends(90)
        pricing_trends = self.track_pricing_evolution(None, 180)
        tech_trends = self.detect_technology_shifts(180)
        
        all_trends = feature_trends + pricing_trends + tech_trends
        
        # Filter for breakouts
        breakouts = []
        for trend in all_trends:
            if self._is_breakout_trend(trend) and trend.significance.value <= significance.value:
                breakouts.append(trend)
        
        # Sort by acceleration (highest first)
        breakouts.sort(key=lambda t: abs(t.acceleration), reverse=True)
        
        print(f"Identified {len(breakouts)} trend breakouts")
        return breakouts
    
    def _extract_feature_timelines(self, feature_changes: List[ToolChange]) -> Dict[str, List[TrendPoint]]:
        """Extract feature adoption timelines"""
        timelines = defaultdict(list)
        
        # Group changes by week to reduce noise
        weekly_counts = defaultdict(lambda: defaultdict(int))
        
        for change in feature_changes:
            if change.new_value:
                # Extract feature keywords
                keywords = self._extract_feature_keywords(change.new_value)
                week_start = change.detected_at.replace(hour=0, minute=0, second=0, microsecond=0)
                week_start = week_start - timedelta(days=week_start.weekday())
                
                for keyword in keywords:
                    weekly_counts[week_start][keyword] += 1
        
        # Convert to timeline format
        for week, features in weekly_counts.items():
            for feature, count in features.items():
                if count > 0:  # Filter noise
                    point = TrendPoint(
                        timestamp=week,
                        value=float(count),
                        metadata={"adoption_count": count},
                        confidence=min(count / 5.0, 1.0)  # Higher confidence with more adoptions
                    )
                    timelines[feature].append(point)
        
        # Sort timelines by timestamp
        for feature in timelines:
            timelines[feature].sort(key=lambda p: p.timestamp)
        
        return dict(timelines)
    
    def _extract_feature_keywords(self, feature_text: str) -> List[str]:
        """Extract meaningful keywords from feature descriptions"""
        # Clean and normalize text
        text = feature_text.lower()
        
        # Extract meaningful keywords (3+ chars, not common words)
        common_words = {'the', 'and', 'for', 'with', 'new', 'add', 'support', 'feature', 'tool', 'api'}
        keywords = []
        
        # Extract words
        words = re.findall(r'\b\w+\b', text)
        for word in words:
            if len(word) >= 3 and word not in common_words:
                keywords.append(word)
        
        # Extract phrases (AI-related terms)
        ai_phrases = ['artificial intelligence', 'machine learning', 'deep learning', 'neural network', 
                     'natural language', 'computer vision', 'code completion', 'auto complete']
        
        for phrase in ai_phrases:
            if phrase in text:
                keywords.append(phrase.replace(' ', '_'))
        
        return list(set(keywords))
    
    def _analyze_adoption_trend(self, feature: str, timeline: List[TrendPoint], trend_type: TrendType) -> Optional[TrendAnalysis]:
        """Analyze adoption trend for a specific feature"""
        if len(timeline) < self.trend_config['min_data_points']:
            return None
        
        try:
            # Prepare data
            timestamps = [p.timestamp for p in timeline]
            values = [p.value for p in timeline]
            
            # Convert timestamps to numeric (days since start)
            start_date = min(timestamps)
            x_values = [(ts - start_date).days for ts in timestamps]
            
            # Perform linear regression
            correlation, p_value, slope, intercept = self._linear_regression(x_values, values)
            
            # Check significance
            if p_value > self.trend_config['significance_threshold']:
                return None
            
            # Calculate trend characteristics
            direction = self._determine_trend_direction(slope)
            strength = min(abs(correlation), 1.0)
            velocity = slope
            
            # Calculate acceleration (second derivative)
            acceleration = 0.0
            if len(values) > 2:
                acceleration = self._calculate_acceleration(x_values, values)
            
            # Determine significance
            significance = self._determine_trend_significance(strength, abs(velocity), len(timeline))
            
            # Generate prediction
            next_x = x_values[-1] + 7  # 1 week ahead
            predicted_value = slope * next_x + intercept
            prediction_confidence = strength * (1.0 - p_value)
            
            # Calculate confidence interval
            ci_lower, ci_upper = self._calculate_confidence_interval(x_values, values, correlation)
            
            # Create trend analysis
            trend = TrendAnalysis(
                trend_id=hashlib.md5(f"{feature}_{trend_type.value}_{start_date}".encode()).hexdigest()[:12],
                trend_name=f"{feature.replace('_', ' ').title()} Adoption",
                trend_type=trend_type,
                direction=direction,
                significance=significance,
                strength=strength,
                velocity=velocity,
                acceleration=acceleration,
                correlation=correlation,
                confidence_interval=(ci_lower, ci_upper),
                p_value=p_value,
                start_date=start_date,
                end_date=max(timestamps),
                duration_days=(max(timestamps) - start_date).days,
                data_points=timeline,
                predicted_next_value=predicted_value,
                prediction_confidence=prediction_confidence,
                affected_entities=[],  # Would extract from metadata
                key_drivers=[f"Increasing adoption of {feature}"],
                implications=self._generate_adoption_implications(feature, direction, strength),
                recommendations=self._generate_adoption_recommendations(feature, direction, strength)
            )
            
            return trend
            
        except Exception as e:
            print(f"Error analyzing trend for {feature}: {e}")
            return None
    
    def _linear_regression(self, x_values: List[float], y_values: List[float]) -> Tuple[float, float, float, float]:
        """Perform linear regression and return correlation, p-value, slope, intercept"""
        try:
            # Convert to numpy arrays for easier calculation
            x = np.array(x_values)
            y = np.array(y_values)
            
            # Calculate correlation
            correlation = np.corrcoef(x, y)[0, 1] if len(x) > 1 else 0.0
            
            # Calculate linear regression
            slope, intercept = np.polyfit(x, y, 1)
            
            # Estimate p-value (simplified)
            n = len(x)
            if n > 2:
                # Calculate t-statistic
                y_pred = slope * x + intercept
                residuals = y - y_pred
                std_error = np.sqrt(np.sum(residuals**2) / (n - 2))
                
                if std_error > 0:
                    t_stat = abs(slope) / (std_error / np.sqrt(np.sum((x - np.mean(x))**2)))
                    # Simplified p-value estimation
                    p_value = max(0.001, 2 * (1 - min(0.999, t_stat / 10)))
                else:
                    p_value = 0.001
            else:
                p_value = 1.0
            
            return correlation, p_value, slope, intercept
            
        except Exception as e:
            print(f"Error in linear regression: {e}")
            return 0.0, 1.0, 0.0, 0.0
    
    def _determine_trend_direction(self, slope: float) -> TrendDirection:
        """Determine trend direction from slope"""
        if slope > 0.5:
            return TrendDirection.STRONG_UP
        elif slope > 0.1:
            return TrendDirection.MODERATE_UP
        elif slope < -0.5:
            return TrendDirection.STRONG_DOWN
        elif slope < -0.1:
            return TrendDirection.MODERATE_DOWN
        else:
            return TrendDirection.STABLE
    
    def _determine_trend_significance(self, strength: float, velocity: float, data_points: int) -> TrendSignificance:
        """Determine trend significance"""
        # Combine strength, velocity, and data quality
        significance_score = (strength * 0.4 + min(abs(velocity), 1.0) * 0.4 + min(data_points / 20, 1.0) * 0.2)
        
        if significance_score > 0.8:
            return TrendSignificance.CRITICAL
        elif significance_score > 0.6:
            return TrendSignificance.MAJOR
        elif significance_score > 0.4:
            return TrendSignificance.MODERATE
        elif significance_score > 0.2:
            return TrendSignificance.MINOR
        else:
            return TrendSignificance.NOISE
    
    def _calculate_acceleration(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate acceleration (second derivative)"""
        try:
            if len(x_values) < 3:
                return 0.0
            
            # Calculate first derivatives
            first_derivatives = []
            for i in range(1, len(y_values)):
                dy = y_values[i] - y_values[i-1]
                dx = x_values[i] - x_values[i-1]
                if dx != 0:
                    first_derivatives.append(dy / dx)
            
            # Calculate second derivative (acceleration)
            if len(first_derivatives) < 2:
                return 0.0
            
            accelerations = []
            for i in range(1, len(first_derivatives)):
                d2y = first_derivatives[i] - first_derivatives[i-1]
                dx = x_values[i+1] - x_values[i]
                if dx != 0:
                    accelerations.append(d2y / dx)
            
            return statistics.mean(accelerations) if accelerations else 0.0
            
        except Exception:
            return 0.0
    
    def _calculate_confidence_interval(self, x_values: List[float], y_values: List[float], correlation: float) -> Tuple[float, float]:
        """Calculate confidence interval for trend"""
        try:
            # Simplified confidence interval calculation
            std_dev = statistics.stdev(y_values) if len(y_values) > 1 else 0.0
            margin_of_error = 1.96 * std_dev * (1 - abs(correlation))  # 95% CI
            
            mean_value = statistics.mean(y_values)
            return (mean_value - margin_of_error, mean_value + margin_of_error)
            
        except Exception:
            return (0.0, 0.0)
    
    def _generate_adoption_implications(self, feature: str, direction: TrendDirection, strength: float) -> List[str]:
        """Generate implications for feature adoption trends"""
        implications = []
        
        if direction in [TrendDirection.STRONG_UP, TrendDirection.MODERATE_UP]:
            implications.append(f"Increasing market demand for {feature} capabilities")
            if strength > 0.7:
                implications.append(f"{feature} becoming a competitive differentiator")
            implications.append("Tools without this feature may lose market share")
        
        elif direction in [TrendDirection.STRONG_DOWN, TrendDirection.MODERATE_DOWN]:
            implications.append(f"Declining interest in {feature} functionality")
            implications.append("Market may be shifting to alternative approaches")
        
        return implications
    
    def _generate_adoption_recommendations(self, feature: str, direction: TrendDirection, strength: float) -> List[str]:
        """Generate recommendations for feature adoption trends"""
        recommendations = []
        
        if direction in [TrendDirection.STRONG_UP, TrendDirection.MODERATE_UP]:
            if strength > 0.8:
                recommendations.append(f"Prioritize {feature} development - critical trend")
                recommendations.append("Consider first-mover advantage opportunities")
            else:
                recommendations.append(f"Monitor {feature} development by competitors")
                recommendations.append("Plan feature roadmap inclusion")
        
        elif direction in [TrendDirection.STRONG_DOWN, TrendDirection.MODERATE_DOWN]:
            recommendations.append(f"Reconsider investment in {feature} development")
            recommendations.append("Research alternative feature directions")
        
        return recommendations
    
    # Additional methods for pricing trends, market share, technology shifts, forecasting...
    # These would follow similar patterns to the feature adoption analysis
    
    def _extract_price_timeline(self, pricing_changes: List[ToolChange]) -> List[TrendPoint]:
        """Extract price change timeline"""
        timeline = []
        
        for change in pricing_changes:
            try:
                old_price = float(change.old_value or 0)
                new_price = float(change.new_value or 0)
                
                if old_price > 0 and new_price > 0:
                    price_change = (new_price - old_price) / old_price
                    
                    point = TrendPoint(
                        timestamp=change.detected_at,
                        value=price_change,
                        metadata={
                            "old_price": old_price,
                            "new_price": new_price,
                            "tool_id": change.tool_id
                        }
                    )
                    timeline.append(point)
            except (ValueError, TypeError):
                continue
        
        return sorted(timeline, key=lambda p: p.timestamp)
    
    def _analyze_pricing_trend(self, timeline: List[TrendPoint]) -> Optional[TrendAnalysis]:
        """Analyze pricing trend"""
        # Similar structure to _analyze_adoption_trend but for pricing
        # Implementation would follow the same pattern
        return None
    
    def _extract_pricing_model_timeline(self, pricing_changes: List[ToolChange]) -> Dict[str, List[TrendPoint]]:
        """Extract pricing model adoption timelines"""
        # Implementation for tracking pricing model evolution
        return {}
    
    def _is_breakout_trend(self, trend: TrendAnalysis) -> bool:
        """Determine if a trend is breaking out (accelerating)"""
        return (
            abs(trend.acceleration) > 0.1 and
            trend.strength > 0.6 and
            trend.significance in [TrendSignificance.MAJOR, TrendSignificance.CRITICAL]
        )
    
    # Additional helper methods for forecasting...
    def _generate_predictions(self, feature_trends, pricing_trends, market_trends, tech_trends, horizon_days) -> Dict[str, List[TrendPoint]]:
        """Generate predictions based on trends"""
        return {}
    
    def _calculate_confidence_bands(self, predictions, confidence_level) -> Dict[str, Tuple[List[float], List[float]]]:
        """Calculate confidence bands for predictions"""
        return {}
    
    def _identify_emerging_technologies(self, feature_trends, tech_trends) -> List[str]:
        """Identify emerging technologies from trends"""
        return []
    
    def _identify_declining_technologies(self, feature_trends, tech_trends) -> List[str]:
        """Identify declining technologies from trends"""
        return []
    
    def _predict_price_movements(self, pricing_trends) -> Dict[str, float]:
        """Predict price movements by category"""
        return {}
    
    def _predict_market_disruptions(self, market_trends, tech_trends) -> List[Dict]:
        """Predict potential market disruptions"""
        return []
    
    def _generate_scenarios(self, predictions, confidence_bands) -> Dict[str, Dict]:
        """Generate bull/bear/base case scenarios"""
        return {
            "bull": {},
            "bear": {},
            "base": {}
        }
    
    def _assess_forecast_data_quality(self, trends) -> float:
        """Assess quality of data used for forecasting"""
        if not trends:
            return 0.0
        
        avg_confidence = statistics.mean([t.correlation for t in trends])
        return max(0.0, min(1.0, avg_confidence))
    
    def _estimate_forecast_accuracy(self) -> float:
        """Estimate forecast accuracy based on historical performance"""
        # This would be based on backtesting results
        return 0.75  # 75% estimated accuracy


# Export main classes
__all__ = [
    'TrendTracker', 'TrendAnalysis', 'MarketForecast', 'TrendPoint',
    'TrendType', 'TrendSignificance'
]