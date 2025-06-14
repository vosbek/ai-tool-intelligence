# admin_interface/admin_cli.py - Command-line interface for admin operations

import argparse
import json
import sys
import csv
from datetime import datetime
from typing import Optional, Dict, List
from tabulate import tabulate

# Import required modules
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .admin_manager import AdminInterfaceManager, AdminActionType, ReviewStatus
from ...models.database import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


class AdminCLI:
    """Command-line interface for admin operations"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
        
        try:
            self.admin_manager = AdminInterfaceManager(self.database_url)
            print("✅ Admin CLI initialized")
        except Exception as e:
            print(f"❌ Failed to initialize admin CLI: {e}")
            sys.exit(1)
    
    def dashboard(self, admin_user: str):
        """Display admin dashboard"""
        try:
            print(f"\n📊 ADMIN DASHBOARD - {admin_user}")
            print("=" * 60)
            
            dashboard_data = self.admin_manager.get_dashboard_data(admin_user)
            
            # System Overview
            print("\n🖥️  SYSTEM OVERVIEW")
            print("-" * 30)
            print(f"Total Tools: {dashboard_data.total_tools}")
            print(f"Active Monitoring: {dashboard_data.active_monitoring}")
            print(f"Pending Reviews: {dashboard_data.pending_reviews}")
            print(f"Quality Issues: {dashboard_data.quality_issues}")
            print(f"Recent Alerts: {dashboard_data.recent_alerts}")
            
            # Data Quality
            print("\n📊 DATA QUALITY")
            print("-" * 30)
            print(f"Average Quality Score: {dashboard_data.avg_quality_score:.2f}")
            print(f"Low Quality Tools: {dashboard_data.low_quality_tools}")
            print(f"Data Completeness: {dashboard_data.data_completeness:.1f}%")
            
            # Processing Stats
            print("\n⚙️  PROCESSING STATISTICS")
            print("-" * 30)
            print(f"Daily Curation Count: {dashboard_data.daily_curation_count}")
            print(f"Weekly Analysis Count: {dashboard_data.weekly_analysis_count}")
            print(f"Error Rate: {dashboard_data.error_rate:.1f}%")
            
            # Critical Reviews
            if dashboard_data.critical_reviews:
                print("\n🚨 CRITICAL REVIEWS")
                print("-" * 30)
                for review in dashboard_data.critical_reviews[:5]:
                    print(f"• {review.description} (ID: {review.item_id}, Priority: {review.priority})")
            
            # System Health
            print("\n💚 SYSTEM HEALTH")
            print("-" * 30)
            for component, status in dashboard_data.system_health.items():
                emoji = "✅" if status in ["healthy", "good", "operational", "active", "running"] else "⚠️"
                print(f"{emoji} {component.replace('_', ' ').title()}: {status}")
            
            print(f"\n✅ Dashboard generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Error generating dashboard: {e}")
    
    def review_tool(self, tool_id: int, action: str, admin_user: str, notes: str = None):
        """Review a specific tool"""
        try:
            print(f"\n🔍 REVIEWING TOOL {tool_id}")
            print("=" * 40)
            print(f"Action: {action}")
            print(f"Admin: {admin_user}")
            if notes:
                print(f"Notes: {notes}")
            
            result = self.admin_manager.review_tool_data(tool_id, admin_user, action, notes)
            
            if 'error' in result:
                print(f"❌ Review failed: {result['error']}")
                return
            
            print(f"\n✅ Review completed successfully")
            print(f"Action: {result['action']}")
            
            if 'new_quality_score' in result:
                print(f"New Quality Score: {result['new_quality_score']:.2f}")
            
        except Exception as e:
            print(f"❌ Error reviewing tool: {e}")
    
    def bulk_operation(self, operation_type: str, admin_user: str, filters: Dict = None, dry_run: bool = True):
        """Perform bulk operations"""
        try:
            print(f"\n🔄 BULK OPERATION: {operation_type.upper()}")
            print("=" * 50)
            print(f"Admin: {admin_user}")
            print(f"Dry Run: {dry_run}")
            
            if filters:
                print(f"Filters: {json.dumps(filters, indent=2)}")
            
            result = self.admin_manager.bulk_curation_operation(
                operation_type, filters or {}, admin_user, dry_run
            )
            
            if 'error' in result:
                print(f"❌ Bulk operation failed: {result['error']}")
                return
            
            if dry_run:
                print(f"\n📋 DRY RUN RESULTS")
                print(f"Affected Tools: {result['affected_count']}")
                
                if result['affected_tools']:
                    print("\nTools that would be affected:")
                    table_data = []
                    for tool in result['affected_tools'][:10]:  # Show first 10
                        table_data.append([
                            tool['id'],
                            tool['name'][:30],
                            tool['category'],
                            f"{tool['quality_score']:.2f}",
                            tool['last_updated'] or 'Never'
                        ])
                    
                    headers = ['ID', 'Name', 'Category', 'Quality', 'Last Updated']
                    print(tabulate(table_data, headers=headers, tablefmt='grid'))
                    
                    if result['affected_count'] > 10:
                        print(f"... and {result['affected_count'] - 10} more tools")
            else:
                print(f"\n✅ BULK OPERATION COMPLETED")
                print(f"Total Processed: {result['total_processed']}")
                print(f"Successful: {result['success_count']}")
                print(f"Errors: {result['error_count']}")
                
                if result['error_count'] > 0:
                    print("\n❌ Failed Operations:")
                    for res in result['results']:
                        if 'error' in res:
                            print(f"• Tool {res['tool_id']} ({res['tool_name']}): {res['error']}")
            
        except Exception as e:
            print(f"❌ Error in bulk operation: {e}")
    
    def list_alert_rules(self, admin_user: str):
        """List all alert rules"""
        try:
            print(f"\n🚨 ALERT RULES")
            print("=" * 30)
            
            result = self.admin_manager.manage_alert_rules('list', admin_user=admin_user)
            
            if 'error' in result:
                print(f"❌ Failed to list alert rules: {result['error']}")
                return
            
            rules = result.get('rules', [])
            
            if not rules:
                print("No alert rules configured")
                return
            
            table_data = []
            for rule in rules:
                table_data.append([
                    rule.get('rule_id', 'Unknown'),
                    rule.get('name', 'Unnamed'),
                    rule.get('severity_threshold', 'N/A'),
                    'Active' if rule.get('is_active', False) else 'Inactive',
                    len(rule.get('channels', [])),
                    rule.get('cooldown_minutes', 'N/A')
                ])
            
            headers = ['Rule ID', 'Name', 'Severity', 'Status', 'Channels', 'Cooldown']
            print(tabulate(table_data, headers=headers, tablefmt='grid'))
            
        except Exception as e:
            print(f"❌ Error listing alert rules: {e}")
    
    def export_data(self, export_type: str, format_type: str, admin_user: str, filters: Dict = None):
        """Export data"""
        try:
            print(f"\n📤 EXPORTING {export_type.upper()} DATA")
            print("=" * 40)
            print(f"Format: {format_type}")
            print(f"Admin: {admin_user}")
            
            if filters:
                print(f"Filters: {json.dumps(filters, indent=2)}")
            
            result = self.admin_manager.export_data(
                export_type, filters or {}, format_type, admin_user
            )
            
            if 'error' in result:
                print(f"❌ Export failed: {result['error']}")
                return
            
            if format_type == 'json':
                print(f"\n✅ Export completed")
                print(f"Records: {result['record_count']}")
                print(f"Export Type: {result['export_type']}")
                
                # Save to file
                filename = f"{export_type}_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"Saved to: {filename}")
            
            elif format_type in ['csv', 'excel']:
                filename = result.get('filename', f"{export_type}_export.{format_type}")
                
                with open(filename, 'wb' if format_type == 'excel' else 'w') as f:
                    if format_type == 'excel':
                        f.write(result['content'])
                    else:
                        f.write(result['content'])
                
                print(f"\n✅ Export completed")
                print(f"Saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting data: {e}")
    
    def system_analytics(self, time_range: int, admin_user: str):
        """Display system analytics"""
        try:
            print(f"\n📈 SYSTEM ANALYTICS ({time_range} days)")
            print("=" * 50)
            
            analytics = self.admin_manager.get_system_analytics(time_range, admin_user)
            
            if 'error' in analytics:
                print(f"❌ Failed to get analytics: {analytics['error']}")
                return
            
            # Processing Statistics
            proc_stats = analytics.get('processing_statistics', {})
            if proc_stats:
                print("\n⚙️  PROCESSING STATISTICS")
                print("-" * 30)
                print(f"Total Tasks: {proc_stats.get('total_tasks', 0)}")
                print(f"Completed Tasks: {proc_stats.get('completed_tasks', 0)}")
                print(f"Completion Rate: {proc_stats.get('completion_rate', 0):.1f}%")
            
            # Quality Trends
            quality_trends = analytics.get('quality_trends', {})
            if quality_trends:
                print("\n📊 QUALITY TRENDS")
                print("-" * 30)
                print(f"Average Quality: {quality_trends.get('average_quality', 0):.2f}")
                
                distribution = quality_trends.get('quality_distribution', {})
                print(f"High Quality (≥0.8): {distribution.get('high', 0)} tools")
                print(f"Medium Quality (0.5-0.8): {distribution.get('medium', 0)} tools")
                print(f"Low Quality (<0.5): {distribution.get('low', 0)} tools")
            
            # Alert Statistics
            alert_stats = analytics.get('alert_statistics', {})
            if alert_stats:
                print("\n🚨 ALERT STATISTICS")
                print("-" * 30)
                print(f"Total Alerts: {alert_stats.get('total_alerts', 0)}")
                
                alert_types = alert_stats.get('alert_types', {})
                if alert_types:
                    print("Alert Types:")
                    for alert_type, count in alert_types.items():
                        print(f"  • {alert_type}: {count}")
            
            # Competitive Analytics
            comp_stats = analytics.get('competitive_analytics', {})
            if comp_stats:
                print("\n🏆 COMPETITIVE ANALYTICS")
                print("-" * 30)
                print(f"Total Analyses: {comp_stats.get('total_analyses', 0)}")
                print(f"Analysis Frequency: {comp_stats.get('analysis_frequency', 0):.2f}/day")
            
            # System Performance
            perf_stats = analytics.get('system_performance', {})
            if perf_stats:
                print("\n⚡ SYSTEM PERFORMANCE")
                print("-" * 30)
                print(f"Avg Processing Time: {perf_stats.get('avg_processing_time', 0):.1f}s")
                print(f"System Uptime: {perf_stats.get('system_uptime', 0):.1f}%")
                print(f"API Response Time: {perf_stats.get('api_response_time', 0):.2f}s")
            
            print(f"\n✅ Analytics generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Error generating analytics: {e}")
    
    def quality_report(self, admin_user: str, threshold: float = 0.0, category_id: int = None, limit: int = 50):
        """Generate quality report"""
        try:
            print(f"\n📊 QUALITY REPORT")
            print("=" * 30)
            print(f"Threshold: ≥{threshold}")
            if category_id:
                print(f"Category ID: {category_id}")
            print(f"Limit: {limit}")
            
            filters = {'threshold': threshold}
            if category_id:
                filters['category_id'] = category_id
            
            quality_data = self.admin_manager.export_data('quality', filters, 'json', admin_user)
            
            if 'error' in quality_data:
                print(f"❌ Failed to get quality data: {quality_data['error']}")
                return
            
            tools = quality_data['data']
            filtered_tools = [tool for tool in tools if tool['quality_score'] >= threshold][:limit]
            
            if not filtered_tools:
                print("No tools found matching criteria")
                return
            
            # Display statistics
            quality_scores = [tool['quality_score'] for tool in filtered_tools]
            print(f"\n📈 STATISTICS")
            print(f"Total Tools: {len(filtered_tools)}")
            print(f"Average Quality: {sum(quality_scores) / len(quality_scores):.2f}")
            print(f"Highest Quality: {max(quality_scores):.2f}")
            print(f"Lowest Quality: {min(quality_scores):.2f}")
            
            # Display table
            print(f"\n📋 TOOL QUALITY SCORES")
            table_data = []
            for tool in filtered_tools[:20]:  # Show top 20
                table_data.append([
                    tool['tool_id'],
                    tool['tool_name'][:30],
                    f"{tool['quality_score']:.2f}",
                    f"{tool['completeness_score']:.1f}%",
                    tool['last_updated'][:10] if tool['last_updated'] else 'Never'
                ])
            
            headers = ['ID', 'Tool Name', 'Quality', 'Complete', 'Updated']
            print(tabulate(table_data, headers=headers, tablefmt='grid'))
            
            if len(filtered_tools) > 20:
                print(f"... and {len(filtered_tools) - 20} more tools")
            
        except Exception as e:
            print(f"❌ Error generating quality report: {e}")
    
    def recent_changes(self, admin_user: str, days: int = 7, limit: int = 50, change_type: str = None):
        """Show recent changes"""
        try:
            print(f"\n📝 RECENT CHANGES ({days} days)")
            print("=" * 40)
            if change_type:
                print(f"Change Type: {change_type}")
            print(f"Limit: {limit}")
            
            filters = {'days': days}
            if change_type:
                filters['change_type'] = change_type
            
            changes_data = self.admin_manager.export_data('changes', filters, 'json', admin_user)
            
            if 'error' in changes_data:
                print(f"❌ Failed to get changes data: {changes_data['error']}")
                return
            
            changes = changes_data['data'][:limit]
            
            if not changes:
                print("No recent changes found")
                return
            
            # Display statistics
            change_types = {}
            for change in changes:
                ct = change['change_type']
                change_types[ct] = change_types.get(ct, 0) + 1
            
            print(f"\n📊 CHANGE STATISTICS")
            print(f"Total Changes: {len(changes)}")
            print("Change Types:")
            for ct, count in sorted(change_types.items()):
                print(f"  • {ct}: {count}")
            
            # Display table
            print(f"\n📋 RECENT CHANGES")
            table_data = []
            for change in changes[:15]:  # Show top 15
                table_data.append([
                    change['id'],
                    change['tool_id'],
                    change['change_type'][:15],
                    change['field_name'][:20] if change['field_name'] else 'N/A',
                    change['detected_at'][:16]
                ])
            
            headers = ['ID', 'Tool', 'Type', 'Field', 'Detected']
            print(tabulate(table_data, headers=headers, tablefmt='grid'))
            
            if len(changes) > 15:
                print(f"... and {len(changes) - 15} more changes")
            
        except Exception as e:
            print(f"❌ Error getting recent changes: {e}")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Admin CLI for AI Tool Intelligence Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s dashboard --admin-user john.doe
  %(prog)s review-tool 1 approve --admin-user john.doe --notes "Quality approved"
  %(prog)s bulk-operation recurate --admin-user john.doe --dry-run
  %(prog)s export tools json --admin-user john.doe
  %(prog)s analytics --admin-user john.doe --time-range 30
  %(prog)s quality-report --admin-user john.doe --threshold 0.5
        """
    )
    
    # Global arguments
    parser.add_argument('--admin-user', required=True, help='Admin username')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Dashboard command
    subparsers.add_parser('dashboard', help='Show admin dashboard')
    
    # Review tool command
    review_parser = subparsers.add_parser('review-tool', help='Review a specific tool')
    review_parser.add_argument('tool_id', type=int, help='Tool ID to review')
    review_parser.add_argument('action', choices=['approve', 'reject', 'flag', 'edit'], help='Review action')
    review_parser.add_argument('--notes', help='Review notes')
    
    # Bulk operation command
    bulk_parser = subparsers.add_parser('bulk-operation', help='Perform bulk operations')
    bulk_parser.add_argument('operation', choices=['recurate', 'approve', 'flag', 'quality_check'], help='Operation type')
    bulk_parser.add_argument('--category-ids', nargs='+', type=int, help='Category IDs to filter')
    bulk_parser.add_argument('--quality-threshold', type=float, help='Quality score threshold')
    bulk_parser.add_argument('--last-updated-days', type=int, help='Days since last update')
    bulk_parser.add_argument('--processing-status', help='Processing status filter')
    bulk_parser.add_argument('--dry-run', action='store_true', default=True, help='Perform dry run (default)')
    bulk_parser.add_argument('--execute', action='store_true', help='Actually execute the operation')
    
    # Alert rules command
    subparsers.add_parser('list-alert-rules', help='List all alert rules')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export data')
    export_parser.add_argument('export_type', choices=['tools', 'changes', 'quality', 'competitive'], help='Data type to export')
    export_parser.add_argument('format', choices=['json', 'csv', 'excel'], help='Export format')
    export_parser.add_argument('--category-id', type=int, help='Category ID filter')
    export_parser.add_argument('--days', type=int, help='Days filter for changes')
    
    # Analytics command
    analytics_parser = subparsers.add_parser('analytics', help='Show system analytics')
    analytics_parser.add_argument('--time-range', type=int, default=30, help='Time range in days (default: 30)')
    
    # Quality report command
    quality_parser = subparsers.add_parser('quality-report', help='Generate quality report')
    quality_parser.add_argument('--threshold', type=float, default=0.0, help='Minimum quality score (default: 0.0)')
    quality_parser.add_argument('--category-id', type=int, help='Category ID filter')
    quality_parser.add_argument('--limit', type=int, default=50, help='Maximum results (default: 50)')
    
    # Recent changes command
    changes_parser = subparsers.add_parser('recent-changes', help='Show recent changes')
    changes_parser.add_argument('--days', type=int, default=7, help='Days to look back (default: 7)')
    changes_parser.add_argument('--limit', type=int, default=50, help='Maximum results (default: 50)')
    changes_parser.add_argument('--change-type', help='Filter by change type')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI
    cli = AdminCLI()
    
    try:
        # Execute commands
        if args.command == 'dashboard':
            cli.dashboard(args.admin_user)
        
        elif args.command == 'review-tool':
            cli.review_tool(args.tool_id, args.action, args.admin_user, args.notes)
        
        elif args.command == 'bulk-operation':
            filters = {}
            if args.category_ids:
                filters['category_ids'] = args.category_ids
            if args.quality_threshold:
                filters['quality_threshold'] = args.quality_threshold
            if args.last_updated_days:
                filters['last_updated_days'] = args.last_updated_days
            if args.processing_status:
                filters['processing_status'] = args.processing_status
            
            dry_run = not args.execute  # Default to dry run unless --execute is specified
            cli.bulk_operation(args.operation, args.admin_user, filters, dry_run)
        
        elif args.command == 'list-alert-rules':
            cli.list_alert_rules(args.admin_user)
        
        elif args.command == 'export':
            filters = {}
            if args.category_id:
                filters['category_id'] = args.category_id
            if args.days:
                filters['days'] = args.days
            
            cli.export_data(args.export_type, args.format, args.admin_user, filters)
        
        elif args.command == 'analytics':
            cli.system_analytics(args.time_range, args.admin_user)
        
        elif args.command == 'quality-report':
            cli.quality_report(args.admin_user, args.threshold, args.category_id, args.limit)
        
        elif args.command == 'recent-changes':
            cli.recent_changes(args.admin_user, args.days, args.limit, args.change_type)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()