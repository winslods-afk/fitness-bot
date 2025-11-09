"""CRUD операции для работы с базой данных."""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from app.db.models import (
    User, Session, WorkoutDay, Exercise, Set, SessionRun, PerformedSet
)


# ========== User ==========
async def get_or_create_user(session: AsyncSession, telegram_id: int) -> User:
    """Получить или создать пользователя."""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        user = User(telegram_id=telegram_id)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


# ========== Session (Program) ==========
async def get_user_sessions(session: AsyncSession, user_id: int) -> List[Session]:
    """Получить все программы пользователя."""
    result = await session.execute(
        select(Session).where(Session.user_id == user_id).order_by(Session.created_at)
    )
    return list(result.scalars().all())


async def get_session_by_id(session: AsyncSession, session_id: int) -> Optional[Session]:
    """Получить программу по ID."""
    result = await session.execute(
        select(Session).where(Session.session_id == session_id)
    )
    return result.scalar_one_or_none()


async def create_session(session: AsyncSession, user_id: int, name: str) -> Session:
    """Создать новую программу."""
    new_session = Session(user_id=user_id, name=name)
    session.add(new_session)
    await session.commit()
    await session.refresh(new_session)
    return new_session


async def delete_session(session: AsyncSession, session_id: int) -> bool:
    """Удалить программу и все связанные данные."""
    result = await session.execute(
        select(Session).where(Session.session_id == session_id)
    )
    session_obj = result.scalar_one_or_none()
    if session_obj:
        await session.delete(session_obj)
        await session.commit()
        return True
    return False


async def count_user_sessions(session: AsyncSession, user_id: int) -> int:
    """Подсчитать количество программ пользователя."""
    result = await session.execute(
        select(func.count(Session.session_id)).where(Session.user_id == user_id)
    )
    return result.scalar() or 0


# ========== WorkoutDay ==========
async def create_workout_day(
    session: AsyncSession, session_id: int, day_index: int, name: str
) -> WorkoutDay:
    """Создать тренировочный день."""
    workout_day = WorkoutDay(session_id=session_id, day_index=day_index, name=name)
    session.add(workout_day)
    await session.commit()
    await session.refresh(workout_day)
    return workout_day


async def get_workout_days(session: AsyncSession, session_id: int) -> List[WorkoutDay]:
    """Получить все дни программы."""
    result = await session.execute(
        select(WorkoutDay)
        .where(WorkoutDay.session_id == session_id)
        .order_by(WorkoutDay.day_index)
        .options(selectinload(WorkoutDay.exercises))
    )
    return list(result.scalars().all())


async def get_workout_day_by_id(session: AsyncSession, day_id: int) -> Optional[WorkoutDay]:
    """Получить день по ID."""
    result = await session.execute(
        select(WorkoutDay)
        .where(WorkoutDay.id == day_id)
        .options(selectinload(WorkoutDay.exercises).selectinload(Exercise.sets))
    )
    return result.scalar_one_or_none()


# ========== Exercise ==========
async def create_exercise(
    session: AsyncSession, workout_day_id: int, name: str, order: int
) -> Exercise:
    """Создать упражнение."""
    exercise = Exercise(workout_day_id=workout_day_id, name=name, order=order)
    session.add(exercise)
    await session.commit()
    await session.refresh(exercise)
    return exercise


async def get_exercises_by_day(session: AsyncSession, workout_day_id: int) -> List[Exercise]:
    """Получить все упражнения дня."""
    result = await session.execute(
        select(Exercise)
        .where(Exercise.workout_day_id == workout_day_id)
        .order_by(Exercise.order)
        .options(selectinload(Exercise.sets))
    )
    return list(result.scalars().all())


# ========== Set ==========
async def create_set(
    session: AsyncSession, exercise_id: int, set_index: int, reps: int, weight: Optional[float] = None
) -> Set:
    """Создать подход."""
    set_obj = Set(exercise_id=exercise_id, set_index=set_index, reps=reps, weight=weight)
    session.add(set_obj)
    await session.commit()
    await session.refresh(set_obj)
    return set_obj


# ========== SessionRun ==========
async def create_session_run(
    session: AsyncSession, user_id: int, session_id: int
) -> SessionRun:
    """Создать запуск тренировки."""
    session_run = SessionRun(user_id=user_id, session_id=session_id)
    session.add(session_run)
    await session.commit()
    await session.refresh(session_run)
    return session_run


async def get_session_run(session: AsyncSession, run_id: int) -> Optional[SessionRun]:
    """Получить запуск тренировки."""
    result = await session.execute(
        select(SessionRun)
        .where(SessionRun.id == run_id)
        .options(selectinload(SessionRun.session))
    )
    return result.scalar_one_or_none()


