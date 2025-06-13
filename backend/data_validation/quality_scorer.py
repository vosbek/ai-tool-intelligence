# data_validation/quality_scorer.py - Automated data validation and quality scoring system

import json
import re
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse
import requests

from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_, desc

# Import enhanced models
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.enhanced_schema import *


@dataclass
class ValidationRule:
    """Individual validation rule"""
    field_name: str
    rule_type: str  # 'required', 'format', 'range', 'custom'
    rule_params: Dict[str, Any]
    weight: float  # How important this rule is (0.0-1.0)
    error_message: str


@dataclass
class ValidationResult:
    """Result of validating a single field"""
    field_name: str
    is_valid: bool
    score: float  # 0.0-1.0
    issues: List[str]
    suggestions: List[str]


@dataclass
class QualityAssessment:
    """Comprehensive quality assessment for an entity"""
    entity_type: str
    entity_id: int
    overall_score: float  # 0-100
    completeness_score: float
    accuracy_score: float
    freshness_score: float
    consistency_score: float
    validation_results: List[ValidationResult]
    quality_grade: DataQuality
    issues_found: List[str]
    recommendations: List[str]
    confidence_level: float


class DataQualityScorer:
    """Automated data validation and quality scoring system"""
    
    def __init__(self, database_url: str = None):
        from sqlalchemy import create_engine
        
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # Define validation rules for different entity types
        self.validation_rules = self._setup_validation_rules()
        
        # URL validation cache
        self.url_cache = {}
        
        print("Data Quality Scorer initialized")
    
    def assess_tool_quality(self, tool_id: int, include_analysis: bool = True) -> QualityAssessment:
        """
        Perform comprehensive quality assessment for a tool
        
        Args:
            tool_id: ID of tool to assess
            include_analysis: Whether to include analysis snapshot data
        
        Returns:
            QualityAssessment with detailed quality metrics
        """
        session = self.Session()
        
        try:
            # Get tool data
            tool = session.query(Tool).filter_by(id=tool_id).first()
            if not tool:
                raise ValueError(f"Tool with ID {tool_id} not found")
            
            print(f"Assessing quality for tool: {tool.name}")
            
            # Run validation rules
            validation_results = self._validate_tool_fields(tool)
            
            # Calculate component scores
            completeness_score = self._calculate_completeness_score(tool, validation_results)
            accuracy_score = self._calculate_accuracy_score(tool, validation_results)
            freshness_score = self._calculate_freshness_score(tool)
            consistency_score = self._calculate_consistency_score(tool)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(
                completeness_score, accuracy_score, freshness_score, consistency_score
            )
            
            # Determine quality grade
            quality_grade = self._determine_quality_grade(overall_score)
            
            # Generate issues and recommendations
            issues_found = self._extract_issues(validation_results)
            recommendations = self._generate_recommendations(tool, validation_results, overall_score)
            
            # Calculate confidence level
            confidence_level = self._calculate_confidence_level(tool, validation_results)
            
            # Include analysis data if requested
            if include_analysis:
                latest_analysis = session.query(AnalysisSnapshot).filter_by(
                    tool_id=tool_id
                ).order_by(desc(AnalysisSnapshot.completed_at)).first()
                
                if latest_analysis:
                    # Enhance scores based on analysis data quality
                    analysis_quality = self._assess_analysis_quality(latest_analysis)
                    accuracy_score = (accuracy_score + analysis_quality['accuracy']) / 2
                    overall_score = self._calculate_overall_score(
                        completeness_score, accuracy_score, freshness_score, consistency_score
                    )
            
            assessment = QualityAssessment(
                entity_type='tool',
                entity_id=tool_id,
                overall_score=overall_score,
                completeness_score=completeness_score,
                accuracy_score=accuracy_score,
                freshness_score=freshness_score,
                consistency_score=consistency_score,
                validation_results=validation_results,
                quality_grade=quality_grade,
                issues_found=issues_found,
                recommendations=recommendations,
                confidence_level=confidence_level
            )
            
            # Save quality report to database
            self._save_quality_report(session, assessment)
            
            return assessment
            
        except Exception as e:
            print(f"Error assessing tool quality: {e}")
            raise
        finally:
            session.close()
    
    def assess_company_quality(self, company_id: int) -> QualityAssessment:
        """Assess quality of company data"""
        session = self.Session()
        
        try:
            company = session.query(Company).filter_by(id=company_id).first()
            if not company:
                raise ValueError(f"Company with ID {company_id} not found")
            
            validation_results = self._validate_company_fields(company)
            
            completeness_score = self._calculate_company_completeness(company, validation_results)
            accuracy_score = self._calculate_company_accuracy(company, validation_results)
            freshness_score = self._calculate_company_freshness(company)
            consistency_score = self._calculate_company_consistency(company)
            
            overall_score = self._calculate_overall_score(
                completeness_score, accuracy_score, freshness_score, consistency_score
            )
            
            quality_grade = self._determine_quality_grade(overall_score)
            issues_found = self._extract_issues(validation_results)
            recommendations = self._generate_company_recommendations(company, validation_results)
            confidence_level = self._calculate_company_confidence(company, validation_results)
            
            assessment = QualityAssessment(
                entity_type='company',
                entity_id=company_id,
                overall_score=overall_score,
                completeness_score=completeness_score,
                accuracy_score=accuracy_score,
                freshness_score=freshness_score,
                consistency_score=consistency_score,
                validation_results=validation_results,
                quality_grade=quality_grade,
                issues_found=issues_found,
                recommendations=recommendations,
                confidence_level=confidence_level
            )
            
            self._save_quality_report(session, assessment)
            return assessment
            
        except Exception as e:
            print(f"Error assessing company quality: {e}")
            raise
        finally:
            session.close()
    
    def assess_version_quality(self, version_id: int) -> QualityAssessment:
        """Assess quality of version data"""
        session = self.Session()
        
        try:
            version = session.query(ToolVersion).filter_by(id=version_id).first()
            if not version:
                raise ValueError(f"Version with ID {version_id} not found")
            
            validation_results = self._validate_version_fields(version)
            
            completeness_score = self._calculate_version_completeness(version, validation_results)
            accuracy_score = self._calculate_version_accuracy(version, validation_results)
            freshness_score = self._calculate_version_freshness(version)
            consistency_score = self._calculate_version_consistency(version)
            
            overall_score = self._calculate_overall_score(
                completeness_score, accuracy_score, freshness_score, consistency_score
            )
            
            quality_grade = self._determine_quality_grade(overall_score)
            issues_found = self._extract_issues(validation_results)
            recommendations = self._generate_version_recommendations(version, validation_results)
            confidence_level = self._calculate_version_confidence(version, validation_results)
            
            assessment = QualityAssessment(
                entity_type='version',
                entity_id=version_id,
                overall_score=overall_score,
                completeness_score=completeness_score,
                accuracy_score=accuracy_score,
                freshness_score=freshness_score,
                consistency_score=consistency_score,
                validation_results=validation_results,
                quality_grade=quality_grade,
                issues_found=issues_found,
                recommendations=recommendations,
                confidence_level=confidence_level
            )
            
            self._save_quality_report(session, assessment)
            return assessment
            
        except Exception as e:
            print(f"Error assessing version quality: {e}")
            raise
        finally:
            session.close()
    
    def bulk_assess_quality(self, entity_type: str, limit: int = None) -> List[QualityAssessment]:
        """Run quality assessment on multiple entities"""
        session = self.Session()
        assessments = []
        
        try:
            if entity_type == 'tool':
                query = session.query(Tool)
                if limit:
                    query = query.limit(limit)
                
                for tool in query.all():
                    try:
                        assessment = self.assess_tool_quality(tool.id, include_analysis=True)
                        assessments.append(assessment)
                    except Exception as e:
                        print(f"Error assessing tool {tool.id}: {e}")
                        continue
            
            elif entity_type == 'company':
                query = session.query(Company)
                if limit:
                    query = query.limit(limit)
                
                for company in query.all():
                    try:
                        assessment = self.assess_company_quality(company.id)
                        assessments.append(assessment)
                    except Exception as e:
                        print(f"Error assessing company {company.id}: {e}")
                        continue
            
            print(f"Completed bulk assessment: {len(assessments)} {entity_type}s assessed")
            return assessments
            
        except Exception as e:
            print(f"Error in bulk assessment: {e}")
            raise
        finally:
            session.close()
    
    def _setup_validation_rules(self) -> Dict[str, List[ValidationRule]]:
        """Setup validation rules for different entity types"""
        return {
            'tool': [
                ValidationRule('name', 'required', {}, 0.2, 'Tool name is required'),
                ValidationRule('description', 'min_length', {'min_length': 10}, 0.15, 'Description should be at least 10 characters'),
                ValidationRule('website_url', 'url_format', {}, 0.1, 'Website URL should be valid'),
                ValidationRule('github_url', 'github_url', {}, 0.1, 'GitHub URL should be valid GitHub repository'),
                ValidationRule('documentation_url', 'url_format', {}, 0.05, 'Documentation URL should be valid'),
                ValidationRule('category_id', 'required', {}, 0.1, 'Tool category is required'),
                ValidationRule('current_version', 'version_format', {}, 0.05, 'Version should follow semantic versioning'),
                ValidationRule('is_open_source', 'license_consistency', {}, 0.05, 'Open source status should match license type'),
                ValidationRule('confidence_score', 'range', {'min': 0, 'max': 100}, 0.1, 'Confidence score should be 0-100'),
                ValidationRule('processing_status', 'enum_value', {'values': [s.value for s in ProcessingStatus]}, 0.1, 'Processing status should be valid')
            ],
            'company': [
                ValidationRule('name', 'required', {}, 0.2, 'Company name is required'),
                ValidationRule('website', 'url_format', {}, 0.1, 'Company website should be valid URL'),
                ValidationRule('founded_year', 'year_range', {'min': 1800, 'max': datetime.now().year}, 0.1, 'Founded year should be reasonable'),
                ValidationRule('employee_count', 'positive_number', {}, 0.1, 'Employee count should be positive'),
                ValidationRule('stock_symbol', 'stock_format', {}, 0.05, 'Stock symbol should be valid format'),
                ValidationRule('estimated_arr', 'positive_number', {}, 0.05, 'ARR should be positive'),
                ValidationRule('total_funding', 'positive_number', {}, 0.05, 'Total funding should be positive'),
                ValidationRule('headquarters', 'location_format', {}, 0.05, 'Headquarters should be in "City, Country" format'),
                ValidationRule('data_quality', 'enum_value', {'values': [d.value for d in DataQuality]}, 0.1, 'Data quality should be valid enum'),
                ValidationRule('confidence_score', 'range', {'min': 0, 'max': 100}, 0.15, 'Confidence score should be 0-100')
            ],
            'version': [
                ValidationRule('version_number', 'required', {}, 0.3, 'Version number is required'),
                ValidationRule('version_number', 'version_format', {}, 0.2, 'Version should follow semantic versioning'),
                ValidationRule('detected_at', 'required', {}, 0.1, 'Detection date is required'),
                ValidationRule('confidence_score', 'range', {'min': 0, 'max': 100}, 0.15, 'Confidence score should be 0-100'),
                ValidationRule('feature_snapshot', 'valid_json', {}, 0.1, 'Feature snapshot should be valid JSON'),
                ValidationRule('pricing_snapshot', 'valid_json', {}, 0.1, 'Pricing snapshot should be valid JSON'),
                ValidationRule('data_quality', 'enum_value', {'values': [d.value for d in DataQuality]}, 0.05, 'Data quality should be valid enum')
            ]
        }
    
    def _validate_tool_fields(self, tool: Tool) -> List[ValidationResult]:
        """Validate tool fields against rules"""
        results = []
        rules = self.validation_rules['tool']
        
        for rule in rules:
            field_value = getattr(tool, rule.field_name, None)
            result = self._apply_validation_rule(rule, field_value)
            results.append(result)
        
        # Additional tool-specific validations
        results.extend(self._validate_tool_urls(tool))
        results.extend(self._validate_tool_relationships(tool))
        
        return results
    
    def _validate_company_fields(self, company: Company) -> List[ValidationResult]:
        """Validate company fields against rules"""
        results = []
        rules = self.validation_rules['company']
        
        for rule in rules:
            field_value = getattr(company, rule.field_name, None)
            result = self._apply_validation_rule(rule, field_value)
            results.append(result)
        
        return results
    
    def _validate_version_fields(self, version: ToolVersion) -> List[ValidationResult]:
        """Validate version fields against rules"""
        results = []
        rules = self.validation_rules['version']
        
        for rule in rules:
            field_value = getattr(version, rule.field_name, None)
            result = self._apply_validation_rule(rule, field_value)
            results.append(result)
        
        return results
    
    def _apply_validation_rule(self, rule: ValidationRule, field_value: Any) -> ValidationResult:
        """Apply a single validation rule"""
        issues = []
        suggestions = []
        is_valid = True
        score = 1.0
        
        try:
            if rule.rule_type == 'required':
                if field_value is None or (isinstance(field_value, str) and field_value.strip() == ''):
                    is_valid = False
                    score = 0.0
                    issues.append(rule.error_message)
                    suggestions.append(f"Please provide a value for {rule.field_name}")
            
            elif rule.rule_type == 'min_length':
                if field_value and len(str(field_value)) < rule.rule_params['min_length']:
                    is_valid = False
                    score = len(str(field_value)) / rule.rule_params['min_length']
                    issues.append(rule.error_message)
                    suggestions.append(f"Provide more detailed {rule.field_name}")
            
            elif rule.rule_type == 'url_format':
                if field_value:
                    if not self._is_valid_url(field_value):
                        is_valid = False
                        score = 0.5
                        issues.append(rule.error_message)
                        suggestions.append(f"Check the URL format for {rule.field_name}")
            
            elif rule.rule_type == 'github_url':
                if field_value:
                    if not self._is_valid_github_url(field_value):
                        is_valid = False
                        score = 0.5
                        issues.append(rule.error_message)
                        suggestions.append("Ensure GitHub URL points to a valid repository")
            
            elif rule.rule_type == 'version_format':
                if field_value:
                    if not self._is_valid_version(field_value):
                        is_valid = False
                        score = 0.7
                        issues.append(rule.error_message)
                        suggestions.append("Use semantic versioning format (e.g., 1.2.3)")
            
            elif rule.rule_type == 'range':
                if field_value is not None:
                    try:
                        value = float(field_value)
                        if value < rule.rule_params['min'] or value > rule.rule_params['max']:
                            is_valid = False
                            score = 0.0
                            issues.append(rule.error_message)
                    except (ValueError, TypeError):
                        is_valid = False
                        score = 0.0
                        issues.append(f"{rule.field_name} should be a number")
            
            elif rule.rule_type == 'enum_value':
                if field_value is not None:
                    if field_value not in rule.rule_params['values']:
                        is_valid = False
                        score = 0.0
                        issues.append(rule.error_message)
            
            elif rule.rule_type == 'positive_number':
                if field_value is not None:
                    try:
                        value = float(field_value)
                        if value <= 0:
                            is_valid = False
                            score = 0.0
                            issues.append(f"{rule.field_name} should be positive")
                    except (ValueError, TypeError):
                        is_valid = False
                        score = 0.0
                        issues.append(f"{rule.field_name} should be a number")
            
            elif rule.rule_type == 'valid_json':
                if field_value:
                    try:
                        json.loads(field_value)
                    except json.JSONDecodeError:
                        is_valid = False
                        score = 0.0
                        issues.append(f"{rule.field_name} contains invalid JSON")
                        suggestions.append("Fix JSON format")
            
        except Exception as e:
            is_valid = False
            score = 0.0
            issues.append(f"Validation error: {str(e)}")
        
        return ValidationResult(
            field_name=rule.field_name,
            is_valid=is_valid,
            score=score,
            issues=issues,
            suggestions=suggestions
        )
    
    def _validate_tool_urls(self, tool: Tool) -> List[ValidationResult]:
        """Additional URL validation for tools"""
        results = []
        
        # Check URL accessibility
        urls_to_check = [
            ('website_url', tool.website_url),
            ('github_url', tool.github_url),
            ('documentation_url', tool.documentation_url)
        ]
        
        for field_name, url in urls_to_check:
            if url:
                accessibility_score = self._check_url_accessibility(url)
                
                result = ValidationResult(
                    field_name=f"{field_name}_accessibility",
                    is_valid=accessibility_score > 0.5,
                    score=accessibility_score,
                    issues=[] if accessibility_score > 0.5 else [f"{field_name} is not accessible"],
                    suggestions=[] if accessibility_score > 0.5 else [f"Check if {field_name} is working"]
                )
                results.append(result)
        
        return results
    
    def _validate_tool_relationships(self, tool: Tool) -> List[ValidationResult]:
        """Validate tool relationships and consistency"""
        results = []
        
        # Check if tool has company data
        has_company = tool.company is not None
        result = ValidationResult(
            field_name='has_company_data',
            is_valid=has_company,
            score=1.0 if has_company else 0.3,
            issues=[] if has_company else ["Tool missing company information"],
            suggestions=[] if has_company else ["Add company data for better analysis"]
        )
        results.append(result)
        
        # Check version consistency
        has_versions = len(tool.versions) > 0
        result = ValidationResult(
            field_name='has_version_data',
            is_valid=has_versions,
            score=1.0 if has_versions else 0.2,
            issues=[] if has_versions else ["Tool has no version data"],
            suggestions=[] if has_versions else ["Create at least one version record"]
        )
        results.append(result)
        
        return results
    
    def _calculate_completeness_score(self, tool: Tool, validation_results: List[ValidationResult]) -> float:
        """Calculate data completeness score"""
        # Count non-null fields
        required_fields = ['name', 'description', 'website_url', 'category_id']
        optional_fields = ['github_url', 'documentation_url', 'license_type', 'current_version']
        
        required_filled = sum(1 for field in required_fields if getattr(tool, field))
        optional_filled = sum(1 for field in optional_fields if getattr(tool, field))
        
        # Weight required fields more heavily
        completeness = (required_filled * 0.7 + optional_filled * 0.3) / (len(required_fields) * 0.7 + len(optional_fields) * 0.3)
        
        # Factor in relationship data
        if tool.company:
            completeness += 0.1
        if tool.versions:
            completeness += 0.1
        
        return min(100.0, completeness * 100)
    
    def _calculate_accuracy_score(self, tool: Tool, validation_results: List[ValidationResult]) -> float:
        """Calculate data accuracy score based on validation results"""
        if not validation_results:
            return 50.0
        
        total_weight = 0.0
        weighted_score = 0.0
        
        rule_weights = {rule.field_name: rule.weight for rule in self.validation_rules['tool']}
        
        for result in validation_results:
            weight = rule_weights.get(result.field_name, 0.05)  # Default weight
            total_weight += weight
            weighted_score += result.score * weight
        
        if total_weight == 0:
            return 50.0
        
        return (weighted_score / total_weight) * 100
    
    def _calculate_freshness_score(self, tool: Tool) -> float:
        """Calculate data freshness score"""
        if not tool.last_processed_at:
            return 0.0
        
        days_since_update = (datetime.utcnow() - tool.last_processed_at).days
        
        # Freshness decreases over time
        if days_since_update <= 1:
            return 100.0
        elif days_since_update <= 7:
            return 90.0
        elif days_since_update <= 30:
            return 75.0
        elif days_since_update <= 90:
            return 50.0
        else:
            return 25.0
    
    def _calculate_consistency_score(self, tool: Tool) -> float:
        """Calculate data consistency score"""
        consistency_checks = []
        
        # Check open source vs license consistency
        if tool.is_open_source and tool.license_type:
            open_source_licenses = ['MIT', 'Apache', 'GPL', 'BSD', 'ISC', 'LGPL']
            has_open_license = any(license_type in tool.license_type.upper() for license_type in open_source_licenses)
            consistency_checks.append(has_open_license)
        else:
            consistency_checks.append(True)  # No conflict
        
        # Check GitHub URL vs open source status
        if tool.github_url and not tool.is_open_source:
            consistency_checks.append(False)  # Usually suspicious
        else:
            consistency_checks.append(True)
        
        # Check pricing vs open source
        if tool.is_open_source and tool.pricing_model in ['paid', 'enterprise']:
            consistency_checks.append(False)  # Can be suspicious but not always wrong
        else:
            consistency_checks.append(True)
        
        return (sum(consistency_checks) / len(consistency_checks)) * 100 if consistency_checks else 100.0
    
    def _calculate_overall_score(self, completeness: float, accuracy: float, freshness: float, consistency: float) -> float:
        """Calculate weighted overall score"""
        weights = {
            'completeness': 0.3,
            'accuracy': 0.4,
            'freshness': 0.2,
            'consistency': 0.1
        }
        
        overall = (
            completeness * weights['completeness'] +
            accuracy * weights['accuracy'] +
            freshness * weights['freshness'] +
            consistency * weights['consistency']
        )
        
        return round(overall, 2)
    
    def _determine_quality_grade(self, overall_score: float) -> DataQuality:
        """Determine quality grade based on overall score"""
        if overall_score >= 90:
            return DataQuality.HIGH
        elif overall_score >= 70:
            return DataQuality.MEDIUM
        elif overall_score >= 50:
            return DataQuality.LOW
        else:
            return DataQuality.UNVERIFIED
    
    def _calculate_confidence_level(self, tool: Tool, validation_results: List[ValidationResult]) -> float:
        """Calculate confidence level in the assessment"""
        # Base confidence on data availability and validation scores
        base_confidence = tool.confidence_score or 50.0
        
        # Adjust based on validation results
        validation_confidence = sum(r.score for r in validation_results) / len(validation_results) if validation_results else 0.5
        
        # Factor in processing status
        status_confidence = {
            ProcessingStatus.COMPLETED: 1.0,
            ProcessingStatus.NEEDS_REVIEW: 0.8,
            ProcessingStatus.RUNNING: 0.6,
            ProcessingStatus.FAILED: 0.3,
            ProcessingStatus.NEVER_RUN: 0.1,
            ProcessingStatus.QUEUED: 0.2
        }.get(tool.processing_status, 0.5)
        
        # Weighted average
        confidence = (base_confidence * 0.4 + validation_confidence * 100 * 0.4 + status_confidence * 100 * 0.2)
        
        return min(100.0, confidence)
    
    def _extract_issues(self, validation_results: List[ValidationResult]) -> List[str]:
        """Extract all issues from validation results"""
        issues = []
        for result in validation_results:
            issues.extend(result.issues)
        return issues
    
    def _generate_recommendations(self, tool: Tool, validation_results: List[ValidationResult], overall_score: float) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Collect suggestions from validation results
        for result in validation_results:
            recommendations.extend(result.suggestions)
        
        # Add score-based recommendations
        if overall_score < 50:
            recommendations.append("Consider comprehensive data review and update")
        elif overall_score < 70:
            recommendations.append("Focus on improving data accuracy and completeness")
        elif overall_score < 90:
            recommendations.append("Minor improvements needed for high quality rating")
        
        # Add specific recommendations based on missing data
        if not tool.company:
            recommendations.append("Add company information for better competitive analysis")
        
        if not tool.versions:
            recommendations.append("Create version records to track tool evolution")
        
        if not tool.last_processed_at:
            recommendations.append("Run analysis to collect current tool data")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _generate_company_recommendations(self, company: Company, validation_results: List[ValidationResult]) -> List[str]:
        """Generate company-specific recommendations"""
        recommendations = []
        
        for result in validation_results:
            recommendations.extend(result.suggestions)
        
        if not company.employee_count:
            recommendations.append("Research and add employee count data")
        
        if not company.total_funding and not company.is_public:
            recommendations.append("Research funding information if available")
        
        return list(set(recommendations))
    
    def _generate_version_recommendations(self, version: ToolVersion, validation_results: List[ValidationResult]) -> List[str]:
        """Generate version-specific recommendations"""
        recommendations = []
        
        for result in validation_results:
            recommendations.extend(result.suggestions)
        
        if not version.feature_snapshot:
            recommendations.append("Add feature data for this version")
        
        if not version.pricing_snapshot:
            recommendations.append("Add pricing data for this version")
        
        return list(set(recommendations))
    
    def _save_quality_report(self, session, assessment: QualityAssessment):
        """Save quality assessment to database"""
        try:
            report = DataQualityReport(
                entity_type=assessment.entity_type,
                entity_id=assessment.entity_id,
                completeness_score=assessment.completeness_score,
                accuracy_score=assessment.accuracy_score,
                freshness_score=assessment.freshness_score,
                consistency_score=assessment.consistency_score,
                overall_quality=assessment.quality_grade,
                issues_found=json.dumps(assessment.issues_found),
                recommendations=json.dumps(assessment.recommendations),
                report_date=datetime.utcnow()
            )
            
            session.add(report)
            session.commit()
            
        except Exception as e:
            print(f"Error saving quality report: {e}")
            session.rollback()
    
    # Additional helper methods for company and version calculations
    def _calculate_company_completeness(self, company: Company, validation_results: List[ValidationResult]) -> float:
        """Calculate company data completeness"""
        required_fields = ['name', 'website']
        optional_fields = ['founded_year', 'headquarters', 'employee_count', 'business_model']
        
        required_filled = sum(1 for field in required_fields if getattr(company, field))
        optional_filled = sum(1 for field in optional_fields if getattr(company, field))
        
        completeness = (required_filled * 0.7 + optional_filled * 0.3) / (len(required_fields) * 0.7 + len(optional_fields) * 0.3)
        return completeness * 100
    
    def _calculate_company_accuracy(self, company: Company, validation_results: List[ValidationResult]) -> float:
        """Calculate company data accuracy"""
        if not validation_results:
            return 50.0
        
        rule_weights = {rule.field_name: rule.weight for rule in self.validation_rules['company']}
        total_weight = sum(rule_weights.get(r.field_name, 0.05) for r in validation_results)
        weighted_score = sum(r.score * rule_weights.get(r.field_name, 0.05) for r in validation_results)
        
        return (weighted_score / total_weight * 100) if total_weight > 0 else 50.0
    
    def _calculate_company_freshness(self, company: Company) -> float:
        """Calculate company data freshness"""
        if not company.updated_at:
            return 25.0
        
        days_since_update = (datetime.utcnow() - company.updated_at).days
        
        if days_since_update <= 30:
            return 100.0
        elif days_since_update <= 90:
            return 75.0
        elif days_since_update <= 180:
            return 50.0
        else:
            return 25.0
    
    def _calculate_company_consistency(self, company: Company) -> float:
        """Calculate company data consistency"""
        # Basic consistency checks for company data
        checks = []
        
        # Public company should have stock symbol
        if company.is_public and not company.stock_symbol:
            checks.append(False)
        else:
            checks.append(True)
        
        # Founded year should be reasonable
        if company.founded_year:
            current_year = datetime.now().year
            checks.append(1800 <= company.founded_year <= current_year)
        else:
            checks.append(True)
        
        return (sum(checks) / len(checks) * 100) if checks else 100.0
    
    def _calculate_version_completeness(self, version: ToolVersion, validation_results: List[ValidationResult]) -> float:
        """Calculate version data completeness"""
        required_fields = ['version_number', 'detected_at']
        optional_fields = ['feature_snapshot', 'pricing_snapshot', 'integration_snapshot']
        
        required_filled = sum(1 for field in required_fields if getattr(version, field))
        optional_filled = sum(1 for field in optional_fields if getattr(version, field))
        
        completeness = (required_filled * 0.8 + optional_filled * 0.2) / (len(required_fields) * 0.8 + len(optional_fields) * 0.2)
        return completeness * 100
    
    def _calculate_version_accuracy(self, version: ToolVersion, validation_results: List[ValidationResult]) -> float:
        """Calculate version data accuracy"""
        if not validation_results:
            return 50.0
        
        rule_weights = {rule.field_name: rule.weight for rule in self.validation_rules['version']}
        total_weight = sum(rule_weights.get(r.field_name, 0.05) for r in validation_results)
        weighted_score = sum(r.score * rule_weights.get(r.field_name, 0.05) for r in validation_results)
        
        return (weighted_score / total_weight * 100) if total_weight > 0 else 50.0
    
    def _calculate_version_freshness(self, version: ToolVersion) -> float:
        """Calculate version data freshness"""
        days_since_detection = (datetime.utcnow() - version.detected_at).days
        
        if days_since_detection <= 7:
            return 100.0
        elif days_since_detection <= 30:
            return 90.0
        elif days_since_detection <= 90:
            return 70.0
        else:
            return 50.0
    
    def _calculate_version_consistency(self, version: ToolVersion) -> float:
        """Calculate version data consistency"""
        # Check version consistency
        checks = []
        
        # Version number format
        if version.version_number:
            checks.append(self._is_valid_version(version.version_number))
        
        # Confidence score range
        if version.confidence_score is not None:
            checks.append(0 <= version.confidence_score <= 100)
        else:
            checks.append(True)
        
        return (sum(checks) / len(checks) * 100) if checks else 100.0
    
    def _calculate_company_confidence(self, company: Company, validation_results: List[ValidationResult]) -> float:
        """Calculate confidence in company assessment"""
        base_confidence = company.confidence_score or 50.0
        validation_confidence = sum(r.score for r in validation_results) / len(validation_results) if validation_results else 0.5
        
        return (base_confidence * 0.6 + validation_confidence * 100 * 0.4)
    
    def _calculate_version_confidence(self, version: ToolVersion, validation_results: List[ValidationResult]) -> float:
        """Calculate confidence in version assessment"""
        base_confidence = version.confidence_score or 50.0
        validation_confidence = sum(r.score for r in validation_results) / len(validation_results) if validation_results else 0.5
        
        return (base_confidence * 0.6 + validation_confidence * 100 * 0.4)
    
    def _assess_analysis_quality(self, analysis: AnalysisSnapshot) -> Dict[str, float]:
        """Assess quality of analysis snapshot data"""
        quality_scores = {'accuracy': 50.0, 'completeness': 50.0}
        
        # Check data completeness
        data_fields = [analysis.github_analysis, analysis.pricing_analysis, 
                      analysis.feature_analysis, analysis.integration_analysis]
        filled_fields = sum(1 for field in data_fields if field)
        quality_scores['completeness'] = (filled_fields / len(data_fields)) * 100
        
        # Check analysis metadata
        if analysis.total_confidence:
            quality_scores['accuracy'] = analysis.total_confidence
        
        return quality_scores
    
    # URL validation helpers
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL has valid format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _is_valid_github_url(self, url: str) -> bool:
        """Check if URL is a valid GitHub repository URL"""
        if not self._is_valid_url(url):
            return False
        
        parsed = urlparse(url)
        if 'github.com' not in parsed.netloc:
            return False
        
        # Basic pattern check for github.com/owner/repo
        path_parts = parsed.path.strip('/').split('/')
        return len(path_parts) >= 2 and all(part for part in path_parts[:2])
    
    def _is_valid_version(self, version: str) -> bool:
        """Check if version follows semantic versioning"""
        if not version:
            return False
        
        # Remove 'v' prefix if present
        version_clean = version.lower().replace('v', '')
        
        # Check semantic versioning pattern
        semantic_pattern = r'^\d+\.\d+(\.\d+)?(-[\w\.-]+)?(\+[\w\.-]+)?$'
        return bool(re.match(semantic_pattern, version_clean))
    
    def _check_url_accessibility(self, url: str) -> float:
        """Check if URL is accessible (cached to avoid repeated requests)"""
        if url in self.url_cache:
            return self.url_cache[url]
        
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                score = 1.0
            elif response.status_code in [301, 302, 303, 307, 308]:
                score = 0.9  # Redirects are okay
            elif response.status_code in [403, 401]:
                score = 0.7  # Forbidden/unauthorized but exists
            elif response.status_code == 404:
                score = 0.0  # Not found
            else:
                score = 0.5  # Other status codes
            
            self.url_cache[url] = score
            return score
            
        except Exception:
            self.url_cache[url] = 0.0
            return 0.0


# Export main class and data structures
__all__ = [
    'DataQualityScorer', 'QualityAssessment', 'ValidationResult', 'ValidationRule'
]