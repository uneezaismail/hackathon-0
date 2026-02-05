# PowerShell script to initialize social media sessions on Windows
# This script works around WSL GUI limitations by running directly on Windows

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("twitter", "facebook", "instagram", "all")]
    [string]$Platform
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Social Media Session Initialization (Windows)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Get the project directory (assuming script is in scripts/setup/)
$ProjectDir = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectDir

Write-Host "Project directory: $ProjectDir" -ForegroundColor Yellow
Write-Host ""

function Initialize-TwitterSession {
    Write-Host "Initializing Twitter Session..." -ForegroundColor Green
    Write-Host ""

    # Run the Python script with uv
    & uv run python scripts/setup/initialize_social_sessions.py twitter
}

function Initialize-FacebookSession {
    Write-Host "Initializing Facebook Session..." -ForegroundColor Green
    Write-Host ""

    # Run the Python script with uv
    & uv run python scripts/setup/initialize_social_sessions.py facebook
}

function Initialize-InstagramSession {
    Write-Host "Initializing Instagram Session..." -ForegroundColor Green
    Write-Host ""

    # Run the Python script with uv
    & uv run python scripts/setup/initialize_social_sessions.py instagram
}

# Execute based on platform
switch ($Platform) {
    "twitter" {
        Initialize-TwitterSession
    }
    "facebook" {
        Initialize-FacebookSession
    }
    "instagram" {
        Initialize-InstagramSession
    }
    "all" {
        Initialize-TwitterSession
        Initialize-FacebookSession
        Initialize-InstagramSession
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Session initialization complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Verify session directories exist in project:" -ForegroundColor White
Write-Host "   - .twitter_session/" -ForegroundColor Gray
Write-Host "   - .facebook_session/" -ForegroundColor Gray
Write-Host "   - .instagram_session/" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Test MCP health checks from WSL:" -ForegroundColor White
Write-Host "   uv run mcp dev mcp_servers/twitter_web_mcp.py" -ForegroundColor Gray
Write-Host ""
