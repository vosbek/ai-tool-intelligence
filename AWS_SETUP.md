# AWS Setup Guide for AI Tool Intelligence Platform

> **Clear, step-by-step AWS credential configuration to eliminate confusion**

## 🎯 Quick Summary

1. **Region**: We use `us-east-1` (not us-west-2)
2. **Model**: Claude 3.5 Sonnet must be enabled in us-east-1
3. **Credentials**: Multiple options with clear priority order
4. **Validation**: Built-in credential checker before startup

## 📋 Prerequisites

- AWS Account with admin access or Bedrock permissions
- AWS CLI installed (optional but recommended)
- Claude 3.5 Sonnet model access enabled

## 🔧 Credential Setup Options (Priority Order)

AWS credentials are checked in this exact order. **Use only ONE method** to avoid conflicts:

### Option 1: Environment Variables (Recommended for Production)

**When to use:** Docker, CI/CD, or when you want explicit control

```bash
# Set environment variables (Linux/Mac)
export AWS_ACCESS_KEY_ID=your-access-key-here
export AWS_SECRET_ACCESS_KEY=your-secret-key-here
export AWS_REGION=us-east-1

# For Windows PowerShell
$env:AWS_ACCESS_KEY_ID="your-access-key-here"
$env:AWS_SECRET_ACCESS_KEY="your-secret-key-here"
$env:AWS_REGION="us-east-1"

# For Windows Command Prompt
set AWS_ACCESS_KEY_ID=your-access-key-here
set AWS_SECRET_ACCESS_KEY=your-secret-key-here
set AWS_REGION=us-east-1
```

### Option 2: .env File (Recommended for Development)

**When to use:** Local development, easy management

Create `backend/.env` file:
```env
AWS_ACCESS_KEY_ID=your-access-key-here
AWS_SECRET_ACCESS_KEY=your-secret-key-here
AWS_REGION=us-east-1
```

### Option 3: AWS Profile (Recommended for Multiple AWS Accounts)

**When to use:** Multiple AWS accounts, shared development machine

```bash
# Setup profile
aws configure --profile ai-tools
# Enter your credentials when prompted

# Use the profile
export AWS_PROFILE=ai-tools

# Or add to .env file
echo "AWS_PROFILE=ai-tools" >> backend/.env
```

### Option 4: Default AWS Credentials (Simplest)

**When to use:** Single AWS account, personal machine

```bash
# One-time setup
aws configure
# Enter your credentials when prompted
# This creates ~/.aws/credentials and ~/.aws/config
```

## ⚠️ Credential Conflicts (IMPORTANT)

**Common Problem:** Having multiple credential sources causes confusion.

**Solution:** Use our credential checker to see which credentials are being used:

```bash
cd backend
python aws_credential_validator.py
```

This will show you:
- Which credential source is being used
- Whether Bedrock access works
- Whether Claude 3.5 Sonnet is available

## 🛡️ Step-by-Step AWS Setup

### Step 1: Create AWS Access Keys

1. Go to [AWS Console](https://console.aws.amazon.com)
2. Navigate to **IAM** → **Users** → **Your User**
3. Go to **Security credentials** tab
4. Click **Create access key**
5. Choose **Command Line Interface (CLI)**
6. Download the credentials

### Step 2: Enable Bedrock Access

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock)
2. **IMPORTANT:** Switch region to **US East (N. Virginia) us-east-1**
3. Go to **Model access** in the left sidebar
4. Click **Request model access**
5. Find **Claude 3.5 Sonnet** and request access
6. Wait for approval (usually instant)

### Step 3: Set Up Credentials (Choose ONE Method)

**For Development (.env file method):**
```bash
cd ai-tool-intelligence
cp backend/.env.example backend/.env
nano backend/.env
```

Add your credentials:
```env
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_REGION=us-east-1
```

### Step 4: Validate Setup

```bash
cd backend
python aws_credential_validator.py
```

Expected output:
```
✅ AWS Identity: arn:aws:iam::123456789012:user/your-user
✅ Bedrock access confirmed in us-east-1
✅ Claude 3.5 Sonnet available in us-east-1
🎉 All AWS credentials and permissions validated successfully!
```

## 🚨 Troubleshooting

### Problem: "No valid AWS credentials found"

**Solutions:**
1. Run the credential validator: `python aws_credential_validator.py`
2. Check if you have conflicting credential sources
3. Verify your access keys are correct

### Problem: "Bedrock access failed"

**Solutions:**
1. Verify you're using `us-east-1` region
2. Check if Bedrock is enabled in your AWS account
3. Verify IAM permissions include Bedrock access

### Problem: "Claude 3.5 Sonnet not available"

**Solutions:**
1. Go to Bedrock Console → Model access
2. Ensure you're in `us-east-1` region
3. Request access to Claude 3.5 Sonnet if not already enabled
4. Wait a few minutes for activation

### Problem: Multiple credential sources conflict

**Solution:**
1. Run `python aws_credential_validator.py` to see which source is being used
2. Remove or comment out unused credential sources
3. Follow the priority order (env vars override profiles override .aws files)

## 🔐 IAM Permissions Required

Your AWS user needs these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels",
                "bedrock:GetFoundationModel"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

## 🖥️ Windows-Specific Notes

### PowerShell Credential Setup
```powershell
# Option 1: Environment variables
$env:AWS_ACCESS_KEY_ID="your-key"
$env:AWS_SECRET_ACCESS_KEY="your-secret"
$env:AWS_REGION="us-east-1"

# Option 2: .env file (recommended)
Copy-Item backend\.env.example backend\.env
notepad backend\.env
```

### Command Prompt Setup
```cmd
set AWS_ACCESS_KEY_ID=your-key
set AWS_SECRET_ACCESS_KEY=your-secret
set AWS_REGION=us-east-1
```

## ✅ Validation Checklist

Before starting the application, ensure:

- [ ] AWS credentials are configured (any one method)
- [ ] Region is set to `us-east-1`
- [ ] Bedrock access is enabled
- [ ] Claude 3.5 Sonnet model is available
- [ ] Credential validator passes all checks

## 🚀 Quick Start Commands

```bash
# 1. Validate credentials
cd backend
python aws_credential_validator.py

# 2. If validation passes, start the app
cd ..
./scripts/start.sh

# 3. Or start manually
cd backend && python app.py
cd frontend && npm start
```

## 💡 Pro Tips

1. **Use .env file for development** - easier to manage and version control friendly (with .env in .gitignore)
2. **Use environment variables for production** - more secure for Docker/cloud deployments
3. **Use AWS profiles for multiple accounts** - clean separation of different AWS environments
4. **Always validate first** - run the credential validator before reporting issues
5. **Keep it simple** - use only one credential method to avoid conflicts

## 🆘 Still Having Issues?

1. Run the credential validator and share the output
2. Check the troubleshooting section above
3. Verify you're using `us-east-1` region
4. Ensure Claude 3.5 Sonnet is enabled in Bedrock Console