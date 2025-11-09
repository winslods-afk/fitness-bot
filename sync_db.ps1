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

# Get list of services
Write-Host "Getting list of services..." -ForegroundColor Cyan
$servicesOutput = railway service 2>&1
Write-Host "Services: $servicesOutput" -ForegroundColor Gray

# Download database
Write-Host "Downloading database from Railway..." -ForegroundColor Cyan

try {
    # Try different possible paths
    $possiblePaths = @(
        "fitness_bot.db",
        "data/fitness_bot.db",
        "/app/fitness_bot.db",
        "/app/data/fitness_bot.db",
        "app/fitness_bot.db"
    )
    
    $success = $false
    foreach ($path in $possiblePaths) {
        Write-Host "Trying: $path" -ForegroundColor Yellow
        
        # Try without service specification first
        railway run cat $path *> $LOCAL_DB_PATH 2>&1
        
        # If that fails, try with service name (if we can detect it)
        if ($LASTEXITCODE -ne 0) {
            # Try to get service name from railway service output
            if ($servicesOutput -match "(\S+)") {
                $serviceName = $matches[1]
                Write-Host "Trying with service: $serviceName" -ForegroundColor Gray
                railway run --service $serviceName cat $path *> $LOCAL_DB_PATH 2>&1
            }
        }
        
        if ($LASTEXITCODE -eq 0 -and (Test-Path $LOCAL_DB_PATH)) {
            $fileSize = (Get-Item $LOCAL_DB_PATH).Length
            if ($fileSize -gt 0) {
                Write-Host "Success! Database found at: $path" -ForegroundColor Green
                Write-Host "File size: $fileSize bytes" -ForegroundColor Green
                $success = $true
                break
            } else {
                if (Test-Path $LOCAL_DB_PATH) {
                    Remove-Item $LOCAL_DB_PATH -Force
                }
            }
        } else {
            if (Test-Path $LOCAL_DB_PATH) {
                Remove-Item $LOCAL_DB_PATH -Force
            }
        }
    }
    
    if (-not $success) {
        Write-Host ""
        Write-Host "Troubleshooting:" -ForegroundColor Yellow
        Write-Host "1. Check if database exists: railway run ls -la" -ForegroundColor Cyan
        Write-Host "2. List services: railway service" -ForegroundColor Cyan
        Write-Host "3. Try manual download: railway run cat /app/data/fitness_bot.db > fitness_bot_remote.db" -ForegroundColor Cyan
        throw "Failed to download database. Check the paths above."
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
