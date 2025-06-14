#!/usr/bin/env python3
"""
Configuration Management System

Provides:
- Environment-specific configurations
- Configuration validation
- Secret management
- Feature flags
- Runtime configuration updates
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import re

class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class ConfigValidationError(Exception):
    """Configuration validation error"""
    pass

@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str
    pool_size: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    max_overflow: int = 20
    echo: bool = False
    
    def __post_init__(self):
        if not self.url:
            raise ConfigValidationError("Database URL is required")

@dataclass
class AWSConfig:
    """AWS configuration"""
    region: str
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    profile: Optional[str] = None
    skip_validation: bool = False
    bedrock_model_id: str = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    
    def __post_init__(self):
        if not self.region:
            raise ConfigValidationError("AWS region is required")
        
        # Validate region format
        if not re.match(r'^[a-z]{2}-[a-z]+-\d+$', self.region):
            raise ConfigValidationError(f"Invalid AWS region format: {self.region}")

@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 10
    auth_lockout_minutes: int = 15
    max_auth_attempts: int = 5
    allowed_origins: List[str] = field(default_factory=lambda: ['http://localhost:3000'])
    enable_cors: bool = True
    enable_rate_limiting: bool = True
    
    def __post_init__(self):
        if not self.secret_key or len(self.secret_key) < 32:
            raise ConfigValidationError("Secret key must be at least 32 characters")

@dataclass
class FeatureFlags:
    """Feature flag configuration"""
    enhanced_features_enabled: bool = True
    real_time_monitoring: bool = True
    competitive_analysis: bool = True
    admin_interface: bool = True
    data_validation: bool = True
    change_detection: bool = True
    logging_monitoring: bool = True
    batch_processing: bool = True

@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    enabled: bool = True
    interval_seconds: int = 60
    metric_retention_hours: int = 168  # 7 days
    health_check_interval: int = 30
    log_level: str = "INFO"
    log_dir: str = "logs"
    max_log_size_mb: int = 100
    log_backup_count: int = 10
    
    def __post_init__(self):
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            raise ConfigValidationError(f"Invalid log level: {self.log_level}")

@dataclass
class AlertConfig:
    """Alert configuration"""
    enabled: bool = True
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    alert_from_email: Optional[str] = None
    alert_to_emails: List[str] = field(default_factory=list)
    slack_webhook_url: Optional[str] = None
    webhook_urls: List[str] = field(default_factory=list)

@dataclass
class ProcessingConfig:
    """Processing configuration"""
    max_concurrent_tools: int = 3
    api_rate_limit: int = 100
    batch_size_limit: int = 50
    request_timeout_seconds: int = 300
    max_retries: int = 3
    retry_delay_seconds: int = 5

@dataclass
class AppConfig:
    """Main application configuration"""
    environment: Environment
    debug: bool
    database: DatabaseConfig
    aws: AWSConfig
    security: SecurityConfig
    features: FeatureFlags
    monitoring: MonitoringConfig
    alerts: AlertConfig
    processing: ProcessingConfig
    host: str = "0.0.0.0"
    port: int = 5000
    
    def __post_init__(self):
        # Additional validation
        if self.environment == Environment.PRODUCTION and self.debug:
            raise ConfigValidationError("Debug mode should not be enabled in production")

class ConfigManager:
    """Configuration manager with validation and environment support"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.config: Optional[AppConfig] = None
        self.logger = logging.getLogger(__name__)
        
    def load_config(self, environment: Optional[str] = None) -> AppConfig:
        """Load and validate configuration"""
        env = Environment(environment or os.getenv('FLASK_ENV', 'development'))
        
        # Load base configuration
        config_data = self._load_config_data(env)
        
        # Override with environment variables
        config_data = self._override_with_env_vars(config_data)
        
        # Validate and create configuration objects
        self.config = self._create_config_objects(config_data, env)
        
        # Validate configuration
        self._validate_config()
        
        self.logger.info(f"Configuration loaded for environment: {env.value}")
        return self.config
    
    def _load_config_data(self, env: Environment) -> Dict[str, Any]:
        """Load configuration data from files and environment"""
        config_data = {}
        
        # Load from config file if specified
        if self.config_file and Path(self.config_file).exists():
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
        
        # Load environment-specific config
        env_config_file = f"config/{env.value}.json"
        if Path(env_config_file).exists():
            with open(env_config_file, 'r') as f:
                env_config = json.load(f)
                config_data.update(env_config)
        
        return config_data
    
    def _override_with_env_vars(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Override configuration with environment variables"""
        
        # Database configuration
        if os.getenv('DATABASE_URL'):
            config_data.setdefault('database', {})['url'] = os.getenv('DATABASE_URL')
        
        # AWS configuration
        aws_config = config_data.setdefault('aws', {})
        if os.getenv('AWS_REGION'):
            aws_config['region'] = os.getenv('AWS_REGION')
        if os.getenv('AWS_ACCESS_KEY_ID'):
            aws_config['access_key_id'] = os.getenv('AWS_ACCESS_KEY_ID')
        if os.getenv('AWS_SECRET_ACCESS_KEY'):
            aws_config['secret_access_key'] = os.getenv('AWS_SECRET_ACCESS_KEY')
        if os.getenv('AWS_PROFILE'):
            aws_config['profile'] = os.getenv('AWS_PROFILE')
        if os.getenv('SKIP_AWS_VALIDATION'):
            aws_config['skip_validation'] = os.getenv('SKIP_AWS_VALIDATION').lower() == 'true'
        
        # Security configuration
        security_config = config_data.setdefault('security', {})
        if os.getenv('SECRET_KEY'):
            security_config['secret_key'] = os.getenv('SECRET_KEY')
        
        # Feature flags
        features_config = config_data.setdefault('features', {})
        if os.getenv('ENHANCED_FEATURES_ENABLED'):
            features_config['enhanced_features_enabled'] = os.getenv('ENHANCED_FEATURES_ENABLED').lower() == 'true'
        if os.getenv('ENABLE_REAL_TIME_MONITORING'):
            features_config['real_time_monitoring'] = os.getenv('ENABLE_REAL_TIME_MONITORING').lower() == 'true'
        
        # Monitoring configuration
        monitoring_config = config_data.setdefault('monitoring', {})
        if os.getenv('ENABLE_MONITORING'):
            monitoring_config['enabled'] = os.getenv('ENABLE_MONITORING').lower() == 'true'
        if os.getenv('MONITORING_INTERVAL_SECONDS'):
            monitoring_config['interval_seconds'] = int(os.getenv('MONITORING_INTERVAL_SECONDS'))
        if os.getenv('LOG_LEVEL'):
            monitoring_config['log_level'] = os.getenv('LOG_LEVEL')
        if os.getenv('LOG_DIR'):
            monitoring_config['log_dir'] = os.getenv('LOG_DIR')
        
        # Alert configuration
        alert_config = config_data.setdefault('alerts', {})
        if os.getenv('SMTP_SERVER'):
            alert_config['smtp_server'] = os.getenv('SMTP_SERVER')
        if os.getenv('SMTP_PORT'):
            alert_config['smtp_port'] = int(os.getenv('SMTP_PORT'))
        if os.getenv('SMTP_USERNAME'):
            alert_config['smtp_username'] = os.getenv('SMTP_USERNAME')
        if os.getenv('SMTP_PASSWORD'):
            alert_config['smtp_password'] = os.getenv('SMTP_PASSWORD')
        if os.getenv('SMTP_USE_TLS'):
            alert_config['smtp_use_tls'] = os.getenv('SMTP_USE_TLS').lower() == 'true'
        if os.getenv('ALERT_FROM_EMAIL'):
            alert_config['alert_from_email'] = os.getenv('ALERT_FROM_EMAIL')
        if os.getenv('ALERT_TO_EMAILS'):
            alert_config['alert_to_emails'] = os.getenv('ALERT_TO_EMAILS').split(',')
        if os.getenv('SLACK_WEBHOOK_URL'):
            alert_config['slack_webhook_url'] = os.getenv('SLACK_WEBHOOK_URL')
        
        # Processing configuration
        processing_config = config_data.setdefault('processing', {})
        if os.getenv('MAX_CONCURRENT_TOOLS'):
            processing_config['max_concurrent_tools'] = int(os.getenv('MAX_CONCURRENT_TOOLS'))
        if os.getenv('API_RATE_LIMIT'):
            processing_config['api_rate_limit'] = int(os.getenv('API_RATE_LIMIT'))
        if os.getenv('BATCH_SIZE_LIMIT'):
            processing_config['batch_size_limit'] = int(os.getenv('BATCH_SIZE_LIMIT'))
        
        return config_data
    
    def _create_config_objects(self, config_data: Dict[str, Any], env: Environment) -> AppConfig:
        """Create configuration objects from data"""
        
        # Set defaults based on environment
        debug = env in [Environment.DEVELOPMENT, Environment.TESTING]
        
        # Database configuration
        db_data = config_data.get('database', {})
        if not db_data.get('url'):
            db_data['url'] = 'sqlite:///ai_tools.db'
        database_config = DatabaseConfig(**db_data)
        
        # AWS configuration
        aws_data = config_data.get('aws', {})
        if not aws_data.get('region'):
            aws_data['region'] = 'us-east-1'
        aws_config = AWSConfig(**aws_data)
        
        # Security configuration
        security_data = config_data.get('security', {})
        if not security_data.get('secret_key'):
            if env == Environment.PRODUCTION:
                raise ConfigValidationError("SECRET_KEY must be set for production")
            security_data['secret_key'] = 'dev-secret-key-change-in-production-' + 'x' * 32
        security_config = SecurityConfig(**security_data)
        
        # Feature flags
        features_config = FeatureFlags(**config_data.get('features', {}))
        
        # Monitoring configuration
        monitoring_config = MonitoringConfig(**config_data.get('monitoring', {}))
        
        # Alert configuration
        alert_config = AlertConfig(**config_data.get('alerts', {}))
        
        # Processing configuration
        processing_config = ProcessingConfig(**config_data.get('processing', {}))
        
        return AppConfig(
            environment=env,
            debug=debug,
            host=config_data.get('host', '0.0.0.0'),
            port=config_data.get('port', 5000),
            database=database_config,
            aws=aws_config,
            security=security_config,
            features=features_config,
            monitoring=monitoring_config,
            alerts=alert_config,
            processing=processing_config
        )
    
    def _validate_config(self):
        """Validate configuration for consistency and requirements"""
        if not self.config:
            raise ConfigValidationError("Configuration not loaded")
        
        # Production-specific validations
        if self.config.environment == Environment.PRODUCTION:
            # Ensure secure settings
            if self.config.debug:
                raise ConfigValidationError("Debug mode must be disabled in production")
            
            if self.config.security.secret_key.startswith('dev-'):
                raise ConfigValidationError("Production secret key must be changed from default")
            
            # Ensure monitoring is enabled
            if not self.config.monitoring.enabled:
                self.logger.warning("Monitoring is disabled in production")
            
            # Validate AWS configuration for production
            if not self.config.aws.skip_validation:
                if not (self.config.aws.access_key_id or self.config.aws.profile):
                    raise ConfigValidationError("AWS credentials must be configured for production")
        
        # Feature dependency validation
        if self.config.features.real_time_monitoring and not self.config.monitoring.enabled:
            raise ConfigValidationError("Real-time monitoring requires monitoring to be enabled")
        
        if self.config.features.change_detection and not self.config.alerts.enabled:
            self.logger.warning("Change detection is enabled but alerts are disabled")
        
        # Email alert validation
        if self.config.alerts.enabled and self.config.alerts.smtp_server:
            if not self.config.alerts.smtp_username or not self.config.alerts.alert_from_email:
                raise ConfigValidationError("SMTP authentication and from email are required for email alerts")
    
    def get_config(self) -> AppConfig:
        """Get current configuration"""
        if not self.config:
            raise ConfigValidationError("Configuration not loaded. Call load_config() first.")
        return self.config
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled"""
        if not self.config:
            return False
        
        return getattr(self.config.features, feature_name, False)
    
    def update_feature_flag(self, feature_name: str, enabled: bool):
        """Update a feature flag at runtime"""
        if not self.config:
            raise ConfigValidationError("Configuration not loaded")
        
        if hasattr(self.config.features, feature_name):
            setattr(self.config.features, feature_name, enabled)
            self.logger.info(f"Feature flag {feature_name} set to {enabled}")
        else:
            raise ConfigValidationError(f"Unknown feature flag: {feature_name}")
    
    def export_config(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        if not self.config:
            raise ConfigValidationError("Configuration not loaded")
        
        def dataclass_to_dict(obj):
            if hasattr(obj, '__dataclass_fields__'):
                result = {}
                for field_name, field_value in obj.__dict__.items():
                    if not include_secrets and 'secret' in field_name.lower():
                        result[field_name] = '***'
                    elif not include_secrets and 'password' in field_name.lower():
                        result[field_name] = '***'
                    elif hasattr(field_value, '__dataclass_fields__'):
                        result[field_name] = dataclass_to_dict(field_value)
                    elif isinstance(field_value, Enum):
                        result[field_name] = field_value.value
                    else:
                        result[field_name] = field_value
                return result
            return obj
        
        return dataclass_to_dict(self.config)

# Global configuration manager
config_manager = ConfigManager()

def get_config() -> AppConfig:
    """Get the global configuration"""
    return config_manager.get_config()

def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled"""
    return config_manager.is_feature_enabled(feature_name)