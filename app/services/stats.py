"""Сервис для работы со статистикой тренировок."""
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import crud
from app.db.models import PerformedSet, Exercise


async def get_comparison_stats(
    session: AsyncSession,
    user_id: int,
    performed_sets: List[PerformedSet]
) -> Dict[int, Dict[int, Optional[float]]]:
    """
    Получить статистику сравнения текущих весов с предыдущими.
    
    Возвращает словарь:
    {
        exercise_id: {
            set_index: previous_weight или None
        }
    }
    """
    stats = {}
    
    for performed_set in performed_sets:
        exercise_id = performed_set.exercise_id
        set_index = performed_set.set_index
        
        if exercise_id not in stats:
            stats[exercise_id] = {}
        
        # Получаем последний вес для этого упражнения и сета
        last_weight = await crud.get_last_weight_for_set(
            session, user_id, exercise_id, set_index
        )
        
        # Исключаем текущую запись (если она уже в БД)
        if last_weight and last_weight == performed_set.weight:
            # Пытаемся найти предыдущую запись
            last_performed = await crud.get_last_performed_set_for_exercise(
                session, user_id, exercise_id, set_index
            )
            if last_performed and last_performed.id != performed_set.id:
                stats[exercise_id][set_index] = last_performed.weight
            else:
                stats[exercise_id][set_index] = None
        else:
            stats[exercise_id][set_index] = last_weight
    
    return stats


def format_comparison(current: float, previous: Optional[float]) -> str:
    """Форматирует сравнение текущего и предыдущего веса."""
    if previous is None:
        return "новая запись"
    
    diff = current - previous
    if diff > 0:
        return f"+{diff:.1f} кг"
    elif diff < 0:
        return f"{diff:.1f} кг"
    else:
        return "без изменений"

