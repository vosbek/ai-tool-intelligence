#Requires -Version 5.1
<#
.SYNOPSIS
    Manage research operations for the AI Tool Intelligence Platform
.DESCRIPTION
    Provides research queue management, tool processing, and batch operations
.EXAMPLE
    .\Research.ps1 -Status
    Shows research queue status
.EXAMPLE
    .\Research.ps1 -Process "Cursor,GitHub Copilot"
    Processes specific tools
.EXAMPLE
    .\Research.ps1 -Category "Agentic IDEs"
    Processes all tools in a category
#>

[CmdletBinding()]
param(
    [switch]$Status,
    [switch]$Failed,
    [switch]$Retry,
    [string]$Process,
    [string]$Category,
    [switch]$Scheduler,
    [switch]$List,
    [int]$MaxConcurrent = 3
)

# Colors for output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Step { param($Message) Write-Host "🔄 $Message" -ForegroundColor Blue }

# Get script directory and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Host "🔬 AI Tool Intelligence Research Manager" -ForegroundColor White

# Check if backend is running
function Test-BackendConnection {
    try {
        $Response = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -TimeoutSec 5
        return $Response.status -eq "healthy"
    } catch {
        return $false
    }
}

if (-not (Test-BackendConnection)) {
    Write-Error "Backend service is not running"
    Write-Info "Start the backend with: .\Start.ps1 -BackendOnly"
    exit 1
}

# Function to make API calls to backend
function Invoke-BackendAPI {
    param($Endpoint, $Method = "GET", $Body = $null)
    
    try {
        $Uri = "http://localhost:5000/api/$Endpoint"
        $Headers = @{ "Content-Type" = "application/json" }
        
        if ($Body) {
            $JsonBody = $Body | ConvertTo-Json -Depth 5
            $Response = Invoke-RestMethod -Uri $Uri -Method $Method -Body $JsonBody -Headers $Headers
        } else {
            $Response = Invoke-RestMethod -Uri $Uri -Method $Method -Headers $Headers
        }
        
        return $Response
    } catch {
        Write-Error "API call failed: $_"
        return $null
    }
}

# Show research status
if ($Status -or (-not $Failed -and -not $Retry -and -not $Process -and -not $Category -and -not $Scheduler -and -not $List)) {
    Write-Step "Fetching research status..."
    
    $Tools = Invoke-BackendAPI -Endpoint "tools?per_page=100"
    if ($Tools) {
        $TotalTools = $Tools.total
        $StatusCounts = $Tools.tools | Group-Object processing_status
        
        Write-Host "`n📊 Research Queue Status" -ForegroundColor Blue
        Write-Host ("=" * 40) -ForegroundColor Gray
        Write-Host "Total Tools: $TotalTools" -ForegroundColor White
        
        foreach ($Status in $StatusCounts) {
            $StatusIcon = switch ($Status.Name) {
                "completed" { "✅" }
                "processing" { "🔄" }
                "error" { "❌" }
                "never_run" { "⏳" }
                default { "❓" }
            }
            
            $StatusColor = switch ($Status.Name) {
                "completed" { "Green" }
                "processing" { "Yellow" }
                "error" { "Red" }
                "never_run" { "Gray" }
                default { "White" }
            }
            
            Write-Host "$StatusIcon $($Status.Name): $($Status.Count)" -ForegroundColor $StatusColor
        }
        
        # Show recently processed tools
        $RecentTools = $Tools.tools | Where-Object { $_.last_processed_at } | 
                       Sort-Object last_processed_at -Descending | Select-Object -First 5
        
        if ($RecentTools) {
            Write-Host "`n🕒 Recently Processed Tools" -ForegroundColor Blue
            Write-Host ("=" * 40) -ForegroundColor Gray
            foreach ($Tool in $RecentTools) {
                $ProcessedDate = [DateTime]::Parse($Tool.last_processed_at).ToString("yyyy-MM-dd HH:mm")
                $StatusIcon = if ($Tool.processing_status -eq "completed") { "✅" } else { "❌" }
                Write-Host "$StatusIcon $($Tool.name) - $ProcessedDate" -ForegroundColor Gray
            }
        }
        
        # Show tools that need processing
        $NeverRun = $Tools.tools | Where-Object { $_.processing_status -eq "never_run" }
        $Failed = $Tools.tools | Where-Object { $_.processing_status -eq "error" }
        
        if ($NeverRun -or $Failed) {
            Write-Host "`n⏳ Tools Pending Research" -ForegroundColor Blue
            Write-Host ("=" * 40) -ForegroundColor Gray
            
            if ($NeverRun) {
                Write-Host "Never processed: $($NeverRun.Count)" -ForegroundColor Yellow
                foreach ($Tool in ($NeverRun | Select-Object -First 3)) {
                    Write-Host "  • $($Tool.name)" -ForegroundColor Gray
                }
                if ($NeverRun.Count -gt 3) {
                    Write-Host "  ... and $($NeverRun.Count - 3) more" -ForegroundColor Gray
                }
            }
            
            if ($Failed) {
                Write-Host "Failed processing: $($Failed.Count)" -ForegroundColor Red
                foreach ($Tool in ($Failed | Select-Object -First 3)) {
                    Write-Host "  • $($Tool.name)" -ForegroundColor Gray
                }
                if ($Failed.Count -gt 3) {
                    Write-Host "  ... and $($Failed.Count - 3) more" -ForegroundColor Gray
                }
            }
        }
    }
}

