# sync_db_loop.ps1
# Синхронизирует базу данных каждые 60 секунд

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$dbScript = Join-Path $scriptPath "sync_db.py"

Write-Host "🔄 Запуск автоматической синхронизации БД..." -ForegroundColor Cyan
Write-Host "Нажмите Ctrl+C для остановки" -ForegroundColor Yellow
Write-Host ""

$updateCount = 0

while ($true) {
    $updateCount++
    $timestamp = Get-Date -Format 'HH:mm:ss'
    
    Write-Host "[$timestamp] Синхронизация #$updateCount..." -ForegroundColor Cyan
    
    $result = python $dbScript 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Успешно обновлено" -ForegroundColor Green
    } else {
        Write-Host "❌ Ошибка при обновлении" -ForegroundColor Red
        Write-Host $result
    }
    
    Write-Host "⏳ Ожидание 60 секунд до следующего обновления..." -ForegroundColor Gray
    Write-Host ""
    
    Start-Sleep -Seconds 60
}

