"""Клавиатуры для бота."""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главная клавиатура с основными опциями."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить программу")],
            [KeyboardButton(text="Удалить программу")],
            [KeyboardButton(text="Посмотреть статистику")],
            [KeyboardButton(text="Начать тренировку")],
            [KeyboardButton(text="Перезапустить Бота")],
        ],
        resize_keyboard=True,
        persistent=True
    )
    return keyboard


def get_days_count_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора количества дней."""
    buttons = []
    for i in range(1, 8):  # От 1 до 7 дней
        buttons.append([InlineKeyboardButton(text=str(i), callback_data=f"days_{i}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_programs_keyboard(programs: List, prefix: str = "select") -> InlineKeyboardMarkup:
    """Клавиатура для выбора программы."""
    buttons = []
    for program in programs:
        buttons.append([
            InlineKeyboardButton(
                text=program.name,
                callback_data=f"{prefix}_program_{program.session_id}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_workout_days_keyboard(days: List) -> InlineKeyboardMarkup:
    """Клавиатура для выбора тренировочного дня."""
    buttons = []
    for day in days:
        buttons.append([
            InlineKeyboardButton(
                text=day.name,
                callback_data=f"select_day_{day.id}"
            )
        ])
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


def get_exercises_keyboard(exercises: List, prefix: str = "stats") -> InlineKeyboardMarkup:
    """Клавиатура для выбора упражнения."""
    buttons = []
    for exercise in exercises:
        buttons.append([
            InlineKeyboardButton(
                text=exercise.name,
                callback_data=f"{prefix}_exercise_{exercise.exercise_id}"
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
