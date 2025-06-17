#!/usr/bin/env python3
"""
Strands Batch CLI - Command line interface for running batch research operations
using the Strands Agents SDK without Flask dependency.
"""

import typer
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sys
import os
from enum import Enum

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from strands_agent import StrandsBatchAgent
from config import Config
from models import JobStatus, AnalysisJob, create_database

app = typer.Typer(help="Strands Batch CLI for AI Tool Research")

class OutputFormat(str, Enum):
    json = "json"
    table = "table"
    summary = "summary"

@app.command()
def init(
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to config file"),
    force: bool = typer.Option(False, "--force", "-f", help="Force reinitialize database")
):
    """Initialize the Strands batch system."""
    typer.echo("🔧 Initializing Strands Batch CLI...")
    
    # Create database
    if create_database(force=force):
        typer.echo("✅ Database initialized successfully")
    else:
        typer.echo("❌ Failed to initialize database")
        raise typer.Exit(1)
    
    # Initialize config
    config = Config()
    if config.validate():
        typer.echo("✅ Configuration validated")
        typer.echo(f"   • Available APIs: {sum(config.get_api_status().values())}")
        typer.echo(f"   • Model: {config.get_model_info()}")
    else:
        typer.echo("⚠️  Configuration has issues - check your API keys")
    
    typer.echo("🚀 Strands Batch CLI ready!")

@app.command()
def status(
    job_id: Optional[str] = typer.Option(None, "--job", "-j", help="Specific job ID to check"),
    format: OutputFormat = typer.Option(OutputFormat.table, "--format", "-f", help="Output format"),
    limit: int = typer.Option(10, "--limit", "-l", help="Limit number of jobs shown")
):
    """Check status of analysis jobs."""
    
    if job_id:
        job = AnalysisJob.get_by_id(job_id)
        if not job:
            typer.echo(f"❌ Job {job_id} not found")
            raise typer.Exit(1)
        
        _display_job_details(job, format)
    else:
        jobs = AnalysisJob.get_recent(limit)
        _display_jobs_table(jobs, format)

