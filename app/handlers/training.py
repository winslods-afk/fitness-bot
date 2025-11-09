"""Обработчики для проведения тренировки."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import crud
from app.services.stats import get_comparison_stats
from app.utils.keyboards import (
    get_main_keyboard, 
    get_programs_keyboard, 
    get_workout_days_keyboard,
    get_start_training_keyboard,
    get_programs_menu_keyboard
)
from app.utils.messages import format_workout_day_info, format_training_summary

router = Router()


class TrainingStates(StatesGroup):
    """Состояния для проведения тренировки."""
    waiting_for_program = State()
    waiting_for_day = State()
    waiting_for_weight = State()
    current_session_run_id = State()
    current_exercises = State()
    current_exercise_index = State()
    current_set_index = State()


@router.message(F.text == "Начать тренировку")
async def start_training(message: Message, state: FSMContext, session: AsyncSession):
    """Начало процесса тренировки."""
    username = message.from_user.username
    user = await crud.get_or_create_user(session, message.from_user.id, username=username)
    programs = await crud.get_user_sessions(session, user.id)
    
    if not programs:
        await message.answer(
            "❌ У вас нет программ тренировок.\n\n"
            "Создайте программу через кнопку 'Добавить программу'.",
            reply_markup=get_programs_menu_keyboard()
        )
        return
    
    if len(programs) == 1:
        # Если программа одна, сразу переходим к выбору дня
        await state.update_data(selected_session_id=programs[0].session_id)
        await state.set_state(TrainingStates.waiting_for_day)
        await show_workout_days(message, session, programs[0].session_id)
    else:
        # Если программ несколько, предлагаем выбрать
        await state.set_state(TrainingStates.waiting_for_program)
        await message.answer(
            "Выберите программу для тренировки:",
            reply_markup=get_programs_keyboard(programs, prefix="train")
        )


@router.callback_query(F.data.startswith("train_program_"))
async def select_training_program(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Выбор программы для тренировки."""
    session_id = int(callback.data.split("_")[-1])
    await callback.answer()
    
    await state.update_data(selected_session_id=session_id)
    await state.set_state(TrainingStates.waiting_for_day)
    await show_workout_days(callback.message, session, session_id)


async def show_workout_days(message_or_callback, session: AsyncSession, session_id: int):
    """Показать список дней программы."""
    days = await crud.get_workout_days(session, session_id)
    
    if not days:
        text = "В этой программе нет тренировочных дней."
        if isinstance(message_or_callback, CallbackQuery):
            await message_or_callback.message.edit_text(text)
        else:
            await message_or_callback.answer(text, reply_markup=get_programs_menu_keyboard())
        return
    
    text = "Выберите тренировочный день:"
    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.edit_text(text, reply_markup=get_workout_days_keyboard(days))
    else:
        await message_or_callback.answer(text, reply_markup=get_workout_days_keyboard(days))


