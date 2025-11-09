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
    - "сведение рук в тренажере (бабочка) 3 подхода"
    - "жим в тренажере 3 подхода 12 повторений"
    - "разгибание рук с верхним блоком 3*10-12"
    - "тяга верхнего блока к груди 3*10-12 25 кг / тяга в тренажере"
    
    Возвращает:
        Tuple[название_упражнения, список_повторений]
    """
    text = text.strip()
    
    # Удаляем информацию о весе и единицах измерения из названия упражнения
    # Формат: "25 кг / тяга в тренажере" -> "тяга в тренажере"
    # Но сохраняем эту информацию для парсинга подходов, если она там есть
    text_clean = re.sub(r'\s*\d+\s*(кг|kg|lb|lbs)\s*[/\-]?\s*', ' ', text, flags=re.IGNORECASE)
    text_clean = text_clean.strip()
    
    # Разделители для названия и подходов (используем длинное тире в первую очередь)
    # Ищем разделитель, который отделяет название от подходов
    # Приоритет: длинное тире, обычный дефис (но только если после него идут числа)
    
    exercise_name = text_clean
    sets_part = ""
    
    # Сначала ищем длинное тире (—) - это самый надежный разделитель
    if "—" in text_clean:
        parts = text_clean.split("—", 1)
        if len(parts) == 2:
            exercise_name = parts[0].strip()
            sets_part = parts[1].strip()
    
    # Если не нашли длинное тире, ищем обычный дефис
    # Но только если после дефиса идет паттерн подходов (числа через дефис или x)
    if not sets_part and "-" in text_clean:
        # Ищем паттерн подходов в конце строки
        # Форматы: "20-12-15", "4x10", "4х10", "3*10-12", "3 подхода"
        pattern = r'[-–]\s*(\d+[xх×*]\d+|\d+-\d+(?:-\d+)*|\d+\s+подход|\d+[*xх×]\d+[-–—]?\d*)'
        match = re.search(pattern, text_clean, re.IGNORECASE)
        if match:
            # Нашли паттерн подходов, разделяем по этому дефису
            split_pos = match.start()
            exercise_name = text_clean[:split_pos].strip()
            sets_part = text_clean[split_pos + 1:].strip()  # Убираем дефис
        else:
            # Если паттерна нет, пробуем разделить по последнему дефису
            # (на случай формата "Название - 20-12-15")
            last_dash = text_clean.rfind("-")
            if last_dash > 0:
                potential_name = text_clean[:last_dash].strip()
                potential_sets = text_clean[last_dash + 1:].strip()
                # Проверяем, что после дефиса есть числа
                if re.search(r'\d', potential_sets):
                    exercise_name = potential_name
                    sets_part = potential_sets
    
    if not sets_part:
        # Если разделителя нет, пытаемся найти паттерн подходов в конце
        # Ищем паттерны типа "4x10", "3*10-12", "20-16-14", "3 подхода", "3 подхода 12 повторений"
        # Паттерны могут быть в конце строки или после названия упражнения
        patterns = [
            r'(\d+[xх×*]\d+[-–—]?\d*)',  # "4x10", "3*10-12"
            r'(\d+-\d+(?:-\d+)*)',  # "20-16-14"
            r'(\d+\s+подход.*\d+\s+повтор)',  # "3 подхода 12 повторений"
            r'(\d+\s+подход)',  # "3 подхода"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_clean, re.IGNORECASE)
            if match:
                exercise_name = text_clean[:match.start()].strip()
                sets_part = match.group(1)
                break
        
        if not sets_part:
            # Если ничего не найдено, возвращаем только название
            # Но сначала убираем лишние пробелы и очищаем название
            exercise_name = re.sub(r'\s+', ' ', exercise_name).strip()
            return exercise_name, []
    
    # Парсим подходы
    reps_list = []
    
    # Формат: "20-16-14-12" или "20–16–14–12" (список повторений с дефисом или длинным тире)
    if re.match(r'^\d+([\-–—]\d+)+$', sets_part):
        # Заменяем длинное тире на обычный дефис для парсинга
        normalized = sets_part.replace('–', '-').replace('—', '-')
        reps_list = [int(x) for x in normalized.split("-")]
    
    # Формат: "4x10", "4х10", "4×10" или "4*10" (количество подходов x повторения)
    # Поддерживаем символ × (умножение), * (звездочка), х, x и длинное тире в диапазонах "8–10"
    elif re.match(r'^\d+[xх×*]\d+$', sets_part) or re.match(r'^\d+[xх×*]\d+[–—\-]\d+$', sets_part):
        # Формат "4×8–10", "4*10-12", "3x10-12" (подходы × повторения-повторения)
        range_match = re.match(r'^(\d+)[xх×*](\d+)[–—\-](\d+)$', sets_part)
        if range_match:
            sets_count = int(range_match.group(1))
            min_reps = int(range_match.group(2))
            max_reps = int(range_match.group(3))
            # Используем минимальное значение для консервативности
            reps = min_reps
            reps_list = [reps] * sets_count
        else:
            # Формат "4×10", "4*10", "3x10" (просто число)
            match = re.match(r'^(\d+)[xх×*](\d+)$', sets_part)
            if match:
                sets_count = int(match.group(1))
                reps = int(match.group(2))
                reps_list = [reps] * sets_count
    
    # Формат: "4 подхода по 10 раз", "4 подхода по 10", "3 подхода 12 повторений", "3 подхода"
    elif re.search(r'подход', sets_part, re.IGNORECASE):
        # Формат "3 подхода 12 повторений" или "3 подхода по 12 повторений"
        match = re.search(r'(\d+)\s+подход[а-я]*\s+(?:по\s+)?(\d+)\s+повтор', sets_part, re.IGNORECASE)
        if match:
            sets_count = int(match.group(1))
            reps = int(match.group(2))
            reps_list = [reps] * sets_count
        else:
            # Формат "4 подхода по 10" или "4 подхода по 10 раз"
            match = re.search(r'(\d+)\s+подход[а-я]*\s+по\s+(\d+)', sets_part, re.IGNORECASE)
            if match:
                sets_count = int(match.group(1))
                reps = int(match.group(2))
                reps_list = [reps] * sets_count
            else:
                # Формат "3 подхода" (без указания повторений) - используем 10 повторений по умолчанию
                match = re.search(r'(\d+)\s+подход', sets_part, re.IGNORECASE)
                if match:
                    sets_count = int(match.group(1))
                    # По умолчанию 10 повторений, если не указано
                    reps = 10
                    reps_list = [reps] * sets_count
    
    # Формат: "4x10, 3x8" или "4×8–10" (несколько групп подходов или диапазоны)
    elif "," in sets_part or ";" in sets_part:
        parts = re.split(r'[,;]', sets_part)
        for part in parts:
            part = part.strip()
            # Формат "4×8–10", "4*10-12" (диапазон)
            range_match = re.match(r'^(\d+)[xх×*](\d+)[–—\-](\d+)$', part)
            if range_match:
                sets_count = int(range_match.group(1))
                min_reps = int(range_match.group(2))
                reps = min_reps  # Используем минимальное значение
                reps_list.extend([reps] * sets_count)
            # Формат "4x10", "4×10", "4*10"
            elif re.match(r'^\d+[xх×*]\d+$', part):
                match = re.match(r'^(\d+)[xх×*](\d+)$', part)
                if match:
                    sets_count = int(match.group(1))
                    reps = int(match.group(2))
                    reps_list.extend([reps] * sets_count)
            # Формат "10" (один подход)
            elif re.match(r'^\d+$', part):
                reps_list.append(int(part))
    
    # Если ничего не распарсилось, пытаемся извлечь числа
    if not reps_list:
        # Пытаемся найти паттерны подходов в тексте
        # Формат "25 кг / тяга в тренажере" - убираем вес и дополнительную информацию
        # Сначала удаляем вес и единицы измерения, а также текст после "/"
        sets_part_clean = re.sub(r'\d+\s*(кг|kg|lb|lbs)\s*[/\-]?\s*.*$', '', sets_part, flags=re.IGNORECASE)
        sets_part_clean = re.sub(r'/\s*.*$', '', sets_part_clean)  # Убираем текст после "/"
        sets_part_clean = sets_part_clean.strip()
        
        # Пытаемся найти числа в оставшейся части
        numbers = re.findall(r'\d+', sets_part_clean)
        if numbers:
            # Если нашли числа, используем их как повторения
            # Если только одно число и оно большое (>15) - это может быть вес, пропускаем
            # Если только одно число и оно маленькое (<20) - это может быть количество подходов или повторений
            if len(numbers) == 1:
                num = int(numbers[0])
                if num < 50:  # Вероятно, это количество повторений или подходов
                    reps_list = [num]
            else:
                # Несколько чисел - это список повторений (например, "20-12-15")
                # Но проверяем, что числа не слишком большие (не вес)
                filtered_numbers = [int(n) for n in numbers if int(n) < 50]
                if filtered_numbers:
                    reps_list = filtered_numbers
        elif re.search(r'\d+', sets_part):
            # Если есть числа в исходной части, но мы их не распарсили
            # Пытаемся извлечь все числа, но фильтруем большие (вероятно, это вес)
            numbers = re.findall(r'\d+', sets_part)
            if numbers:
                filtered_numbers = [int(n) for n in numbers if int(n) < 50]
                if filtered_numbers:
                    reps_list = filtered_numbers
    
    # Очищаем название упражнения от лишних пробелов и символов
    exercise_name = re.sub(r'\s+', ' ', exercise_name).strip()
    # Убираем информацию о весе из названия, если она осталась
    exercise_name = re.sub(r'\s*\d+\s*(кг|kg|lb|lbs)\s*[/\-]?\s*', '', exercise_name, flags=re.IGNORECASE)
    exercise_name = re.sub(r'\s*/\s*.*$', '', exercise_name)  # Убираем текст после "/"
    exercise_name = exercise_name.strip()
    
    return exercise_name, reps_list


def format_exercise_name(exercise_name: str, sets_count: int) -> str:
    """Форматирует название упражнения с количеством подходов."""
    return f"{exercise_name} — {sets_count} подхода"

