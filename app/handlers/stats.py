"""Обработчик статистики тренировок."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.db import crud
from app.utils.keyboards import (
    get_main_keyboard,
    get_programs_keyboard,
    get_workout_days_keyboard,
    get_exercises_keyboard,
    get_stats_back_keyboard
)

router = Router()


class StatsStates(StatesGroup):
    """Состояния для просмотра статистики."""
    selecting_program = State()
    selecting_day = State()
    selecting_exercise = State()


@router.message(F.text == "Посмотреть статистику")
async def cmd_view_stats(message: Message, state: FSMContext, session: AsyncSession):
    """Начало просмотра статистики."""
    user = await crud.get_or_create_user(session, message.from_user.id)
    programs = await crud.get_user_sessions(session, user.id)
    
    if not programs:
        await message.answer(
            "❌ У вас пока нет программ тренировок.\n\n"
            "Создайте программу через кнопку 'Добавить программу'.",
            reply_markup=get_main_keyboard()
        )
        return
    
    if len(programs) == 1:
        # Если программа одна, сразу переходим к выбору дня
        program = programs[0]
        await state.update_data(program_id=program.session_id, program_name=program.name)
        await show_workout_days(message, state, session, program.session_id)
    else:
        # Если программ несколько, предлагаем выбрать
        await state.set_state(StatsStates.selecting_program)
        await message.answer(
            "📊 Выберите программу для просмотра статистики:",
            reply_markup=get_programs_keyboard(programs, prefix="stats")
        )


@router.callback_query(F.data.startswith("stats_program_"))
async def select_program_for_stats(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Обработка выбора программы для статистики."""
    program_id = int(callback.data.split("_")[-1])
    program = await crud.get_session_by_id(session, program_id)
    
    if not program:
        await callback.answer("❌ Программа не найдена", show_alert=True)
        await callback.message.delete()
        await state.clear()
        return
    
    await state.update_data(program_id=program_id, program_name=program.name)
    await callback.message.delete()
    await show_workout_days(callback.message, state, session, program_id)


async def show_workout_days(message: Message, state: FSMContext, session: AsyncSession, program_id: int):
    """Показать список тренировочных дней."""
    days = await crud.get_workout_days(session, program_id)
    
    if not days:
        await message.answer(
            "❌ В этой программе нет тренировочных дней.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        return
    
    await state.set_state(StatsStates.selecting_day)
    await message.answer(
        "📅 Выберите тренировочный день:",
        reply_markup=get_workout_days_keyboard(days)
    )


@router.callback_query(F.data.startswith("select_day_"))
async def select_day_for_stats(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Обработка выбора дня для статистики."""
    # Проверяем, находимся ли мы в режиме статистики
    current_state = await state.get_state()
    if current_state != StatsStates.selecting_day.state:
        await callback.answer()
        return
    
    day_id = int(callback.data.split("_")[-1])
    day = await crud.get_workout_day_by_id(session, day_id)
    
    if not day:
        await callback.answer("❌ День не найден", show_alert=True)
        await callback.message.delete()
        await state.clear()
        return
    
    await state.update_data(day_id=day_id, day_name=day.name)
    await callback.message.delete()
    await show_exercises(callback.message, state, session, day_id)


async def show_exercises(message: Message, state: FSMContext, session: AsyncSession, day_id: int):
    """Показать список упражнений дня."""
    exercises = await crud.get_exercises_by_day(session, day_id)
    
    if not exercises:
        await message.answer(
            "❌ В этом дне нет упражнений.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        return
    
    await state.set_state(StatsStates.selecting_exercise)
    await message.answer(
        "💪 Выберите упражнение для просмотра статистики:",
        reply_markup=get_exercises_keyboard(exercises, prefix="stats")
    )


@router.callback_query(F.data.startswith("stats_exercise_"))
async def show_exercise_stats(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Показать статистику по упражнению."""
    exercise_id = int(callback.data.split("_")[-1])
    exercise = await crud.get_exercise_by_id(session, exercise_id)
    
    if not exercise:
        await callback.answer("❌ Упражнение не найдено", show_alert=True)
        await callback.message.delete()
        await state.clear()
        return
    
    data = await state.get_data()
    user = await crud.get_or_create_user(session, callback.from_user.id)
    
    # Получаем статистику
    stats = await crud.get_exercise_statistics(session, user.id, exercise_id)
    
    # Формируем сообщение
    text = f"📊 <b>Упражнение: {exercise.name}</b>\n\n"
    
    if not stats:
        text += "❌ По этому упражнению пока нет данных о выполненных подходах."
    else:
        # Сортируем подходы по индексу
        for set_index in sorted(stats.keys()):
            # Получаем информацию о подходе из шаблона
            set_info = None
            for s in exercise.sets:
                if s.set_index == set_index:
                    set_info = s
                    break
            
            reps = set_info.reps if set_info else "?"
            text += f"<b>{set_index + 1} Подход, {reps} повторений</b>\n"
            
            # Показываем историю весов
            for timestamp, weight in stats[set_index]:
                date_str = timestamp.strftime("%d.%m")
                text += f"{date_str} - {weight:.1f} КГ\n"
            
            text += "\n"
    
    # Кнопка "Назад"
    day_id = data.get("day_id")
    if day_id:
        await callback.message.edit_text(
            text,
            reply_markup=get_stats_back_keyboard("day", day_id),
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(text, parse_mode="HTML")
        await callback.message.answer(
            "◀️ Назад",
            reply_markup=get_main_keyboard()
        )


@router.callback_query(F.data.startswith("stats_back_"))
async def stats_back(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Обработка кнопки 'Назад' в статистике."""
    parts = callback.data.split("_")
    back_to = parts[2]  # day или program
    item_id = int(parts[3])
    
    await callback.message.delete()
    
    if back_to == "day":
        # Возврат к выбору упражнений
        data = await state.get_data()
        await state.update_data(day_id=item_id)
        await show_exercises(callback.message, state, session, item_id)
    elif back_to == "program":
        # Возврат к выбору дней
        data = await state.get_data()
        await state.update_data(program_id=item_id)
        await show_workout_days(callback.message, state, session, item_id)
    else:
        # Возврат в главное меню
        await state.clear()
        await callback.message.answer(
            "Главное меню",
            reply_markup=get_main_keyboard()
        )



