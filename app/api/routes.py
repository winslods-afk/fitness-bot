"""API routes для работы с базой данных."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.auth import verify_api_key
from app.api.schemas import (
    UserCreate, UserResponse,
    ProgramCreate, ProgramResponse, ProgramDetailResponse, ProgramUpdate,
    WorkoutDayCreate, WorkoutDayResponse,
    ExerciseCreate, ExerciseResponse, ExerciseUpdate,
    SetCreate, SetResponse, SetUpdate,
    SessionRunCreate, SessionRunResponse,
    PerformedSetCreate, PerformedSetResponse
)
from app.db.init_db import async_session_maker
from app.db.models import User, Session, WorkoutDay, Exercise, Set, SessionRun, PerformedSet
from app.db import crud

router = APIRouter()


async def get_db_session():
    """Dependency для получения сессии базы данных."""
    async with async_session_maker() as session:
        yield session


# ========== User Endpoints ==========
@router.get("/users", dependencies=[Depends(verify_api_key)], response_model=dict)
async def get_users_with_programs(session: AsyncSession = Depends(get_db_session)):
    """
    Получить список всех пользователей с их программами и количеством программ.
    
    Требует авторизации через API ключ в заголовке X-API-Key.
    """
    try:
        result = await session.execute(
            select(User).order_by(User.created_at)
        )
        users = result.scalars().all()
        
        users_data = []
        for user in users:
            programs = await crud.get_user_sessions(session, user.id)
            programs_count = len(programs)
            
            programs_data = []
            for program in programs:
                programs_data.append({
                    "id": program.session_id,
                    "name": program.name,
                    "created_at": program.created_at.isoformat() if program.created_at else None
                })
            
            users_data.append({
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "programs_count": programs_count,
                "programs": programs_data
            })
        
        return {
            "users": users_data,
            "total_users": len(users_data),
            "total_programs": sum(u["programs_count"] for u in users_data)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении данных: {str(e)}"
        )


@router.get("/users/{user_id}", dependencies=[Depends(verify_api_key)], response_model=UserResponse)
async def get_user(user_id: int, session: AsyncSession = Depends(get_db_session)):
    """Получить пользователя по ID."""
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )
    return user


@router.post("/users", dependencies=[Depends(verify_api_key)], response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, session: AsyncSession = Depends(get_db_session)):
    """Создать нового пользователя."""
    # Проверяем, существует ли пользователь с таким telegram_id
    result = await session.execute(
        select(User).where(User.telegram_id == user_data.telegram_id)
    )
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Пользователь с telegram_id {user_data.telegram_id} уже существует"
        )
    
    user = await crud.get_or_create_user(session, user_data.telegram_id, user_data.username)
    return user


@router.delete("/users/{user_id}", dependencies=[Depends(verify_api_key)], status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, session: AsyncSession = Depends(get_db_session)):
    """Удалить пользователя и все связанные данные."""
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )
    
    await session.delete(user)
    await session.commit()
    return None


# ========== Program (Session) Endpoints ==========
@router.get("/programs", dependencies=[Depends(verify_api_key)], response_model=List[ProgramResponse])
async def get_programs(
    user_id: Optional[int] = None,
    session: AsyncSession = Depends(get_db_session)
):
    """Получить список всех программ. Опционально фильтр по user_id."""
    if user_id:
        programs = await crud.get_user_sessions(session, user_id)
    else:
        programs = await crud.get_all_sessions(session)
    return programs


@router.get("/programs/{program_id}", dependencies=[Depends(verify_api_key)], response_model=ProgramDetailResponse)
async def get_program(program_id: int, session: AsyncSession = Depends(get_db_session)):
    """Получить программу с детальной информацией (дни, упражнения, подходы)."""
    program = await crud.get_session_with_details(session, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Программа с ID {program_id} не найдена"
        )
    return program


@router.post("/programs", dependencies=[Depends(verify_api_key)], response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
async def create_program(program_data: ProgramCreate, session: AsyncSession = Depends(get_db_session)):
    """Создать новую программу."""
    # Проверяем, существует ли пользователь
    result = await session.execute(
        select(User).where(User.id == program_data.user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {program_data.user_id} не найден"
        )
    
    program = await crud.create_session(session, program_data.user_id, program_data.name)
    return program


@router.put("/programs/{program_id}", dependencies=[Depends(verify_api_key)], response_model=ProgramResponse)
async def update_program(
    program_id: int,
    program_data: ProgramUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """Обновить программу."""
    program = await crud.get_session_by_id(session, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Программа с ID {program_id} не найдена"
        )
    
    if program_data.name is not None:
        program.name = program_data.name
        await session.commit()
        await session.refresh(program)
    
    return program


@router.delete("/programs/{program_id}", dependencies=[Depends(verify_api_key)], status_code=status.HTTP_204_NO_CONTENT)
async def delete_program(program_id: int, session: AsyncSession = Depends(get_db_session)):
    """Удалить программу и все связанные данные."""
    deleted = await crud.delete_session(session, program_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Программа с ID {program_id} не найдена"
        )
    return None


# ========== WorkoutDay Endpoints ==========
@router.get("/programs/{program_id}/days", dependencies=[Depends(verify_api_key)], response_model=List[WorkoutDayResponse])
async def get_program_days(program_id: int, session: AsyncSession = Depends(get_db_session)):
    """Получить все дни программы."""
    # Проверяем, существует ли программа
    program = await crud.get_session_by_id(session, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Программа с ID {program_id} не найдена"
        )
    
    days = await crud.get_workout_days(session, program_id)
    return days


@router.post("/programs/{program_id}/days", dependencies=[Depends(verify_api_key)], response_model=WorkoutDayResponse, status_code=status.HTTP_201_CREATED)
async def create_workout_day(
    program_id: int,
    day_data: WorkoutDayCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Создать новый день в программе."""
    # Проверяем, существует ли программа
    program = await crud.get_session_by_id(session, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Программа с ID {program_id} не найдена"
        )
    
    if day_data.session_id != program_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_id в теле запроса должен совпадать с program_id в URL"
        )
    
    day = await crud.create_workout_day(session, program_id, day_data.day_index, day_data.name)
    return day


