"""Модели базы данных."""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Float, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """Модель пользователя."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    session_runs = relationship("SessionRun", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    """Модель программы тренировок."""
    __tablename__ = "sessions"
    
    session_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="sessions")
    workout_days = relationship("WorkoutDay", back_populates="session", cascade="all, delete-orphan")
    session_runs = relationship("SessionRun", back_populates="session", cascade="all, delete-orphan")


class WorkoutDay(Base):
    """Модель тренировочного дня."""
    __tablename__ = "workout_days"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False)
    day_index = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    
    session = relationship("Session", back_populates="workout_days")
    exercises = relationship("Exercise", back_populates="workout_day", cascade="all, delete-orphan", order_by="Exercise.order")
    
    __table_args__ = (
        Index("idx_session_day", "session_id", "day_index"),
    )


class Exercise(Base):
    """Модель упражнения."""
    __tablename__ = "exercises"
    
    exercise_id = Column(Integer, primary_key=True, index=True)
    workout_day_id = Column(Integer, ForeignKey("workout_days.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    
    workout_day = relationship("WorkoutDay", back_populates="exercises")
    sets = relationship("Set", back_populates="exercise", cascade="all, delete-orphan", order_by="Set.set_index")
    performed_sets = relationship("PerformedSet", back_populates="exercise", cascade="all, delete-orphan")


class Set(Base):
    """Модель подхода (шаблон)."""
    __tablename__ = "sets"
    
    set_id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.exercise_id", ondelete="CASCADE"), nullable=False)
    set_index = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Float, nullable=True)  # Для сохранения прошлых весов
    
    exercise = relationship("Exercise", back_populates="sets")
    
    __table_args__ = (
        Index("idx_exercise_set", "exercise_id", "set_index"),
    )


class SessionRun(Base):
    """Модель запуска тренировки."""
    __tablename__ = "session_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="session_runs")
    session = relationship("Session", back_populates="session_runs")
    performed_sets = relationship("PerformedSet", back_populates="session_run", cascade="all, delete-orphan")


class PerformedSet(Base):
    """Модель выполненного подхода."""
    __tablename__ = "performed_sets"
    
    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.exercise_id", ondelete="CASCADE"), nullable=False)
    set_index = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    session_run_id = Column(Integer, ForeignKey("session_runs.id", ondelete="CASCADE"), nullable=False)
    
    exercise = relationship("Exercise", back_populates="performed_sets")
    session_run = relationship("SessionRun", back_populates="performed_sets")
    
    __table_args__ = (
        Index("idx_exercise_set_run", "exercise_id", "set_index", "session_run_id"),
    )

