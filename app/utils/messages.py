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
    """Форматирует информацию о тренировочном дне в исходном формате."""
    text = f"📅 {day.name}\n\n"
    
    if not exercises:
        text += "Упражнения пока не добавлены."
        return text
    
    for exercise in exercises:
        # Показываем упражнение в исходном формате
        # Если в name сохранен исходный формат (содержит дефисы с числами), показываем его
        # Иначе восстанавливаем из sets
        exercise_name = exercise.name
        
        # Проверяем, является ли name исходным форматом (содержит паттерн "— число-число" или "— числоxчисло")
        import re
        if re.search(r'—\s*\d+[-\d]*[xх]?\d*', exercise_name) or re.search(r'-\s*\d+[-\d]*[xх]?\d*', exercise_name):
            # Это исходный формат, показываем как есть
            text += f"{exercise_name}\n"
        else:
            # Это formatted_name, восстанавливаем исходный формат из sets
            if exercise.sets:
                reps_list = [str(set_obj.reps) for set_obj in sorted(exercise.sets, key=lambda x: x.set_index)]
                # Извлекаем базовое название (убираем " — N подхода")
                base_name = re.sub(r'\s*—\s*\d+\s+подхода?', '', exercise_name).strip()
                # Формируем исходный формат: "Название — 16-10-12"
                original_format = f"{base_name} — {'-'.join(reps_list)}"
                text += f"{original_format}\n"
            else:
                text += f"{exercise_name}\n"
    
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

