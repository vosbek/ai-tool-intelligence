"""
Configuration management for Strands Batch CLI
"""

import os
from typing import Dict, Optional, Tuple, Any
from pathlib import Path
from dotenv import load_dotenv

class Config:
    """Configuration manager for Strands Batch CLI"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """Initialize configuration"""
        self.config_file = config_file or Path('.env')
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment and .env file"""
        if self.config_file.exists():
            load_dotenv(self.config_file)
        
        # Strands/Model Configuration
        self.model_provider = os.getenv('MODEL_PROVIDER', 'bedrock')
        self.model_id = os.getenv('MODEL_ID', 'us.amazon.nova-pro-v1:0')
        self.model_temperature = float(os.getenv('MODEL_TEMPERATURE', '0.3'))
        self.model_streaming = os.getenv('MODEL_STREAMING', 'true').lower() == 'true'
        
        # AWS Configuration
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
        
        # OpenAI Configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # GitHub API
        self.github_token = os.getenv('GITHUB_TOKEN')
        
        # Firecrawl (Enhanced web scraping)
        self.firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')
        
        # Other APIs
        self.alpha_vantage_api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.exchange_rate_api_key = os.getenv('EXCHANGE_RATE_API_KEY')
        
        # Database Configuration
        self.database_path = os.getenv('DATABASE_PATH', 'strands_batch.db')
        
        # Processing Configuration
        self.max_concurrent_jobs = int(os.getenv('MAX_CONCURRENT_JOBS', '1'))
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
        self.rate_limit_delay = float(os.getenv('RATE_LIMIT_DELAY', '1.0'))
    
    def validate(self) -> bool:
        """Validate configuration"""
        required_for_model = []
        
        if self.model_provider == 'bedrock':
            if not self.aws_access_key_id or not self.aws_secret_access_key:
                required_for_model.append("AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
        elif self.model_provider == 'openai':
            if not self.openai_api_key:
                required_for_model.append("OpenAI API key (OPENAI_API_KEY)")
        
        if required_for_model:
            print(f"❌ Missing required configuration: {', '.join(required_for_model)}")
            return False
        
        return True
    
    def get_api_status(self) -> Dict[str, bool]:
        """Get status of available APIs"""
        return {
            'github': bool(self.github_token),
            'firecrawl': bool(self.firecrawl_api_key),
            'alpha_vantage': bool(self.alpha_vantage_api_key),
            'news_api': bool(self.news_api_key),
            'exchange_rate': bool(self.exchange_rate_api_key),
            'aws': bool(self.aws_access_key_id and self.aws_secret_access_key),
            'openai': bool(self.openai_api_key)
        }
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration"""
        return {
            'provider': self.model_provider,
            'model_id': self.model_id,
            'temperature': self.model_temperature,
            'streaming': self.model_streaming,
            'region': self.aws_region if self.model_provider == 'bedrock' else None
        }
    
    def get_model_info(self) -> str:
        """Get model information string"""
        if self.model_provider == 'bedrock':
            return f"Bedrock: {self.model_id} ({self.aws_region})"
        elif self.model_provider == 'openai':
            return f"OpenAI: {self.model_id}"
        else:
            return f"Unknown: {self.model_provider}"
    
    def test_apis(self) -> Dict[str, Tuple[bool, str]]:
        """Test API connections"""
        results = {}
        
        # Test GitHub API
        if self.github_token:
            try:
                import requests
                response = requests.get(
                    'https://api.github.com/user',
                    headers={'Authorization': f'token {self.github_token}'},
                    timeout=10
                )
                results['github'] = (response.status_code == 200, f"Status: {response.status_code}")
            except Exception as e:
                results['github'] = (False, f"Error: {str(e)}")
        else:
            results['github'] = (False, "No token configured")
        
        # Test AWS (if using Bedrock)
        if self.model_provider == 'bedrock' and self.aws_access_key_id:
            try:
                import boto3
                client = boto3.client(
                    'bedrock-runtime',
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    region_name=self.aws_region
                )
                # Try to list models (this will fail if no permissions, but will validate credentials)
                client.list_models()
                results['aws'] = (True, "Credentials valid")
            except Exception as e:
                results['aws'] = (False, f"Error: {str(e)}")
        else:
            results['aws'] = (False, "Not configured for Bedrock")
        
        # Test OpenAI (if configured)
        if self.openai_api_key:
            try:
                import requests
                response = requests.get(
                    'https://api.openai.com/v1/models',
                    headers={'Authorization': f'Bearer {self.openai_api_key}'},
                    timeout=10
                )
                results['openai'] = (response.status_code == 200, f"Status: {response.status_code}")
            except Exception as e:
                results['openai'] = (False, f"Error: {str(e)}")
        else:
            results['openai'] = (False, "No API key configured")
        
        # Test Firecrawl
        if self.firecrawl_api_key:
            try:
                import requests
                response = requests.get(
                    'https://api.firecrawl.dev/v0/crawl/status/test',
                    headers={'Authorization': f'Bearer {self.firecrawl_api_key}'},
                    timeout=10
                )
                results['firecrawl'] = (response.status_code in [200, 404], "Connection OK")
            except Exception as e:
                results['firecrawl'] = (False, f"Error: {str(e)}")
        else:
            results['firecrawl'] = (False, "No API key configured")
        
        return results
    
    def set(self, key: str, value: str):
        """Set configuration value"""
        # Update environment variable
        os.environ[key.upper()] = value
        
        # Update .env file
        env_lines = []
        found = False
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                env_lines = f.readlines()
        
        # Update existing key or add new one
        for i, line in enumerate(env_lines):
            if line.strip().startswith(f"{key.upper()}="):
                env_lines[i] = f"{key.upper()}={value}\n"
                found = True
                break
        
        if not found:
            env_lines.append(f"{key.upper()}={value}\n")
        
        # Write back to file
        with open(self.config_file, 'w') as f:
            f.writelines(env_lines)
        
        # Reload configuration
        self._load_config()
    
    def create_sample_config(self) -> str:
        """Create a sample .env configuration file"""
        sample_config = """# Strands Batch CLI Configuration

# Model Configuration
MODEL_PROVIDER=bedrock  # bedrock, openai
MODEL_ID=us.amazon.nova-pro-v1:0
MODEL_TEMPERATURE=0.3
MODEL_STREAMING=true

# AWS Configuration (for Bedrock)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-west-2

# OpenAI Configuration (alternative to Bedrock)
OPENAI_API_KEY=your_openai_api_key

# GitHub API (for repository analysis)
GITHUB_TOKEN=your_github_token

# Enhanced Web Scraping (Firecrawl)
FIRECRAWL_API_KEY=your_firecrawl_api_key

# Additional APIs (optional)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
NEWS_API_KEY=your_news_api_key
EXCHANGE_RATE_API_KEY=your_exchange_rate_key

# Database
DATABASE_PATH=strands_batch.db

# Processing Configuration
MAX_CONCURRENT_JOBS=1
REQUEST_TIMEOUT=30
RATE_LIMIT_DELAY=1.0
"""
        return sample_config