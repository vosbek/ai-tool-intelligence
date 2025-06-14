#!/usr/bin/env python3
"""
AWS Credential Validator for AI Tool Intelligence Platform

This script validates AWS credentials and Bedrock access in the correct priority order:
1. Environment variables
2. AWS profiles 
3. .aws/credentials file
4. Default credential chain
"""

import os
import sys
import json
from typing import Dict, Optional, Tuple
from pathlib import Path

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound
except ImportError:
    print("❌ boto3 not installed. Run: pip install boto3")
    sys.exit(1)

class AWSCredentialValidator:
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.required_model = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        
    def validate_credentials(self) -> Dict:
        """Validate AWS credentials and return status"""
        print("🔍 Validating AWS credentials...")
        
        results = {
            "credentials_valid": False,
            "credential_source": None,
            "region": self.region,
            "sts_identity": None,
            "bedrock_access": False,
            "claude_model_available": False,
            "errors": []
        }
        
        # Step 1: Try to establish credentials
        credential_source, session = self._get_credentials()
        if not credential_source:
            results["errors"].append("No valid AWS credentials found")
            return results
            
        results["credential_source"] = credential_source
        results["credentials_valid"] = True
        
        # Step 2: Verify identity with STS
        try:
            sts_client = session.client('sts', region_name=self.region)
            identity = sts_client.get_caller_identity()
            results["sts_identity"] = {
                "account": identity.get("Account"),
                "user_id": identity.get("UserId"),
                "arn": identity.get("Arn")
            }
            print(f"✅ AWS Identity: {identity.get('Arn')}")
        except Exception as e:
            results["errors"].append(f"STS identity verification failed: {str(e)}")
            return results
            
        # Step 3: Check Bedrock access
        try:
            bedrock_client = session.client('bedrock', region_name=self.region)
            bedrock_client.list_foundation_models()
            results["bedrock_access"] = True
            print(f"✅ Bedrock access confirmed in {self.region}")
        except Exception as e:
            results["errors"].append(f"Bedrock access failed: {str(e)}")
            
        # Step 4: Check Claude model availability
        if results["bedrock_access"]:
            try:
                bedrock_client = session.client('bedrock', region_name=self.region)
                models = bedrock_client.list_foundation_models()
                
                claude_available = any(
                    model['modelId'] == self.required_model 
                    for model in models.get('modelSummaries', [])
                )
                
                if claude_available:
                    results["claude_model_available"] = True
                    print(f"✅ Claude 3.5 Sonnet available in {self.region}")
                else:
                    results["errors"].append(f"Claude 3.5 Sonnet not available in {self.region}")
                    # List available Claude models
                    claude_models = [
                        model['modelId'] for model in models.get('modelSummaries', [])
                        if 'claude' in model['modelId'].lower()
                    ]
                    if claude_models:
                        results["errors"].append(f"Available Claude models: {claude_models}")
                        
            except Exception as e:
                results["errors"].append(f"Claude model check failed: {str(e)}")
                
        return results
    
    def _get_credentials(self) -> Tuple[Optional[str], Optional[boto3.Session]]:
        """Try to get credentials in priority order"""
        
        # Priority 1: Environment variables
        env_creds = self._check_environment_variables()
        if env_creds:
            try:
                session = boto3.Session(
                    aws_access_key_id=env_creds['access_key'],
                    aws_secret_access_key=env_creds['secret_key'],
                    region_name=env_creds.get('region', self.region)
                )
                # Test the session
                session.client('sts').get_caller_identity()
                print(f"✅ Using environment variables")
                return "Environment Variables", session
            except Exception as e:
                print(f"⚠️  Environment variables present but invalid: {e}")
        
        # Priority 2: AWS Profile (includes SSO profiles)
        profile_name = os.getenv('AWS_PROFILE', 'default')
        try:
            session = boto3.Session(profile_name=profile_name, region_name=self.region)
            identity = session.client('sts').get_caller_identity()
            
            # Check if this is an SSO session
            credentials = session.get_credentials()
            if credentials and hasattr(credentials, 'token') and credentials.token:
                print(f"✅ Using AWS SSO profile: {profile_name}")
                return f"AWS SSO Profile ({profile_name})", session
            else:
                print(f"✅ Using AWS profile: {profile_name}")
                return f"AWS Profile ({profile_name})", session
                
        except (ProfileNotFound, NoCredentialsError):
            print(f"⚠️  AWS profile '{profile_name}' not found or invalid")
            if profile_name != 'default':
                print(f"💡 Hint: If using SSO, ensure you're logged in with: aws sso login --profile {profile_name}")
        except Exception as e:
            error_msg = str(e).lower()
            if 'sso' in error_msg or 'token' in error_msg:
                print(f"⚠️  AWS SSO session expired or invalid")
                print(f"💡 Try: aws sso login --profile {profile_name}")
            else:
                print(f"⚠️  AWS profile error: {e}")
        
        # Priority 3: Default credential chain (includes .aws/credentials and other sources)
        try:
            session = boto3.Session(region_name=self.region)
            identity = session.client('sts').get_caller_identity()
            
            # Try to determine source
            credentials = session.get_credentials()
            if credentials:
                # Check if it's SSO
                if hasattr(credentials, 'token') and credentials.token:
                    print(f"✅ Using AWS SSO (default profile)")
                    return "AWS SSO (default)", session
                # Check if it's from .aws/credentials file
                aws_dir = Path.home() / '.aws'
                if (aws_dir / 'credentials').exists():
                    print(f"✅ Using .aws/credentials file")
                    return ".aws/credentials file", session
                else:
                    print(f"✅ Using default credential chain")
                    return "Default credential chain", session
        except Exception as e:
            error_msg = str(e).lower()
            if 'sso' in error_msg or 'token' in error_msg:
                print(f"⚠️  Default AWS SSO session expired")
                print(f"💡 Try: aws sso login")
            else:
                print(f"⚠️  Default credential chain failed: {e}")
        
        return None, None
    
    def _check_environment_variables(self) -> Optional[Dict]:
        """Check for AWS environment variables"""
        access_key = os.getenv('AWS_ACCESS_KEY_ID')
        secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        region = os.getenv('AWS_REGION', os.getenv('AWS_DEFAULT_REGION'))
        
        if access_key and secret_key:
            return {
                'access_key': access_key,
                'secret_key': secret_key,
                'region': region
            }
        return None
    
    def print_credential_guide(self):
        """Print setup instructions"""
        print("\n📋 AWS Credential Setup Guide")
        print("=" * 50)
        print("\nCredentials are checked in this priority order:")
        print("1. Environment Variables (highest priority)")
        print("2. AWS Profile (including SSO profiles)")
        print("3. .aws/credentials file")
        print("4. Default credential chain")
        
        print("\n🔧 Setup Options:")
        
        print("\n1. AWS SSO (Recommended for Enterprise):")
        print("   # Configure SSO profile")
        print("   aws configure sso --profile your-sso-profile")
        print("   # Follow prompts for:")
        print("   #   - SSO start URL (e.g., https://company.awsapps.com/start)")
        print("   #   - SSO region")
        print("   #   - Account ID and role")
        print("   #   - Default region (us-east-1)")
        print("   ")
        print("   # Login to SSO")
        print("   aws sso login --profile your-sso-profile")
        print("   ")
        print("   # Use the profile")
        print("   export AWS_PROFILE=your-sso-profile")
        print("   # OR set in .env file:")
        print("   # AWS_PROFILE=your-sso-profile")
        
        print("\n2. Environment Variables (for Docker/CI):")
        print("   export AWS_ACCESS_KEY_ID=your-access-key")
        print("   export AWS_SECRET_ACCESS_KEY=your-secret-key")
        print("   export AWS_REGION=us-east-1")
        
        print("\n3. .env file (for local development):")
        print("   AWS_ACCESS_KEY_ID=your-access-key")
        print("   AWS_SECRET_ACCESS_KEY=your-secret-key")
        print("   AWS_REGION=us-east-1")
        print("   # OR for SSO:")
        print("   AWS_PROFILE=your-sso-profile")
        
        print("\n4. AWS Profile (traditional credentials):")
        print("   aws configure --profile your-profile")
        print("   export AWS_PROFILE=your-profile")
        
        print("\n5. .aws/credentials file (default):")
        print("   aws configure")
        print("   (This creates ~/.aws/credentials and ~/.aws/config)")
        
        print(f"\n🚨 Required:")
        print(f"   - AWS Account with Bedrock access")
        print(f"   - Claude 3.5 Sonnet enabled in {self.region}")
        print(f"   - Proper IAM permissions for Bedrock")
        
        print(f"\n💡 SSO Troubleshooting:")
        print(f"   - If SSO session expires: aws sso login --profile your-profile")
        print(f"   - Check SSO status: aws sts get-caller-identity --profile your-profile")
        print(f"   - List configured profiles: aws configure list-profiles")
        print(f"   - SSO browser issues: Use --no-browser flag or check browser settings")

