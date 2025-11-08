"""Парсер для разбора строк с упражнениями и подходами."""
import re
from typing import List, Tuple, Optional


def parse_exercise_string(text: str) -> Tuple[str, List[int]]:
    """
    Парсит строку с упражнением и подходами.
    
    Поддерживаемые форматы:
    - "Гакк-присед — 20-16-14-12"
    - "Гакк-присед — 4х10"
    - "Гакк-присед — 4x10"
    - "Гакк-присед — 4 подхода по 10 раз"
    - "Гакк-присед — 4x10, 3x8"
    
    Возвращает:
        Tuple[название_упражнения, список_повторений]
    """
    text = text.strip()
    
    # Разделители для названия и подходов
    separators = ["—", "-", "–", "—"]
    exercise_name = text
    sets_part = ""
    
    for sep in separators:
        if sep in text:
            parts = text.split(sep, 1)
            if len(parts) == 2:
                exercise_name = parts[0].strip()
                sets_part = parts[1].strip()
                break
    
    if not sets_part:
        # Если разделителя нет, пытаемся найти паттерн подходов в конце
        # Ищем паттерны типа "4x10" или "20-16-14"
        pattern = r'(\d+[xх]\d+|\d+-\d+(?:-\d+)*)'
        match = re.search(pattern, text)
        if match:
            exercise_name = text[:match.start()].strip()
            sets_part = match.group(1)
        else:
            # Если ничего не найдено, возвращаем только название
            return exercise_name, []
    
    # Парсим подходы
    reps_list = []
    
    # Формат: "20-16-14-12" (список повторений)
    if re.match(r'^\d+(-\d+)+$', sets_part):
        reps_list = [int(x) for x in sets_part.split("-")]
    
    # Формат: "4x10" или "4х10" (количество подходов x повторения)
    elif re.match(r'^\d+[xх]\d+$', sets_part):
        match = re.match(r'^(\d+)[xх](\d+)$', sets_part)
        if match:
            sets_count = int(match.group(1))
            reps = int(match.group(2))
            reps_list = [reps] * sets_count
    
    # Формат: "4 подхода по 10 раз" или "4 подхода по 10"
    elif re.search(r'подход', sets_part, re.IGNORECASE):
        match = re.search(r'(\d+)\s+подход[а-я]*\s+по\s+(\d+)', sets_part, re.IGNORECASE)
        if match:
            sets_count = int(match.group(1))
            reps = int(match.group(2))
            reps_list = [reps] * sets_count
    
    # Формат: "4x10, 3x8" (несколько групп подходов)
    elif "," in sets_part or ";" in sets_part:
        parts = re.split(r'[,;]', sets_part)
        for part in parts:
            part = part.strip()
            # Формат "4x10"
            if re.match(r'^\d+[xх]\d+$', part):
                match = re.match(r'^(\d+)[xх](\d+)$', part)
                if match:
                    sets_count = int(match.group(1))
                    reps = int(match.group(2))
                    reps_list.extend([reps] * sets_count)
            # Формат "10" (один подход)
            elif re.match(r'^\d+$', part):
                reps_list.append(int(part))
    
    # Если ничего не распарсилось, пытаемся извлечь числа
    if not reps_list:
        numbers = re.findall(r'\d+', sets_part)
        if numbers:
            reps_list = [int(n) for n in numbers]
    
    return exercise_name, reps_list


def format_exercise_name(exercise_name: str, sets_count: int) -> str:
    """Форматирует название упражнения с количеством подходов."""
    return f"{exercise_name} — {sets_count} подхода"

