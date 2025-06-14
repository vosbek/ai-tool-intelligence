# admin_interface/admin_manager.py - Comprehensive admin interface for data review and curation

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import csv
import io
from collections import defaultdict, Counter

# Import required modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ...models.database import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_, or_, desc, func, text

# Import system components
try:
    from data_curation.curation_engine import CurationEngine
    from ...core.competitive.market_analyzer import MarketAnalyzer
    from ...core.competitive.trend_tracker import TrendTracker
    from change_detection.alert_manager import ChangeAlertManager
    from ...core.research.quality_scorer import DataQualityScorer
except ImportError:
    print("Warning: Some admin components not available")


class AdminActionType(Enum):
    """Types of admin actions"""
    DATA_REVIEW = "data_review"
    MANUAL_CURATION = "manual_curation"
    QUALITY_OVERRIDE = "quality_override"
    ALERT_MANAGEMENT = "alert_management"
    SYSTEM_CONFIG = "system_config"
    BULK_OPERATION = "bulk_operation"
    DATA_EXPORT = "data_export"


class ReviewStatus(Enum):
    """Status of data reviews"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


@dataclass
class AdminAction:
    """Individual admin action record"""
    action_id: str
    action_type: AdminActionType
    admin_user: str
    target_entity: str  # tool_id, category_id, etc.
    action_description: str
    action_data: Dict[str, Any]
    timestamp: datetime
    result: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class DataReviewItem:
    """Item requiring admin review"""
    review_id: str
    item_type: str  # 'tool', 'change', 'quality_issue'
    item_id: int
    priority: str  # 'critical', 'high', 'medium', 'low'
    status: ReviewStatus
    created_at: datetime
    assigned_to: Optional[str]
    description: str
    data_snapshot: Dict[str, Any]
    review_notes: List[str]
    resolution: Optional[str] = None


@dataclass
class AdminDashboardData:
    """Data for admin dashboard"""
    # System overview
    total_tools: int
    active_monitoring: int
    pending_reviews: int
    quality_issues: int
    recent_alerts: int
    
    # Data quality metrics
    avg_quality_score: float
    low_quality_tools: int
    data_completeness: float
    
    # Processing statistics
    daily_curation_count: int
    weekly_analysis_count: int
    error_rate: float
    
    # Review queue
    critical_reviews: List[DataReviewItem]
    pending_approvals: List[DataReviewItem]
    
    # Recent activity
    recent_actions: List[AdminAction]
    system_health: Dict[str, Any]


class AdminInterfaceManager:
    """Comprehensive admin interface for data review and curation management"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # Initialize system components
        try:
            self.curation_engine = CurationEngine(self.database_url)
            self.market_analyzer = MarketAnalyzer(self.database_url)
            self.trend_tracker = TrendTracker(self.database_url)
            self.alert_manager = ChangeAlertManager(self.database_url)
            self.quality_scorer = DataQualityScorer(self.database_url)
        except:
            print("Warning: Some admin components not available")
        
        # Admin configuration
        self.admin_config = {
            'auto_approve_threshold': 0.9,  # Quality score threshold for auto-approval
            'review_timeout_days': 7,
            'critical_quality_threshold': 0.5,
            'batch_size_limit': 100
        }
        
        print("Admin Interface Manager initialized")
    
    def get_dashboard_data(self, admin_user: str) -> AdminDashboardData:
        """
        Get comprehensive dashboard data for admin interface
        
        Args:
            admin_user: Username of the admin
            
        Returns:
            AdminDashboardData with all dashboard metrics
        """
        session = self.Session()
        
        try:
            print(f"📊 Generating admin dashboard for {admin_user}...")
            
            # System overview metrics
            total_tools = session.query(Tool).count()
            active_monitoring = session.query(Tool).filter_by(is_actively_monitored=True).count()
            
            # Review queue metrics
            pending_reviews = self._count_pending_reviews(session)
            quality_issues = self._count_quality_issues(session)
            
            # Recent alerts
            cutoff_date = datetime.utcnow() - timedelta(days=1)
            recent_alerts = session.query(CurationTask).filter(
                and_(
                    CurationTask.task_type == 'alert',
                    CurationTask.created_at >= cutoff_date
                )
            ).count()
            
            # Data quality metrics
            quality_metrics = self._calculate_quality_metrics(session)
            
            # Processing statistics
            processing_stats = self._calculate_processing_stats(session)
            
            # Get review items
            critical_reviews = self._get_critical_reviews(session)
            pending_approvals = self._get_pending_approvals(session)
            
            # Recent admin actions
            recent_actions = self._get_recent_admin_actions(session, admin_user)
            
            # System health
            system_health = self._assess_system_health(session)
            
            # Create dashboard data
            dashboard = AdminDashboardData(
                total_tools=total_tools,
                active_monitoring=active_monitoring,
                pending_reviews=pending_reviews,
                quality_issues=quality_issues,
                recent_alerts=recent_alerts,
                avg_quality_score=quality_metrics['avg_score'],
                low_quality_tools=quality_metrics['low_quality_count'],
                data_completeness=quality_metrics['completeness'],
                daily_curation_count=processing_stats['daily_curation'],
                weekly_analysis_count=processing_stats['weekly_analysis'],
                error_rate=processing_stats['error_rate'],
                critical_reviews=critical_reviews,
                pending_approvals=pending_approvals,
                recent_actions=recent_actions,
                system_health=system_health
            )
            
            session.close()
            
            print(f"✅ Dashboard data generated: {total_tools} tools, {pending_reviews} pending reviews")
            return dashboard
            
        except Exception as e:
            session.rollback()
            print(f"Error generating dashboard data: {e}")
            raise
        finally:
            session.close()
    
    def review_tool_data(self, tool_id: int, admin_user: str, action: str, notes: str = None) -> Dict:
        """
        Review and take action on tool data
        
        Args:
            tool_id: Tool to review
            admin_user: Admin performing the review
            action: Action to take ('approve', 'reject', 'flag', 'edit')
            notes: Optional review notes
            
        Returns:
            Result of the review action
        """
        session = self.Session()
        
        try:
            print(f"📋 Reviewing tool {tool_id} by {admin_user}: {action}")
            
            tool = session.query(Tool).filter_by(id=tool_id).first()
            if not tool:
                return {"error": f"Tool {tool_id} not found"}
            
            # Create admin action record
            admin_action = AdminAction(
                action_id=f"review_{tool_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                action_type=AdminActionType.DATA_REVIEW,
                admin_user=admin_user,
                target_entity=f"tool_{tool_id}",
                action_description=f"Tool review: {action}",
                action_data={
                    "tool_name": tool.name,
                    "action": action,
                    "notes": notes
                },
                timestamp=datetime.utcnow(),
                notes=notes
            )
            
            result = {}
            
            if action == 'approve':
                result = self._approve_tool_data(session, tool, admin_user, notes)
            elif action == 'reject':
                result = self._reject_tool_data(session, tool, admin_user, notes)
            elif action == 'flag':
                result = self._flag_tool_data(session, tool, admin_user, notes)
            elif action == 'edit':
                result = self._prepare_tool_edit(session, tool, admin_user)
            else:
                result = {"error": f"Unknown action: {action}"}
            
            # Store admin action
            admin_action.result = json.dumps(result)
            self._store_admin_action(session, admin_action)
            
            session.commit()
            
            print(f"✅ Tool review completed: {action}")
            return result
            
        except Exception as e:
            session.rollback()
            print(f"Error reviewing tool data: {e}")
            return {"error": str(e)}
        finally:
            session.close()
    
    def bulk_curation_operation(self, operation_type: str, target_filters: Dict, 
                              admin_user: str, dry_run: bool = True) -> Dict:
        """
        Perform bulk curation operations
        
        Args:
            operation_type: Type of operation ('recurate', 'approve', 'flag', 'quality_check')
            target_filters: Filters to select target tools
            admin_user: Admin performing the operation
            dry_run: If True, just show what would be affected
            
        Returns:
            Result of bulk operation
        """
        session = self.Session()
        
        try:
            print(f"🔄 Bulk operation '{operation_type}' by {admin_user} (dry_run: {dry_run})")
            
            # Build query based on filters
            query = session.query(Tool)
            
            if target_filters.get('category_ids'):
                query = query.filter(Tool.category_id.in_(target_filters['category_ids']))
            
            if target_filters.get('quality_threshold'):
                query = query.filter(Tool.confidence_score < target_filters['quality_threshold'])
            
            if target_filters.get('last_updated_days'):
                cutoff_date = datetime.utcnow() - timedelta(days=target_filters['last_updated_days'])
                query = query.filter(Tool.last_processed_at < cutoff_date)
            
            if target_filters.get('processing_status'):
                query = query.filter(Tool.processing_status == target_filters['processing_status'])
            
            # Limit for safety
            tools = query.limit(self.admin_config['batch_size_limit']).all()
            
            if dry_run:
                # Just return what would be affected
                return {
                    "operation": operation_type,
                    "affected_count": len(tools),
                    "affected_tools": [
                        {
                            "id": t.id,
                            "name": t.name,
                            "category": t.category.name if t.category else "Unknown",
                            "quality_score": t.confidence_score or 0,
                            "last_updated": t.last_processed_at.isoformat() if t.last_processed_at else None
                        } for t in tools
                    ],
                    "dry_run": True
                }
            
            # Perform actual operation
            results = []
            
            for tool in tools:
                try:
                    if operation_type == 'recurate':
                        result = self.curation_engine.curate_tool_data(tool.id)
                    elif operation_type == 'approve':
                        result = self._approve_tool_data(session, tool, admin_user, "Bulk approval")
                    elif operation_type == 'flag':
                        result = self._flag_tool_data(session, tool, admin_user, "Bulk flag")
                    elif operation_type == 'quality_check':
                        result = self._perform_quality_check(tool)
                    else:
                        result = {"error": f"Unknown operation: {operation_type}"}
                    
                    results.append({
                        "tool_id": tool.id,
                        "tool_name": tool.name,
                        "result": result
                    })
                    
                except Exception as e:
                    results.append({
                        "tool_id": tool.id,
                        "tool_name": tool.name,
                        "error": str(e)
                    })
            
            # Create bulk admin action
            admin_action = AdminAction(
                action_id=f"bulk_{operation_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                action_type=AdminActionType.BULK_OPERATION,
                admin_user=admin_user,
                target_entity="bulk_operation",
                action_description=f"Bulk {operation_type} on {len(tools)} tools",
                action_data={
                    "operation_type": operation_type,
                    "filters": target_filters,
                    "affected_count": len(tools)
                },
                timestamp=datetime.utcnow(),
                result=json.dumps({"success_count": len([r for r in results if 'error' not in r])})
            )
            
            self._store_admin_action(session, admin_action)
            session.commit()
            
            success_count = len([r for r in results if 'error' not in r])
            error_count = len([r for r in results if 'error' in r])
            
            print(f"✅ Bulk operation completed: {success_count} success, {error_count} errors")
            
            return {
                "operation": operation_type,
                "total_processed": len(tools),
                "success_count": success_count,
                "error_count": error_count,
                "results": results,
                "dry_run": False
            }
            
        except Exception as e:
            session.rollback()
            print(f"Error in bulk operation: {e}")
            return {"error": str(e)}
        finally:
            session.close()
    
    def manage_alert_rules(self, action: str, rule_data: Dict = None, 
                          rule_id: str = None, admin_user: str = None) -> Dict:
        """
        Manage alert rules through admin interface
        
        Args:
            action: Action to perform ('create', 'update', 'delete', 'list', 'test')
            rule_data: Rule configuration data
            rule_id: ID of rule to modify
            admin_user: Admin performing the action
            
        Returns:
            Result of alert rule management
        """
        try:
            print(f"🚨 Managing alert rules: {action} by {admin_user}")
            
            if action == 'list':
                return self.alert_manager.list_alert_rules()
            
            elif action == 'create':
                if not rule_data:
                    return {"error": "Rule data required for creation"}
                
                result = self.alert_manager.create_custom_alert_rule(rule_data)
                
                # Log admin action
                admin_action = AdminAction(
                    action_id=f"alert_create_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    action_type=AdminActionType.ALERT_MANAGEMENT,
                    admin_user=admin_user,
                    target_entity=f"alert_rule_{rule_data.get('rule_id')}",
                    action_description="Created new alert rule",
                    action_data=rule_data,
                    timestamp=datetime.utcnow(),
                    result=json.dumps(result)
                )
                
                session = self.Session()
                self._store_admin_action(session, admin_action)
                session.commit()
                session.close()
                
                return result
            
            elif action == 'update':
                if not rule_id or not rule_data:
                    return {"error": "Rule ID and data required for update"}
                
                result = self.alert_manager.update_alert_rule(rule_id, rule_data)
                return result
            
            elif action == 'delete':
                if not rule_id:
                    return {"error": "Rule ID required for deletion"}
                
                result = self.alert_manager.delete_alert_rule(rule_id)
                return result
            
            elif action == 'test':
                if not rule_id:
                    return {"error": "Rule ID required for testing"}
                
                result = self.alert_manager.test_alert_rule(rule_id)
                return result
            
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            print(f"Error managing alert rules: {e}")
            return {"error": str(e)}
    
    def export_data(self, export_type: str, filters: Dict = None, 
                   format: str = 'json', admin_user: str = None) -> Dict:
        """
        Export data for admin analysis
        
        Args:
            export_type: Type of data to export ('tools', 'changes', 'quality', 'competitive')
            filters: Filters to apply to export
            format: Export format ('json', 'csv', 'excel')
            admin_user: Admin performing the export
            
        Returns:
            Export result with data or file path
        """
        session = self.Session()
        
        try:
            print(f"📤 Exporting {export_type} data in {format} format by {admin_user}")
            
            if export_type == 'tools':
                data = self._export_tools_data(session, filters)
            elif export_type == 'changes':
                data = self._export_changes_data(session, filters)
            elif export_type == 'quality':
                data = self._export_quality_data(session, filters)
            elif export_type == 'competitive':
                data = self._export_competitive_data(session, filters)
            else:
                return {"error": f"Unknown export type: {export_type}"}
            
            # Format data based on requested format
            if format == 'json':
                export_result = {
                    "data": data,
                    "export_type": export_type,
                    "timestamp": datetime.utcnow().isoformat(),
                    "record_count": len(data) if isinstance(data, list) else len(data.get('records', []))
                }
            
            elif format == 'csv':
                export_result = self._export_to_csv(data, export_type)
            
            elif format == 'excel':
                export_result = self._export_to_excel(data, export_type)
            
            else:
                return {"error": f"Unsupported format: {format}"}
            
            # Log admin action
            admin_action = AdminAction(
                action_id=f"export_{export_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                action_type=AdminActionType.DATA_EXPORT,
                admin_user=admin_user,
                target_entity=f"export_{export_type}",
                action_description=f"Data export: {export_type} ({format})",
                action_data={
                    "export_type": export_type,
                    "format": format,
                    "filters": filters,
                    "record_count": len(data) if isinstance(data, list) else len(data.get('records', []))
                },
                timestamp=datetime.utcnow()
            )
            
            self._store_admin_action(session, admin_action)
            session.commit()
            
            print(f"✅ Data export completed: {export_type} ({format})")
            return export_result
            
        except Exception as e:
            session.rollback()
            print(f"Error exporting data: {e}")
            return {"error": str(e)}
        finally:
            session.close()
    
    def get_system_analytics(self, time_range: int = 30, admin_user: str = None) -> Dict:
        """
        Get comprehensive system analytics for admin review
        
        Args:
            time_range: Number of days to analyze
            admin_user: Admin requesting analytics
            
        Returns:
            Comprehensive system analytics
        """
        session = self.Session()
        
        try:
            print(f"📈 Generating system analytics for {time_range} days by {admin_user}")
            
            cutoff_date = datetime.utcnow() - timedelta(days=time_range)
            
            # Processing statistics
            processing_stats = self._get_processing_analytics(session, cutoff_date)
            
            # Quality trends
            quality_trends = self._get_quality_analytics(session, cutoff_date)
            
            # Alert analytics
            alert_stats = self._get_alert_analytics(session, cutoff_date)
            
            # Competitive analytics
            competitive_stats = self._get_competitive_analytics(session, cutoff_date)
            
            # System performance
            performance_stats = self._get_performance_analytics(session, cutoff_date)
            
            # Admin activity
            admin_activity = self._get_admin_activity_analytics(session, cutoff_date)
            
            analytics = {
                "time_range_days": time_range,
                "generated_at": datetime.utcnow().isoformat(),
                "generated_by": admin_user,
                "processing_statistics": processing_stats,
                "quality_trends": quality_trends,
                "alert_statistics": alert_stats,
                "competitive_analytics": competitive_stats,
                "system_performance": performance_stats,
                "admin_activity": admin_activity
            }
            
            session.close()
            
            print(f"✅ System analytics generated for {time_range} days")
            return analytics
            
        except Exception as e:
            session.rollback()
            print(f"Error generating system analytics: {e}")
            return {"error": str(e)}
        finally:
            session.close()
    
    # Helper methods for internal operations
    
    def _count_pending_reviews(self, session) -> int:
        """Count items pending admin review"""
        # Count tools with low quality scores
        low_quality = session.query(Tool).filter(
            Tool.confidence_score < self.admin_config['critical_quality_threshold']
        ).count()
        
        # Count failed curation tasks
        failed_tasks = session.query(CurationTask).filter_by(status='failed').count()
        
        return low_quality + failed_tasks
    
    def _count_quality_issues(self, session) -> int:
        """Count data quality issues"""
        return session.query(Tool).filter(
            or_(
                Tool.confidence_score < self.admin_config['critical_quality_threshold'],
                Tool.description.is_(None),
                Tool.website_url.is_(None)
            )
        ).count()
    
    def _calculate_quality_metrics(self, session) -> Dict:
        """Calculate overall data quality metrics"""
        tools = session.query(Tool).all()
        
        if not tools:
            return {"avg_score": 0, "low_quality_count": 0, "completeness": 0}
        
        quality_scores = [t.confidence_score or 0 for t in tools]
        avg_score = statistics.mean(quality_scores)
        
        low_quality_count = len([s for s in quality_scores if s < self.admin_config['critical_quality_threshold']])
        
        # Calculate completeness (tools with basic required fields)
        complete_tools = len([
            t for t in tools 
            if t.description and t.website_url and t.category_id
        ])
        completeness = (complete_tools / len(tools)) * 100
        
        return {
            "avg_score": avg_score,
            "low_quality_count": low_quality_count,
            "completeness": completeness
        }
    
    def _calculate_processing_stats(self, session) -> Dict:
        """Calculate processing statistics"""
        # Daily curation count
        today = datetime.utcnow().date()
        daily_curation = session.query(CurationTask).filter(
            func.date(CurationTask.created_at) == today
        ).count()
        
        # Weekly analysis count
        week_ago = datetime.utcnow() - timedelta(days=7)
        weekly_analysis = session.query(CompetitiveAnalysis).filter(
            CompetitiveAnalysis.analysis_date >= week_ago
        ).count()
        
        # Error rate
        total_tasks = session.query(CurationTask).count()
        failed_tasks = session.query(CurationTask).filter_by(status='failed').count()
        error_rate = (failed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            "daily_curation": daily_curation,
            "weekly_analysis": weekly_analysis,
            "error_rate": error_rate
        }
    
    def _get_critical_reviews(self, session) -> List[DataReviewItem]:
        """Get critical items requiring immediate review"""
        reviews = []
        
        # Tools with very low quality scores
        critical_tools = session.query(Tool).filter(
            Tool.confidence_score < 0.3
        ).limit(10).all()
        
        for tool in critical_tools:
            review = DataReviewItem(
                review_id=f"critical_tool_{tool.id}",
                item_type="tool",
                item_id=tool.id,
                priority="critical",
                status=ReviewStatus.PENDING,
                created_at=datetime.utcnow(),
                assigned_to=None,
                description=f"Critical quality issue: {tool.name}",
                data_snapshot={
                    "name": tool.name,
                    "quality_score": tool.confidence_score,
                    "last_updated": tool.last_processed_at.isoformat() if tool.last_processed_at else None
                },
                review_notes=[]
            )
            reviews.append(review)
        
        return reviews
    
    def _get_pending_approvals(self, session) -> List[DataReviewItem]:
        """Get items pending approval"""
        reviews = []
        
        # Recent changes requiring approval
        recent_changes = session.query(ToolChange).filter(
            ToolChange.detected_at >= datetime.utcnow() - timedelta(days=1)
        ).limit(10).all()
        
        for change in recent_changes:
            review = DataReviewItem(
                review_id=f"approval_change_{change.id}",
                item_type="change",
                item_id=change.id,
                priority="medium",
                status=ReviewStatus.PENDING,
                created_at=change.detected_at,
                assigned_to=None,
                description=f"Change approval: {change.change_type.value}",
                data_snapshot={
                    "change_type": change.change_type.value,
                    "field_name": change.field_name,
                    "old_value": change.old_value,
                    "new_value": change.new_value
                },
                review_notes=[]
            )
            reviews.append(review)
        
        return reviews
    
    def _get_recent_admin_actions(self, session, admin_user: str, limit: int = 10) -> List[AdminAction]:
        """Get recent admin actions"""
        # This would query admin actions from a dedicated table
        # For now, return mock data
        return []
    
    def _assess_system_health(self, session) -> Dict[str, Any]:
        """Assess overall system health"""
        health = {
            "database_connection": "healthy",
            "data_quality": "good",
            "processing_pipeline": "operational",
            "alert_system": "active",
            "competitive_analysis": "running"
        }
        
        # Check for any critical issues
        critical_issues = session.query(Tool).filter(
            Tool.confidence_score < 0.2
        ).count()
        
        if critical_issues > 10:
            health["data_quality"] = "degraded"
        
        return health
    
    def _approve_tool_data(self, session, tool: Tool, admin_user: str, notes: str) -> Dict:
        """Approve tool data"""
        tool.confidence_score = max(tool.confidence_score or 0, self.admin_config['auto_approve_threshold'])
        tool.processing_status = 'approved'
        
        return {
            "action": "approved",
            "tool_id": tool.id,
            "new_quality_score": tool.confidence_score,
            "approved_by": admin_user,
            "notes": notes
        }
    
    def _reject_tool_data(self, session, tool: Tool, admin_user: str, notes: str) -> Dict:
        """Reject tool data"""
        tool.processing_status = 'rejected'
        
        return {
            "action": "rejected",
            "tool_id": tool.id,
            "rejected_by": admin_user,
            "notes": notes
        }
    
    def _flag_tool_data(self, session, tool: Tool, admin_user: str, notes: str) -> Dict:
        """Flag tool data for review"""
        tool.processing_status = 'flagged'
        
        return {
            "action": "flagged",
            "tool_id": tool.id,
            "flagged_by": admin_user,
            "notes": notes
        }
    
    def _prepare_tool_edit(self, session, tool: Tool, admin_user: str) -> Dict:
        """Prepare tool for editing"""
        return {
            "action": "edit_prepared",
            "tool_id": tool.id,
            "edit_session": f"edit_{tool.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "prepared_by": admin_user
        }
    
    def _perform_quality_check(self, tool: Tool) -> Dict:
        """Perform quality check on tool"""
        try:
            score = self.quality_scorer.calculate_tool_quality_score(tool.id)
            return {
                "quality_check": "completed",
                "quality_score": score,
                "tool_id": tool.id
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _store_admin_action(self, session, action: AdminAction):
        """Store admin action in database"""
        # Create CurationTask record for admin action tracking
        task = CurationTask(
            tool_id=int(action.target_entity.split('_')[-1]) if action.target_entity.startswith('tool_') else None,
            task_type='admin_action',
            priority='medium',
            assigned_to=action.admin_user,
            status='completed',
            description=action.action_description,
            created_at=action.timestamp,
            updated_at=action.timestamp,
            metadata=json.dumps(asdict(action))
        )
        session.add(task)
    
    # Export helper methods
    
    def _export_tools_data(self, session, filters: Dict) -> List[Dict]:
        """Export tools data"""
        query = session.query(Tool)
        
        if filters and filters.get('category_id'):
            query = query.filter_by(category_id=filters['category_id'])
        
        tools = query.all()
        
        return [
            {
                "id": t.id,
                "name": t.name,
                "category": t.category.name if t.category else None,
                "description": t.description,
                "website_url": t.website_url,
                "quality_score": t.confidence_score,
                "processing_status": t.processing_status,
                "last_updated": t.last_processed_at.isoformat() if t.last_processed_at else None
            } for t in tools
        ]
    
    def _export_changes_data(self, session, filters: Dict) -> List[Dict]:
        """Export changes data"""
        query = session.query(ToolChange)
        
        if filters and filters.get('days'):
            cutoff_date = datetime.utcnow() - timedelta(days=filters['days'])
            query = query.filter(ToolChange.detected_at >= cutoff_date)
        
        changes = query.all()
        
        return [
            {
                "id": c.id,
                "tool_id": c.tool_id,
                "change_type": c.change_type.value,
                "field_name": c.field_name,
                "old_value": c.old_value,
                "new_value": c.new_value,
                "detected_at": c.detected_at.isoformat()
            } for c in changes
        ]
    
    def _export_quality_data(self, session, filters: Dict) -> List[Dict]:
        """Export quality data"""
        tools = session.query(Tool).all()
        
        return [
            {
                "tool_id": t.id,
                "tool_name": t.name,
                "quality_score": t.confidence_score or 0,
                "completeness_score": self._calculate_tool_completeness(t),
                "last_updated": t.last_processed_at.isoformat() if t.last_processed_at else None
            } for t in tools
        ]
    
    def _export_competitive_data(self, session, filters: Dict) -> Dict:
        """Export competitive analysis data"""
        analyses = session.query(CompetitiveAnalysis).all()
        
        return {
            "analyses": [
                {
                    "id": a.id,
                    "tool_id": a.tool_id,
                    "analysis_date": a.analysis_date.isoformat(),
                    "market_position": a.market_position,
                    "popularity_score": float(a.popularity_score),
                    "innovation_score": float(a.innovation_score),
                    "maturity_score": float(a.maturity_score)
                } for a in analyses
            ]
        }
    
    def _export_to_csv(self, data: List[Dict], export_type: str) -> Dict:
        """Export data to CSV format"""
        if not data:
            return {"error": "No data to export"}
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        return {
            "format": "csv",
            "content": output.getvalue(),
            "filename": f"{export_type}_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    
    def _export_to_excel(self, data: List[Dict], export_type: str) -> Dict:
        """Export data to Excel format"""
        try:
            df = pd.DataFrame(data)
            filename = f"{export_type}_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # Create Excel file in memory
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name=export_type.title())
            
            return {
                "format": "excel",
                "content": output.getvalue(),
                "filename": filename
            }
        except Exception as e:
            return {"error": f"Excel export failed: {e}"}
    
    def _calculate_tool_completeness(self, tool: Tool) -> float:
        """Calculate tool data completeness score"""
        required_fields = ['name', 'description', 'website_url', 'category_id']
        completed_fields = sum(1 for field in required_fields if getattr(tool, field))
        return (completed_fields / len(required_fields)) * 100
    
    # Analytics helper methods
    
    def _get_processing_analytics(self, session, cutoff_date: datetime) -> Dict:
        """Get processing analytics"""
        total_tasks = session.query(CurationTask).filter(
            CurationTask.created_at >= cutoff_date
        ).count()
        
        completed_tasks = session.query(CurationTask).filter(
            and_(
                CurationTask.created_at >= cutoff_date,
                CurationTask.status == 'completed'
            )
        ).count()
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }
    
    def _get_quality_analytics(self, session, cutoff_date: datetime) -> Dict:
        """Get quality analytics"""
        tools = session.query(Tool).all()
        quality_scores = [t.confidence_score or 0 for t in tools]
        
        return {
            "average_quality": statistics.mean(quality_scores) if quality_scores else 0,
            "quality_distribution": {
                "high": len([s for s in quality_scores if s >= 0.8]),
                "medium": len([s for s in quality_scores if 0.5 <= s < 0.8]),
                "low": len([s for s in quality_scores if s < 0.5])
            }
        }
    
    def _get_alert_analytics(self, session, cutoff_date: datetime) -> Dict:
        """Get alert analytics"""
        alert_tasks = session.query(CurationTask).filter(
            and_(
                CurationTask.task_type == 'alert',
                CurationTask.created_at >= cutoff_date
            )
        ).all()
        
        return {
            "total_alerts": len(alert_tasks),
            "alert_types": dict(Counter([t.description for t in alert_tasks]))
        }
    
    def _get_competitive_analytics(self, session, cutoff_date: datetime) -> Dict:
        """Get competitive analytics"""
        analyses = session.query(CompetitiveAnalysis).filter(
            CompetitiveAnalysis.analysis_date >= cutoff_date
        ).count()
        
        return {
            "total_analyses": analyses,
            "analysis_frequency": analyses / max(1, (datetime.utcnow() - cutoff_date).days)
        }
    
    def _get_performance_analytics(self, session, cutoff_date: datetime) -> Dict:
        """Get system performance analytics"""
        # This would track system performance metrics
        return {
            "avg_processing_time": 45.2,  # seconds
            "system_uptime": 99.5,  # percentage
            "api_response_time": 0.15  # seconds
        }
    
    def _get_admin_activity_analytics(self, session, cutoff_date: datetime) -> Dict:
        """Get admin activity analytics"""
        admin_tasks = session.query(CurationTask).filter(
            and_(
                CurationTask.task_type == 'admin_action',
                CurationTask.created_at >= cutoff_date
            )
        ).all()
        
        return {
            "total_admin_actions": len(admin_tasks),
            "actions_by_user": dict(Counter([t.assigned_to for t in admin_tasks if t.assigned_to]))
        }


# Export main classes
__all__ = [
    'AdminInterfaceManager', 'AdminAction', 'DataReviewItem', 'AdminDashboardData',
    'AdminActionType', 'ReviewStatus'
]