@router.callback_query(F.data.startswith("select_day_"))
async def select_training_day(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Выбор дня для тренировки."""
    current_state = await state.get_state()
    data = await state.get_data()
    
    # ПЕРВЫМ делом проверяем, не статистика ли это (stats_day_ обрабатывается в stats)
    if callback.data.startswith("stats_day_"):
        # Это статистика, пропускаем
        return
    
    # Проверяем, что это состояние тренировки
    is_training_state = current_state in [
        TrainingStates.waiting_for_day.state, 
        TrainingStates.waiting_for_program.state
    ]
    
    if not is_training_state:
        # Это не тренировка, пропускаем
        return
    
    day_id = int(callback.data.split("_")[-1])
    session_id = data.get("selected_session_id")
    
    # Если session_id не установлен, пытаемся получить из workout_day
    if not session_id:
        workout_day = await crud.get_workout_day_by_id(session, day_id)
        if workout_day:
            session_id = workout_day.session_id
            await state.update_data(selected_session_id=session_id)
        else:
            # Если не можем получить session_id, это не наша задача
            return
    
    await callback.answer()
    
    # Получаем день с упражнениями
    workout_day = await crud.get_workout_day_by_id(session, day_id)
    
    if not workout_day:
        await callback.message.edit_text("День не найден.")
        return
    
    # Получаем упражнения
    exercises = await crud.get_exercises_by_day(session, day_id)
    
    if not exercises:
        await callback.message.edit_text("В этом дне нет упражнений.")
        return
    
    # Формируем список упражнений и подходов для тренировки
    exercises_list = []
    for exercise in exercises:
        sets_list = []
        for set_obj in sorted(exercise.sets, key=lambda x: x.set_index):
            sets_list.append({
                "set_index": set_obj.set_index,
                "reps": set_obj.reps
            })
        exercises_list.append({
            "exercise_id": exercise.exercise_id,
            "name": exercise.name,
            "sets": sets_list
        })
    
    # Показываем информацию о дне
    day_info = format_workout_day_info(workout_day, exercises)
    await callback.message.edit_text(
        day_info + "\n\nГотовы начать тренировку?",
        reply_markup=get_start_training_keyboard()
    )
    
    # Сохраняем данные для тренировки
    await state.update_data(
        day_id=day_id,
        exercises=exercises_list,
        current_exercise_index=0,
        current_set_index=0
    )


@router.callback_query(F.data == "start_training")
async def begin_training(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Начало тренировки."""
    await callback.answer()
    
    data = await state.get_data()
    session_id = data.get("selected_session_id")
    exercises = data.get("exercises", [])
    
    if not exercises:
        await callback.message.edit_text("Ошибка: нет упражнений для тренировки.")
        return
    
    # Создаём запись о запуске тренировки
    username = callback.from_user.username
    user = await crud.get_or_create_user(session, callback.from_user.id, username=username)
    session_run = await crud.create_session_run(session, user.id, session_id)
    
    await state.update_data(
        current_session_run_id=session_run.id,
        current_user_id=user.id,  # Сохраняем user_id для использования в поиске
        current_exercise_index=0,
        current_set_index=0
    )
    await state.set_state(TrainingStates.waiting_for_weight)
    
    # Начинаем с первого упражнения и первого подхода
    # Обновляем data из состояния, чтобы получить актуальные значения
    data = await state.get_data()
    await ask_for_weight(callback.message, session, state, data)


async def ask_for_weight(
    message: Message, session: AsyncSession, state: FSMContext, data: dict
):
    """Запросить вес для текущего подхода."""
    exercises = data.get("exercises", [])
    current_exercise_index = data.get("current_exercise_index", 0)
    current_set_index = data.get("current_set_index", 0)
    
    if current_exercise_index >= len(exercises):
        # Тренировка завершена
        await finish_training(message, session, state, data)
        return
    
    exercise = exercises[current_exercise_index]
    sets = exercise["sets"]
    
    if current_set_index >= len(sets):
        # Переходим к следующему упражнению
        await state.update_data(
            current_exercise_index=current_exercise_index + 1,
            current_set_index=0
        )
        data = await state.get_data()
        await ask_for_weight(message, session, state, data)
        return
    
    current_set = sets[current_set_index]
    
    # Логируем для отладки
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Asking for weight: exercise_id={exercise['exercise_id']}, current_set_index={current_set_index}, set_index={current_set['set_index']}, reps={current_set['reps']}, total_sets={len(sets)}")
    
    # Получаем прошлый вес (если есть)
    # Используем user_id из состояния (из SessionRun), чтобы избежать проблем с разными user_id
    user_id = data.get("current_user_id")
    if not user_id:
        # Если user_id не сохранен в состоянии, получаем пользователя
        username = message.from_user.username
        user = await crud.get_or_create_user(session, message.from_user.id, username=username)
        user_id = user.id
        await state.update_data(current_user_id=user_id)
    
    logger.info(f"Searching for previous weight: user_id={user_id}, exercise_id={exercise['exercise_id']}, set_index={current_set['set_index']}, exercise_name='{exercise['name']}'")
    
    # Сначала пытаемся найти по exercise_id (для той же программы)
    last_weight = await crud.get_last_weight_for_set(
        session, user_id, exercise["exercise_id"], current_set["set_index"]
    )
    logger.info(f"Searching for last weight by exercise_id: found={last_weight is not None}, weight={last_weight}")
    
    # Если не нашли, ищем по названию упражнения (для других программ)
    if not last_weight:
        last_weight = await crud.get_last_weight_for_exercise_by_name(
            session, user_id, exercise["name"], current_set["set_index"]
        )
        logger.info(f"Searching for last weight by name: found={last_weight is not None}, weight={last_weight}, exercise_name='{exercise['name']}'")
    
    # Получаем информацию о прошлой тренировке для контекста
    last_performed_set = await crud.get_last_performed_set_for_exercise(
        session, user_id, exercise["exercise_id"], current_set["set_index"]
    )
    logger.info(f"Searching for last performed set by exercise_id: found={last_performed_set is not None}")
    
    # Если не нашли по ID, ищем по названию
    if not last_performed_set:
        last_performed_set = await crud.get_last_performed_set_for_exercise_by_name(
            session, user_id, exercise["name"], current_set["set_index"]
        )
        logger.info(f"Searching for last performed set by name: found={last_performed_set is not None}, exercise_name='{exercise['name']}'")
    
    # Формируем сообщение
    text = f"💪 {exercise['name']}\n"
    text += f"Подход {current_set['set_index']}: {current_set['reps']} раз\n\n"
    
    if last_weight:
        text += f"📊 Прошлый вес: {last_weight} кг\n"
        if last_performed_set and last_performed_set.timestamp:
            from datetime import datetime
            # Форматируем дату последней тренировки
            date_str = last_performed_set.timestamp.strftime("%d.%m.%Y")
            text += f"   (последняя тренировка: {date_str})\n"
        text += "\n"
    else:
        text += "📊 Это первый раз для этого подхода\n\n"
    
    text += "Введите вес для этого подхода (в кг):"
    
    bot_message = await message.answer(text)
    # Сохраняем ID сообщения для последующего удаления
    await state.update_data(last_bot_message_id=bot_message.message_id)


@router.message(TrainingStates.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext, session: AsyncSession):
    """Обработка введённого веса."""
    try:
        weight = float(message.text.replace(",", "."))
        
        if weight < 0:
            await message.answer("Вес не может быть отрицательным. Введите корректное значение:")
            return
        
        data = await state.get_data()
        exercises = data.get("exercises", [])
        current_exercise_index = data.get("current_exercise_index", 0)
        current_set_index = data.get("current_set_index", 0)
        session_run_id = data.get("current_session_run_id")
        
        if current_exercise_index >= len(exercises):
            await finish_training(message, session, state, data)
            return
        
        exercise = exercises[current_exercise_index]
        current_set = exercise["sets"][current_set_index]
        
        # Логируем для отладки
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Saving performed set: exercise_id={exercise['exercise_id']}, set_index={current_set['set_index']}, weight={weight}, session_run_id={session_run_id}")
        
        # Сохраняем выполненный подход
        await crud.create_performed_set(
            session,
            exercise["exercise_id"],
            current_set["set_index"],
            weight,
            session_run_id
        )
        
        logger.info(f"Performed set saved successfully")
        
        # Удаляем предыдущее сообщение бота и сообщение пользователя
        last_bot_msg_id = data.get("last_bot_message_id")
        try:
            if last_bot_msg_id:
                await message.bot.delete_message(message.chat.id, last_bot_msg_id)
            await message.delete()
        except Exception:
            pass  # Игнорируем ошибки удаления
        
        # Переходим к следующему подходу
        current_set_index += 1
        if current_set_index >= len(exercise["sets"]):
            # Упражнение завершено - показываем сообщение
            exercise_name = exercise["name"]
            # Извлекаем базовое название
            import re
            # Если это исходный формат (содержит " — числа"), извлекаем название до " —"
            if " — " in exercise_name or " - " in exercise_name:
                # Исходный формат: "Хаммер верхний — 16-10-12"
                base_name = re.split(r'\s*[—–-]\s*', exercise_name)[0].strip()
            else:
                # Форматированное название: "Хаммер верхний — 3 подхода"
                base_name = re.sub(r'\s*—\s*\d+\s+подхода?', '', exercise_name).strip()
            await message.answer(f"✅ Упражнение «{base_name}» завершено")
            
            # Переходим к следующему упражнению
            current_exercise_index += 1
            current_set_index = 0
        
        await state.update_data(
            current_exercise_index=current_exercise_index,
            current_set_index=current_set_index
        )
        
        # Запрашиваем вес для следующего подхода
        data = await state.get_data()
        await ask_for_weight(message, session, state, data)
        
    except ValueError:
        await message.answer("Пожалуйста, введите число (например: 20 или 20.5):")


async def finish_training(message: Message, session: AsyncSession, state: FSMContext, data: dict):
    """Завершение тренировки и показ итогов."""
    session_run_id = data.get("current_session_run_id")
    
    # Получаем все выполненные подходы
    performed_sets = await crud.get_performed_sets_by_run(session, session_run_id)
    
    if not performed_sets:
        await message.answer("Тренировка завершена, но данные не были сохранены.")
        await state.clear()
        return
    
    # Получаем название программы
    session_run = await crud.get_session_run(session, session_run_id)
    program_name = ""
    if session_run and session_run.session:
        program_name = session_run.session.name
    
    # Получаем статистику сравнения
    username = message.from_user.username
    user = await crud.get_or_create_user(session, message.from_user.id, username=username)
    stats = await get_comparison_stats(session, user.id, performed_sets)
    
    # Показываем сообщение о завершении тренировки
    if program_name:
        await message.answer(f"🎉 Тренировка «{program_name}» закончена!")
    else:
        await message.answer("🎉 Тренировка закончена!")
    
    # Формируем итоговое сообщение
    summary = format_training_summary(performed_sets, stats)
    
    await message.answer(summary, reply_markup=get_programs_menu_keyboard())
    await state.clear()


@router.callback_query(F.data == "cancel_training")
async def cancel_training(callback: CallbackQuery, state: FSMContext):
    """Отмена тренировки."""
    await state.clear()
    await callback.message.edit_text("Тренировка отменена.")
    await callback.answer()

