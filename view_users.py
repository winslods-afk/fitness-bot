"""Скрипт для просмотра всех пользователей бота."""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, func

from app.db.models import User, Session, SessionRun
from app.config import DATABASE_URL

# Создаём async engine
engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def view_users():
    """Просмотр всех пользователей с их статистикой."""
    async with async_session_maker() as session:
        print("=" * 60)
        print("👥 ВСЕ ПОЛЬЗОВАТЕЛИ БОТА")
        print("=" * 60)
        print()
        
        # Получаем всех пользователей
        result = await session.execute(select(User).order_by(User.created_at))
        users = result.scalars().all()
        
        if not users:
            print("❌ Пользователей пока нет")
            return
        
        print(f"Всего пользователей: {len(users)}\n")
        
        for i, user in enumerate(users, 1):
            print(f"{i}. Telegram ID: {user.telegram_id}")
            print(f"   ID в БД: {user.id}")
            print(f"   Дата регистрации: {user.created_at}")
            
            # Подсчитываем программы пользователя
            result_sessions = await session.execute(
                select(func.count(Session.session_id))
                .where(Session.user_id == user.id)
            )
            programs_count = result_sessions.scalar() or 0
            
            # Подсчитываем тренировки пользователя
            result_runs = await session.execute(
                select(func.count(SessionRun.id))
                .where(SessionRun.user_id == user.id)
            )
            workouts_count = result_runs.scalar() or 0
            
            print(f"   📋 Программ: {programs_count}")
            print(f"   🏋️ Тренировок: {workouts_count}")
            print()
        
        print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(view_users())
    except KeyboardInterrupt:
        print("\nПрервано пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        asyncio.run(engine.dispose())

