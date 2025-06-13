# data_validation/quality_integration.py - Integration between quality scoring and curation systems

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_, desc

# Import required modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.enhanced_schema import *
from data_validation.quality_scorer import DataQualityScorer, QualityAssessment
from data_curation.curation_engine import DataCurationEngine, CurationResult


@dataclass
class QualityTriggeredTask:
    """Task triggered by quality assessment"""
    task_type: str  # 'urgent_review', 'data_refresh', 'validation_fix'
    priority: int
    entity_type: str
    entity_id: int
    quality_issue: str
    suggested_action: str
    estimated_effort: str  # 'low', 'medium', 'high'


class QualityIntegrationManager:
    """Manages integration between quality scoring and curation systems"""
    
    def __init__(self, database_url: str = None):
        from sqlalchemy import create_engine
        
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # Initialize component systems
        self.quality_scorer = DataQualityScorer(database_url)
        self.curation_engine = DataCurationEngine(database_url)
        
        # Quality thresholds for automated actions
        self.quality_thresholds = {
            'urgent_review': 30.0,      # Score below this triggers urgent review
            'auto_refresh': 50.0,       # Score below this triggers data refresh
            'validation_alert': 70.0,   # Score below this triggers validation alert
            'freshness_days': 30,       # Days before data is considered stale
            'consistency_threshold': 60.0  # Consistency score threshold
        }
        
        print("Quality Integration Manager initialized")
    
    def run_integrated_quality_check(self, tool_id: int) -> Dict:
        """
        Run comprehensive quality check with integrated curation actions
        
        Args:
            tool_id: ID of tool to check
            
        Returns:
            Dictionary with quality assessment and actions taken
        """
        session = self.Session()
        
        try:
            tool = session.query(Tool).filter_by(id=tool_id).first()
            if not tool:
                raise ValueError(f"Tool with ID {tool_id} not found")
            
            print(f"Running integrated quality check for: {tool.name}")
            
            # 1. Run quality assessment
            quality_assessment = self.quality_scorer.assess_tool_quality(tool_id, include_analysis=True)
            
            # 2. Determine if curation is needed based on quality
            curation_needed = self._should_trigger_curation(quality_assessment)
            curation_result = None
            
            if curation_needed:
                print(f"Quality score {quality_assessment.overall_score:.1f} triggers curation")
                curation_result = self.curation_engine.curate_tool_data(tool_id, force_analysis=True)
                
                # Re-assess quality after curation
                post_curation_assessment = self.quality_scorer.assess_tool_quality(tool_id, include_analysis=True)
                quality_improvement = post_curation_assessment.overall_score - quality_assessment.overall_score
                
                print(f"Quality improved by {quality_improvement:.1f} points after curation")
                quality_assessment = post_curation_assessment
            
            # 3. Generate quality-triggered tasks
            triggered_tasks = self._generate_quality_tasks(quality_assessment)
            
            # 4. Create curation tasks for manual review if needed
            manual_tasks = self._create_manual_curation_tasks(session, quality_assessment, triggered_tasks)
            
            # 5. Update tool quality metadata
            self._update_tool_quality_metadata(session, tool, quality_assessment)
            
            session.commit()
            
            result = {
                "tool_id": tool_id,
                "quality_assessment": {
                    "overall_score": quality_assessment.overall_score,
                    "quality_grade": quality_assessment.quality_grade.value,
                    "component_scores": {
                        "completeness": quality_assessment.completeness_score,
                        "accuracy": quality_assessment.accuracy_score,
                        "freshness": quality_assessment.freshness_score,
                        "consistency": quality_assessment.consistency_score
                    },
                    "confidence_level": quality_assessment.confidence_level,
                    "issues_found": quality_assessment.issues_found,
                    "recommendations": quality_assessment.recommendations
                },
                "curation_triggered": curation_needed,
                "curation_result": {
                    "version_created": curation_result.version_created if curation_result else False,
                    "changes_detected": len(curation_result.changes_detected) if curation_result else 0
                } if curation_result else None,
                "triggered_tasks": [self._task_to_dict(task) for task in triggered_tasks],
                "manual_tasks_created": len(manual_tasks),
                "actions_taken": self._summarize_actions(curation_needed, triggered_tasks, manual_tasks)
            }
            
            return result
            
        except Exception as e:
            session.rollback()
            print(f"Error in integrated quality check: {e}")
            raise
        finally:
            session.close()
    
    def run_quality_monitoring_sweep(self, max_tools: int = None) -> Dict:
        """
        Run quality monitoring across all tools with intelligent prioritization
        
        Args:
            max_tools: Maximum number of tools to process (None for all)
            
        Returns:
            Summary of quality monitoring results
        """
        session = self.Session()
        
        try:
            print("🔍 Starting quality monitoring sweep...")
            
            # Get tools prioritized by quality monitoring needs
            prioritized_tools = self._get_prioritized_tools_for_monitoring(session, max_tools)
            
            results = {
                "sweep_started": datetime.utcnow().isoformat(),
                "total_tools_processed": 0,
                "tools_needing_curation": 0,
                "urgent_issues_found": 0,
                "total_tasks_created": 0,
                "quality_improvements": [],
                "errors": []
            }
            
            for tool in prioritized_tools:
                try:
                    print(f"Processing tool: {tool.name} (priority: {tool.priority_level})")
                    
                    # Run integrated quality check
                    tool_result = self.run_integrated_quality_check(tool.id)
                    
                    results["total_tools_processed"] += 1
                    
                    if tool_result["curation_triggered"]:
                        results["tools_needing_curation"] += 1
                    
                    # Count urgent issues
                    quality_score = tool_result["quality_assessment"]["overall_score"]
                    if quality_score < self.quality_thresholds["urgent_review"]:
                        results["urgent_issues_found"] += 1
                    
                    results["total_tasks_created"] += len(tool_result["triggered_tasks"])
                    results["total_tasks_created"] += tool_result["manual_tasks_created"]
                    
                    # Track quality improvements
                    if tool_result["curation_triggered"]:
                        results["quality_improvements"].append({
                            "tool_id": tool.id,
                            "tool_name": tool.name,
                            "final_score": quality_score,
                            "changes_detected": tool_result["curation_result"]["changes_detected"]
                        })
                    
                except Exception as e:
                    error_info = {
                        "tool_id": tool.id,
                        "tool_name": tool.name,
                        "error": str(e)
                    }
                    results["errors"].append(error_info)
                    print(f"Error processing tool {tool.name}: {e}")
                    continue
            
            results["sweep_completed"] = datetime.utcnow().isoformat()
            
            # Print summary
            self._print_sweep_summary(results)
            
            return results
            
        except Exception as e:
            print(f"Error in quality monitoring sweep: {e}")
            raise
        finally:
            session.close()
    
    def create_quality_alerts(self, min_score: float = 50.0) -> List[Dict]:
        """Create alerts for tools with quality issues"""
        session = self.Session()
        alerts = []
        
        try:
            # Get recent quality reports below threshold
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            
            from models.enhanced_schema import DataQualityReport
            
            low_quality_reports = session.query(DataQualityReport).filter(
                and_(
                    DataQualityReport.report_date >= cutoff_date,
                    DataQualityReport.entity_type == 'tool',
                    or_(
                        (DataQualityReport.completeness_score + DataQualityReport.accuracy_score + 
                         DataQualityReport.freshness_score + DataQualityReport.consistency_score) / 4 < min_score,
                        DataQualityReport.overall_quality.in_([DataQuality.LOW, DataQuality.UNVERIFIED])
                    )
                )
            ).all()
            
            for report in low_quality_reports:
                tool = session.query(Tool).filter_by(id=report.entity_id).first()
                if not tool:
                    continue
                
                # Calculate overall score
                overall_score = (report.completeness_score + report.accuracy_score + 
                               report.freshness_score + report.consistency_score) / 4
                
                alert = {
                    "tool_id": tool.id,
                    "tool_name": tool.name,
                    "overall_score": overall_score,
                    "quality_grade": report.overall_quality.value,
                    "report_date": report.report_date.isoformat(),
                    "component_scores": {
                        "completeness": report.completeness_score,
                        "accuracy": report.accuracy_score,
                        "freshness": report.freshness_score,
                        "consistency": report.consistency_score
                    },
                    "issues": json.loads(report.issues_found) if report.issues_found else [],
                    "recommendations": json.loads(report.recommendations) if report.recommendations else [],
                    "alert_level": self._determine_alert_level(overall_score),
                    "suggested_actions": self._get_alert_actions(overall_score, tool)
                }
                
                alerts.append(alert)
            
            # Sort by severity (lowest scores first)
            alerts.sort(key=lambda x: x["overall_score"])
            
            print(f"Created {len(alerts)} quality alerts")
            return alerts
            
        except Exception as e:
            print(f"Error creating quality alerts: {e}")
            return []
        finally:
            session.close()
    
    def optimize_monitoring_schedule(self) -> Dict:
        """Optimize monitoring schedule based on quality patterns"""
        session = self.Session()
        
        try:
            print("🎯 Optimizing monitoring schedule based on quality patterns...")
            
            # Analyze quality patterns for all tools
            tools = session.query(Tool).filter(Tool.is_actively_monitored == True).all()
            
            schedule_updates = []
            
            for tool in tools:
                # Get recent quality assessments
                recent_reports = session.query(DataQualityReport).filter(
                    and_(
                        DataQualityReport.entity_type == 'tool',
                        DataQualityReport.entity_id == tool.id,
                        DataQualityReport.report_date >= datetime.utcnow() - timedelta(days=90)
                    )
                ).order_by(desc(DataQualityReport.report_date)).limit(10).all()
                
                if not recent_reports:
                    continue
                
                # Calculate quality trends
                scores = []
                for report in recent_reports:
                    overall = (report.completeness_score + report.accuracy_score + 
                             report.freshness_score + report.consistency_score) / 4
                    scores.append(overall)
                
                # Determine optimal frequency
                new_frequency = self._calculate_optimal_frequency(scores, tool.monitoring_frequency_days)
                
                if new_frequency != tool.monitoring_frequency_days:
                    old_frequency = tool.monitoring_frequency_days
                    tool.monitoring_frequency_days = new_frequency
                    
                    # Update next process date
                    tool.next_process_date = datetime.utcnow() + timedelta(days=new_frequency)
                    
                    schedule_updates.append({
                        "tool_id": tool.id,
                        "tool_name": tool.name,
                        "old_frequency": old_frequency,
                        "new_frequency": new_frequency,
                        "reason": self._get_frequency_reason(scores)
                    })
            
            session.commit()
            
            optimization_result = {
                "tools_analyzed": len(tools),
                "schedules_updated": len(schedule_updates),
                "updates": schedule_updates,
                "optimization_completed": datetime.utcnow().isoformat()
            }
            
            print(f"Updated monitoring schedule for {len(schedule_updates)} tools")
            return optimization_result
            
        except Exception as e:
            session.rollback()
            print(f"Error optimizing monitoring schedule: {e}")
            raise
        finally:
            session.close()
    
    def _should_trigger_curation(self, assessment: QualityAssessment) -> bool:
        """Determine if curation should be triggered based on quality assessment"""
        # Trigger curation if overall score is low
        if assessment.overall_score < self.quality_thresholds['auto_refresh']:
            return True
        
        # Trigger if freshness is very poor
        if assessment.freshness_score < 25.0:
            return True
        
        # Trigger if accuracy is poor
        if assessment.accuracy_score < 40.0:
            return True
        
        # Trigger if there are many validation issues
        failed_validations = sum(1 for r in assessment.validation_results if not r.is_valid)
        if failed_validations > 5:
            return True
        
        return False
    
    def _generate_quality_tasks(self, assessment: QualityAssessment) -> List[QualityTriggeredTask]:
        """Generate tasks based on quality assessment"""
        tasks = []
        
        # Urgent review for very low scores
        if assessment.overall_score < self.quality_thresholds['urgent_review']:
            tasks.append(QualityTriggeredTask(
                task_type='urgent_review',
                priority=1,
                entity_type=assessment.entity_type,
                entity_id=assessment.entity_id,
                quality_issue=f"Critical quality score: {assessment.overall_score:.1f}",
                suggested_action="Comprehensive manual review and data validation required",
                estimated_effort='high'
            ))
        
        # Data refresh for stale information
        if assessment.freshness_score < 50.0:
            tasks.append(QualityTriggeredTask(
                task_type='data_refresh',
                priority=2,
                entity_type=assessment.entity_type,
                entity_id=assessment.entity_id,
                quality_issue=f"Stale data: freshness score {assessment.freshness_score:.1f}",
                suggested_action="Run fresh analysis to update tool information",
                estimated_effort='medium'
            ))
        
        # Validation fixes for specific field issues
        validation_issues = [r for r in assessment.validation_results if not r.is_valid and r.score < 0.5]
        if validation_issues:
            for issue in validation_issues[:3]:  # Limit to top 3 issues
                tasks.append(QualityTriggeredTask(
                    task_type='validation_fix',
                    priority=3,
                    entity_type=assessment.entity_type,
                    entity_id=assessment.entity_id,
                    quality_issue=f"Validation failed: {issue.field_name}",
                    suggested_action=f"Fix validation issue: {'; '.join(issue.issues)}",
                    estimated_effort='low'
                ))
        
        # Consistency issues
        if assessment.consistency_score < self.quality_thresholds['consistency_threshold']:
            tasks.append(QualityTriggeredTask(
                task_type='consistency_review',
                priority=2,
                entity_type=assessment.entity_type,
                entity_id=assessment.entity_id,
                quality_issue=f"Data consistency issues: score {assessment.consistency_score:.1f}",
                suggested_action="Review and fix data consistency problems",
                estimated_effort='medium'
            ))
        
        return tasks
    
    def _create_manual_curation_tasks(self, session, assessment: QualityAssessment, 
                                    triggered_tasks: List[QualityTriggeredTask]) -> List[CurationTask]:
        """Create manual curation tasks in the database"""
        manual_tasks = []
        
        try:
            for triggered_task in triggered_tasks:
                # Map to curation task
                curation_task = CurationTask(
                    task_type=triggered_task.task_type,
                    priority=triggered_task.priority,
                    entity_type=triggered_task.entity_type,
                    entity_id=triggered_task.entity_id,
                    title=f"{triggered_task.task_type.replace('_', ' ').title()}: {triggered_task.quality_issue}",
                    description=triggered_task.suggested_action,
                    suggested_action=f"Effort: {triggered_task.estimated_effort}",
                    status='pending'
                )
                
                session.add(curation_task)
                manual_tasks.append(curation_task)
            
            session.flush()  # Get IDs
            
        except Exception as e:
            print(f"Error creating manual curation tasks: {e}")
            session.rollback()
        
        return manual_tasks
    
    def _update_tool_quality_metadata(self, session, tool: Tool, assessment: QualityAssessment):
        """Update tool with quality metadata"""
        try:
            tool.overall_data_quality = assessment.quality_grade
            tool.confidence_score = assessment.confidence_level
            tool.data_completeness = assessment.completeness_score
            
            # Update processing status based on quality
            if assessment.overall_score < self.quality_thresholds['urgent_review']:
                tool.processing_status = ProcessingStatus.NEEDS_REVIEW
            elif assessment.overall_score < self.quality_thresholds['validation_alert']:
                # Keep current status but don't mark as completed if quality is poor
                if tool.processing_status == ProcessingStatus.COMPLETED:
                    tool.processing_status = ProcessingStatus.NEEDS_REVIEW
            
        except Exception as e:
            print(f"Error updating tool quality metadata: {e}")
    
    def _get_prioritized_tools_for_monitoring(self, session, max_tools: int = None) -> List[Tool]:
        """Get tools prioritized for quality monitoring"""
        # Build prioritization query
        query = session.query(Tool).filter(Tool.is_actively_monitored == True)
        
        # Priority factors:
        # 1. Never processed tools (highest priority)
        # 2. Tools past their next process date
        # 3. Tools with high priority levels
        # 4. Tools with poor historical quality
        
        now = datetime.utcnow()
        
        # Get tools needing processing, ordered by priority
        tools = query.filter(
            or_(
                Tool.processing_status == ProcessingStatus.NEVER_RUN,
                Tool.next_process_date <= now,
                Tool.processing_status == ProcessingStatus.FAILED
            )
        ).order_by(
            Tool.priority_level.asc(),  # Lower priority number = higher priority
            Tool.last_processed_at.asc().nullsfirst()  # Older or never processed first
        )
        
        if max_tools:
            tools = tools.limit(max_tools)
        
        return tools.all()
    
    def _task_to_dict(self, task: QualityTriggeredTask) -> Dict:
        """Convert quality triggered task to dictionary"""
        return {
            "task_type": task.task_type,
            "priority": task.priority,
            "entity_type": task.entity_type,
            "entity_id": task.entity_id,
            "quality_issue": task.quality_issue,
            "suggested_action": task.suggested_action,
            "estimated_effort": task.estimated_effort
        }
    
    def _summarize_actions(self, curation_triggered: bool, triggered_tasks: List[QualityTriggeredTask], 
                          manual_tasks: List[CurationTask]) -> List[str]:
        """Summarize actions taken during quality check"""
        actions = []
        
        if curation_triggered:
            actions.append("Triggered automatic data curation")
        
        if triggered_tasks:
            actions.append(f"Generated {len(triggered_tasks)} quality improvement tasks")
        
        if manual_tasks:
            actions.append(f"Created {len(manual_tasks)} manual curation tasks")
        
        if not actions:
            actions.append("No immediate actions required - quality is acceptable")
        
        return actions
    
    def _print_sweep_summary(self, results: Dict):
        """Print summary of monitoring sweep results"""
        print(f"\\n📊 QUALITY MONITORING SWEEP SUMMARY")
        print(f"Tools processed: {results['total_tools_processed']}")
        print(f"Tools needing curation: {results['tools_needing_curation']}")
        print(f"Urgent issues found: {results['urgent_issues_found']}")
        print(f"Tasks created: {results['total_tasks_created']}")
        
        if results['quality_improvements']:
            print(f"\\n✅ Quality improvements:")
            for improvement in results['quality_improvements'][:5]:  # Show top 5
                print(f"  • {improvement['tool_name']}: score {improvement['final_score']:.1f}, "
                      f"{improvement['changes_detected']} changes")
        
        if results['errors']:
            print(f"\\n❌ Errors occurred:")
            for error in results['errors'][:3]:  # Show first 3 errors
                print(f"  • {error['tool_name']}: {error['error']}")
    
    def _determine_alert_level(self, score: float) -> str:
        """Determine alert level based on score"""
        if score < 30:
            return "critical"
        elif score < 50:
            return "high"
        elif score < 70:
            return "medium"
        else:
            return "low"
    
    def _get_alert_actions(self, score: float, tool: Tool) -> List[str]:
        """Get suggested actions for quality alert"""
        actions = []
        
        if score < 30:
            actions.extend([
                "Immediate manual review required",
                "Consider removing from active monitoring until fixed",
                "Run comprehensive data collection"
            ])
        elif score < 50:
            actions.extend([
                "Schedule manual review within 48 hours",
                "Run fresh analysis",
                "Verify core data fields"
            ])
        elif score < 70:
            actions.extend([
                "Schedule review within a week",
                "Update stale information",
                "Check for recent changes"
            ])
        
        # Add tool-specific suggestions
        if not tool.last_processed_at:
            actions.append("Run initial analysis - never processed")
        
        if not tool.company:
            actions.append("Add company information")
        
        return actions
    
    def _calculate_optimal_frequency(self, quality_scores: List[float], current_frequency: int) -> int:
        """Calculate optimal monitoring frequency based on quality trends"""
        if not quality_scores:
            return current_frequency
        
        avg_score = sum(quality_scores) / len(quality_scores)
        
        # Calculate score trend
        if len(quality_scores) >= 3:
            recent_avg = sum(quality_scores[:3]) / 3
            older_avg = sum(quality_scores[3:]) / len(quality_scores[3:]) if len(quality_scores) > 3 else recent_avg
            trend = recent_avg - older_avg
        else:
            trend = 0
        
        # Determine frequency based on average score and trend
        if avg_score < 40:
            return min(current_frequency, 3)  # More frequent for poor quality
        elif avg_score < 60:
            return min(current_frequency, 7)  # Weekly for medium quality
        elif avg_score > 85 and trend >= 0:
            return max(current_frequency, 14)  # Less frequent for high quality
        else:
            return current_frequency  # Keep current frequency
    
    def _get_frequency_reason(self, quality_scores: List[float]) -> str:
        """Get reason for frequency change"""
        if not quality_scores:
            return "No historical data"
        
        avg_score = sum(quality_scores) / len(quality_scores)
        
        if avg_score < 40:
            return "Poor quality requires frequent monitoring"
        elif avg_score < 60:
            return "Medium quality needs regular monitoring"
        elif avg_score > 85:
            return "High quality allows less frequent monitoring"
        else:
            return "Standard monitoring frequency maintained"


# Export main class
__all__ = ['QualityIntegrationManager', 'QualityTriggeredTask']