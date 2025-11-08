"""Генератор программ тренировок через AI."""
import re
from typing import Optional, Dict, List, Tuple


def parse_ai_program_response(ai_response: str) -> Optional[Dict]:
    """
    Парсит ответ AI с программой тренировок.
    
    Ожидаемый формат от AI:
    ПРОГРАММА: Название программы
    
    ДЕНЬ 1: Название дня
    Упражнение 1 — подходы
    Упражнение 2 — подходы
    ...
    
    ДЕНЬ 2: Название дня
    ...
    
    Возвращает словарь с программой или None, если не удалось распарсить.
    """
    lines = ai_response.strip().split('\n')
    
    program_name = None
    days = []
    current_day = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Парсим название программы
        if line.upper().startswith("ПРОГРАММА:"):
            program_name = line.split(":", 1)[1].strip()
            continue
        
        # Парсим день
        day_match = re.match(r'ДЕНЬ\s+(\d+):\s*(.+)', line, re.IGNORECASE)
        if day_match:
            # Сохраняем предыдущий день, если есть
            if current_day:
                days.append(current_day)
            
            day_name = day_match.group(2).strip()
            current_day = {
                "name": day_name,
                "exercises": []
            }
            continue
        
        # Парсим упражнение (если есть текущий день)
        if current_day and ("—" in line or "-" in line or "х" in line.lower() or "x" in line.lower()):
            # Убираем нумерацию, если есть (например, "1. " или "• ")
            exercise_line = re.sub(r'^[\d•\-\*]\s*', '', line).strip()
            
            # Проверяем, что это упражнение (содержит паттерн подходов)
            if re.search(r'\d+[xх\-]', exercise_line) or re.search(r'\d+\s+подход', exercise_line, re.IGNORECASE):
                current_day["exercises"].append(exercise_line)
    
    # Добавляем последний день
    if current_day:
        days.append(current_day)
    
    # Если не нашли программу через формат, пытаемся найти в свободном тексте
    if not program_name or not days:
        return _parse_free_format(ai_response)
    
    if program_name and days:
        return {
            "name": program_name,
            "days": days
        }
    
    return None


def _parse_free_format(text: str) -> Optional[Dict]:
    """Парсит программу из свободного формата."""
    # Ищем паттерны типа "Программа: ..." или "Название: ..."
    program_match = re.search(r'(?:Программа|Название)[:\-]\s*(.+)', text, re.IGNORECASE)
    program_name = program_match.group(1).strip() if program_match else "Программа от AI"
    
    # Ищем дни по паттернам "День 1", "День 2" или просто списки упражнений
    days = []
    
    # Разбиваем на блоки по дням
    day_patterns = [
        r'День\s+(\d+)[:\-]\s*(.+?)(?=День\s+\d+|$)',
        r'День\s+(\d+)\s+(.+?)(?=День\s+\d+|$)',
    ]
    
    for pattern in day_patterns:
        day_matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in day_matches:
            day_name = match.group(2).strip().split('\n')[0]  # Первая строка - название дня
            day_content = match.group(2)
            
            exercises = []
            for line in day_content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Проверяем, что это упражнение
                if ("—" in line or "-" in line or "х" in line.lower() or "x" in line.lower() or 
                    re.search(r'\d+\s+подход', line, re.IGNORECASE)):
                    # Убираем нумерацию
                    exercise_line = re.sub(r'^[\d•\-\*]\s*', '', line).strip()
                    if exercise_line and len(exercise_line) > 3:
                        exercises.append(exercise_line)
            
            if exercises:
                days.append({
                    "name": day_name if day_name else f"День {len(days) + 1}",
                    "exercises": exercises
                })
    
    # Если не нашли структурированные дни, пытаемся извлечь упражнения
    if not days:
        all_exercises = []
        for line in text.split('\n'):
            line = line.strip()
            if ("—" in line or "-" in line or "х" in line.lower() or "x" in line.lower() or 
                re.search(r'\d+\s+подход', line, re.IGNORECASE)):
                exercise_line = re.sub(r'^[\d•\-\*]\s*', '', line).strip()
                if exercise_line and len(exercise_line) > 3:
                    all_exercises.append(exercise_line)
        
        if all_exercises:
            # Создаём один день со всеми упражнениями
            days.append({
                "name": "Тренировка",
                "exercises": all_exercises
            })
    
    if days:
        return {
            "name": program_name,
            "days": days
        }
    
    return None


def format_program_for_ai_request(user_request: str) -> str:
    """Форматирует запрос пользователя для AI с инструкциями по формату."""
    return f"""Пользователь просит создать программу тренировок: "{user_request}"

Создай программу тренировок в следующем формате:

ПРОГРАММА: [Название программы]

ДЕНЬ 1: [Название дня]
[Упражнение 1] — [подходы в формате: 12-10-8 или 4х10]
[Упражнение 2] — [подходы]
...

ДЕНЬ 2: [Название дня]
[Упражнение 1] — [подходы]
...

Важно:
- Используй формат "Название — 12-10-8" или "Название — 4х10"
- Названия упражнений должны быть понятными
- Количество дней: 3-5 (в зависимости от запроса)
- Учитывай уровень подготовки из запроса пользователя
- Отвечай ТОЛЬКО программой, без дополнительных комментариев"""

