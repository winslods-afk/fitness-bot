# Database sync script for Railway (PowerShell version)
# Downloads database from Railway and updates local copy

$LOCAL_DB_PATH = Join-Path $PSScriptRoot "fitness_bot_remote.db"
$REMOTE_DB_PATH = "fitness_bot.db"

Write-Host "Syncing database with Railway..." -ForegroundColor Cyan

# Check if Railway CLI is installed
$railwayVersion = railway --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Railway CLI is not installed!" -ForegroundColor Red
    Write-Host "Install it with: npm i -g @railway/cli" -ForegroundColor Yellow
    exit 1
}

Write-Host "OK: Railway CLI found: $railwayVersion" -ForegroundColor Green

# Check if project is linked
$status = railway status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Project is not linked to Railway!" -ForegroundColor Red
    Write-Host "Run: railway link" -ForegroundColor Yellow
    exit 1
}

Write-Host "OK: Project is linked to Railway" -ForegroundColor Green

# Download database
Write-Host "Downloading database from Railway..." -ForegroundColor Cyan

try {
    # Try main path
    $dbContent = railway run cat $REMOTE_DB_PATH 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        # Try alternative path
        Write-Host "Trying alternative path: data/fitness_bot.db" -ForegroundColor Yellow
        $dbContent = railway run cat "data/fitness_bot.db" 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to download database"
        }
    }
    
    # Save binary data
    if ($PSVersionTable.PSVersion.Major -ge 6) {
        # PowerShell Core - use -AsByteStream
        $dbContent | Set-Content -Path $LOCAL_DB_PATH -AsByteStream -NoNewline
    } else {
        # PowerShell 5.x - use .NET method
        [System.IO.File]::WriteAllBytes($LOCAL_DB_PATH, $dbContent)
    }
    
    if (Test-Path $LOCAL_DB_PATH) {
        $fileSize = (Get-Item $LOCAL_DB_PATH).Length
        Write-Host "OK: Database downloaded successfully!" -ForegroundColor Green
        Write-Host "   Size: $([math]::Round($fileSize / 1KB, 2)) KB" -ForegroundColor Cyan
        Write-Host "   Path: $LOCAL_DB_PATH" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Open the file in DBeaver:" -ForegroundColor Yellow
        Write-Host "   $LOCAL_DB_PATH" -ForegroundColor Cyan
    } else {
        throw "Database file was not created"
    }
}
catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
    exit 1
}
