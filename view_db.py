"""Скрипт для просмотра базы данных."""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.models import User, Session, WorkoutDay, Exercise, Set, SessionRun, PerformedSet
from app.config import DATABASE_URL

# Создаём async engine
engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def view_database():
    """Просмотр содержимого базы данных."""
    async with async_session_maker() as session:
        print("=" * 60)
        print("ПРОСМОТР БАЗЫ ДАННЫХ FITNESS BOT")
        print("=" * 60)
        print()
        
        # Пользователи
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"👥 ПОЛЬЗОВАТЕЛИ ({len(users)}):")
        for user in users:
            print(f"  ID: {user.id}, Telegram ID: {user.telegram_id}, Создан: {user.created_at}")
        print()
        
        # Программы
        result = await session.execute(select(Session))
        sessions = result.scalars().all()
        print(f"📋 ПРОГРАММЫ ({len(sessions)}):")
        for session_obj in sessions:
            print(f"  ID: {session_obj.session_id}, Название: {session_obj.name}")
            print(f"    Пользователь ID: {session_obj.user_id}, Создана: {session_obj.created_at}")
            
            # Дни программы
            result_days = await session.execute(
                select(WorkoutDay)
                .where(WorkoutDay.session_id == session_obj.session_id)
                .order_by(WorkoutDay.day_index)
                .options(selectinload(WorkoutDay.exercises).selectinload(Exercise.sets))
            )
            days = result_days.scalars().all()
            for day in days:
                print(f"    📅 День {day.day_index + 1}: {day.name}")
                
                # Упражнения дня
                for exercise in day.exercises:
                    sets_info = []
                    for set_obj in sorted(exercise.sets, key=lambda x: x.set_index):
                        sets_info.append(f"{set_obj.reps} раз")
                    sets_str = "-".join(sets_info)
                    print(f"      💪 {exercise.name} ({sets_str})")
        print()
        
        # Запуски тренировок
        result = await session.execute(
            select(SessionRun)
            .options(selectinload(SessionRun.session))
            .order_by(SessionRun.started_at.desc())
            .limit(10)
        )
        runs = result.scalars().all()
        print(f"🏋️ ПОСЛЕДНИЕ ТРЕНИРОВКИ ({len(runs)}):")
        for run in runs:
            program_name = run.session.name if run.session else "Неизвестно"
            print(f"  ID: {run.id}, Программа: {program_name}")
            print(f"    Пользователь ID: {run.user_id}, Начало: {run.started_at}")
            
            # Выполненные подходы
            result_sets = await session.execute(
                select(PerformedSet)
                .where(PerformedSet.session_run_id == run.id)
                .options(selectinload(PerformedSet.exercise))
                .order_by(PerformedSet.exercise_id, PerformedSet.set_index)
            )
            performed_sets = result_sets.scalars().all()
            if performed_sets:
                current_exercise = None
                for ps in performed_sets:
                    if current_exercise != ps.exercise:
                        current_exercise = ps.exercise
                        print(f"      💪 {ps.exercise.name}:")
                    print(f"        Подход {ps.set_index}: {ps.weight} кг")
            print()
        
        # Статистика
        print("=" * 60)
        print("СТАТИСТИКА:")
        print("=" * 60)
        
        result = await session.execute(select(func.count(User.id)))
        user_count = result.scalar()
        print(f"Всего пользователей: {user_count}")
        
        result = await session.execute(select(func.count(Session.session_id)))
        session_count = result.scalar()
        print(f"Всего программ: {session_count}")
        
        result = await session.execute(select(func.count(SessionRun.id)))
        run_count = result.scalar()
        print(f"Всего тренировок: {run_count}")
        
        result = await session.execute(select(func.count(PerformedSet.id)))
        set_count = result.scalar()
        print(f"Всего выполненных подходов: {set_count}")
        print()


if __name__ == "__main__":
    try:
        asyncio.run(view_database())
    except KeyboardInterrupt:
        print("\nПрервано пользователем")
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        asyncio.run(engine.dispose())