# List all tools
if ($List) {
    Write-Step "Fetching all tools..."
    
    $Tools = Invoke-BackendAPI -Endpoint "tools?per_page=200"
    if ($Tools) {
        Write-Host "`n📋 All Tools" -ForegroundColor Blue
        Write-Host ("=" * 60) -ForegroundColor Gray
        
        foreach ($Tool in $Tools.tools) {
            $StatusIcon = switch ($Tool.processing_status) {
                "completed" { "✅" }
                "processing" { "🔄" }
                "error" { "❌" }
                "never_run" { "⏳" }
                default { "❓" }
            }
            
            $LastProcessed = if ($Tool.last_processed_at) { 
                [DateTime]::Parse($Tool.last_processed_at).ToString("MM/dd") 
            } else { 
                "Never" 
            }
            
            Write-Host "$StatusIcon $($Tool.name.PadRight(25)) | $($Tool.processing_status.PadRight(12)) | $LastProcessed" -ForegroundColor White
        }
    }
}

# Show failed tools
if ($Failed) {
    Write-Step "Fetching failed tools..."
    
    $Tools = Invoke-BackendAPI -Endpoint "tools?status=error&per_page=100"
    if ($Tools -and $Tools.tools) {
        Write-Host "`n❌ Failed Tools" -ForegroundColor Red
        Write-Host ("=" * 40) -ForegroundColor Gray
        
        foreach ($Tool in $Tools.tools) {
            Write-Host "• $($Tool.name)" -ForegroundColor Red
            if ($Tool.last_processed_at) {
                $FailedDate = [DateTime]::Parse($Tool.last_processed_at).ToString("yyyy-MM-dd HH:mm")
                Write-Host "  Last attempt: $FailedDate" -ForegroundColor Gray
            }
        }
        
        Write-Host "`nTo retry all failed tools: .\Research.ps1 -Retry" -ForegroundColor Yellow
    } else {
        Write-Success "No failed tools found"
    }
}

# Retry failed tools
if ($Retry) {
    Write-Step "Retrying failed tools..."
    
    $FailedTools = Invoke-BackendAPI -Endpoint "tools?status=error&per_page=100"
    if ($FailedTools -and $FailedTools.tools) {
        Write-Info "Found $($FailedTools.tools.Count) failed tools to retry"
        
        foreach ($Tool in $FailedTools.tools) {
            Write-Info "Retrying research for: $($Tool.name)"
            
            $Response = Invoke-BackendAPI -Endpoint "tools/$($Tool.id)/research" -Method "POST"
            if ($Response) {
                if ($Response.status -eq "completed") {
                    Write-Success "✅ $($Tool.name) - Research completed"
                } elseif ($Response.status -eq "failed") {
                    Write-Error "❌ $($Tool.name) - Research failed again"
                } else {
                    Write-Info "🔄 $($Tool.name) - Research started"
                }
            }
            
            # Small delay between requests
            Start-Sleep 2
        }
    } else {
        Write-Success "No failed tools to retry"
    }
}

# Process specific tools
if ($Process) {
    $ToolNames = $Process -split ',' | ForEach-Object { $_.Trim() }
    Write-Step "Processing tools: $($ToolNames -join ', ')"
    
    foreach ($ToolName in $ToolNames) {
        # Find the tool
        $Tools = Invoke-BackendAPI -Endpoint "tools?per_page=200"
        $Tool = $Tools.tools | Where-Object { $_.name -eq $ToolName }
        
        if ($Tool) {
            Write-Info "Starting research for: $ToolName"
            
            $Response = Invoke-BackendAPI -Endpoint "tools/$($Tool.id)/research" -Method "POST"
            if ($Response) {
                Write-Success "Research queued for $ToolName"
                
                # Monitor progress
                $MaxWait = 300  # 5 minutes
                $Waited = 0
                
                do {
                    Start-Sleep 10
                    $Waited += 10
                    
                    $Updated = Invoke-BackendAPI -Endpoint "tools/$($Tool.id)"
                    if ($Updated) {
                        if ($Updated.processing_status -eq "completed") {
                            Write-Success "✅ $ToolName - Research completed"
                            break
                        } elseif ($Updated.processing_status -eq "error") {
                            Write-Error "❌ $ToolName - Research failed"
                            break
                        } else {
                            Write-Info "🔄 $ToolName - Still processing... ($Waited/$MaxWait seconds)"
                        }
                    }
                } while ($Waited -lt $MaxWait)
                
                if ($Waited -ge $MaxWait) {
                    Write-Warning "⏰ $ToolName - Research timed out after $MaxWait seconds"
                }
            }
        } else {
            Write-Error "Tool not found: $ToolName"
            
            # Show available tools for reference
            Write-Info "Available tools:"
            $Tools.tools | Select-Object -First 10 | ForEach-Object {
                Write-Host "  • $($_.name)" -ForegroundColor Gray
            }
        }
    }
}