@app.command()
def run(
    tool_name: str = typer.Argument(..., help="Name of the tool to analyze"),
    website_url: str = typer.Option(..., "--url", "-u", help="Tool website URL"),
    github_url: Optional[str] = typer.Option(None, "--github", "-g", help="GitHub repository URL"),
    docs_url: Optional[str] = typer.Option(None, "--docs", "-d", help="Documentation URL"),
    company_name: Optional[str] = typer.Option(None, "--company", "-c", help="Company name"),
    force: bool = typer.Option(False, "--force", help="Force re-analysis if already exists"),
    async_mode: bool = typer.Option(False, "--async", "-a", help="Run in background"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Save results to file")
):
    """Run analysis on a single tool."""
    
    tool_data = {
        "name": tool_name,
        "website_url": website_url,
        "github_url": github_url,
        "docs_url": docs_url,
        "company_name": company_name or tool_name.split()[0]
    }
    
    typer.echo(f"🔍 Starting analysis for: {tool_name}")
    
    # Check if already exists and not forcing
    existing_job = AnalysisJob.get_by_tool_name(tool_name)
    if existing_job and not force:
        if existing_job.status == JobStatus.COMPLETED:
            typer.echo(f"✅ Tool already analyzed. Use --force to re-analyze.")
            typer.echo(f"   Job ID: {existing_job.job_id}")
            typer.echo(f"   Completed: {existing_job.completed_at}")
            if output_file:
                _save_results_to_file(existing_job.results, output_file)
            return
        elif existing_job.status == JobStatus.RUNNING:
            typer.echo(f"🔄 Analysis already in progress.")
            typer.echo(f"   Job ID: {existing_job.job_id}")
            typer.echo(f"   Started: {existing_job.created_at}")
            return
    
    # Create new job
    job = AnalysisJob.create(tool_data)
    typer.echo(f"📝 Created job: {job.job_id}")
    
    if async_mode:
        typer.echo(f"🚀 Running in background. Check status with: strands-batch status --job {job.job_id}")
        # TODO: Implement background processing
        return
    
    # Run synchronous analysis
    agent = StrandsBatchAgent()
    
    try:
        with typer.progressbar(range(5), label="Analyzing tool") as progress:
            for i in progress:
                # This is a placeholder for actual progress tracking
                pass
        
        results = agent.analyze_tool(tool_data)
        
        if "error" in results:
            job.update_status(JobStatus.ERROR, error_message=results["error"])
            typer.echo(f"❌ Analysis failed: {results['error']}")
            raise typer.Exit(1)
        
        job.update_status(JobStatus.COMPLETED, results=results)
        typer.echo(f"✅ Analysis completed successfully!")
        
        # Display summary
        _display_analysis_summary(results)
        
        # Save to file if requested
        if output_file:
            _save_results_to_file(results, output_file)
            typer.echo(f"💾 Results saved to: {output_file}")
        
    except Exception as e:
        job.update_status(JobStatus.ERROR, error_message=str(e))
        typer.echo(f"❌ Analysis failed: {str(e)}")
        raise typer.Exit(1)

@app.command()
def batch(
    input_file: Path = typer.Argument(..., help="JSON file with tools to analyze"),
    concurrent: int = typer.Option(1, "--concurrent", "-c", help="Number of concurrent analyses"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Directory to save results"),
    force: bool = typer.Option(False, "--force", help="Force re-analysis of existing tools")
):
    """Run batch analysis on multiple tools from a JSON file."""
    
    if not input_file.exists():
        typer.echo(f"❌ Input file not found: {input_file}")
        raise typer.Exit(1)
    
    try:
        with open(input_file) as f:
            tools_data = json.load(f)
    except json.JSONDecodeError as e:
        typer.echo(f"❌ Invalid JSON file: {e}")
        raise typer.Exit(1)
    
    if not isinstance(tools_data, list):
        typer.echo("❌ JSON file must contain a list of tools")
        raise typer.Exit(1)
    
    typer.echo(f"📋 Processing {len(tools_data)} tools...")
    
    agent = StrandsBatchAgent()
    jobs = []
    
    # Create jobs for all tools
    for tool_data in tools_data:
        if "name" not in tool_data:
            typer.echo(f"⚠️  Skipping tool without name: {tool_data}")
            continue
        
        # Check if already exists
        existing_job = AnalysisJob.get_by_tool_name(tool_data["name"])
        if existing_job and not force:
            if existing_job.status == JobStatus.COMPLETED:
                typer.echo(f"⏭️  Skipping completed: {tool_data['name']}")
                continue
            elif existing_job.status == JobStatus.RUNNING:
                typer.echo(f"⏭️  Skipping running: {tool_data['name']}")
                continue
        
        job = AnalysisJob.create(tool_data)
        jobs.append((job, tool_data))
    
    typer.echo(f"🚀 Starting analysis of {len(jobs)} tools...")
    
    # Process jobs (TODO: implement concurrent processing)
    completed = 0
    failed = 0
    
    with typer.progressbar(jobs, label="Processing tools") as progress:
        for job, tool_data in progress:
            try:
                results = agent.analyze_tool(tool_data)
                
                if "error" in results:
                    job.update_status(JobStatus.ERROR, error_message=results["error"])
                    failed += 1
                else:
                    job.update_status(JobStatus.COMPLETED, results=results)
                    completed += 1
                    
                    # Save individual results if output directory specified
                    if output_dir:
                        output_dir.mkdir(exist_ok=True)
                        output_file = output_dir / f"{tool_data['name'].replace(' ', '_')}.json"
                        _save_results_to_file(results, output_file)
                
            except Exception as e:
                job.update_status(JobStatus.ERROR, error_message=str(e))
                failed += 1
    
    typer.echo(f"✅ Batch analysis completed!")
    typer.echo(f"   • Completed: {completed}")
    typer.echo(f"   • Failed: {failed}")
    typer.echo(f"   • Total: {len(jobs)}")

@app.command()
def export(
    format: OutputFormat = typer.Option(OutputFormat.json, "--format", "-f", help="Export format"),
    output_file: Path = typer.Option(..., "--output", "-o", help="Output file path"),
    status_filter: Optional[str] = typer.Option(None, "--status", help="Filter by status"),
    limit: Optional[int] = typer.Option(None, "--limit", help="Limit number of results")
):
    """Export analysis results."""
    
    jobs = AnalysisJob.get_all(status_filter, limit)
    
    if format == OutputFormat.json:
        _export_json(jobs, output_file)
    else:
        typer.echo(f"❌ Export format {format} not yet implemented")
        raise typer.Exit(1)
    
    typer.echo(f"📁 Exported {len(jobs)} results to: {output_file}")

@app.command()
def clean(
    days: int = typer.Option(30, "--days", "-d", help="Delete jobs older than N days"),
    status: Optional[str] = typer.Option(None, "--status", help="Only delete jobs with specific status"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be deleted without deleting"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt")
):
    """Clean up old analysis jobs."""
    
    count = AnalysisJob.count_old(days, status)
    
    if count == 0:
        typer.echo("✅ No jobs to clean")
        return
    
    typer.echo(f"🗑️  Found {count} jobs to delete (older than {days} days)")
    
    if dry_run:
        jobs = AnalysisJob.get_old(days, status, limit=10)
        typer.echo("Would delete:")
        for job in jobs:
            typer.echo(f"   • {job.job_id} - {job.tool_name} ({job.status})")
        return
    
    if not confirm:
        if not typer.confirm(f"Delete {count} jobs?"):
            typer.echo("❌ Cancelled")
            return
    
    deleted = AnalysisJob.delete_old(days, status)
    typer.echo(f"✅ Deleted {deleted} jobs")

@app.command()
def config(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    set_key: Optional[str] = typer.Option(None, "--set", help="Set configuration key"),
    value: Optional[str] = typer.Option(None, "--value", help="Configuration value"),
    test: bool = typer.Option(False, "--test", help="Test API connections")
):
    """Manage configuration."""
    
    config = Config()
    
    if show:
        _display_config(config)
    elif set_key and value:
        config.set(set_key, value)
        typer.echo(f"✅ Set {set_key} = {value}")
    elif test:
        _test_config(config)
    else:
        typer.echo("Use --show, --set, or --test")

def _display_job_details(job: AnalysisJob, format: OutputFormat):
    """Display detailed job information."""
    if format == OutputFormat.json:
        data = {
            "job_id": job.job_id,
            "tool_name": job.tool_name,
            "status": job.status.value,
            "created_at": job.created_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message,
            "results": job.results
        }
        typer.echo(json.dumps(data, indent=2))
    else:
        typer.echo(f"Job ID: {job.job_id}")
        typer.echo(f"Tool: {job.tool_name}")
        typer.echo(f"Status: {job.status.value}")
        typer.echo(f"Created: {job.created_at}")
        if job.completed_at:
            typer.echo(f"Completed: {job.completed_at}")
        if job.error_message:
            typer.echo(f"Error: {job.error_message}")

def _display_jobs_table(jobs: List[AnalysisJob], format: OutputFormat):
    """Display jobs in table format."""
    if not jobs:
        typer.echo("No jobs found")
        return
    
    if format == OutputFormat.json:
        data = []
        for job in jobs:
            data.append({
                "job_id": job.job_id,
                "tool_name": job.tool_name,
                "status": job.status.value,
                "created_at": job.created_at.isoformat(),
                "completed_at": job.completed_at.isoformat() if job.completed_at else None
            })
        typer.echo(json.dumps(data, indent=2))
    else:
        # Table format
        typer.echo(f"{'Job ID':<10} {'Tool Name':<25} {'Status':<12} {'Created':<20}")
        typer.echo("-" * 70)
        for job in jobs:
            status_emoji = {
                JobStatus.PENDING: "⏳",
                JobStatus.RUNNING: "🔄",
                JobStatus.COMPLETED: "✅",
                JobStatus.ERROR: "❌"
            }.get(job.status, "❓")
            
            typer.echo(f"{job.job_id[:8]:<10} {job.tool_name[:24]:<25} {status_emoji} {job.status.value:<10} {job.created_at.strftime('%Y-%m-%d %H:%M'):<20}")

def _display_analysis_summary(results: Dict):
    """Display a summary of analysis results."""
    typer.echo("\n📊 Analysis Summary:")
    
    metadata = results.get("analysis_metadata", {})
    typer.echo(f"   • Tools used: {len(metadata.get('tools_used', []))}")
    typer.echo(f"   • Confidence: {metadata.get('total_confidence', 0)}%")
    typer.echo(f"   • Completeness: {metadata.get('data_completeness', 0)}%")
    
    summary = results.get("overall_summary", {})
    if summary:
        typer.echo(f"   • Popularity: {summary.get('popularity_score', 0)}/100")
        typer.echo(f"   • Activity: {summary.get('activity_level', 'unknown')}")
        typer.echo(f"   • Pricing: {summary.get('pricing_model', 'unknown')}")
        typer.echo(f"   • Recommendation: {summary.get('recommendation_score', 0)}/100")

def _save_results_to_file(results: Dict, output_file: Path):
    """Save results to a file."""
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

def _export_json(jobs: List[AnalysisJob], output_file: Path):
    """Export jobs to JSON format."""
    data = []
    for job in jobs:
        data.append({
            "job_id": job.job_id,
            "tool_name": job.tool_name,
            "status": job.status.value,
            "created_at": job.created_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message,
            "tool_data": job.tool_data,
            "results": job.results
        })
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def _display_config(config: Config):
    """Display current configuration."""
    typer.echo("🔧 Configuration:")
    api_status = config.get_api_status()
    model_info = config.get_model_info()
    
    typer.echo(f"   • Model: {model_info}")
    typer.echo(f"   • APIs Available: {sum(api_status.values())}/{len(api_status)}")
    
    for api, available in api_status.items():
        status = "✅" if available else "❌"
        typer.echo(f"     {status} {api}")

def _test_config(config: Config):
    """Test API connections."""
    typer.echo("🔍 Testing API connections...")
    
    api_status = config.test_apis()
    for api, (status, message) in api_status.items():
        emoji = "✅" if status else "❌"
        typer.echo(f"   {emoji} {api}: {message}")

if __name__ == "__main__":
    app()