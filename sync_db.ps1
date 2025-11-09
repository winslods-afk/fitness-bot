# Скрипт для синхронизации базы данных с Railway (PowerShell версия)
# Скачивает базу данных с хостинга и обновляет локальную копию.

$LOCAL_DB_PATH = Join-Path $PSScriptRoot "fitness_bot_remote.db"
$REMOTE_DB_PATH = "fitness_bot.db"  # Путь на Railway

Write-Host "Синхронизация базы данных с Railway..." -ForegroundColor Cyan

# Проверяем, установлен ли Railway CLI
$railwayVersion = railway --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ОШИБКА: Railway CLI не установлен!" -ForegroundColor Red
    Write-Host "Установите его командой: npm i -g @railway/cli" -ForegroundColor Yellow
    exit 1
}

Write-Host "OK: Railway CLI найден: $railwayVersion" -ForegroundColor Green

# Проверяем, подключен ли проект
$status = railway status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ОШИБКА: Проект не подключен к Railway!" -ForegroundColor Red
    Write-Host "Выполните: railway link" -ForegroundColor Yellow
    exit 1
}

Write-Host "OK: Проект подключен к Railway" -ForegroundColor Green

# Скачиваем базу данных
Write-Host "Скачивание базы данных с Railway..." -ForegroundColor Cyan

try {
    # Пробуем основной путь
    railway run cat $REMOTE_DB_PATH 2>&1 | Out-File -FilePath $LOCAL_DB_PATH -Encoding Byte
    
    if ($LASTEXITCODE -ne 0) {
        # Пробуем альтернативный путь
        Write-Host "Пробую альтернативный путь: data/fitness_bot.db" -ForegroundColor Yellow
        railway run cat "data/fitness_bot.db" 2>&1 | Out-File -FilePath $LOCAL_DB_PATH -Encoding Byte
        
        if ($LASTEXITCODE -ne 0) {
            throw "Не удалось скачать базу данных"
        }
    }
    
    if (Test-Path $LOCAL_DB_PATH) {
        $fileSize = (Get-Item $LOCAL_DB_PATH).Length
        Write-Host "OK: База данных успешно скачана!" -ForegroundColor Green
        Write-Host "   Размер: $([math]::Round($fileSize / 1KB, 2)) KB" -ForegroundColor Cyan
        Write-Host "   Путь: $LOCAL_DB_PATH" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Откройте файл в DBeaver:" -ForegroundColor Yellow
        Write-Host "   $LOCAL_DB_PATH" -ForegroundColor Cyan
    } else {
        throw "Файл базы данных не был создан"
    }
}
catch {
    Write-Host "ОШИБКА: $_" -ForegroundColor Red
    exit 1
}