# Process tools by category
if ($Category) {
    Write-Step "Processing tools in category: $Category"
    
    # Get categories first
    $Categories = Invoke-BackendAPI -Endpoint "categories"
    $TargetCategory = $Categories | Where-Object { $_.name -eq $Category }
    
    if ($TargetCategory) {
        $Tools = Invoke-BackendAPI -Endpoint "tools?category_id=$($TargetCategory.id)&per_page=100"
        
        if ($Tools -and $Tools.tools) {
            Write-Info "Found $($Tools.tools.Count) tools in category '$Category'"
            
            $ProcessedCount = 0
            foreach ($Tool in $Tools.tools) {
                if ($Tool.processing_status -ne "processing") {
                    Write-Info "Processing: $($Tool.name)"
                    
                    $Response = Invoke-BackendAPI -Endpoint "tools/$($Tool.id)/research" -Method "POST"
                    if ($Response) {
                        Write-Success "Research started for $($Tool.name)"
                        $ProcessedCount++
                        
                        # Respect rate limiting
                        Start-Sleep 5
                    }
                } else {
                    Write-Info "Skipping $($Tool.name) - already processing"
                }
            }
            
            Write-Success "Queued research for $ProcessedCount tools in category '$Category'"
        } else {
            Write-Warning "No tools found in category '$Category'"
        }
    } else {
        Write-Error "Category not found: $Category"
        
        # Show available categories
        Write-Info "Available categories:"
        $Categories | ForEach-Object {
            Write-Host "  • $($_.name)" -ForegroundColor Gray
        }
    }
}

# Start automated scheduler
if ($Scheduler) {
    Write-Step "Starting automated research scheduler..."
    Write-Warning "This will run continuously until stopped with Ctrl+C"
    
    $SchedulerRunning = $true
    
    # Cleanup on exit
    Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action { 
        Write-Host "`nScheduler stopped" -ForegroundColor Yellow
    }
    
    try {
        while ($SchedulerRunning) {
            Write-Info "Scheduler cycle started - $(Get-Date -Format 'HH:mm:ss')"
            
            # Get tools that need processing
            $Tools = Invoke-BackendAPI -Endpoint "tools?per_page=200"
            if ($Tools) {
                $NeedProcessing = $Tools.tools | Where-Object { 
                    $_.processing_status -eq "never_run" -or 
                    ($_.processing_status -eq "error" -and $_.last_processed_at) 
                }
                
                if ($NeedProcessing) {
                    Write-Info "Found $($NeedProcessing.Count) tools needing research"
                    
                    # Process up to MaxConcurrent tools
                    $ToProcess = $NeedProcessing | Select-Object -First $MaxConcurrent
                    
                    foreach ($Tool in $ToProcess) {
                        Write-Info "Auto-processing: $($Tool.name)"
                        $Response = Invoke-BackendAPI -Endpoint "tools/$($Tool.id)/research" -Method "POST"
                        if ($Response) {
                            Write-Success "Queued: $($Tool.name)"
                        }
                        Start-Sleep 3
                    }
                } else {
                    Write-Info "No tools need processing at this time"
                }
            }
            
            # Wait 10 minutes before next cycle
            Write-Info "Waiting 10 minutes until next scheduler cycle..."
            Start-Sleep 600
        }
    } catch {
        Write-Warning "Scheduler interrupted: $_"
    }
}

# Show help if no parameters
if (-not $Status -and -not $Failed -and -not $Retry -and -not $Process -and -not $Category -and -not $Scheduler -and -not $List) {
    Write-Host @"

🔬 Research Manager Commands:

Basic Operations:
  .\Research.ps1 -Status              # Show research queue status
  .\Research.ps1 -List                # List all tools and their status
  .\Research.ps1 -Failed              # Show failed tools
  .\Research.ps1 -Retry               # Retry all failed tools

Process Tools:
  .\Research.ps1 -Process "Tool1,Tool2"     # Process specific tools
  .\Research.ps1 -Category "Category Name"  # Process all tools in category

Automation:
  .\Research.ps1 -Scheduler           # Start automated scheduler

Examples:
  .\Research.ps1 -Process "Cursor,GitHub Copilot"
  .\Research.ps1 -Category "Agentic IDEs"
  .\Research.ps1 -Status

Notes:
  • Backend must be running for research operations
  • Research requires AWS credentials configured in backend\.env
  • Each tool research takes 2-5 minutes depending on complexity
  • Use Ctrl+C to stop the scheduler

"@ -ForegroundColor White
}
