# data_curation/curation_engine.py - Automated data curation and change detection

import json
import difflib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import hashlib
import re

from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_, desc

# Import enhanced models
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.enhanced_schema import *
from enhanced_strands_agent import EnhancedStrandsAgentService


@dataclass
class ChangeDetection:
    """Container for detected changes"""
    change_type: ChangeType
    field_name: str
    old_value: Any
    new_value: Any
    confidence: float
    summary: str
    impact_score: int = 1


@dataclass
class CurationResult:
    """Result of data curation process"""
    tool_id: int
    version_created: bool
    changes_detected: List[ChangeDetection]
    data_quality_score: float
    confidence_score: float
    issues_found: List[str]
    recommendations: List[str]


class DataCurationEngine:
    """Automated data curation engine with change detection"""
    
    def __init__(self, database_url: str = None):
        from sqlalchemy import create_engine
        
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # Initialize enhanced strands agent
        self.agent_service = EnhancedStrandsAgentService()
        
        # Version detection patterns
        self.version_patterns = [
            r'v?(\d+)\.(\d+)\.(\d+)',  # v1.2.3 or 1.2.3
            r'v?(\d+)\.(\d+)',         # v1.2 or 1.2
            r'Version\s+(\d+(?:\.\d+)*)',  # Version 1.2.3
            r'Release\s+(\d+(?:\.\d+)*)',  # Release 1.2
        ]
        
        print("Data Curation Engine initialized")
    
    def curate_tool_data(self, tool_id: int, force_analysis: bool = False) -> CurationResult:
        """
        Perform comprehensive data curation for a tool
        
        Args:
            tool_id: ID of tool to curate
            force_analysis: Force new analysis even if recently done
        
        Returns:
            CurationResult with details of curation process
        """
        session = self.Session()
        
        try:
            # Get tool data
            tool = session.query(Tool).filter_by(id=tool_id).first()
            if not tool:
                raise ValueError(f"Tool with ID {tool_id} not found")
            
            print(f"Starting curation for tool: {tool.name}")
            
            # Check if we need to run analysis
            if not force_analysis and self._should_skip_analysis(tool):
                print(f"Skipping analysis for {tool.name} - too recent")
                return CurationResult(
                    tool_id=tool_id,
                    version_created=False,
                    changes_detected=[],
                    data_quality_score=tool.confidence_score or 0.0,
                    confidence_score=tool.confidence_score or 0.0,
                    issues_found=["Analysis skipped - too recent"],
                    recommendations=["Wait for next scheduled analysis"]
                )
            
            # Get latest analysis for comparison
            latest_snapshot = session.query(AnalysisSnapshot).filter_by(
                tool_id=tool_id
            ).order_by(desc(AnalysisSnapshot.completed_at)).first()
            
            # Run fresh analysis
            print(f"Running fresh analysis for {tool.name}")
            fresh_analysis = self._run_fresh_analysis(tool)
            
            if not fresh_analysis:
                return CurationResult(
                    tool_id=tool_id,
                    version_created=False,
                    changes_detected=[],
                    data_quality_score=0.0,
                    confidence_score=0.0,
                    issues_found=["Analysis failed"],
                    recommendations=["Check tool URLs and retry"]
                )
            
            # Create analysis snapshot
            snapshot = self._create_analysis_snapshot(session, tool, fresh_analysis)
            
            # Detect changes if we have previous data
            changes_detected = []
            if latest_snapshot:
                changes_detected = self._detect_changes(
                    latest_snapshot, 
                    fresh_analysis, 
                    tool
                )
            
            # Record changes in database
            for change in changes_detected:
                self._record_change(session, tool_id, change)
            
            # Check if we need to create a new version
            version_created = False
            if self._should_create_new_version(tool, changes_detected, fresh_analysis):
                new_version = self._create_new_version(session, tool, fresh_analysis)
                version_created = True
                print(f"Created new version: {new_version.version_number}")
            else:
                # Update existing version with fresh data
                self._update_current_version(session, tool, fresh_analysis)
            
            # Calculate data quality scores
            quality_scores = self._calculate_data_quality(fresh_analysis, changes_detected)
            
            # Update tool with new information
            tool.last_processed_at = datetime.utcnow()
            tool.processing_status = ProcessingStatus.COMPLETED
            tool.confidence_score = quality_scores['confidence_score']
            tool.overall_data_quality = self._get_quality_enum(quality_scores['overall_quality'])
            
            if changes_detected:
                tool.last_change_detected_at = datetime.utcnow()
            
            # Schedule next analysis
            tool.next_process_date = self._calculate_next_analysis_date(tool, changes_detected)
            
            # Generate curation tasks if needed
            issues_found, recommendations = self._generate_curation_tasks(
                session, tool, fresh_analysis, quality_scores, changes_detected
            )
            
            session.commit()
            
            print(f"Curation completed for {tool.name}")
            print(f"  Changes detected: {len(changes_detected)}")
            print(f"  Version created: {version_created}")
            print(f"  Data quality: {quality_scores['overall_quality']}")
            
            return CurationResult(
                tool_id=tool_id,
                version_created=version_created,
                changes_detected=changes_detected,
                data_quality_score=quality_scores['data_quality_score'],
                confidence_score=quality_scores['confidence_score'],
                issues_found=issues_found,
                recommendations=recommendations
            )
            
        except Exception as e:
            session.rollback()
            print(f"Error during curation: {e}")
            
            # Update tool status to failed
            tool.processing_status = ProcessingStatus.FAILED
            tool.last_processed_at = datetime.utcnow()
            session.commit()
            
            return CurationResult(
                tool_id=tool_id,
                version_created=False,
                changes_detected=[],
                data_quality_score=0.0,
                confidence_score=0.0,
                issues_found=[str(e)],
                recommendations=["Check tool configuration and retry"]
            )
        finally:
            session.close()
    
    def _should_skip_analysis(self, tool: Tool) -> bool:
        """Check if we should skip analysis based on frequency settings"""
        if not tool.last_processed_at:
            return False
        
        time_since_last = datetime.utcnow() - tool.last_processed_at
        min_interval = timedelta(days=tool.monitoring_frequency_days or 7)
        
        return time_since_last < min_interval
    
    def _run_fresh_analysis(self, tool: Tool) -> Optional[Dict]:
        """Run fresh analysis using enhanced strands agent"""
        try:
            tool_data = {
                "name": tool.name,
                "website_url": tool.website_url,
                "github_url": tool.github_url,
                "docs_url": tool.documentation_url,
                "company_name": tool.company.name if tool.company else None
            }
            
            result = self.agent_service.analyze_tool(tool_data)
            
            if "error" in result:
                print(f"Analysis error: {result['error']}")
                return None
            
            return result
            
        except Exception as e:
            print(f"Error running fresh analysis: {e}")
            return None
    
    def _create_analysis_snapshot(self, session, tool: Tool, analysis_data: Dict) -> AnalysisSnapshot:
        """Create a new analysis snapshot"""
        snapshot = AnalysisSnapshot(
            tool_id=tool.id,
            analysis_type=AnalysisType.SCHEDULED,
            github_analysis=json.dumps(analysis_data.get('github_analysis')),
            pricing_analysis=json.dumps(analysis_data.get('pricing_analysis')),
            company_analysis=json.dumps(analysis_data.get('company_analysis')),
            feature_analysis=json.dumps(analysis_data.get('feature_analysis')),
            integration_analysis=json.dumps(analysis_data.get('integration_analysis')),
            tools_used=json.dumps(analysis_data.get('analysis_metadata', {}).get('tools_used', [])),
            total_confidence=analysis_data.get('analysis_metadata', {}).get('total_confidence', 0.0),
            data_completeness=analysis_data.get('analysis_metadata', {}).get('data_completeness', 0.0),
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            status=ProcessingStatus.COMPLETED
        )
        
        session.add(snapshot)
        session.flush()
        
        return snapshot
    
    def _detect_changes(self, old_snapshot: AnalysisSnapshot, new_analysis: Dict, tool: Tool) -> List[ChangeDetection]:
        """Detect changes between old and new analysis"""
        changes = []
        
        try:
            # Parse old analysis data
            old_data = {}
            if old_snapshot.github_analysis:
                old_data['github'] = json.loads(old_snapshot.github_analysis)
            if old_snapshot.pricing_analysis:
                old_data['pricing'] = json.loads(old_snapshot.pricing_analysis)
            if old_snapshot.feature_analysis:
                old_data['features'] = json.loads(old_snapshot.feature_analysis)
            if old_snapshot.integration_analysis:
                old_data['integrations'] = json.loads(old_snapshot.integration_analysis)
            
            # Detect version changes
            version_changes = self._detect_version_changes(old_data, new_analysis)
            changes.extend(version_changes)
            
            # Detect pricing changes
            pricing_changes = self._detect_pricing_changes(old_data, new_analysis)
            changes.extend(pricing_changes)
            
            # Detect feature changes
            feature_changes = self._detect_feature_changes(old_data, new_analysis)
            changes.extend(feature_changes)
            
            # Detect integration changes
            integration_changes = self._detect_integration_changes(old_data, new_analysis)
            changes.extend(integration_changes)
            
            # Detect GitHub metric changes
            github_changes = self._detect_github_changes(old_data, new_analysis)
            changes.extend(github_changes)
            
        except Exception as e:
            print(f"Error detecting changes: {e}")
        
        return changes
    
    def _detect_version_changes(self, old_data: Dict, new_data: Dict) -> List[ChangeDetection]:
        """Detect version number changes"""
        changes = []
        
        try:
            old_github = old_data.get('github', {})
            new_github = new_data.get('github_analysis', {})
            
            old_version = self._extract_version_from_github(old_github)
            new_version = self._extract_version_from_github(new_github)
            
            if old_version and new_version and old_version != new_version:
                changes.append(ChangeDetection(
                    change_type=ChangeType.VERSION_BUMP,
                    field_name='version',
                    old_value=old_version,
                    new_value=new_version,
                    confidence=0.9,
                    summary=f"Version updated from {old_version} to {new_version}",
                    impact_score=4
                ))
            
        except Exception as e:
            print(f"Error detecting version changes: {e}")
        
        return changes
    
    def _detect_pricing_changes(self, old_data: Dict, new_data: Dict) -> List[ChangeDetection]:
        """Detect pricing and business model changes"""
        changes = []
        
        try:
            old_pricing = old_data.get('pricing', {})
            new_pricing = new_data.get('pricing_analysis', {})
            
            # Check pricing model changes
            old_model = old_pricing.get('pricing_model')
            new_model = new_pricing.get('pricing_model')
            
            if old_model and new_model and old_model != new_model:
                changes.append(ChangeDetection(
                    change_type=ChangeType.PRICE_CHANGE,
                    field_name='pricing_model',
                    old_value=old_model,
                    new_value=new_model,
                    confidence=0.8,
                    summary=f"Pricing model changed from {old_model} to {new_model}",
                    impact_score=3
                ))
            
            # Check free tier availability
            old_free = old_pricing.get('free_tier_available')
            new_free = new_pricing.get('free_tier_available')
            
            if old_free is not None and new_free is not None and old_free != new_free:
                action = "added" if new_free else "removed"
                changes.append(ChangeDetection(
                    change_type=ChangeType.PRICE_CHANGE,
                    field_name='free_tier_available',
                    old_value=old_free,
                    new_value=new_free,
                    confidence=0.85,
                    summary=f"Free tier {action}",
                    impact_score=4
                ))
            
            # Check subscription tiers
            old_tiers = old_pricing.get('subscription_tiers', [])
            new_tiers = new_pricing.get('subscription_tiers', [])
            
            if len(old_tiers) != len(new_tiers):
                changes.append(ChangeDetection(
                    change_type=ChangeType.PRICE_CHANGE,
                    field_name='subscription_tiers',
                    old_value=f"{len(old_tiers)} tiers",
                    new_value=f"{len(new_tiers)} tiers",
                    confidence=0.7,
                    summary=f"Number of pricing tiers changed from {len(old_tiers)} to {len(new_tiers)}",
                    impact_score=2
                ))
            
        except Exception as e:
            print(f"Error detecting pricing changes: {e}")
        
        return changes
    
    def _detect_feature_changes(self, old_data: Dict, new_data: Dict) -> List[ChangeDetection]:
        """Detect feature additions, removals, and modifications"""
        changes = []
        
        try:
            old_features = old_data.get('features', {})
            new_features = new_data.get('feature_analysis', {})
            
            # Compare different feature categories
            categories = ['core_features', 'ai_ml_features', 'enterprise_features', 'integration_features']
            
            for category in categories:
                old_category_features = self._extract_feature_names(old_features.get(category, []))
                new_category_features = self._extract_feature_names(new_features.get(category, []))
                
                # Find added features
                added_features = new_category_features - old_category_features
                for feature in added_features:
                    changes.append(ChangeDetection(
                        change_type=ChangeType.ADDED,
                        field_name=f'{category}_feature',
                        old_value=None,
                        new_value=feature,
                        confidence=0.75,
                        summary=f"Added {category.replace('_', ' ')} feature: {feature}",
                        impact_score=2
                    ))
                
                # Find removed features
                removed_features = old_category_features - new_category_features
                for feature in removed_features:
                    changes.append(ChangeDetection(
                        change_type=ChangeType.REMOVED,
                        field_name=f'{category}_feature',
                        old_value=feature,
                        new_value=None,
                        confidence=0.7,
                        summary=f"Removed {category.replace('_', ' ')} feature: {feature}",
                        impact_score=3
                    ))
        
        except Exception as e:
            print(f"Error detecting feature changes: {e}")
        
        return changes
    
    def _detect_integration_changes(self, old_data: Dict, new_data: Dict) -> List[ChangeDetection]:
        """Detect integration additions and removals"""
        changes = []
        
        try:
            old_integrations = old_data.get('integrations', {})
            new_integrations = new_data.get('integration_analysis', {})
            
            # Compare integration categories
            categories = ['ide_integrations', 'cicd_integrations', 'cloud_integrations']
            
            for category in categories:
                old_names = self._extract_integration_names(old_integrations.get(category, []))
                new_names = self._extract_integration_names(new_integrations.get(category, []))
                
                # Find added integrations
                added = new_names - old_names
                for integration in added:
                    changes.append(ChangeDetection(
                        change_type=ChangeType.ADDED,
                        field_name=f'{category}_integration',
                        old_value=None,
                        new_value=integration,
                        confidence=0.8,
                        summary=f"Added {category.replace('_', ' ')} integration: {integration}",
                        impact_score=2
                    ))
                
                # Find removed integrations
                removed = old_names - new_names
                for integration in removed:
                    changes.append(ChangeDetection(
                        change_type=ChangeType.REMOVED,
                        field_name=f'{category}_integration',
                        old_value=integration,
                        new_value=None,
                        confidence=0.75,
                        summary=f"Removed {category.replace('_', ' ')} integration: {integration}",
                        impact_score=2
                    ))
        
        except Exception as e:
            print(f"Error detecting integration changes: {e}")
        
        return changes
    
    def _detect_github_changes(self, old_data: Dict, new_data: Dict) -> List[ChangeDetection]:
        """Detect significant GitHub metric changes"""
        changes = []
        
        try:
            old_github = old_data.get('github', {})
            new_github = new_data.get('github_analysis', {})
            
            old_stats = old_github.get('basic_stats', {})
            new_stats = new_github.get('basic_stats', {})
            
            # Check significant star count changes (>10% change)
            old_stars = old_stats.get('stars', 0)
            new_stars = new_stats.get('stars', 0)
            
            if old_stars > 0 and new_stars > 0:
                change_percent = abs(new_stars - old_stars) / old_stars
                if change_percent > 0.1:  # >10% change
                    changes.append(ChangeDetection(
                        change_type=ChangeType.MODIFIED,
                        field_name='github_stars',
                        old_value=old_stars,
                        new_value=new_stars,
                        confidence=0.95,
                        summary=f"GitHub stars changed from {old_stars:,} to {new_stars:,} ({change_percent:.1%})",
                        impact_score=1
                    ))
            
            # Check for new releases
            old_releases = old_github.get('recent_releases', [])
            new_releases = new_github.get('recent_releases', [])
            
            if new_releases and (not old_releases or new_releases[0] != old_releases[0]):
                latest_release = new_releases[0] if new_releases else {}
                changes.append(ChangeDetection(
                    change_type=ChangeType.VERSION_BUMP,
                    field_name='latest_release',
                    old_value=old_releases[0]['tag'] if old_releases else None,
                    new_value=latest_release.get('tag'),
                    confidence=0.9,
                    summary=f"New release detected: {latest_release.get('tag')}",
                    impact_score=3
                ))
        
        except Exception as e:
            print(f"Error detecting GitHub changes: {e}")
        
        return changes
    
    def _extract_version_from_github(self, github_data: Dict) -> Optional[str]:
        """Extract version number from GitHub data"""
        try:
            # Try latest release first
            releases = github_data.get('recent_releases', [])
            if releases:
                tag = releases[0].get('tag', '')
                version = self._parse_version_string(tag)
                if version:
                    return version
            
            # Try repository topics/tags
            topics = github_data.get('repository_info', {}).get('topics', [])
            for topic in topics:
                version = self._parse_version_string(topic)
                if version:
                    return version
            
            return None
            
        except Exception:
            return None
    
    def _parse_version_string(self, version_str: str) -> Optional[str]:
        """Parse version string using common patterns"""
        for pattern in self.version_patterns:
            match = re.search(pattern, version_str, re.IGNORECASE)
            if match:
                return match.group(0).replace('v', '').replace('V', '')
        return None
    
    def _extract_feature_names(self, features_list: List) -> set:
        """Extract feature names from features list"""
        names = set()
        for feature in features_list:
            if isinstance(feature, dict):
                name = feature.get('feature_name') or feature.get('name')
                if name:
                    names.add(name.strip().lower())
            elif isinstance(feature, str):
                names.add(feature.strip().lower())
        return names
    
    def _extract_integration_names(self, integrations_list: List) -> set:
        """Extract integration names from integrations list"""
        names = set()
        for integration in integrations_list:
            if isinstance(integration, dict):
                name = integration.get('integration_name') or integration.get('name')
                if name:
                    names.add(name.strip().lower())
            elif isinstance(integration, str):
                names.add(integration.strip().lower())
        return names
    
    def _record_change(self, session, tool_id: int, change: ChangeDetection):
        """Record a detected change in the database"""
        try:
            tool_change = ToolChange(
                tool_id=tool_id,
                change_type=change.change_type,
                change_category=change.field_name.split('_')[0],  # Extract category
                field_name=change.field_name,
                old_value=str(change.old_value) if change.old_value is not None else None,
                new_value=str(change.new_value) if change.new_value is not None else None,
                change_summary=change.summary,
                impact_score=change.impact_score,
                detected_at=datetime.utcnow(),
                detection_method='automated',
                confidence_score=change.confidence * 100,  # Convert to 0-100 scale
                is_reviewed=False
            )
            
            session.add(tool_change)
            
        except Exception as e:
            print(f"Error recording change: {e}")
    
    def _should_create_new_version(self, tool: Tool, changes: List[ChangeDetection], analysis: Dict) -> bool:
        """Determine if we should create a new version based on changes"""
        # Create new version if:
        # 1. Version number changed
        # 2. Significant feature changes
        # 3. Major pricing changes
        
        version_changes = [c for c in changes if c.change_type == ChangeType.VERSION_BUMP]
        if version_changes:
            return True
        
        high_impact_changes = [c for c in changes if c.impact_score >= 3]
        if len(high_impact_changes) >= 2:
            return True
        
        feature_changes = [c for c in changes if 'feature' in c.field_name and c.change_type in [ChangeType.ADDED, ChangeType.REMOVED]]
        if len(feature_changes) >= 3:
            return True
        
        return False
    
    def _create_new_version(self, session, tool: Tool, analysis: Dict) -> ToolVersion:
        """Create a new tool version"""
        # Determine version number
        new_version_number = self._determine_new_version_number(tool, analysis)
        
        version = ToolVersion(
            tool_id=tool.id,
            version_number=new_version_number,
            detected_at=datetime.utcnow(),
            is_stable=True,
            data_quality=DataQuality.MEDIUM,
            confidence_score=analysis.get('analysis_metadata', {}).get('total_confidence', 70.0),
            feature_snapshot=json.dumps(analysis.get('feature_analysis', {})),
            pricing_snapshot=json.dumps(analysis.get('pricing_analysis', {})),
            integration_snapshot=json.dumps(analysis.get('integration_analysis', {})),
            github_metrics_snapshot=json.dumps(analysis.get('github_analysis', {}))
        )
        
        session.add(version)
        session.flush()
        
        # Update tool's current version
        tool.current_version = new_version_number
        tool.current_version_id = version.id
        
        # Create version-specific features, pricing, and integrations
        self._create_version_features(session, version, analysis.get('feature_analysis', {}))
        self._create_version_pricing(session, version, analysis.get('pricing_analysis', {}))
        self._create_version_integrations(session, version, analysis.get('integration_analysis', {}))
        
        return version
    
    def _determine_new_version_number(self, tool: Tool, analysis: Dict) -> str:
        """Determine the version number for a new version"""
        # Try to extract from GitHub releases
        github_data = analysis.get('github_analysis', {})
        detected_version = self._extract_version_from_github(github_data)
        
        if detected_version:
            return detected_version
        
        # Increment current version
        current = tool.current_version or "1.0.0"
        parts = current.split('.')
        
        try:
            if len(parts) >= 3:
                # Increment patch version
                parts[2] = str(int(parts[2]) + 1)
            elif len(parts) == 2:
                # Add patch version
                parts.append("1")
            else:
                # Start fresh
                parts = ["1", "0", "1"]
            
            return '.'.join(parts)
        except ValueError:
            # Fallback to timestamp-based version
            return f"auto.{datetime.now().strftime('%Y%m%d')}"
    
    def _update_current_version(self, session, tool: Tool, analysis: Dict):
        """Update the current version with fresh data"""
        if not tool.current_version_id:
            return
        
        current_version = session.query(ToolVersion).filter_by(id=tool.current_version_id).first()
        if current_version:
            # Update snapshots with latest data
            current_version.feature_snapshot = json.dumps(analysis.get('feature_analysis', {}))
            current_version.pricing_snapshot = json.dumps(analysis.get('pricing_analysis', {}))
            current_version.integration_snapshot = json.dumps(analysis.get('integration_analysis', {}))
            current_version.github_metrics_snapshot = json.dumps(analysis.get('github_analysis', {}))
            current_version.confidence_score = analysis.get('analysis_metadata', {}).get('total_confidence', 70.0)
    
    def _create_version_features(self, session, version: ToolVersion, feature_data: Dict):
        """Create version-specific features"""
        try:
            categories = ['core_features', 'ai_ml_features', 'enterprise_features', 'integration_features']
            
            for category in categories:
                features = feature_data.get(category, [])
                for feature_item in features:
                    if isinstance(feature_item, dict):
                        feature = VersionFeature(
                            version_id=version.id,
                            tool_id=version.tool_id,
                            feature_category=category,
                            feature_name=feature_item.get('feature_name', ''),
                            feature_description=feature_item.get('feature_description', ''),
                            is_core_feature=category == 'core_features',
                            is_ai_feature=category == 'ai_ml_features',
                            is_enterprise_feature=category == 'enterprise_features',
                            confidence_score=feature_item.get('confidence_score', 70.0),
                            extraction_method=feature_item.get('extraction_method', 'automated')
                        )
                        session.add(feature)
                        
        except Exception as e:
            print(f"Error creating version features: {e}")
    
    def _create_version_pricing(self, session, version: ToolVersion, pricing_data: Dict):
        """Create version-specific pricing"""
        try:
            if pricing_data.get('subscription_tiers'):
                for tier in pricing_data['subscription_tiers']:
                    pricing = VersionPricing(
                        version_id=version.id,
                        tool_id=version.tool_id,
                        pricing_model=pricing_data.get('pricing_model'),
                        tier_name=tier.get('name'),
                        price_monthly=tier.get('price_monthly'),
                        price_yearly=tier.get('price_yearly'),
                        currency=pricing_data.get('currency', 'USD'),
                        free_tier_available=pricing_data.get('free_tier_available', False),
                        trial_period_days=pricing_data.get('trial_period_days'),
                        enterprise_available=pricing_data.get('enterprise_available', False),
                        pricing_details=json.dumps(tier),
                        confidence_score=70.0
                    )
                    session.add(pricing)
                    
        except Exception as e:
            print(f"Error creating version pricing: {e}")
    
    def _create_version_integrations(self, session, version: ToolVersion, integration_data: Dict):
        """Create version-specific integrations"""
        try:
            categories = ['ide_integrations', 'cicd_integrations', 'cloud_integrations', 'development_tools']
            
            for category in categories:
                integrations = integration_data.get(category, [])
                for integration_item in integrations:
                    if isinstance(integration_item, dict):
                        integration = VersionIntegration(
                            version_id=version.id,
                            tool_id=version.tool_id,
                            integration_category=category.replace('_integrations', '').replace('_tools', ''),
                            integration_name=integration_item.get('integration_name', ''),
                            integration_type=integration_item.get('integration_type', 'unknown'),
                            is_verified=integration_item.get('verification_status') == 'verified',
                            marketplace_url=integration_item.get('marketplace_url'),
                            setup_complexity=integration_item.get('setup_complexity', 'unknown'),
                            confidence_score=integration_item.get('confidence_score', 70.0)
                        )
                        session.add(integration)
                        
        except Exception as e:
            print(f"Error creating version integrations: {e}")
    
    def _calculate_data_quality(self, analysis: Dict, changes: List[ChangeDetection]) -> Dict:
        """Calculate comprehensive data quality scores"""
        # Base confidence from analysis
        base_confidence = analysis.get('analysis_metadata', {}).get('total_confidence', 0.0)
        data_completeness = analysis.get('analysis_metadata', {}).get('data_completeness', 0.0)
        
        # Adjust based on changes detected
        change_confidence = 1.0
        if changes:
            # Higher confidence if we can detect changes (means we have good comparison data)
            change_confidence = 1.1
        
        # Calculate final scores
        confidence_score = min(100.0, base_confidence * change_confidence)
        data_quality_score = (confidence_score + data_completeness) / 2
        
        # Determine overall quality enum
        if data_quality_score >= 90:
            overall_quality = "high"
        elif data_quality_score >= 70:
            overall_quality = "medium"
        elif data_quality_score >= 50:
            overall_quality = "low"
        else:
            overall_quality = "unverified"
        
        return {
            'confidence_score': confidence_score,
            'data_quality_score': data_quality_score,
            'overall_quality': overall_quality
        }
    
    def _get_quality_enum(self, quality_str: str) -> DataQuality:
        """Convert quality string to enum"""
        mapping = {
            'high': DataQuality.HIGH,
            'medium': DataQuality.MEDIUM,
            'low': DataQuality.LOW,
            'unverified': DataQuality.UNVERIFIED
        }
        return mapping.get(quality_str, DataQuality.UNVERIFIED)
    
    def _calculate_next_analysis_date(self, tool: Tool, changes: List[ChangeDetection]) -> datetime:
        """Calculate when to run next analysis based on change frequency"""
        base_frequency = tool.monitoring_frequency_days or 7
        
        # Adjust frequency based on recent changes
        if changes:
            high_impact_changes = [c for c in changes if c.impact_score >= 3]
            if high_impact_changes:
                # More frequent monitoring for active tools
                base_frequency = max(1, base_frequency // 2)
        else:
            # Less frequent monitoring for stable tools
            base_frequency = min(30, base_frequency * 2)
        
        return datetime.utcnow() + timedelta(days=base_frequency)
    
    def _generate_curation_tasks(self, session, tool: Tool, analysis: Dict, 
                                quality_scores: Dict, changes: List[ChangeDetection]) -> Tuple[List[str], List[str]]:
        """Generate curation tasks for manual review"""
        issues_found = []
        recommendations = []
        
        # Check data quality issues
        if quality_scores['data_quality_score'] < 70:
            issues_found.append("Low data quality score")
            recommendations.append("Review and verify tool information manually")
            
            # Create curation task
            task = CurationTask(
                task_type='review',
                priority=2,
                entity_type='tool',
                entity_id=tool.id,
                title=f"Review data quality for {tool.name}",
                description=f"Data quality score is {quality_scores['data_quality_score']:.1f}%",
                suggested_action="Manually verify and update tool information"
            )
            session.add(task)
        
        # Check for high-impact changes
        high_impact_changes = [c for c in changes if c.impact_score >= 4]
        if high_impact_changes:
            issues_found.append(f"{len(high_impact_changes)} high-impact changes detected")
            recommendations.append("Review significant changes for accuracy")
            
            for change in high_impact_changes:
                task = CurationTask(
                    task_type='verify',
                    priority=1,
                    entity_type='tool',
                    entity_id=tool.id,
                    title=f"Verify change: {change.summary}",
                    description=f"High-impact change detected: {change.field_name}",
                    suggested_action="Manually verify this change is accurate"
                )
                session.add(task)
        
        # Check for missing critical data
        if not tool.website_url:
            issues_found.append("Missing website URL")
            recommendations.append("Add website URL for better analysis")
        
        if not tool.github_url and tool.is_open_source:
            issues_found.append("Missing GitHub URL for open source tool")
            recommendations.append("Add GitHub repository URL")
        
        return issues_found, recommendations


# Export main class
__all__ = ['DataCurationEngine', 'ChangeDetection', 'CurationResult']