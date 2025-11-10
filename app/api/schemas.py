"""Pydantic схемы для валидации данных API."""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# ========== User Schemas ==========
class UserBase(BaseModel):
    """Базовая схема пользователя."""
    telegram_id: int
    username: Optional[str] = None


class UserCreate(UserBase):
    """Схема для создания пользователя."""
    pass


class UserResponse(UserBase):
    """Схема ответа с данными пользователя."""
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== Program (Session) Schemas ==========
class ProgramBase(BaseModel):
    """Базовая схема программы."""
    name: str = Field(..., min_length=1, max_length=200)


class ProgramCreate(ProgramBase):
    """Схема для создания программы."""
    user_id: int


class ProgramResponse(ProgramBase):
    """Схема ответа с данными программы."""
    session_id: int
    user_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProgramDetailResponse(ProgramResponse):
    """Схема ответа с детальной информацией о программе."""
    days: List["WorkoutDayResponse"] = []

    class Config:
        from_attributes = True


# ========== WorkoutDay Schemas ==========
class WorkoutDayBase(BaseModel):
    """Базовая схема дня тренировки."""
    name: str = Field(..., min_length=1, max_length=200)
    day_index: int = Field(..., ge=0)


class WorkoutDayCreate(WorkoutDayBase):
    """Схема для создания дня тренировки."""
    session_id: int


class WorkoutDayResponse(WorkoutDayBase):
    """Схема ответа с данными дня тренировки."""
    id: int
    session_id: int
    exercises: List["ExerciseResponse"] = []

    class Config:
        from_attributes = True


# ========== Exercise Schemas ==========
class ExerciseBase(BaseModel):
    """Базовая схема упражнения."""
    name: str = Field(..., min_length=1, max_length=200)
    order: int = Field(..., ge=0)


class ExerciseCreate(ExerciseBase):
    """Схема для создания упражнения."""
    workout_day_id: int


class ExerciseResponse(ExerciseBase):
    """Схема ответа с данными упражнения."""
    exercise_id: int
    workout_day_id: int
    sets: List["SetResponse"] = []

    class Config:
        from_attributes = True


# ========== Set Schemas ==========
class SetBase(BaseModel):
    """Базовая схема подхода."""
    set_index: int = Field(..., ge=0)
    reps: int = Field(..., gt=0)
    weight: Optional[float] = Field(None, ge=0)


class SetCreate(SetBase):
    """Схема для создания подхода."""
    exercise_id: int


class SetResponse(SetBase):
    """Схема ответа с данными подхода."""
    set_id: int
    exercise_id: int

    class Config:
        from_attributes = True


# ========== SessionRun Schemas ==========
class SessionRunBase(BaseModel):
    """Базовая схема запуска тренировки."""
    user_id: int
    session_id: int


class SessionRunCreate(SessionRunBase):
    """Схема для создания запуска тренировки."""
    pass


class SessionRunResponse(SessionRunBase):
    """Схема ответа с данными запуска тренировки."""
    id: int
    started_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== PerformedSet Schemas ==========
class PerformedSetBase(BaseModel):
    """Базовая схема выполненного подхода."""
    exercise_id: int
    set_index: int = Field(..., ge=0)
    weight: float = Field(..., gt=0)
    session_run_id: int


class PerformedSetCreate(PerformedSetBase):
    """Схема для создания выполненного подхода."""
    pass


class PerformedSetResponse(PerformedSetBase):
    """Схема ответа с данными выполненного подхода."""
    id: int
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== Update Schemas ==========
class ProgramUpdate(BaseModel):
    """Схема для обновления программы."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)


class ExerciseUpdate(BaseModel):
    """Схема для обновления упражнения."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    order: Optional[int] = Field(None, ge=0)


class SetUpdate(BaseModel):
    """Схема для обновления подхода."""
    reps: Optional[int] = Field(None, gt=0)
    weight: Optional[float] = Field(None, ge=0)


# Разрешаем forward references
ProgramDetailResponse.model_rebuild()
WorkoutDayResponse.model_rebuild()
ExerciseResponse.model_rebuild()

