"""
Скрипт для проверки подключения к PostgreSQL и миграции данных.
Использование:
    python check_postgres.py
Или с переменной окружения:
    DATABASE_URL=postgresql://... python check_postgres.py
"""
import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_postgres():
    """Проверка подключения к PostgreSQL и миграции."""
    # Получите DATABASE_URL из переменных окружения
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL не установлена")
        print("💡 Установите переменную окружения DATABASE_URL")
        print("💡 Или используйте: railway variables get DATABASE_URL")
        return False
    
    # Преобразуем postgres:// в postgresql+asyncpg://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgresql://"):
        if not database_url.startswith("postgresql+asyncpg://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Маскируем пароль для вывода
    safe_url = database_url.split("@")[0] if "@" in database_url else database_url
    print(f"🔌 Подключение к: {safe_url}@***")
    
    try:
        engine = create_async_engine(database_url, echo=False)
        
        async with engine.begin() as conn:
            # Проверяем версию PostgreSQL
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✅ PostgreSQL версия: {version.split(',')[0]}")
            
            # Проверяем таблицы
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            
            expected_tables = [
                'users', 'sessions', 'workout_days', 
                'exercises', 'sets', 'session_runs', 'performed_sets'
            ]
            
            print(f"\n📊 Найдено таблиц: {len(tables)}")
            found_tables = [table[0] for table in tables]
            
            for table in expected_tables:
                if table in found_tables:
                    print(f"  ✅ {table}")
                else:
                    print(f"  ❌ {table} - не найдена")
            
            # Проверяем данные в таблицах
            print("\n📈 Данные в таблицах:")
            for table in expected_tables:
                if table in found_tables:
                    try:
                        result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.scalar()
                        print(f"  - {table}: {count} записей")
                    except Exception as e:
                        print(f"  - {table}: ошибка при чтении - {e}")
            
            # Проверяем пользователей
            if 'users' in found_tables:
                result = await conn.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result.scalar()
                if user_count > 0:
                    result = await conn.execute(text("""
                        SELECT telegram_id, created_at 
                        FROM users 
                        ORDER BY created_at DESC 
                        LIMIT 5
                    """))
                    users = result.fetchall()
                    print(f"\n👥 Последние пользователи ({user_count} всего):")
                    for user in users:
                        print(f"  - Telegram ID: {user[0]}, создан: {user[1]}")
            
            # Проверяем программы
            if 'sessions' in found_tables:
                result = await conn.execute(text("SELECT COUNT(*) FROM sessions"))
                session_count = result.scalar()
                if session_count > 0:
                    result = await conn.execute(text("""
                        SELECT s.session_id, s.name, s.created_at, u.telegram_id
                        FROM sessions s
                        JOIN users u ON s.user_id = u.id
                        ORDER BY s.created_at DESC 
                        LIMIT 5
                    """))
                    sessions = result.fetchall()
                    print(f"\n💪 Последние программы ({session_count} всего):")
                    for session in sessions:
                        print(f"  - ID: {session[0]}, название: {session[1]}, пользователь: {session[3]}, создана: {session[2]}")
        
        await engine.dispose()
        print("\n✅ Подключение к PostgreSQL работает!")
        print("✅ Миграция на PostgreSQL выполнена успешно!")
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка подключения: {e}")
        print("💡 Проверьте:")
        print("  1. PostgreSQL сервис запущен в Railway")
        print("  2. Переменная DATABASE_URL установлена правильно")
        print("  3. asyncpg установлен: pip install asyncpg")
        return False

if __name__ == "__main__":
    print("🔍 Проверка подключения к PostgreSQL...")
    print("=" * 60)
    success = asyncio.run(check_postgres())
    print("=" * 60)
    sys.exit(0 if success else 1)

