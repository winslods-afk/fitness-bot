@echo off
echo ========================================
echo Тестирование Fitness Bot API
echo ========================================
echo.

echo 1. Проверка доступности API...
curl http://localhost:8000/health
echo.
echo.

echo 2. Получение пользователей и программ...
curl -H "X-API-Key: dotainstructor" http://localhost:8000/api/users
echo.
echo.

echo ========================================
echo Тестирование завершено!
echo ========================================
pause

