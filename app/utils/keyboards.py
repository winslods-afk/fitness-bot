"""Клавиатуры для бота."""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главная клавиатура с основными опциями."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Добавить программу"),
                KeyboardButton(text="Начать тренировку")
            ],
            [
                KeyboardButton(text="Удалить программу"),
                KeyboardButton(text="Посмотреть статистику")
            ],
            [KeyboardButton(text="Перезапустить Бота")],
        ],
        resize_keyboard=True,
        persistent=True
    )
    return keyboard


def get_programs_menu_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура подменю 'Мои Программы тренировок'."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Добавить программу"),
                KeyboardButton(text="Начать тренировку")
            ],
            [
                KeyboardButton(text="Удалить программу"),
                KeyboardButton(text="Посмотреть статистику")
            ],
            [KeyboardButton(text="◀️ Назад")],
        ],
        resize_keyboard=True,
        persistent=True
    )
    return keyboard


def get_add_program_method_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора способа добавления программы."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Внести по дням", callback_data="add_manual")],
            [InlineKeyboardButton(text="📋 Отправить готовую программу", callback_data="add_ready")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_programs_menu")],
        ]
    )


def get_days_count_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора количества дней."""
    buttons = []
    # Группируем по 2 кнопки в ряду
    for i in range(1, 8, 2):  # От 1 до 7 дней, шаг 2
        row = [InlineKeyboardButton(text=str(i), callback_data=f"days_{i}")]
        if i + 1 <= 7:
            row.append(InlineKeyboardButton(text=str(i + 1), callback_data=f"days_{i + 1}"))
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_programs_keyboard(programs: List, prefix: str = "select") -> InlineKeyboardMarkup:
    """Клавиатура для выбора программы."""
    buttons = []
    # Группируем по 2 кнопки в ряду
    for i in range(0, len(programs), 2):
        row = [
            InlineKeyboardButton(
                text=programs[i].name,
                callback_data=f"{prefix}_program_{programs[i].session_id}"
            )
        ]
        if i + 1 < len(programs):
            row.append(
                InlineKeyboardButton(
                    text=programs[i + 1].name,
                    callback_data=f"{prefix}_program_{programs[i + 1].session_id}"
                )
            )
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_workout_days_keyboard(days: List, prefix: str = "select_day") -> InlineKeyboardMarkup:
    """Клавиатура для выбора тренировочного дня."""
    buttons = []
    # Группируем по 2 кнопки в ряду
    for i in range(0, len(days), 2):
        row = [
            InlineKeyboardButton(
                text=days[i].name,
                callback_data=f"{prefix}_{days[i].id}"
            )
        ]
        if i + 1 < len(days):
            row.append(
                InlineKeyboardButton(
                    text=days[i + 1].name,
                    callback_data=f"{prefix}_{days[i + 1].id}"
                )
            )
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirm_keyboard(action: str, item_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения действия."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да",
                    callback_data=f"confirm_{action}_{item_id}"
                ),
                InlineKeyboardButton(
                    text="Нет",
                    callback_data=f"cancel_{action}_{item_id}"
                )
            ]
        ]
    )


def get_start_training_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для начала тренировки."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Начать", callback_data="start_training")],
            [InlineKeyboardButton(text="Отмена", callback_data="cancel_training")]
        ]
    )


def get_finish_day_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для завершения дня."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Завершить день", callback_data="finish_day")]
        ]
    )


def get_exercises_keyboard(exercises: List, prefix: str = "stats", back_to: Optional[str] = None, back_item_id: Optional[int] = None) -> InlineKeyboardMarkup:
    """Клавиатура для выбора упражнения."""
    buttons = []
    # Группируем по 2 кнопки в ряду
    for i in range(0, len(exercises), 2):
        row = [
            InlineKeyboardButton(
                text=exercises[i].name,
                callback_data=f"{prefix}_exercise_{exercises[i].exercise_id}"
            )
        ]
        if i + 1 < len(exercises):
            row.append(
                InlineKeyboardButton(
                    text=exercises[i + 1].name,
                    callback_data=f"{prefix}_exercise_{exercises[i + 1].exercise_id}"
                )
            )
        buttons.append(row)
    # Добавляем кнопку "Назад", если указаны параметры
    if back_to and back_item_id is not None:
        buttons.append([
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data=f"stats_back_{back_to}_{back_item_id}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_stats_back_keyboard(back_to: str, item_id: int) -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой 'Назад' для статистики."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data=f"stats_back_{back_to}_{item_id}")]
        ]
    )