# ========== Exercise Endpoints ==========
@router.get("/exercises/{exercise_id}", dependencies=[Depends(verify_api_key)], response_model=ExerciseResponse)
async def get_exercise(exercise_id: int, session: AsyncSession = Depends(get_db_session)):
    """Получить упражнение по ID."""
    exercise = await crud.get_exercise_by_id(session, exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Упражнение с ID {exercise_id} не найдено"
        )
    return exercise


@router.post("/days/{day_id}/exercises", dependencies=[Depends(verify_api_key)], response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
async def create_exercise(
    day_id: int,
    exercise_data: ExerciseCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Создать новое упражнение в дне."""
    # Проверяем, существует ли день
    day = await crud.get_workout_day_by_id(session, day_id)
    if not day:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"День с ID {day_id} не найден"
        )
    
    if exercise_data.workout_day_id != day_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="workout_day_id в теле запроса должен совпадать с day_id в URL"
        )
    
    exercise = await crud.create_exercise(session, day_id, exercise_data.name, exercise_data.order)
    return exercise


@router.put("/exercises/{exercise_id}", dependencies=[Depends(verify_api_key)], response_model=ExerciseResponse)
async def update_exercise(
    exercise_id: int,
    exercise_data: ExerciseUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """Обновить упражнение."""
    exercise = await crud.get_exercise_by_id(session, exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Упражнение с ID {exercise_id} не найдено"
        )
    
    if exercise_data.name is not None:
        exercise.name = exercise_data.name
    if exercise_data.order is not None:
        exercise.order = exercise_data.order
    
    await session.commit()
    await session.refresh(exercise)
    return exercise


# ========== Set Endpoints ==========
@router.post("/exercises/{exercise_id}/sets", dependencies=[Depends(verify_api_key)], response_model=SetResponse, status_code=status.HTTP_201_CREATED)
async def create_set(
    exercise_id: int,
    set_data: SetCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Создать новый подход для упражнения."""
    # Проверяем, существует ли упражнение
    exercise = await crud.get_exercise_by_id(session, exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Упражнение с ID {exercise_id} не найдено"
        )
    
    if set_data.exercise_id != exercise_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="exercise_id в теле запроса должен совпадать с exercise_id в URL"
        )
    
    set_obj = await crud.create_set(
        session, exercise_id, set_data.set_index, set_data.reps, set_data.weight
    )
    return set_obj


# ========== SessionRun Endpoints ==========
@router.get("/session-runs/{run_id}", dependencies=[Depends(verify_api_key)], response_model=SessionRunResponse)
async def get_session_run(run_id: int, session: AsyncSession = Depends(get_db_session)):
    """Получить запуск тренировки по ID."""
    run = await crud.get_session_run(session, run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запуск тренировки с ID {run_id} не найден"
        )
    return run


@router.post("/session-runs", dependencies=[Depends(verify_api_key)], response_model=SessionRunResponse, status_code=status.HTTP_201_CREATED)
async def create_session_run(run_data: SessionRunCreate, session: AsyncSession = Depends(get_db_session)):
    """Создать новый запуск тренировки."""
    # Проверяем, существует ли пользователь
    result = await session.execute(
        select(User).where(User.id == run_data.user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {run_data.user_id} не найден"
        )
    
    # Проверяем, существует ли программа
    program = await crud.get_session_by_id(session, run_data.session_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Программа с ID {run_data.session_id} не найдена"
        )
    
    run = await crud.create_session_run(session, run_data.user_id, run_data.session_id)
    return run


# ========== PerformedSet Endpoints ==========
@router.post("/performed-sets", dependencies=[Depends(verify_api_key)], response_model=PerformedSetResponse, status_code=status.HTTP_201_CREATED)
async def create_performed_set(set_data: PerformedSetCreate, session: AsyncSession = Depends(get_db_session)):
    """Создать запись о выполненном подходе."""
    # Проверяем, существует ли упражнение
    exercise = await crud.get_exercise_by_id(session, set_data.exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Упражнение с ID {set_data.exercise_id} не найдено"
        )
    
    # Проверяем, существует ли запуск тренировки
    run = await crud.get_session_run(session, set_data.session_run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запуск тренировки с ID {set_data.session_run_id} не найден"
        )
    
    performed_set = await crud.create_performed_set(
        session,
        set_data.exercise_id,
        set_data.set_index,
        set_data.weight,
        set_data.session_run_id
    )
    return performed_set


@router.get("/session-runs/{run_id}/performed-sets", dependencies=[Depends(verify_api_key)], response_model=List[PerformedSetResponse])
async def get_performed_sets(run_id: int, session: AsyncSession = Depends(get_db_session)):
    """Получить все выполненные подходы для запуска тренировки."""
    # Проверяем, существует ли запуск тренировки
    run = await crud.get_session_run(session, run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запуск тренировки с ID {run_id} не найден"
        )
    
    performed_sets = await crud.get_performed_sets_by_run(session, run_id)
    return performed_sets

