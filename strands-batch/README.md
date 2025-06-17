# Strands Batch CLI

A command-line interface for batch processing AI tool research using the Strands Agents SDK, built on top of the existing enhanced research capabilities.

## Features

- 🤖 **Strands Agent Integration**: Uses official Strands SDK with enhanced research tools
- 📊 **Batch Processing**: Analyze multiple tools from JSON input files
- 🔍 **Status Tracking**: Monitor job progress with persistent status tracking
- 📈 **Comprehensive Analysis**: GitHub, pricing, company, feature, and integration analysis
- 🛠️ **CLI Interface**: Easy-to-use command-line interface with Typer
- 💾 **Data Persistence**: SQLite database for job history and results
- 🔧 **Configurable**: Support for multiple AI models (Bedrock, OpenAI)

## Installation

1. **Clone and navigate to the strands-batch directory:**
   ```bash
   cd strands-batch
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the system:**
   ```bash
   python cli.py init
   ```

## Configuration

Create a `.env` file with your API keys and configuration:

```env
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

# Optional APIs
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
NEWS_API_KEY=your_news_api_key
EXCHANGE_RATE_API_KEY=your_exchange_rate_key
```

### API Keys Setup

1. **GitHub Token**: Create at https://github.com/settings/tokens
2. **AWS Credentials**: For Bedrock model access
3. **OpenAI API Key**: Alternative to Bedrock
4. **Firecrawl API Key**: For enhanced web scraping (optional but recommended)

## Usage

### Initialize System
```bash
python cli.py init
```

### Analyze Single Tool
```bash
python cli.py run "GitHub Copilot" \
  --url "https://github.com/features/copilot" \
  --github "https://github.com/github/copilot-docs" \
  --company "GitHub"
```

### Check Status
```bash
# Check all recent jobs
python cli.py status

# Check specific job
python cli.py status --job abc123

# Show as JSON
python cli.py status --format json
```

### Batch Analysis
Create a JSON file with tools to analyze:

```json
[
  {
    "name": "GitHub Copilot",
    "website_url": "https://github.com/features/copilot",
    "github_url": "https://github.com/github/copilot-docs",
    "company_name": "GitHub"
  },
  {
    "name": "Cursor",
    "website_url": "https://cursor.sh",
    "github_url": "https://github.com/getcursor/cursor",
    "company_name": "Anysphere"
  }
]
```

Run batch analysis:
```bash
python cli.py batch tools.json --output-dir results/
```

### Export Results
```bash
# Export all completed jobs
python cli.py export --format json --output results.json --status completed

# Export recent jobs
python cli.py export --format json --output recent.json --limit 10
```

### Manage Configuration
```bash
# Show current config
python cli.py config --show

# Test API connections
python cli.py config --test

# Set configuration
python cli.py config --set MODEL_PROVIDER --value openai
```

### Clean Up Old Jobs
```bash
# See what would be deleted (dry run)
python cli.py clean --days 30 --dry-run

# Delete old jobs
python cli.py clean --days 30 --yes
```

## Command Reference

### `init`
Initialize the database and validate configuration.

**Options:**
- `--config, -c`: Path to config file
- `--force, -f`: Force reinitialize database

### `run`
Analyze a single tool.

**Arguments:**
- `tool_name`: Name of the tool to analyze

**Options:**
- `--url, -u`: Tool website URL (required)
- `--github, -g`: GitHub repository URL
- `--docs, -d`: Documentation URL
- `--company, -c`: Company name
- `--force`: Force re-analysis if already exists
- `--async, -a`: Run in background
- `--output, -o`: Save results to file

### `batch`
Run batch analysis on multiple tools.

**Arguments:**
- `input_file`: JSON file with tools to analyze

**Options:**
- `--concurrent, -c`: Number of concurrent analyses (default: 1)
- `--output-dir, -o`: Directory to save results
- `--force`: Force re-analysis of existing tools

### `status`
Check status of analysis jobs.

**Options:**
- `--job, -j`: Specific job ID to check
- `--format, -f`: Output format (table, json, summary)
- `--limit, -l`: Limit number of jobs shown

### `export`
Export analysis results.

**Options:**
- `--format, -f`: Export format (json)
- `--output, -o`: Output file path (required)
- `--status`: Filter by status
- `--limit`: Limit number of results

### `clean`
Clean up old analysis jobs.

**Options:**
- `--days, -d`: Delete jobs older than N days (default: 30)
- `--status`: Only delete jobs with specific status
- `--dry-run`: Show what would be deleted without deleting
- `--yes, -y`: Skip confirmation prompt

### `config`
Manage configuration.

**Options:**
- `--show`: Show current configuration
- `--set`: Set configuration key
- `--value`: Configuration value
- `--test`: Test API connections

## Job Statuses

- **pending**: Job created but not started
- **running**: Job currently in progress
- **completed**: Job finished successfully
- **error**: Job failed with error

## Data Structure

Analysis results include:
- **GitHub Analysis**: Repository metrics, activity, contributors
- **Pricing Analysis**: Pricing models, tiers, business information
- **Company Analysis**: Company background, funding, leadership
- **Feature Analysis**: Feature categorization and capabilities
- **Integration Analysis**: Ecosystem integrations and APIs
- **Overall Summary**: Recommendation scores and key insights

## Architecture

The CLI is built on top of the existing enhanced research tools:

1. **CLI Layer** (`cli.py`): Typer-based command interface
2. **Agent Layer** (`strands_agent.py`): Strands SDK integration
3. **Research Tools**: Enhanced analysis functions from parent project
4. **Data Layer** (`models.py`): SQLite-based job tracking
5. **Configuration** (`config.py`): Environment and API management

## Troubleshooting

### Common Issues

1. **"Strands SDK not available"**
   - Install: `pip install strands-agents strands-agents-tools`

2. **"AWS credentials not found"**
   - Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
   - Ensure Bedrock access is enabled in your AWS account

3. **"GitHub API rate limited"**
   - Set GITHUB_TOKEN in your .env file
   - Use authenticated requests for higher rate limits

4. **"Analysis failed"**
   - Check job status with `python cli.py status --job <job_id>`
   - Review error messages in the job details

### Debug Mode

Set environment variable for verbose output:
```bash
export DEBUG=1
python cli.py run "Tool Name" --url "https://example.com"
```

## Contributing

This CLI builds on the existing enhanced research capabilities. To add new features:

1. Add new tools to the existing research modules
2. Update `strands_agent.py` to use new tools
3. Add CLI commands in `cli.py` as needed
4. Update database schema in `models.py` if required

## License

Same as parent project.