# admin_interface/admin_api.py - Flask API endpoints for admin interface

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from typing import Dict, List, Optional
import json
import io
import tempfile
import os

# Import admin manager
try:
    from .admin_manager import AdminInterfaceManager, AdminActionType, ReviewStatus
except ImportError:
    print("Warning: Admin interface not available")
    AdminInterfaceManager = None

# Create blueprint for admin routes
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Initialize admin manager
if AdminInterfaceManager:
    admin_manager = AdminInterfaceManager()
else:
    admin_manager = None


def require_admin(f):
    """Decorator to require admin authentication"""
    def decorated_function(*args, **kwargs):
        # In a real implementation, you would check authentication here
        # For now, we'll use a simple header check
        admin_user = request.headers.get('X-Admin-User')
        if not admin_user:
            return jsonify({'error': 'Admin authentication required'}), 401
        
        # Add admin_user to request context
        request.admin_user = admin_user
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function


@admin_bp.route('/dashboard', methods=['GET'])
@require_admin
def get_admin_dashboard():
    """
    Get admin dashboard data
    
    Returns comprehensive dashboard with system metrics, pending reviews, and alerts
    """
    if not admin_manager:
        return jsonify({'error': 'Admin interface not available'}), 503
    
    try:
        dashboard_data = admin_manager.get_dashboard_data(request.admin_user)
        
        # Convert to JSON-serializable format
        return jsonify({
            'dashboard': {
                'system_overview': {
                    'total_tools': dashboard_data.total_tools,
                    'active_monitoring': dashboard_data.active_monitoring,
                    'pending_reviews': dashboard_data.pending_reviews,
                    'quality_issues': dashboard_data.quality_issues,
                    'recent_alerts': dashboard_data.recent_alerts
                },
                'data_quality': {
                    'avg_quality_score': dashboard_data.avg_quality_score,
                    'low_quality_tools': dashboard_data.low_quality_tools,
                    'data_completeness': dashboard_data.data_completeness
                },
                'processing_stats': {
                    'daily_curation_count': dashboard_data.daily_curation_count,
                    'weekly_analysis_count': dashboard_data.weekly_analysis_count,
                    'error_rate': dashboard_data.error_rate
                },
                'critical_reviews': [
                    {
                        'review_id': r.review_id,
                        'item_type': r.item_type,
                        'item_id': r.item_id,
                        'priority': r.priority,
                        'status': r.status.value,
                        'description': r.description,
                        'created_at': r.created_at.isoformat(),
                        'data_snapshot': r.data_snapshot
                    } for r in dashboard_data.critical_reviews
                ],
                'pending_approvals': [
                    {
                        'review_id': r.review_id,
                        'item_type': r.item_type,
                        'item_id': r.item_id,
                        'priority': r.priority,
                        'status': r.status.value,
                        'description': r.description,
                        'created_at': r.created_at.isoformat(),
                        'data_snapshot': r.data_snapshot
                    } for r in dashboard_data.pending_approvals
                ],
                'system_health': dashboard_data.system_health
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/tools/<int:tool_id>/review', methods=['POST'])
@require_admin
def review_tool_data(tool_id):
    """
    Review and take action on tool data
    
    Expected JSON body:
    {
        "action": "approve|reject|flag|edit",
        "notes": "Optional review notes"
    }
    """
    if not admin_manager:
        return jsonify({'error': 'Admin interface not available'}), 503
    
    try:
        data = request.get_json()
        action = data.get('action')
        notes = data.get('notes')
        
        if action not in ['approve', 'reject', 'flag', 'edit']:
            return jsonify({'error': 'Invalid action. Must be one of: approve, reject, flag, edit'}), 400
        
        result = admin_manager.review_tool_data(tool_id, request.admin_user, action, notes)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify({
            'review_result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/bulk-operations', methods=['POST'])
@require_admin
def bulk_curation_operation():
    """
    Perform bulk curation operations
    
    Expected JSON body:
    {
        "operation_type": "recurate|approve|flag|quality_check",
        "target_filters": {
            "category_ids": [1, 2, 3],
            "quality_threshold": 0.5,
            "last_updated_days": 30,
            "processing_status": "error"
        },
        "dry_run": true
    }
    """
    if not admin_manager:
        return jsonify({'error': 'Admin interface not available'}), 503
    
    try:
        data = request.get_json()
        operation_type = data.get('operation_type')
        target_filters = data.get('target_filters', {})
        dry_run = data.get('dry_run', True)
        
        if operation_type not in ['recurate', 'approve', 'flag', 'quality_check']:
            return jsonify({
                'error': 'Invalid operation type. Must be one of: recurate, approve, flag, quality_check'
            }), 400
        
        result = admin_manager.bulk_curation_operation(
            operation_type, target_filters, request.admin_user, dry_run
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify({
            'bulk_operation_result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/alert-rules', methods=['GET', 'POST', 'PUT', 'DELETE'])
@require_admin
def manage_alert_rules():
    """
    Manage alert rules
    
    GET: List all alert rules
    POST: Create new alert rule
    PUT: Update existing alert rule
    DELETE: Delete alert rule
    """
    if not admin_manager:
        return jsonify({'error': 'Admin interface not available'}), 503
    
    try:
        if request.method == 'GET':
            result = admin_manager.manage_alert_rules('list', admin_user=request.admin_user)
        
        elif request.method == 'POST':
            data = request.get_json()
            rule_data = data.get('rule_data')
            
            if not rule_data:
                return jsonify({'error': 'rule_data required for creation'}), 400
            
            result = admin_manager.manage_alert_rules(
                'create', rule_data=rule_data, admin_user=request.admin_user
            )
        
        elif request.method == 'PUT':
            data = request.get_json()
            rule_id = data.get('rule_id')
            rule_data = data.get('rule_data')
            
            if not rule_id or not rule_data:
                return jsonify({'error': 'rule_id and rule_data required for update'}), 400
            
            result = admin_manager.manage_alert_rules(
                'update', rule_data=rule_data, rule_id=rule_id, admin_user=request.admin_user
            )
        
        elif request.method == 'DELETE':
            rule_id = request.args.get('rule_id')
            
            if not rule_id:
                return jsonify({'error': 'rule_id required for deletion'}), 400
            
            result = admin_manager.manage_alert_rules(
                'delete', rule_id=rule_id, admin_user=request.admin_user
            )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify({
            'alert_rules_result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/alert-rules/<rule_id>/test', methods=['POST'])
@require_admin
def test_alert_rule(rule_id):
    """
    Test a specific alert rule
    """
    if not admin_manager:
        return jsonify({'error': 'Admin interface not available'}), 503
    
    try:
        result = admin_manager.manage_alert_rules(
            'test', rule_id=rule_id, admin_user=request.admin_user
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify({
            'test_result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/export', methods=['POST'])
@require_admin
def export_data():
    """
    Export data for admin analysis
    
    Expected JSON body:
    {
        "export_type": "tools|changes|quality|competitive",
        "format": "json|csv|excel",
        "filters": {
            "category_id": 1,
            "days": 30
        }
    }
    """
    if not admin_manager:
        return jsonify({'error': 'Admin interface not available'}), 503
    
    try:
        data = request.get_json()
        export_type = data.get('export_type')
        format_type = data.get('format', 'json')
        filters = data.get('filters', {})
        
        if export_type not in ['tools', 'changes', 'quality', 'competitive']:
            return jsonify({
                'error': 'Invalid export type. Must be one of: tools, changes, quality, competitive'
            }), 400
        
        if format_type not in ['json', 'csv', 'excel']:
            return jsonify({
                'error': 'Invalid format. Must be one of: json, csv, excel'
            }), 400
        
        result = admin_manager.export_data(
            export_type, filters, format_type, request.admin_user
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        # Handle file downloads for CSV and Excel
        if format_type in ['csv', 'excel']:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            
            if format_type == 'csv':
                temp_file.write(result['content'].encode('utf-8'))
                mimetype = 'text/csv'
            else:  # excel
                temp_file.write(result['content'])
                mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            
            temp_file.close()
            
            return send_file(
                temp_file.name,
                as_attachment=True,
                download_name=result['filename'],
                mimetype=mimetype
            )
        
        else:  # json
            return jsonify({
                'export_result': result,
                'timestamp': datetime.utcnow().isoformat()
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/analytics', methods=['GET'])
@require_admin
def get_system_analytics():
    """
    Get comprehensive system analytics
    
    Query parameters:
    - time_range: Number of days to analyze (default: 30)
    """
    if not admin_manager:
        return jsonify({'error': 'Admin interface not available'}), 503
    
    try:
        time_range = request.args.get('time_range', 30, type=int)
        
        if time_range < 1 or time_range > 365:
            return jsonify({'error': 'time_range must be between 1 and 365 days'}), 400
        
        analytics = admin_manager.get_system_analytics(time_range, request.admin_user)
        
        if 'error' in analytics:
            return jsonify(analytics), 400
        
        return jsonify({
            'system_analytics': analytics,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/tools/quality-scores', methods=['GET'])
@require_admin
def get_quality_scores():
    """
    Get quality scores for all tools
    
    Query parameters:
    - threshold: Minimum quality score to include (default: 0)
    - limit: Maximum number of results (default: 100)
    - category_id: Filter by category ID
    """
    if not admin_manager:
        return jsonify({'error': 'Admin interface not available'}), 503
    
    try:
        threshold = request.args.get('threshold', 0.0, type=float)
        limit = request.args.get('limit', 100, type=int)
        category_id = request.args.get('category_id', type=int)
        
        filters = {'threshold': threshold}
        if category_id:
            filters['category_id'] = category_id
        
        # Export quality data and return subset
        quality_data = admin_manager.export_data('quality', filters, 'json', request.admin_user)
        
        if 'error' in quality_data:
            return jsonify(quality_data), 400
        
        # Filter and limit results
        tools = quality_data['data']
        filtered_tools = [
            tool for tool in tools 
            if tool['quality_score'] >= threshold
        ][:limit]
        
        return jsonify({
            'quality_scores': filtered_tools,
            'total_count': len(filtered_tools),
            'filters_applied': {
                'threshold': threshold,
                'limit': limit,
                'category_id': category_id
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/changes/recent', methods=['GET'])
@require_admin
def get_recent_changes():
    """
    Get recent changes for admin review
    
    Query parameters:
    - days: Number of days to look back (default: 7)
    - limit: Maximum number of results (default: 50)
    - change_type: Filter by change type
    """
    if not admin_manager:
        return jsonify({'error': 'Admin interface not available'}), 503
    
    try:
        days = request.args.get('days', 7, type=int)
        limit = request.args.get('limit', 50, type=int)
        change_type = request.args.get('change_type')
        
        filters = {'days': days}
        if change_type:
            filters['change_type'] = change_type
        
        # Export changes data
        changes_data = admin_manager.export_data('changes', filters, 'json', request.admin_user)
        
        if 'error' in changes_data:
            return jsonify(changes_data), 400
        
        # Limit results
        changes = changes_data['data'][:limit]
        
        return jsonify({
            'recent_changes': changes,
            'total_count': len(changes),
            'filters_applied': {
                'days': days,
                'limit': limit,
                'change_type': change_type
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/system/health', methods=['GET'])
@require_admin
def get_system_health():
    """
    Get detailed system health information
    """
    if not admin_manager:
        return jsonify({'error': 'Admin interface not available'}), 503
    
    try:
        dashboard_data = admin_manager.get_dashboard_data(request.admin_user)
        
        health_info = {
            'system_health': dashboard_data.system_health,
            'data_quality': {
                'avg_quality_score': dashboard_data.avg_quality_score,
                'low_quality_tools': dashboard_data.low_quality_tools,
                'data_completeness': dashboard_data.data_completeness
            },
            'processing_status': {
                'daily_curation_count': dashboard_data.daily_curation_count,
                'weekly_analysis_count': dashboard_data.weekly_analysis_count,
                'error_rate': dashboard_data.error_rate
            },
            'alerts': {
                'pending_reviews': dashboard_data.pending_reviews,
                'quality_issues': dashboard_data.quality_issues,
                'recent_alerts': dashboard_data.recent_alerts
            }
        }
        
        return jsonify({
            'system_health': health_info,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/config', methods=['GET', 'POST'])
@require_admin
def manage_system_config():
    """
    Manage system configuration
    
    GET: Get current configuration
    POST: Update configuration
    """
    if not admin_manager:
        return jsonify({'error': 'Admin interface not available'}), 503
    
    try:
        if request.method == 'GET':
            # Return current admin configuration
            return jsonify({
                'config': admin_manager.admin_config,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        elif request.method == 'POST':
            data = request.get_json()
            new_config = data.get('config', {})
            
            # Validate and update configuration
            valid_keys = [
                'auto_approve_threshold',
                'review_timeout_days', 
                'critical_quality_threshold',
                'batch_size_limit'
            ]
            
            updated_config = {}
            for key, value in new_config.items():
                if key in valid_keys:
                    # Basic validation
                    if key.endswith('_threshold') and (value < 0 or value > 1):
                        return jsonify({'error': f'{key} must be between 0 and 1'}), 400
                    if key == 'review_timeout_days' and (value < 1 or value > 365):
                        return jsonify({'error': 'review_timeout_days must be between 1 and 365'}), 400
                    if key == 'batch_size_limit' and (value < 1 or value > 1000):
                        return jsonify({'error': 'batch_size_limit must be between 1 and 1000'}), 400
                    
                    updated_config[key] = value
                    admin_manager.admin_config[key] = value
            
            return jsonify({
                'config_updated': updated_config,
                'current_config': admin_manager.admin_config,
                'timestamp': datetime.utcnow().isoformat()
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Error handlers for admin blueprint
@admin_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'error': 'Unauthorized access to admin interface',
        'message': 'Valid admin authentication required'
    }), 401


@admin_bp.errorhandler(403)
def forbidden(error):
    return jsonify({
        'error': 'Forbidden access to admin interface',
        'message': 'Insufficient admin privileges'
    }), 403


@admin_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal admin interface error',
        'message': 'An unexpected error occurred in the admin system'
    }), 500