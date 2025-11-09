# Скрипт для синхронизации базы данных с Railway (PowerShell версия)
# Скачивает базу данных с хостинга и обновляет локальную копию.

$LOCAL_DB_PATH = Join-Path $PSScriptRoot "fitness_bot_remote.db"
$REMOTE_DB_PATH = "fitness_bot.db"  # Путь на Railway

Write-Host "🔄 Синхронизация базы данных с Railway..." -ForegroundColor Cyan

try {
    # Проверяем, установлен ли Railway CLI
    $railwayVersion = railway --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Railway CLI не установлен!" -ForegroundColor Red
        Write-Host "Установите его командой: npm i -g @railway/cli" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "✅ Railway CLI найден: $railwayVersion" -ForegroundColor Green
    
    # Проверяем, подключен ли проект
    $status = railway status 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Проект не подключен к Railway!" -ForegroundColor Red
        Write-Host "Выполните: railway link" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "✅ Проект подключен к Railway" -ForegroundColor Green
    
    # Скачиваем базу данных
    Write-Host "📥 Скачивание базы данных с Railway..." -ForegroundColor Cyan
    
    # Пробуем основной путь
    railway run cat $REMOTE_DB_PATH 2>&1 | Out-File -FilePath $LOCAL_DB_PATH -Encoding Byte
    
    if ($LASTEXITCODE -ne 0) {
        # Пробуем альтернативный путь
        Write-Host "Пробую альтернативный путь: data/fitness_bot.db" -ForegroundColor Yellow
        railway run cat "data/fitness_bot.db" 2>&1 | Out-File -FilePath $LOCAL_DB_PATH -Encoding Byte
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Ошибка при скачивании базы данных" -ForegroundColor Red
            exit 1
        }
    }
    
    if (Test-Path $LOCAL_DB_PATH) {
        $fileSize = (Get-Item $LOCAL_DB_PATH).Length
        Write-Host "✅ База данных успешно скачана!" -ForegroundColor Green
        Write-Host "   Размер: $([math]::Round($fileSize / 1KB, 2)) KB" -ForegroundColor Cyan
        Write-Host "   Путь: $LOCAL_DB_PATH" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "💡 Откройте файл в DBeaver:" -ForegroundColor Yellow
        Write-Host "   $LOCAL_DB_PATH" -ForegroundColor Cyan
        exit 0
    } else {
        Write-Host "❌ Файл базы данных не был создан" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "❌ Ошибка: $_" -ForegroundColor Red
    exit 1
}

