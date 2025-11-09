"""
Скрипт для синхронизации базы данных с Railway.
Скачивает базу данных с хостинга и обновляет локальную копию.
"""
import subprocess
import os
import sys
from pathlib import Path

# Путь к локальной копии базы данных
LOCAL_DB_PATH = Path(__file__).parent / "fitness_bot_remote.db"
REMOTE_DB_PATH = "fitness_bot.db"  # Путь на Railway


def sync_database():
    """Синхронизирует базу данных с Railway."""
    print("🔄 Синхронизация базы данных с Railway...")
    
    try:
        # Проверяем, установлен ли Railway CLI
        result = subprocess.run(
            ["railway", "--version"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ Railway CLI не установлен!")
            print("Установите его командой: npm i -g @railway/cli")
            return False
        
        # Проверяем, подключен ли проект
        result = subprocess.run(
            ["railway", "status"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ Проект не подключен к Railway!")
            print("Выполните: railway link")
            return False
        
        # Скачиваем базу данных
        print(f"📥 Скачивание базы данных с Railway...")
        
        with open(LOCAL_DB_PATH, "wb") as f:
            result = subprocess.run(
                ["railway", "run", "cat", REMOTE_DB_PATH],
                stdout=f,
                stderr=subprocess.PIPE
            )
        
        if result.returncode != 0:
            print(f"❌ Ошибка при скачивании: {result.stderr.decode()}")
            # Пробуем альтернативный путь
            print("Пробую альтернативный путь: data/fitness_bot.db")
            with open(LOCAL_DB_PATH, "wb") as f:
                result = subprocess.run(
                    ["railway", "run", "cat", "data/fitness_bot.db"],
                    stdout=f,
                    stderr=subprocess.PIPE
                )
            
            if result.returncode != 0:
                print(f"❌ Ошибка: {result.stderr.decode()}")
                return False
        
        file_size = LOCAL_DB_PATH.stat().st_size
        print(f"✅ База данных успешно скачана!")
        print(f"   Размер: {file_size / 1024:.2f} KB")
        print(f"   Путь: {LOCAL_DB_PATH.absolute()}")
        print(f"\n💡 Откройте файл в DBeaver:")
        print(f"   {LOCAL_DB_PATH.absolute()}")
        
        return True
        
    except FileNotFoundError:
        print("❌ Railway CLI не найден!")
        print("Установите его командой: npm i -g @railway/cli")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False


if __name__ == "__main__":
    success = sync_database()
    sys.exit(0 if success else 1)

