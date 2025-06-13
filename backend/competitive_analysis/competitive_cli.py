# competitive_analysis/competitive_cli.py - Command-line interface for competitive analysis

import argparse
import json
import sys
from datetime import datetime
from typing import Optional

# Import required modules
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from competitive_analysis.market_analyzer import MarketAnalyzer, CompetitiveMetrics
from competitive_analysis.trend_tracker import TrendTracker, TrendType, TrendSignificance
from models.enhanced_schema import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


class CompetitiveAnalysisCLI:
    """Command-line interface for competitive analysis operations"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
        
        self.market_analyzer = MarketAnalyzer(self.database_url)
        self.trend_tracker = TrendTracker(self.database_url)
    
    def analyze_category(self, category_id: int, depth: str = 'standard', output_format: str = 'summary'):
        """Analyze competitive landscape for a category"""
        try:
            print(f"\n🔍 Analyzing competitive landscape for category {category_id}...")
            
            # Get category name
            session = self.Session()
            category = session.query(Category).filter_by(id=category_id).first()
            if not category:
                print(f"❌ Category {category_id} not found")
                return
            
            category_name = category.name
            session.close()
            
            print(f"📊 Category: {category_name}")
            print(f"📈 Analysis depth: {depth}")
            
            # Perform analysis
            report = self.market_analyzer.analyze_category_competition(category_id, depth)
            
            # Output results
            if output_format == 'json':
                self._output_json_report(report)
            elif output_format == 'detailed':
                self._output_detailed_report(report)
            else:  # summary
                self._output_summary_report(report)
            
            print(f"\n✅ Analysis completed for {category_name}")
            
        except Exception as e:
            print(f"❌ Error analyzing category: {e}")
    
    def compare_tools(self, tool_ids: list, comparison_type: str = 'comprehensive'):
        """Compare specific tools"""
        try:
            print(f"\n🔍 Comparing {len(tool_ids)} tools...")
            print(f"🔧 Comparison type: {comparison_type}")
            
            # Get tool names
            session = self.Session()
            tools = session.query(Tool).filter(Tool.id.in_(tool_ids)).all()
            tool_names = [t.name for t in tools]
            session.close()
            
            print(f"🛠️  Tools: {', '.join(tool_names)}")
            
            # Perform comparison
            comparison = self.market_analyzer.compare_tools(tool_ids, comparison_type)
            
            # Output results
            self._output_tool_comparison(comparison, tool_names)
            
            print(f"\n✅ Tool comparison completed")
            
        except Exception as e:
            print(f"❌ Error comparing tools: {e}")
    
    def track_trends(self, trend_type: str = 'all', days: int = 90):
        """Track market trends"""
        try:
            print(f"\n📈 Tracking {trend_type} trends over {days} days...")
            
            trends = []
            
            if trend_type in ['all', 'features']:
                print("🔍 Analyzing feature adoption trends...")
                feature_trends = self.trend_tracker.track_feature_adoption_trends(days)
                trends.extend(feature_trends)
            
            if trend_type in ['all', 'pricing']:
                print("💰 Analyzing pricing evolution trends...")
                pricing_trends = self.trend_tracker.track_pricing_evolution(None, days)
                trends.extend(pricing_trends)
            
            if trend_type in ['all', 'technology']:
                print("🚀 Detecting technology shifts...")
                tech_trends = self.trend_tracker.detect_technology_shifts(days)
                trends.extend(tech_trends)
            
            # Output results
            self._output_trend_analysis(trends, trend_type)
            
            print(f"\n✅ Trend tracking completed - {len(trends)} trends identified")
            
        except Exception as e:
            print(f"❌ Error tracking trends: {e}")
    
    def generate_forecast(self, category_id: Optional[int] = None, horizon_days: int = 90):
        """Generate market forecast"""
        try:
            print(f"\n🔮 Generating market forecast for {horizon_days} days...")
            
            if category_id:
                session = self.Session()
                category = session.query(Category).filter_by(id=category_id).first()
                scope = category.name if category else f"Category {category_id}"
                session.close()
            else:
                scope = "All Categories"
            
            print(f"📊 Scope: {scope}")
            
            # Generate forecast
            forecast = self.trend_tracker.generate_market_forecast(category_id, horizon_days)
            
            # Output results
            self._output_market_forecast(forecast)
            
            print(f"\n✅ Market forecast generated")
            
        except Exception as e:
            print(f"❌ Error generating forecast: {e}")
    
    def detect_opportunities(self, category_id: Optional[int] = None):
        """Detect market opportunities"""
        try:
            print(f"\n💡 Detecting market opportunities...")
            
            if category_id:
                session = self.Session()
                category = session.query(Category).filter_by(id=category_id).first()
                scope = category.name if category else f"Category {category_id}"
                session.close()
            else:
                scope = "All Categories"
            
            print(f"📊 Scope: {scope}")
            
            # Detect opportunities
            opportunities = self.market_analyzer.detect_market_opportunities(category_id)
            
            # Output results
            self._output_opportunity_analysis(opportunities)
            
            print(f"\n✅ Opportunity detection completed")
            
        except Exception as e:
            print(f"❌ Error detecting opportunities: {e}")
    
    def identify_breakouts(self, significance: str = 'major'):
        """Identify trend breakouts"""
        try:
            print(f"\n🚨 Identifying {significance} trend breakouts...")
            
            # Map significance
            significance_map = {
                'critical': TrendSignificance.CRITICAL,
                'major': TrendSignificance.MAJOR,
                'moderate': TrendSignificance.MODERATE,
                'minor': TrendSignificance.MINOR
            }
            
            sig_level = significance_map.get(significance, TrendSignificance.MAJOR)
            
            # Identify breakouts
            breakouts = self.trend_tracker.identify_trend_breakouts(sig_level)
            
            # Output results
            self._output_breakout_analysis(breakouts, significance)
            
            print(f"\n✅ Breakout analysis completed - {len(breakouts)} breakouts identified")
            
        except Exception as e:
            print(f"❌ Error identifying breakouts: {e}")
    
    def generate_intelligence_report(self, category_id: Optional[int] = None, include_predictions: bool = True):
        """Generate comprehensive competitive intelligence report"""
        try:
            print(f"\n📋 Generating comprehensive competitive intelligence report...")
            
            if category_id:
                session = self.Session()
                category = session.query(Category).filter_by(id=category_id).first()
                scope = category.name if category else f"Category {category_id}"
                session.close()
            else:
                scope = "AI Developer Tools Market"
            
            print(f"📊 Scope: {scope}")
            print(f"🔮 Include predictions: {include_predictions}")
            
            # Generate report
            report = self.market_analyzer.generate_competitive_intelligence_report(
                category_id, include_predictions
            )
            
            # Output results
            self._output_intelligence_report(report)
            
            print(f"\n✅ Competitive intelligence report generated")
            
        except Exception as e:
            print(f"❌ Error generating intelligence report: {e}")
    
    def list_categories(self):
        """List available categories"""
        try:
            session = self.Session()
            categories = session.query(Category).all()
            session.close()
            
            print("\n📁 Available Categories:")
            print("=" * 50)
            
            for category in categories:
                # Count tools in category
                session = self.Session()
                tool_count = session.query(Tool).filter_by(category_id=category.id).count()
                session.close()
                
                print(f"ID: {category.id:2d} | {category.name:30s} | Tools: {tool_count:3d}")
            
            print("=" * 50)
            print(f"Total: {len(categories)} categories")
            
        except Exception as e:
            print(f"❌ Error listing categories: {e}")
    
    def list_tools(self, category_id: Optional[int] = None, limit: int = 20):
        """List tools in a category"""
        try:
            session = self.Session()
            
            if category_id:
                tools = session.query(Tool).filter_by(category_id=category_id).limit(limit).all()
                category = session.query(Category).filter_by(id=category_id).first()
                category_name = category.name if category else f"Category {category_id}"
            else:
                tools = session.query(Tool).limit(limit).all()
                category_name = "All Categories"
            
            session.close()
            
            print(f"\n🛠️  Tools in {category_name}:")
            print("=" * 70)
            
            for tool in tools:
                priority = getattr(tool, 'priority_level', 'N/A')
                status = "Active" if getattr(tool, 'is_actively_monitored', False) else "Inactive"
                print(f"ID: {tool.id:3d} | {tool.name:30s} | Priority: {priority} | Status: {status}")
            
            print("=" * 70)
            print(f"Showing {len(tools)} tools (limit: {limit})")
            
        except Exception as e:
            print(f"❌ Error listing tools: {e}")
    
    def _output_summary_report(self, report):
        """Output summary competitive analysis report"""
        print("\n📊 COMPETITIVE ANALYSIS SUMMARY")
        print("=" * 50)
        print(f"Category: {report.category}")
        print(f"Total Tools: {report.total_tools}")
        print(f"Active Tools: {report.active_tools}")
        print(f"Analysis Confidence: {report.confidence_level:.1f}%")
        print(f"Data Freshness: {report.data_freshness:.1f}%")
        
        print("\n🏆 Market Leaders:")
        for leader in report.market_leaders[:3]:
            print(f"  • {leader.tool_name} (Score: {leader.overall_score:.1f})")
        
        print("\n🚀 Emerging Players:")
        for emerging in report.emerging_players[:3]:
            print(f"  • {emerging.tool_name} (Innovation: {emerging.innovation_score:.1f})")
        
        print("\n📈 Key Insights:")
        for insight in report.key_insights[:5]:
            print(f"  • {insight}")
        
        print("\n💡 Top Recommendations:")
        for rec in report.recommendations[:3]:
            print(f"  • {rec}")
    
    def _output_detailed_report(self, report):
        """Output detailed competitive analysis report"""
        self._output_summary_report(report)
        
        print("\n\n🔍 DETAILED ANALYSIS")
        print("=" * 50)
        
        print("\n📊 Market Segments:")
        for segment, count in report.market_segments.items():
            print(f"  {segment}: {count} tools")
        
        print("\n🏅 All Market Leaders:")
        for leader in report.market_leaders:
            print(f"  • {leader.tool_name}")
            print(f"    Overall Score: {leader.overall_score:.1f}")
            print(f"    Features: {leader.feature_score:.1f} | Popularity: {leader.popularity_score:.1f}")
            print(f"    Innovation: {leader.innovation_score:.1f} | Maturity: {leader.maturity_score:.1f}")
        
        print("\n⚡ Challengers:")
        for challenger in report.challengers:
            print(f"  • {challenger.tool_name} (Score: {challenger.overall_score:.1f})")
        
        print("\n🎯 Trending Features:")
        for feature in report.trending_features[:5]:
            print(f"  • {feature.get('feature', 'Unknown')} (Mentions: {feature.get('mention_count', 0)})")
        
        print("\n💰 Pricing Trends:")
        for trend in report.pricing_trends[:3]:
            print(f"  • {trend.get('trend', 'Unknown')}: {trend.get('description', 'No description')}")
        
        print("\n🚀 Technology Trends:")
        for trend in report.technology_trends[:3]:
            print(f"  • {trend.trend_name}: {trend.description}")
    
    def _output_json_report(self, report):
        """Output report in JSON format"""
        # Convert report to JSON-serializable format
        report_dict = {
            "analysis_id": report.analysis_id,
            "generated_at": report.generated_at.isoformat(),
            "category": report.category,
            "total_tools": report.total_tools,
            "active_tools": report.active_tools,
            "confidence_level": report.confidence_level,
            "data_freshness": report.data_freshness,
            "market_leaders": [
                {
                    "tool_name": m.tool_name,
                    "overall_score": m.overall_score,
                    "feature_score": m.feature_score,
                    "popularity_score": m.popularity_score,
                    "innovation_score": m.innovation_score,
                    "maturity_score": m.maturity_score
                } for m in report.market_leaders
            ],
            "key_insights": report.key_insights,
            "recommendations": report.recommendations,
            "trending_features": report.trending_features,
            "pricing_trends": report.pricing_trends
        }
        
        print(json.dumps(report_dict, indent=2))
    
    def _output_tool_comparison(self, comparison, tool_names):
        """Output tool comparison results"""
        print("\n⚖️  TOOL COMPARISON")
        print("=" * 50)
        print(f"Tools: {', '.join(tool_names)}")
        print(f"Comparison Type: {comparison.get('comparison_type', 'Unknown')}")
        print(f"Analysis Date: {comparison.get('comparison_date', 'Unknown')}")
        
        # Add comparison details here
        print("\n📊 Comparison complete - detailed results available in JSON format")
    
    def _output_trend_analysis(self, trends, trend_type):
        """Output trend analysis results"""
        print(f"\n📈 TREND ANALYSIS - {trend_type.upper()}")
        print("=" * 50)
        
        if not trends:
            print("No significant trends detected")
            return
        
        for trend in trends[:10]:  # Show top 10 trends
            print(f"\n🔍 {trend.trend_name}")
            print(f"  Direction: {trend.direction.value}")
            print(f"  Significance: {trend.significance.value}")
            print(f"  Strength: {trend.strength:.2f}")
            print(f"  Velocity: {trend.velocity:.2f}")
            print(f"  Duration: {trend.duration_days} days")
            
            if trend.implications:
                print(f"  Implications: {'; '.join(trend.implications[:2])}")
    
    def _output_market_forecast(self, forecast):
        """Output market forecast results"""
        print(f"\n🔮 MARKET FORECAST")
        print("=" * 50)
        print(f"Forecast ID: {forecast.forecast_id}")
        print(f"Generated: {forecast.generated_at}")
        print(f"Horizon: {forecast.forecast_horizon_days} days")
        print(f"Data Quality: {forecast.data_quality:.2f}")
        print(f"Accuracy Estimate: {forecast.forecast_accuracy_estimate:.2f}")
        
        print("\n🚀 Emerging Technologies:")
        for tech in forecast.emerging_technologies[:5]:
            print(f"  • {tech}")
        
        print("\n📉 Declining Technologies:")
        for tech in forecast.declining_technologies[:5]:
            print(f"  • {tech}")
        
        print("\n💰 Price Movement Predictions:")
        for category, movement in forecast.price_movements.items():
            direction = "↗️" if movement > 0 else "↘️" if movement < 0 else "➡️"
            print(f"  {direction} {category}: {movement:+.1f}%")
    
    def _output_opportunity_analysis(self, opportunities):
        """Output opportunity analysis results"""
        print(f"\n💡 MARKET OPPORTUNITIES")
        print("=" * 50)
        print(f"Analysis Date: {opportunities.get('analysis_date', 'Unknown')}")
        print(f"Scope: {opportunities.get('scope', 'Unknown')}")
        print(f"Tools Analyzed: {opportunities.get('tools_analyzed', 0)}")
        
        top_opportunities = opportunities.get('top_opportunities', [])
        if top_opportunities:
            print("\n🎯 Top Opportunities:")
            for i, opp in enumerate(top_opportunities[:5], 1):
                print(f"  {i}. {opp.get('title', 'Unknown opportunity')}")
                print(f"     Score: {opp.get('score', 0):.2f}")
        
        summary = opportunities.get('opportunity_summary', {})
        if summary:
            print(f"\n📊 Summary: {summary.get('total_opportunities', 0)} opportunities identified")
    
    def _output_breakout_analysis(self, breakouts, significance):
        """Output breakout analysis results"""
        print(f"\n🚨 TREND BREAKOUTS - {significance.upper()}")
        print("=" * 50)
        
        if not breakouts:
            print(f"No {significance} trend breakouts detected")
            return
        
        for breakout in breakouts:
            print(f"\n⚡ {breakout.trend_name}")
            print(f"  Direction: {breakout.direction.value}")
            print(f"  Acceleration: {breakout.acceleration:.3f}")
            print(f"  Strength: {breakout.strength:.2f}")
            print(f"  Confidence: {breakout.prediction_confidence:.2f}")
            
            if breakout.key_drivers:
                print(f"  Key Drivers: {'; '.join(breakout.key_drivers[:2])}")
    
    def _output_intelligence_report(self, report):
        """Output intelligence report results"""
        print(f"\n📋 COMPETITIVE INTELLIGENCE REPORT")
        print("=" * 50)
        print(f"Report ID: {report.get('report_id', 'Unknown')}")
        print(f"Generated: {report.get('generated_at', 'Unknown')}")
        print(f"Scope: {report.get('scope', 'Unknown')}")
        
        exec_summary = report.get('executive_summary', {})
        if exec_summary:
            print("\n📈 Executive Summary:")
            for key, value in exec_summary.items():
                if isinstance(value, (int, float)):
                    print(f"  {key}: {value}")
                elif isinstance(value, str):
                    print(f"  {key}: {value}")
        
        recommendations = report.get('strategic_recommendations', [])
        if recommendations:
            print("\n🎯 Strategic Recommendations:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"  {i}. {rec}")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Competitive Analysis CLI for AI Tool Intelligence Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze-category 1 --depth comprehensive
  %(prog)s compare-tools 1 2 3 --type features
  %(prog)s track-trends --type features --days 30
  %(prog)s generate-forecast --category 1 --horizon 60
  %(prog)s detect-opportunities
  %(prog)s identify-breakouts --significance major
  %(prog)s generate-report --category 1
  %(prog)s list-categories
  %(prog)s list-tools --category 1
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze category command
    analyze_parser = subparsers.add_parser('analyze-category', help='Analyze competitive landscape for a category')
    analyze_parser.add_argument('category_id', type=int, help='Category ID to analyze')
    analyze_parser.add_argument('--depth', choices=['basic', 'standard', 'comprehensive'], default='standard', help='Analysis depth')
    analyze_parser.add_argument('--format', choices=['summary', 'detailed', 'json'], default='summary', help='Output format')
    
    # Compare tools command
    compare_parser = subparsers.add_parser('compare-tools', help='Compare specific tools')
    compare_parser.add_argument('tool_ids', nargs='+', type=int, help='Tool IDs to compare')
    compare_parser.add_argument('--type', choices=['features', 'pricing', 'comprehensive'], default='comprehensive', help='Comparison type')
    
    # Track trends command
    trends_parser = subparsers.add_parser('track-trends', help='Track market trends')
    trends_parser.add_argument('--type', choices=['all', 'features', 'pricing', 'technology'], default='all', help='Trend type to track')
    trends_parser.add_argument('--days', type=int, default=90, help='Number of days to analyze')
    
    # Generate forecast command
    forecast_parser = subparsers.add_parser('generate-forecast', help='Generate market forecast')
    forecast_parser.add_argument('--category', type=int, help='Category ID to forecast (optional)')
    forecast_parser.add_argument('--horizon', type=int, default=90, help='Forecast horizon in days')
    
    # Detect opportunities command
    opportunities_parser = subparsers.add_parser('detect-opportunities', help='Detect market opportunities')
    opportunities_parser.add_argument('--category', type=int, help='Category ID to analyze (optional)')
    
    # Identify breakouts command
    breakouts_parser = subparsers.add_parser('identify-breakouts', help='Identify trend breakouts')
    breakouts_parser.add_argument('--significance', choices=['critical', 'major', 'moderate', 'minor'], default='major', help='Minimum significance level')
    
    # Generate intelligence report command
    report_parser = subparsers.add_parser('generate-report', help='Generate comprehensive competitive intelligence report')
    report_parser.add_argument('--category', type=int, help='Category ID to focus on (optional)')
    report_parser.add_argument('--no-predictions', action='store_true', help='Exclude predictions from report')
    
    # List categories command
    subparsers.add_parser('list-categories', help='List available categories')
    
    # List tools command
    tools_parser = subparsers.add_parser('list-tools', help='List tools')
    tools_parser.add_argument('--category', type=int, help='Category ID to filter by (optional)')
    tools_parser.add_argument('--limit', type=int, default=20, help='Maximum number of tools to show')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI
    cli = CompetitiveAnalysisCLI()
    
    try:
        # Execute commands
        if args.command == 'analyze-category':
            cli.analyze_category(args.category_id, args.depth, args.format)
        
        elif args.command == 'compare-tools':
            cli.compare_tools(args.tool_ids, args.type)
        
        elif args.command == 'track-trends':
            cli.track_trends(args.type, args.days)
        
        elif args.command == 'generate-forecast':
            cli.generate_forecast(args.category, args.horizon)
        
        elif args.command == 'detect-opportunities':
            cli.detect_opportunities(args.category)
        
        elif args.command == 'identify-breakouts':
            cli.identify_breakouts(args.significance)
        
        elif args.command == 'generate-report':
            cli.generate_intelligence_report(args.category, not args.no_predictions)
        
        elif args.command == 'list-categories':
            cli.list_categories()
        
        elif args.command == 'list-tools':
            cli.list_tools(args.category, args.limit)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()