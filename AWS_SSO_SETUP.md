# AWS SSO Setup Guide for AI Tool Intelligence Platform

This guide shows you how to configure AWS SSO (Single Sign-On) for use with the AI Tool Intelligence Platform.

## ✅ **Yes, AWS SSO Works!**

The application fully supports AWS SSO authentication. The enhanced credential validator automatically detects and works with SSO profiles.

## 🚀 Quick Setup

### 1. Configure AWS SSO Profile

```bash
# Configure a new SSO profile
aws configure sso --profile my-sso-profile

# You'll be prompted for:
# SSO start URL: https://your-company.awsapps.com/start
# SSO region: us-east-1 (or your SSO region)
# Account ID: 123456789012
# Role name: DeveloperAccess (or your role)
# Default region: us-east-1
# Default output format: json
```

### 2. Login to AWS SSO

```bash
# Login using your SSO profile
aws sso login --profile my-sso-profile

# This will:
# 1. Open your browser
# 2. Redirect to your company's SSO login page
# 3. Authenticate with your corporate credentials
# 4. Authorize the AWS CLI
```

### 3. Configure the Platform

**Option A: Use Environment Variable**
```bash
# Set the profile to use
export AWS_PROFILE=my-sso-profile

# Start the platform
python backend/app.py
```

**Option B: Use .env File**
```bash
# Edit your .env file
nano backend/.env

# Add this line:
AWS_PROFILE=my-sso-profile
```

### 4. Verify Setup

```bash
# Test the credential validator
python backend/aws_credential_validator.py

# Expected output:
# ✅ Using AWS SSO profile: my-sso-profile
# ✅ AWS Identity: arn:aws:sts::123456789012:assumed-role/DeveloperAccess/user@company.com
# ✅ Bedrock access confirmed in us-east-1
# ✅ Claude 3.5 Sonnet available
```

## 🔧 Common SSO Scenarios

### Multiple AWS Accounts

If you have access to multiple AWS accounts:

```bash
# Configure profiles for different accounts
aws configure sso --profile dev-account
aws configure sso --profile prod-account

# Use specific account
export AWS_PROFILE=dev-account
python backend/app.py
```

### Role-Based Access

If you have different roles in the same account:

```bash
# Configure profiles for different roles
aws configure sso --profile developer-role
aws configure sso --profile admin-role

# Use specific role
export AWS_PROFILE=admin-role
```

### Default Profile Setup

To make SSO your default:

```bash
# Configure the default profile as SSO
aws configure sso

# No need to set AWS_PROFILE
python backend/app.py
```

## 🔄 Session Management

### Check SSO Status

```bash
# Check if you're logged in
aws sts get-caller-identity --profile my-sso-profile

# If session expired, you'll see an error
```

### Refresh Session

```bash
# Re-login when session expires
aws sso login --profile my-sso-profile

# Sessions typically last 8-12 hours
```

### Automatic Session Refresh

The platform will detect expired SSO sessions and provide helpful error messages:

```
⚠️  AWS SSO session expired or invalid
💡 Try: aws sso login --profile my-sso-profile
```

## 🛠️ Troubleshooting

### 1. SSO Session Expired

**Problem:** Application fails with SSO token errors

**Solution:**
```bash
aws sso login --profile my-sso-profile
```

### 2. Browser Issues

**Problem:** SSO login doesn't open browser or browser blocks popup

**Solution:**
```bash
# Use manual browser copy-paste method
aws sso login --profile my-sso-profile --no-browser

# Follow the instructions to copy the URL manually
```

### 3. Profile Not Found

**Problem:** `ProfileNotFound` error

**Solution:**
```bash
# List available profiles
aws configure list-profiles

# Ensure your profile name is correct
export AWS_PROFILE=correct-profile-name
```

### 4. Permission Issues

**Problem:** Bedrock access denied with SSO

**Solution:**
- Verify your SSO role has Bedrock permissions
- Check with your AWS administrator
- Required permissions:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "bedrock:InvokeModel",
          "bedrock:ListFoundationModels"
        ],
        "Resource": "*"
      }
    ]
  }
  ```

### 5. Region Issues

**Problem:** Claude model not available

**Solution:**
```bash
# Ensure you're using us-east-1 region
aws configure set region us-east-1 --profile my-sso-profile

# Or set in environment
export AWS_REGION=us-east-1
```

## 📋 Configuration Examples

### Corporate SSO Setup

```bash
# Example for company "Acme Corp"
aws configure sso --profile acme-dev

# Prompts:
# SSO start URL: https://acme.awsapps.com/start
# SSO region: us-east-1
# Account ID: 111122223333
# Role name: DeveloperAccess
# Default region: us-east-1
```

### Multi-Account Setup

```bash
# Development account
aws configure sso --profile acme-dev
# Production account  
aws configure sso --profile acme-prod

# Switch between environments
export AWS_PROFILE=acme-dev    # For development
export AWS_PROFILE=acme-prod   # For production
```

### .env File Configuration

```bash
# For development environment
AWS_PROFILE=acme-dev
AWS_REGION=us-east-1
SKIP_AWS_VALIDATION=false

# For production environment  
AWS_PROFILE=acme-prod
AWS_REGION=us-east-1
SKIP_AWS_VALIDATION=false
```

## 🎯 Best Practices

### 1. Session Management

- **Login Daily**: SSO sessions typically expire after 8-12 hours
- **Multiple Terminals**: Each terminal session may need separate login
- **Automation**: Consider using longer-lived credentials for CI/CD

### 2. Profile Organization

- **Descriptive Names**: Use clear profile names like `company-dev`, `company-prod`
- **Consistent Regions**: Always use `us-east-1` for Bedrock access
- **Document Roles**: Keep track of which roles have Bedrock permissions

### 3. Security

- **Regular Refresh**: Re-login regularly for security
- **Least Privilege**: Only request necessary permissions
- **Audit Access**: Regularly review SSO access logs

## 🚀 Platform Integration

The AI Tool Intelligence Platform automatically:

- ✅ **Detects SSO Sessions**: Recognizes when you're using SSO
- ✅ **Validates Permissions**: Checks Bedrock and Claude access
- ✅ **Provides Guidance**: Shows helpful error messages for SSO issues
- ✅ **Supports All Features**: Full platform functionality with SSO

### Supported Authentication Methods (in priority order):

1. **Environment Variables** (highest priority)
2. **AWS SSO Profiles** ← Your setup
3. **Traditional AWS Profiles**
4. **Default Credential Chain**

## 📞 Getting Help

If you encounter issues:

1. **Test Credentials**: `python backend/aws_credential_validator.py`
2. **Check SSO Status**: `aws sts get-caller-identity --profile your-profile`
3. **Re-login**: `aws sso login --profile your-profile`
4. **Contact Support**: Include the output of the credential validator

---

**🎉 You're all set!** Your AWS SSO setup will work seamlessly with the AI Tool Intelligence Platform. The enhanced credential validator provides detailed feedback and troubleshooting guidance specifically for SSO users.