"""Обработчики для добавления программы тренировок."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import MAX_PROGRAMS_PER_USER
from app.db import crud
from app.services.parser import parse_exercise_string, format_exercise_name
from app.utils.keyboards import get_main_keyboard, get_days_count_keyboard
from app.utils.messages import get_program_limit_message

router = Router()


class AddProgramStates(StatesGroup):
    """Состояния для добавления программы."""
    waiting_for_days_count = State()
    waiting_for_day_name = State()
    waiting_for_exercise = State()
    waiting_for_program_name = State()
    current_day_index = State()
    current_days_count = State()
    program_data = State()  # Хранит временные данные программы


@router.message(F.text == "Добавить программу")
async def start_add_program(message: Message, state: FSMContext, session: AsyncSession):
    """Начало процесса добавления программы."""
    user = await crud.get_or_create_user(session, message.from_user.id)
    
    # Проверяем лимит программ
    programs_count = await crud.count_user_sessions(session, user.id)
    if programs_count >= MAX_PROGRAMS_PER_USER:
        await message.answer(
            get_program_limit_message(),
            reply_markup=get_main_keyboard()
        )
        return
    
    await state.set_state(AddProgramStates.waiting_for_days_count)
    await message.answer(
        "Сколько тренировочных дней будет в программе?",
        reply_markup=get_days_count_keyboard()
    )


@router.callback_query(F.data.startswith("days_"))
async def process_days_count(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора количества дней."""
    days_count = int(callback.data.split("_")[1])
    
    await state.update_data(
        days_count=days_count,
        current_day_index=0,
        program_data={"days": []}
    )
    await state.set_state(AddProgramStates.waiting_for_day_name)
    
    await callback.message.edit_text(
        f"Введите название для дня {days_count} (например: Спина, Грудь, Ноги):"
    )
    await callback.answer()


@router.message(AddProgramStates.waiting_for_day_name)
async def process_day_name(message: Message, state: FSMContext):
    """Обработка названия дня."""
    day_name = message.text.strip()
    
    if not day_name:
        await message.answer("Пожалуйста, введите название дня.")
        return
    
    data = await state.get_data()
    current_day_index = data.get("current_day_index", 0)
    days_count = data.get("days_count", 0)
    program_data = data.get("program_data", {"days": []})
    
    # Сохраняем день
    program_data["days"].append({
        "name": day_name,
        "exercises": []
    })
    
    await state.update_data(program_data=program_data)
    await state.set_state(AddProgramStates.waiting_for_exercise)
    
    await message.answer(
        f"День «{day_name}» добавлен.\n\n"
        f"Теперь добавьте упражнения для этого дня.\n"
        f"Формат: название упражнения — подходы\n\n"
        f"Примеры:\n"
        f"• Гакк-присед — 20-16-14-12\n"
        f"• Жим лёжа — 4х10\n"
        f"• Подтягивания — 4 подхода по 10 раз\n\n"
        f"Когда закончите с упражнениями для этого дня, отправьте /done"
    )


@router.message(AddProgramStates.waiting_for_exercise, F.text == "/done")
async def finish_day(message: Message, state: FSMContext):
    """Завершение добавления упражнений для дня."""
    data = await state.get_data()
    current_day_index = data.get("current_day_index", 0)
    days_count = data.get("days_count", 0)
    program_data = data.get("program_data", {"days": []})
    
    current_day_index += 1
    
    if current_day_index >= days_count:
        # Все дни добавлены, запрашиваем название программы
        await state.set_state(AddProgramStates.waiting_for_program_name)
        await message.answer(
            "Все дни добавлены! Введите название для программы:"
        )
    else:
        # Переходим к следующему дню
        await state.update_data(current_day_index=current_day_index)
        await state.set_state(AddProgramStates.waiting_for_day_name)
        await message.answer(
            f"Введите название для дня {current_day_index + 1}:"
        )


@router.message(AddProgramStates.waiting_for_exercise)
async def process_exercise(message: Message, state: FSMContext):
    """Обработка упражнения."""
    exercise_text = message.text.strip()
    
    if not exercise_text:
        await message.answer("Пожалуйста, введите упражнение в правильном формате.")
        return
    
    try:
        exercise_name, reps_list = parse_exercise_string(exercise_text)
        
        if not exercise_name:
            await message.answer("Не удалось распознать название упражнения. Попробуйте ещё раз.")
            return
        
        if not reps_list:
            await message.answer(
                "Не удалось распознать подходы. Используйте формат:\n"
                "• Название — 20-16-14-12\n"
                "• Название — 4х10\n"
                "• Название — 4 подхода по 10 раз"
            )
            return
        
        data = await state.get_data()
        program_data = data.get("program_data", {"days": []})
        current_day_index = data.get("current_day_index", 0)
        
        # Форматируем название упражнения
        formatted_name = format_exercise_name(exercise_name, len(reps_list))
        
        # Добавляем упражнение
        program_data["days"][current_day_index]["exercises"].append({
            "name": formatted_name,
            "reps": reps_list
        })
        
        await state.update_data(program_data=program_data)
        
        # Подтверждение
        sets_text = ", ".join([str(r) for r in reps_list])
        await message.answer(
            f"✅ Добавлено: {formatted_name}\n"
            f"Подходы: {sets_text}\n\n"
            f"Продолжайте добавлять упражнения или отправьте /done для завершения дня."
        )
        
    except Exception as e:
        await message.answer(
            f"Ошибка при обработке упражнения: {str(e)}\n"
            f"Попробуйте ввести в другом формате."
        )


@router.message(AddProgramStates.waiting_for_program_name)
async def process_program_name(message: Message, state: FSMContext, session: AsyncSession):
    """Обработка названия программы и сохранение в БД."""
    program_name = message.text.strip()
    
    if not program_name:
        await message.answer("Пожалуйста, введите название программы.")
        return
    
    data = await state.get_data()
    program_data = data.get("program_data", {"days": []})
    
    # Получаем пользователя
    user = await crud.get_or_create_user(session, message.from_user.id)
    
    # Создаём программу
    session_obj = await crud.create_session(session, user.id, program_name)
    
    # Создаём дни и упражнения
    for day_index, day_data in enumerate(program_data["days"]):
        workout_day = await crud.create_workout_day(
            session, session_obj.session_id, day_index, day_data["name"]
        )
        
        for exercise_order, exercise_data in enumerate(day_data["exercises"]):
            exercise = await crud.create_exercise(
                session, workout_day.id, exercise_data["name"], exercise_order
            )
            
            # Создаём подходы
            for set_index, reps in enumerate(exercise_data["reps"], start=1):
                await crud.create_set(session, exercise.exercise_id, set_index, reps)
    
    await state.clear()
    
    await message.answer(
        f"✅ Программа «{program_name}» успешно создана!\n\n"
        f"Добавлено дней: {len(program_data['days'])}\n"
        f"Теперь вы можете начать тренировку.",
        reply_markup=get_main_keyboard()
    )

