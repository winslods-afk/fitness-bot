@echo off
echo ========================================
echo Запуск Fitness Bot API
echo ========================================
echo.

REM Проверка установки зависимостей
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo [ОШИБКА] FastAPI не установлен!
    echo.
    echo Установка зависимостей...
    pip install -r requirements.txt
    echo.
)

echo Запуск API сервера...
echo API будет доступен на: http://localhost:8000
echo.
echo Для остановки нажмите Ctrl+C
echo.

python api_server.py

pause