def main():
    """Main validation function"""
    print("🚀 AI Tool Intelligence Platform - AWS Credential Validator")
    print("=" * 60)
    
    validator = AWSCredentialValidator()
    results = validator.validate_credentials()
    
    print("\n📊 Validation Results:")
    print("-" * 30)
    
    if results["credentials_valid"]:
        print(f"✅ Credentials: Valid ({results['credential_source']})")
        if results["sts_identity"]:
            print(f"✅ Account: {results['sts_identity']['account']}")
            print(f"✅ Region: {results['region']}")
    else:
        print("❌ Credentials: Invalid")
    
    if results["bedrock_access"]:
        print("✅ Bedrock: Accessible")
    else:
        print("❌ Bedrock: Not accessible")
        
    if results["claude_model_available"]:
        print("✅ Claude 3.5 Sonnet: Available")
    else:
        print("❌ Claude 3.5 Sonnet: Not available")
    
    if results["errors"]:
        print("\n❌ Errors:")
        for error in results["errors"]:
            print(f"   • {error}")
    
    # Print setup guide if there are issues
    if not results["credentials_valid"] or not results["bedrock_access"] or not results["claude_model_available"]:
        validator.print_credential_guide()
        return False
    
    print("\n🎉 All AWS credentials and permissions validated successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)