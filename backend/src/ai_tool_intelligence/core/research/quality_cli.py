#!/usr/bin/env python3
# data_validation/quality_cli.py - CLI tool for data validation and quality scoring

import argparse
import json
import sys
import os
from datetime import datetime
from typing import List, Dict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .quality_scorer import DataQualityScorer, QualityAssessment
from ...models.database import Tool, Company, ToolVersion, DataQuality
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class QualityReportCLI:
    """Command-line interface for data quality assessment"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
        self.scorer = DataQualityScorer(self.database_url)
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def assess_single_tool(self, tool_id: int, verbose: bool = False) -> Dict:
        """Assess a single tool and display results"""
        try:
            assessment = self.scorer.assess_tool_quality(tool_id, include_analysis=True)
            
            if verbose:
                self._print_detailed_assessment(assessment)
            else:
                self._print_summary_assessment(assessment)
            
            return self._assessment_to_dict(assessment)
            
        except Exception as e:
            print(f"Error assessing tool {tool_id}: {e}")
            return {"error": str(e)}
    
    def assess_all_tools(self, limit: int = None, min_score: float = None) -> Dict:
        """Assess all tools and provide summary"""
        try:
            print("🔍 Running quality assessment on all tools...")
            
            assessments = self.scorer.bulk_assess_quality('tool', limit=limit)
            
            # Filter by minimum score if specified
            if min_score is not None:
                assessments = [a for a in assessments if a.overall_score >= min_score]
            
            self._print_bulk_summary(assessments, 'tools')
            
            return {
                "total_assessed": len(assessments),
                "assessments": [self._assessment_to_dict(a) for a in assessments]
            }
            
        except Exception as e:
            print(f"Error in bulk assessment: {e}")
            return {"error": str(e)}
    
    def generate_quality_report(self, output_file: str = None, format_type: str = 'json') -> str:
        """Generate comprehensive quality report"""
        try:
            print("📊 Generating comprehensive quality report...")
            
            # Assess all entity types
            tool_assessments = self.scorer.bulk_assess_quality('tool')
            company_assessments = self.scorer.bulk_assess_quality('company')
            
            # Calculate summary statistics
            report_data = {
                "report_generated": datetime.utcnow().isoformat(),
                "summary": {
                    "total_tools_assessed": len(tool_assessments),
                    "total_companies_assessed": len(company_assessments),
                    "tools_by_quality": self._group_by_quality(tool_assessments),
                    "companies_by_quality": self._group_by_quality(company_assessments),
                    "average_scores": self._calculate_average_scores(tool_assessments + company_assessments)
                },
                "tools": [self._assessment_to_dict(a) for a in tool_assessments],
                "companies": [self._assessment_to_dict(a) for a in company_assessments],
                "recommendations": self._generate_overall_recommendations(tool_assessments + company_assessments)
            }
            
            # Save to file if requested
            if output_file:
                if format_type == 'json':
                    with open(output_file, 'w') as f:
                        json.dump(report_data, f, indent=2)
                elif format_type == 'txt':
                    self._save_text_report(report_data, output_file)
                
                print(f"📄 Report saved to: {output_file}")
            
            # Print summary to console
            self._print_report_summary(report_data)
            
            return output_file or "console_output"
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return ""
    
    def identify_quality_issues(self, min_score: float = 70.0) -> Dict:
        """Identify entities with quality issues"""
        try:
            print(f"🚨 Identifying entities with quality score below {min_score}...")
            
            # Get all assessments
            tool_assessments = self.scorer.bulk_assess_quality('tool')
            company_assessments = self.scorer.bulk_assess_quality('company')
            
            # Filter low-quality entities
            low_quality_tools = [a for a in tool_assessments if a.overall_score < min_score]
            low_quality_companies = [a for a in company_assessments if a.overall_score < min_score]
            
            # Group issues by type
            issues_by_type = {}
            for assessment in low_quality_tools + low_quality_companies:
                for issue in assessment.issues_found:
                    if issue not in issues_by_type:
                        issues_by_type[issue] = []
                    issues_by_type[issue].append({
                        "entity_type": assessment.entity_type,
                        "entity_id": assessment.entity_id,
                        "score": assessment.overall_score
                    })
            
            print(f"Found {len(low_quality_tools)} tools and {len(low_quality_companies)} companies with quality issues")
            
            # Print top issues
            sorted_issues = sorted(issues_by_type.items(), key=lambda x: len(x[1]), reverse=True)
            print("\\nTop quality issues:")
            for issue, entities in sorted_issues[:10]:
                print(f"  • {issue}: {len(entities)} entities")
            
            return {
                "low_quality_tools": [self._assessment_to_dict(a) for a in low_quality_tools],
                "low_quality_companies": [self._assessment_to_dict(a) for a in low_quality_companies],
                "issues_by_type": issues_by_type,
                "summary": {
                    "total_low_quality": len(low_quality_tools) + len(low_quality_companies),
                    "unique_issue_types": len(issues_by_type)
                }
            }
            
        except Exception as e:
            print(f"Error identifying quality issues: {e}")
            return {"error": str(e)}
    
    def track_quality_trends(self, days: int = 30) -> Dict:
        """Track quality trends over time"""
        session = self.Session()
        
        try:
            from models.enhanced_schema import DataQualityReport
            from sqlalchemy import and_
            
            # Get quality reports from the last N days
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            reports = session.query(DataQualityReport).filter(
                DataQualityReport.report_date >= cutoff_date
            ).order_by(DataQualityReport.report_date).all()
            
            # Group by date and calculate daily averages
            daily_scores = {}
            for report in reports:
                date_key = report.report_date.date().isoformat()
                if date_key not in daily_scores:
                    daily_scores[date_key] = []
                
                # Calculate overall score from components
                overall = (report.completeness_score + report.accuracy_score + 
                          report.freshness_score + report.consistency_score) / 4
                daily_scores[date_key].append(overall)
            
            # Calculate daily averages
            trend_data = {}
            for date, scores in daily_scores.items():
                trend_data[date] = {
                    "average_score": sum(scores) / len(scores),
                    "entities_assessed": len(scores),
                    "min_score": min(scores),
                    "max_score": max(scores)
                }
            
            print(f"📈 Quality trends over the last {days} days:")
            for date, data in sorted(trend_data.items())[-7:]:  # Show last 7 days
                print(f"  {date}: Avg {data['average_score']:.1f} ({data['entities_assessed']} entities)")
            
            return {
                "period_days": days,
                "trend_data": trend_data,
                "total_reports": len(reports),
                "date_range": {
                    "start": min(daily_scores.keys()) if daily_scores else None,
                    "end": max(daily_scores.keys()) if daily_scores else None
                }
            }
            
        except Exception as e:
            print(f"Error tracking quality trends: {e}")
            return {"error": str(e)}
        finally:
            session.close()
    
    def _print_detailed_assessment(self, assessment: QualityAssessment):
        """Print detailed assessment results"""
        print(f"\\n{'='*60}")
        print(f"QUALITY ASSESSMENT - {assessment.entity_type.upper()} #{assessment.entity_id}")
        print(f"{'='*60}")
        
        print(f"Overall Score: {assessment.overall_score:.1f}/100 ({assessment.quality_grade.value})")
        print(f"Confidence Level: {assessment.confidence_level:.1f}%")
        
        print(f"\\nComponent Scores:")
        print(f"  📊 Completeness: {assessment.completeness_score:.1f}/100")
        print(f"  🎯 Accuracy: {assessment.accuracy_score:.1f}/100")
        print(f"  ⏰ Freshness: {assessment.freshness_score:.1f}/100")
        print(f"  🔄 Consistency: {assessment.consistency_score:.1f}/100")
        
        if assessment.issues_found:
            print(f"\\n⚠️  Issues Found ({len(assessment.issues_found)}):")
            for issue in assessment.issues_found:
                print(f"    • {issue}")
        
        if assessment.recommendations:
            print(f"\\n💡 Recommendations ({len(assessment.recommendations)}):")
            for rec in assessment.recommendations:
                print(f"    • {rec}")
        
        print(f"\\n🔍 Field Validation Results:")
        passed = sum(1 for r in assessment.validation_results if r.is_valid)
        total = len(assessment.validation_results)
        print(f"    Passed: {passed}/{total} validations")
        
        for result in assessment.validation_results:
            status = "✅" if result.is_valid else "❌"
            print(f"    {status} {result.field_name}: {result.score:.2f}")
            if result.issues:
                for issue in result.issues:
                    print(f"        ⚠️  {issue}")
    
    def _print_summary_assessment(self, assessment: QualityAssessment):
        """Print summary assessment results"""
        grade_emoji = {
            DataQuality.HIGH: "🟢",
            DataQuality.MEDIUM: "🟡", 
            DataQuality.LOW: "🟠",
            DataQuality.UNVERIFIED: "🔴"
        }
        
        emoji = grade_emoji.get(assessment.quality_grade, "⚪")
        print(f"{emoji} {assessment.entity_type.capitalize()} #{assessment.entity_id}: "
              f"{assessment.overall_score:.1f}/100 ({assessment.quality_grade.value})")
        
        if assessment.issues_found:
            print(f"     Issues: {len(assessment.issues_found)}")
    
    def _print_bulk_summary(self, assessments: List[QualityAssessment], entity_type: str):
        """Print summary of bulk assessment"""
        if not assessments:
            print(f"No {entity_type} assessed.")
            return
        
        # Calculate summary statistics
        scores = [a.overall_score for a in assessments]
        avg_score = sum(scores) / len(scores)
        
        quality_counts = {}
        for assessment in assessments:
            grade = assessment.quality_grade
            quality_counts[grade] = quality_counts.get(grade, 0) + 1
        
        print(f"\\n📊 Quality Assessment Summary - {len(assessments)} {entity_type}")
        print(f"Average Score: {avg_score:.1f}/100")
        print(f"Score Range: {min(scores):.1f} - {max(scores):.1f}")
        
        print(f"\\nQuality Distribution:")
        for grade, count in quality_counts.items():
            percentage = (count / len(assessments)) * 100
            print(f"  {grade.value}: {count} ({percentage:.1f}%)")
        
        # Show bottom performers
        low_performers = sorted(assessments, key=lambda a: a.overall_score)[:5]
        print(f"\\n🚨 Lowest Quality {entity_type.capitalize()}:")
        for assessment in low_performers:
            self._print_summary_assessment(assessment)
    
    def _assessment_to_dict(self, assessment: QualityAssessment) -> Dict:
        """Convert assessment to dictionary for JSON serialization"""
        return {
            "entity_type": assessment.entity_type,
            "entity_id": assessment.entity_id,
            "overall_score": assessment.overall_score,
            "quality_grade": assessment.quality_grade.value,
            "component_scores": {
                "completeness": assessment.completeness_score,
                "accuracy": assessment.accuracy_score,
                "freshness": assessment.freshness_score,
                "consistency": assessment.consistency_score
            },
            "confidence_level": assessment.confidence_level,
            "issues_count": len(assessment.issues_found),
            "recommendations_count": len(assessment.recommendations),
            "issues": assessment.issues_found,
            "recommendations": assessment.recommendations,
            "validation_results": [
                {
                    "field": r.field_name,
                    "valid": r.is_valid,
                    "score": r.score,
                    "issues": r.issues
                } for r in assessment.validation_results
            ]
        }
    
    def _group_by_quality(self, assessments: List[QualityAssessment]) -> Dict:
        """Group assessments by quality grade"""
        groups = {}
        for assessment in assessments:
            grade = assessment.quality_grade.value
            if grade not in groups:
                groups[grade] = 0
            groups[grade] += 1
        return groups
    
    def _calculate_average_scores(self, assessments: List[QualityAssessment]) -> Dict:
        """Calculate average scores across all assessments"""
        if not assessments:
            return {}
        
        total_overall = sum(a.overall_score for a in assessments)
        total_completeness = sum(a.completeness_score for a in assessments)
        total_accuracy = sum(a.accuracy_score for a in assessments)
        total_freshness = sum(a.freshness_score for a in assessments)
        total_consistency = sum(a.consistency_score for a in assessments)
        
        count = len(assessments)
        
        return {
            "overall": total_overall / count,
            "completeness": total_completeness / count,
            "accuracy": total_accuracy / count,
            "freshness": total_freshness / count,
            "consistency": total_consistency / count
        }
    
    def _generate_overall_recommendations(self, assessments: List[QualityAssessment]) -> List[str]:
        """Generate overall recommendations based on all assessments"""
        all_issues = []
        for assessment in assessments:
            all_issues.extend(assessment.issues_found)
        
        # Count issue frequency
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        # Generate recommendations for most common issues
        recommendations = []
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        
        for issue, count in sorted_issues[:10]:
            if count > 1:
                recommendations.append(f"Address '{issue}' affecting {count} entities")
        
        return recommendations
    
    def _save_text_report(self, report_data: Dict, output_file: str):
        """Save report as text file"""
        with open(output_file, 'w') as f:
            f.write("DATA QUALITY REPORT\\n")
            f.write("="*50 + "\\n\\n")
            
            f.write(f"Generated: {report_data['report_generated']}\\n\\n")
            
            # Summary
            summary = report_data['summary']
            f.write("SUMMARY\\n")
            f.write("-"*20 + "\\n")
            f.write(f"Tools assessed: {summary['total_tools_assessed']}\\n")
            f.write(f"Companies assessed: {summary['total_companies_assessed']}\\n\\n")
            
            # Quality distribution
            f.write("QUALITY DISTRIBUTION\\n")
            f.write("-"*20 + "\\n")
            for grade, count in summary['tools_by_quality'].items():
                f.write(f"Tools - {grade}: {count}\\n")
            for grade, count in summary['companies_by_quality'].items():
                f.write(f"Companies - {grade}: {count}\\n")
            
            f.write("\\n")
            
            # Average scores
            avg = summary['average_scores']
            f.write("AVERAGE SCORES\\n")
            f.write("-"*20 + "\\n")
            f.write(f"Overall: {avg['overall']:.1f}\\n")
            f.write(f"Completeness: {avg['completeness']:.1f}\\n")
            f.write(f"Accuracy: {avg['accuracy']:.1f}\\n")
            f.write(f"Freshness: {avg['freshness']:.1f}\\n")
            f.write(f"Consistency: {avg['consistency']:.1f}\\n\\n")
            
            # Recommendations
            f.write("RECOMMENDATIONS\\n")
            f.write("-"*20 + "\\n")
            for rec in report_data['recommendations']:
                f.write(f"• {rec}\\n")
    
    def _print_report_summary(self, report_data: Dict):
        """Print report summary to console"""
        summary = report_data['summary']
        
        print(f"\\n📊 DATA QUALITY REPORT SUMMARY")
        print(f"Generated: {report_data['report_generated']}")
        print(f"\\nEntities Assessed:")
        print(f"  Tools: {summary['total_tools_assessed']}")
        print(f"  Companies: {summary['total_companies_assessed']}")
        
        print(f"\\nAverage Scores:")
        avg = summary['average_scores']
        print(f"  Overall: {avg['overall']:.1f}/100")
        print(f"  Completeness: {avg['completeness']:.1f}/100")
        print(f"  Accuracy: {avg['accuracy']:.1f}/100")
        print(f"  Freshness: {avg['freshness']:.1f}/100")
        print(f"  Consistency: {avg['consistency']:.1f}/100")
        
        if report_data['recommendations']:
            print(f"\\nTop Recommendations:")
            for rec in report_data['recommendations'][:5]:
                print(f"  • {rec}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Data Quality Assessment CLI")
    parser.add_argument('--database-url', help='Database URL')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Single tool assessment
    tool_parser = subparsers.add_parser('tool', help='Assess single tool quality')
    tool_parser.add_argument('tool_id', type=int, help='Tool ID to assess')
    tool_parser.add_argument('--verbose', '-v', action='store_true', help='Detailed output')
    
    # Bulk assessment
    bulk_parser = subparsers.add_parser('bulk', help='Assess all entities')
    bulk_parser.add_argument('--limit', type=int, help='Limit number of entities')
    bulk_parser.add_argument('--min-score', type=float, help='Minimum score filter')
    
    # Generate report
    report_parser = subparsers.add_parser('report', help='Generate quality report')
    report_parser.add_argument('--output', '-o', help='Output file path')
    report_parser.add_argument('--format', choices=['json', 'txt'], default='json', help='Output format')
    
    # Identify issues
    issues_parser = subparsers.add_parser('issues', help='Identify quality issues')
    issues_parser.add_argument('--min-score', type=float, default=70.0, help='Minimum quality score')
    
    # Track trends
    trends_parser = subparsers.add_parser('trends', help='Track quality trends')
    trends_parser.add_argument('--days', type=int, default=30, help='Number of days to analyze')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI
    cli = QualityReportCLI(args.database_url)
    
    try:
        if args.command == 'tool':
            cli.assess_single_tool(args.tool_id, args.verbose)
        
        elif args.command == 'bulk':
            cli.assess_all_tools(args.limit, args.min_score)
        
        elif args.command == 'report':
            cli.generate_quality_report(args.output, args.format)
        
        elif args.command == 'issues':
            cli.identify_quality_issues(args.min_score)
        
        elif args.command == 'trends':
            cli.track_quality_trends(args.days)
    
    except KeyboardInterrupt:
        print("\\n⏹️  Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()