# ========== PerformedSet ==========
async def create_performed_set(
    session: AsyncSession,
    exercise_id: int,
    set_index: int,
    weight: float,
    session_run_id: int
) -> PerformedSet:
    """Создать запись о выполненном подходе."""
    performed_set = PerformedSet(
        exercise_id=exercise_id,
        set_index=set_index,
        weight=weight,
        session_run_id=session_run_id
    )
    session.add(performed_set)
    await session.commit()
    await session.refresh(performed_set)
    return performed_set


async def get_last_weight_for_set(
    session: AsyncSession, user_id: int, exercise_id: int, set_index: int
) -> Optional[float]:
    """Получить последний вес для конкретного подхода упражнения."""
    # Находим последний выполненный подход для этого упражнения и сета
    subquery = (
        select(PerformedSet.weight)
        .join(SessionRun, PerformedSet.session_run_id == SessionRun.id)
        .where(
            SessionRun.user_id == user_id,
            PerformedSet.exercise_id == exercise_id,
            PerformedSet.set_index == set_index
        )
        .order_by(desc(PerformedSet.timestamp))
        .limit(1)
    )
    result = await session.execute(subquery)
    return result.scalar_one_or_none()


async def get_performed_sets_by_run(
    session: AsyncSession, session_run_id: int
) -> List[PerformedSet]:
    """Получить все выполненные подходы для запуска тренировки."""
    result = await session.execute(
        select(PerformedSet)
        .where(PerformedSet.session_run_id == session_run_id)
        .options(selectinload(PerformedSet.exercise))
        .order_by(PerformedSet.exercise_id, PerformedSet.set_index)
    )
    return list(result.scalars().all())


async def get_last_performed_set_for_exercise(
    session: AsyncSession, user_id: int, exercise_id: int, set_index: int
) -> Optional[PerformedSet]:
    """Получить последний выполненный подход для упражнения и сета."""
    result = await session.execute(
        select(PerformedSet)
        .join(SessionRun, PerformedSet.session_run_id == SessionRun.id)
        .where(
            SessionRun.user_id == user_id,
            PerformedSet.exercise_id == exercise_id,
            PerformedSet.set_index == set_index
        )
        .order_by(desc(PerformedSet.timestamp))
        .limit(1)
        .options(selectinload(PerformedSet.exercise))
    )
    return result.scalar_one_or_none()


async def get_last_weight_for_exercise_by_name(
    session: AsyncSession, user_id: int, exercise_name: str, set_index: int
) -> Optional[float]:
    """Получить последний вес для упражнения по названию (независимо от exercise_id)."""
    # Ищем по названию упражнения среди всех упражнений пользователя
    subquery = (
        select(PerformedSet.weight)
        .join(SessionRun, PerformedSet.session_run_id == SessionRun.id)
        .join(Exercise, PerformedSet.exercise_id == Exercise.exercise_id)
        .where(
            SessionRun.user_id == user_id,
            Exercise.name == exercise_name,
            PerformedSet.set_index == set_index
        )
        .order_by(desc(PerformedSet.timestamp))
        .limit(1)
    )
    result = await session.execute(subquery)
    return result.scalar_one_or_none()


async def get_last_performed_set_for_exercise_by_name(
    session: AsyncSession, user_id: int, exercise_name: str, set_index: int
) -> Optional[PerformedSet]:
    """Получить последний выполненный подход для упражнения по названию."""
    result = await session.execute(
        select(PerformedSet)
        .join(SessionRun, PerformedSet.session_run_id == SessionRun.id)
        .join(Exercise, PerformedSet.exercise_id == Exercise.exercise_id)
        .where(
            SessionRun.user_id == user_id,
            Exercise.name == exercise_name,
            PerformedSet.set_index == set_index
        )
        .order_by(desc(PerformedSet.timestamp))
        .limit(1)
        .options(selectinload(PerformedSet.exercise))
    )
    return result.scalar_one_or_none()


async def get_exercise_statistics(
    session: AsyncSession, user_id: int, exercise_id: int
) -> dict:
    """
    Получить статистику по упражнению.
    Возвращает словарь: {set_index: [(timestamp, weight), ...]}
    """
    # Получаем все выполненные подходы для этого упражнения
    result = await session.execute(
        select(PerformedSet)
        .join(SessionRun, PerformedSet.session_run_id == SessionRun.id)
        .where(
            SessionRun.user_id == user_id,
            PerformedSet.exercise_id == exercise_id
        )
        .order_by(PerformedSet.set_index, PerformedSet.timestamp)
    )
    performed_sets = list(result.scalars().all())
    
    # Группируем по set_index
    stats = {}
    for ps in performed_sets:
        if ps.set_index not in stats:
            stats[ps.set_index] = []
        stats[ps.set_index].append((ps.timestamp, ps.weight))
    
    return stats


async def get_exercise_by_id(session: AsyncSession, exercise_id: int) -> Optional[Exercise]:
    """Получить упражнение по ID."""
    result = await session.execute(
        select(Exercise)
        .where(Exercise.exercise_id == exercise_id)
        .options(selectinload(Exercise.sets))
    )
    return result.scalar_one_or_none()
