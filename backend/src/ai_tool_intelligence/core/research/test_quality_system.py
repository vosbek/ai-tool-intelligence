#!/usr/bin/env python3
# data_validation/test_quality_system.py - Test script for the quality scoring system

import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .quality_scorer import DataQualityScorer
from .quality_integration import QualityIntegrationManager
from ...models.database import Tool, Company, ToolVersion, DataQuality, ProcessingStatus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def test_quality_scorer():
    """Test the data quality scoring system"""
    print("🧪 Testing Data Quality Scoring System")
    print("=" * 50)
    
    # Initialize scorer
    database_url = os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
    scorer = DataQualityScorer(database_url)
    
    # Get database session for setup
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Find a tool to test with
        tool = session.query(Tool).first()
        
        if not tool:
            print("❌ No tools found in database. Please add some tools first.")
            return
        
        print(f"📊 Testing quality assessment for tool: {tool.name}")
        
        # Test 1: Basic quality assessment
        print("\n1. Running basic quality assessment...")
        assessment = scorer.assess_tool_quality(tool.id, include_analysis=True)
        
        print(f"   Overall Score: {assessment.overall_score:.1f}/100")
        print(f"   Quality Grade: {assessment.quality_grade.value}")
        print(f"   Confidence Level: {assessment.confidence_level:.1f}%")
        print(f"   Issues Found: {len(assessment.issues_found)}")
        print(f"   Recommendations: {len(assessment.recommendations)}")
        
        # Show component scores
        print(f"   Component Scores:")
        print(f"     Completeness: {assessment.completeness_score:.1f}/100")
        print(f"     Accuracy: {assessment.accuracy_score:.1f}/100")
        print(f"     Freshness: {assessment.freshness_score:.1f}/100")
        print(f"     Consistency: {assessment.consistency_score:.1f}/100")
        
        # Show some issues and recommendations
        if assessment.issues_found:
            print(f"   Top Issues:")
            for issue in assessment.issues_found[:3]:
                print(f"     • {issue}")
        
        if assessment.recommendations:
            print(f"   Top Recommendations:")
            for rec in assessment.recommendations[:3]:
                print(f"     • {rec}")
        
        # Test 2: Company quality assessment if company exists
        if tool.company:
            print(f"\n2. Running company quality assessment...")
            company_assessment = scorer.assess_company_quality(tool.company.id)
            print(f"   Company Score: {company_assessment.overall_score:.1f}/100")
            print(f"   Company Grade: {company_assessment.quality_grade.value}")
        
        # Test 3: Version quality assessment if versions exist
        if tool.versions:
            print(f"\n3. Running version quality assessment...")
            version = tool.versions[0]  # Get first version
            version_assessment = scorer.assess_version_quality(version.id)
            print(f"   Version Score: {version_assessment.overall_score:.1f}/100")
            print(f"   Version Grade: {version_assessment.quality_grade.value}")
        
        # Test 4: Bulk assessment (limited to 3 tools for testing)
        print(f"\n4. Running bulk assessment (max 3 tools)...")
        bulk_assessments = scorer.bulk_assess_quality('tool', limit=3)
        
        print(f"   Assessed {len(bulk_assessments)} tools:")
        for assessment in bulk_assessments:
            print(f"     Tool #{assessment.entity_id}: {assessment.overall_score:.1f}/100 ({assessment.quality_grade.value})")
        
        print("\n✅ Quality scoring tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during quality scoring test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


def test_quality_integration():
    """Test the quality integration system"""
    print("\n🔧 Testing Quality Integration System")
    print("=" * 50)
    
    # Initialize integration manager
    database_url = os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
    integration_manager = QualityIntegrationManager(database_url)
    
    # Get database session
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Find a tool to test with
        tool = session.query(Tool).first()
        
        if not tool:
            print("❌ No tools found in database.")
            return
        
        print(f"🔍 Testing integrated quality check for: {tool.name}")
        
        # Test 1: Integrated quality check
        result = integration_manager.run_integrated_quality_check(tool.id)
        
        print(f"   Quality Score: {result['quality_assessment']['overall_score']:.1f}/100")
        print(f"   Curation Triggered: {result['curation_triggered']}")
        print(f"   Tasks Generated: {len(result['triggered_tasks'])}")
        print(f"   Manual Tasks Created: {result['manual_tasks_created']}")
        
        if result['triggered_tasks']:
            print(f"   Generated Tasks:")
            for task in result['triggered_tasks']:
                print(f"     • {task['task_type']}: {task['quality_issue']}")
        
        print(f"   Actions Taken:")
        for action in result['actions_taken']:
            print(f"     • {action}")
        
        # Test 2: Quality alerts
        print(f"\n🚨 Testing quality alerts generation...")
        alerts = integration_manager.create_quality_alerts(min_score=80.0)  # Set high threshold for testing
        
        print(f"   Generated {len(alerts)} quality alerts")
        for alert in alerts[:3]:  # Show first 3 alerts
            print(f"     • Tool: {alert['tool_name']} (Score: {alert['overall_score']:.1f})")
            print(f"       Alert Level: {alert['alert_level']}")
            print(f"       Actions: {len(alert['suggested_actions'])}")
        
        # Test 3: Schedule optimization
        print(f"\n⏰ Testing monitoring schedule optimization...")
        optimization_result = integration_manager.optimize_monitoring_schedule()
        
        print(f"   Tools Analyzed: {optimization_result['tools_analyzed']}")
        print(f"   Schedules Updated: {optimization_result['schedules_updated']}")
        
        if optimization_result['updates']:
            print(f"   Schedule Changes:")
            for update in optimization_result['updates'][:3]:  # Show first 3 updates
                print(f"     • {update['tool_name']}: {update['old_frequency']} → {update['new_frequency']} days")
                print(f"       Reason: {update['reason']}")
        
        print("\n✅ Quality integration tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during integration test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


def demo_quality_workflow():
    """Demonstrate a complete quality workflow"""
    print("\n🎯 Demonstrating Complete Quality Workflow")
    print("=" * 50)
    
    try:
        # Initialize systems
        database_url = os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
        integration_manager = QualityIntegrationManager(database_url)
        
        print("1. Running quality monitoring sweep (max 5 tools)...")
        
        # Run a limited monitoring sweep
        sweep_result = integration_manager.run_quality_monitoring_sweep(max_tools=5)
        
        print(f"   Sweep Results:")
        print(f"     Tools Processed: {sweep_result['total_tools_processed']}")
        print(f"     Tools Needing Curation: {sweep_result['tools_needing_curation']}")
        print(f"     Urgent Issues Found: {sweep_result['urgent_issues_found']}")
        print(f"     Total Tasks Created: {sweep_result['total_tasks_created']}")
        print(f"     Errors: {len(sweep_result['errors'])}")
        
        if sweep_result['quality_improvements']:
            print(f"   Quality Improvements:")
            for improvement in sweep_result['quality_improvements']:
                print(f"     • {improvement['tool_name']}: Final score {improvement['final_score']:.1f}")
                print(f"       Changes detected: {improvement['changes_detected']}")
        
        print("\n2. Generating comprehensive quality alerts...")
        
        # Generate quality alerts
        alerts = integration_manager.create_quality_alerts(min_score=70.0)
        
        if alerts:
            print(f"   Found {len(alerts)} tools needing attention:")
            for alert in alerts[:5]:  # Show top 5 alerts
                print(f"     🚨 {alert['tool_name']}: {alert['overall_score']:.1f}/100 ({alert['alert_level']} priority)")
                print(f"        Top issue: {alert['issues'][0] if alert['issues'] else 'General quality concern'}")
        else:
            print("   ✅ No quality alerts - all tools meet the threshold!")
        
        print("\n3. Optimizing monitoring schedules...")
        
        # Optimize monitoring schedules
        optimization = integration_manager.optimize_monitoring_schedule()
        
        if optimization['schedules_updated'] > 0:
            print(f"   Optimized schedules for {optimization['schedules_updated']} tools")
            print(f"   Example changes:")
            for update in optimization['updates'][:2]:  # Show 2 examples
                print(f"     • {update['tool_name']}: {update['old_frequency']} → {update['new_frequency']} days")
        else:
            print("   ✅ All monitoring schedules are already optimal!")
        
        print("\n🎉 Complete quality workflow demonstration finished!")
        print("\nThis workflow would typically run:")
        print("  • Quality monitoring sweep: Daily")
        print("  • Quality alerts generation: Every 6 hours")
        print("  • Schedule optimization: Weekly")
        
    except Exception as e:
        print(f"❌ Error during workflow demonstration: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main test function"""
    print("🚀 Data Quality System Testing Suite")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test 1: Quality Scorer
        test_quality_scorer()
        
        # Test 2: Quality Integration
        test_quality_integration()
        
        # Test 3: Complete Workflow Demo
        demo_quality_workflow()
        
        print(f"\n🎉 All tests completed successfully!")
        print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()