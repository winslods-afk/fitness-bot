"""Шаблоны сообщений для бота."""
from typing import List, Dict


def get_welcome_message() -> str:
    """Приветственное сообщение."""
    return "привет, добавь свою программу"


def get_program_limit_message() -> str:
    """Сообщение о достижении лимита программ."""
    return (
        "❌ У вас уже есть максимальное количество программ (2).\n\n"
        "Чтобы добавить новую программу, сначала удалите одну из существующих "
        "через меню «Удалить программу»."
    )


def format_program_list(programs: List) -> str:
    """Форматирует список программ."""
    if not programs:
        return "У вас пока нет программ."
    
    text = "📋 Ваши программы:\n\n"
    for i, program in enumerate(programs, 1):
        text += f"{i}. {program.name}\n"
    
    return text


def format_workout_day_info(day, exercises: List) -> str:
    """Форматирует информацию о тренировочном дне."""
    text = f"📅 {day.name}\n\n"
    
    if not exercises:
        text += "Упражнения пока не добавлены."
        return text
    
    for exercise in exercises:
        text += f"💪 {exercise.name}\n"
        if exercise.sets:
            sets_info = []
            for set_obj in sorted(exercise.sets, key=lambda x: x.set_index):
                reps_text = f"{set_obj.reps} раз"
                if set_obj.weight:
                    reps_text += f" (вес: {set_obj.weight} кг)"
                sets_info.append(f"  Подход {set_obj.set_index}: {reps_text}")
            text += "\n".join(sets_info) + "\n\n"
    
    return text


def format_training_summary(performed_sets: List, stats: Dict) -> str:
    """Форматирует итоговую сводку тренировки."""
    from app.services.stats import format_comparison
    
    text = "✅ Тренировка завершена!\n\n"
    text += "📊 Итоги:\n\n"
    
    current_exercise = None
    for performed_set in performed_sets:
        exercise = performed_set.exercise
        if current_exercise != exercise:
            if current_exercise is not None:
                text += "\n"
            text += f"💪 {exercise.name}\n"
            current_exercise = exercise
        
        previous_weight = stats.get(exercise.exercise_id, {}).get(performed_set.set_index)
        comparison = format_comparison(performed_set.weight, previous_weight)
        
        text += f"  Подход {performed_set.set_index}: {performed_set.weight} кг ({comparison})\n"
    
    return text

