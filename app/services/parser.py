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
    
    # Разделители для названия и подходов (используем длинное тире в первую очередь)
    # Ищем разделитель, который отделяет название от подходов
    # Приоритет: длинное тире, обычный дефис (но только если после него идут числа)
    
    exercise_name = text
    sets_part = ""
    
    # Сначала ищем длинное тире (—) - это самый надежный разделитель
    if "—" in text:
        parts = text.split("—", 1)
        if len(parts) == 2:
            exercise_name = parts[0].strip()
            sets_part = parts[1].strip()
    
    # Если не нашли длинное тире, ищем обычный дефис
    # Но только если после дефиса идет паттерн подходов (числа через дефис или x)
    if not sets_part and "-" in text:
        # Ищем паттерн подходов в конце строки
        # Форматы: "20-12-15", "4x10", "4х10"
        pattern = r'[-–]\s*(\d+[xх]\d+|\d+-\d+(?:-\d+)*|\d+\s+подход)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Нашли паттерн подходов, разделяем по этому дефису
            split_pos = match.start()
            exercise_name = text[:split_pos].strip()
            sets_part = text[split_pos + 1:].strip()  # Убираем дефис
        else:
            # Если паттерна нет, пробуем разделить по последнему дефису
            # (на случай формата "Название - 20-12-15")
            last_dash = text.rfind("-")
            if last_dash > 0:
                potential_name = text[:last_dash].strip()
                potential_sets = text[last_dash + 1:].strip()
                # Проверяем, что после дефиса есть числа
                if re.search(r'\d', potential_sets):
                    exercise_name = potential_name
                    sets_part = potential_sets
    
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
    
    # Формат: "20-16-14-12" или "20–16–14–12" (список повторений с дефисом или длинным тире)
    if re.match(r'^\d+([\-–—]\d+)+$', sets_part):
        # Заменяем длинное тире на обычный дефис для парсинга
        normalized = sets_part.replace('–', '-').replace('—', '-')
        reps_list = [int(x) for x in normalized.split("-")]
    
    # Формат: "4x10", "4х10" или "4×10" (количество подходов x повторения)
    # Поддерживаем символ × (умножение) и длинное тире в диапазонах "8–10"
    elif re.match(r'^\d+[xх×]\d+$', sets_part) or re.match(r'^\d+[xх×]\d+[–—]\d+$', sets_part):
        # Формат "4×8–10" (подходы × повторения-повторения)
        range_match = re.match(r'^(\d+)[xх×](\d+)[–—](\d+)$', sets_part)
        if range_match:
            sets_count = int(range_match.group(1))
            min_reps = int(range_match.group(2))
            max_reps = int(range_match.group(3))
            # Используем среднее значение или минимальное
            reps = min_reps
            reps_list = [reps] * sets_count
        else:
            # Формат "4×10" (просто число)
            match = re.match(r'^(\d+)[xх×](\d+)$', sets_part)
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
    
    # Формат: "4x10, 3x8" или "4×8–10" (несколько групп подходов или диапазоны)
    elif "," in sets_part or ";" in sets_part:
        parts = re.split(r'[,;]', sets_part)
        for part in parts:
            part = part.strip()
            # Формат "4×8–10" (диапазон)
            range_match = re.match(r'^(\d+)[xх×](\d+)[–—](\d+)$', part)
            if range_match:
                sets_count = int(range_match.group(1))
                min_reps = int(range_match.group(2))
                reps = min_reps  # Используем минимальное значение
                reps_list.extend([reps] * sets_count)
            # Формат "4x10" или "4×10"
            elif re.match(r'^\d+[xх×]\d+$', part):
                match = re.match(r'^(\d+)[xх×](\d+)$', part)
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

