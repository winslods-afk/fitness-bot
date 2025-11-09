"""Обработчик создания программы через AI."""
import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import crud
from app.config import MAX_PROGRAMS_PER_USER
from app.services.ai_assistant import get_ai_response, is_ai_enabled
from app.services.program_generator import parse_ai_program_response, format_program_for_ai_request
from app.services.parser import parse_exercise_string, format_exercise_name
from app.utils.keyboards import get_main_keyboard, get_confirm_keyboard
from app.utils.messages import get_program_limit_message

router = Router()


class AIProgramStates(StatesGroup):
    """Состояния для создания программы через AI."""
    waiting_for_confirmation = State()
    program_data = State()


def get_save_program_keyboard(program_name: str) -> InlineKeyboardMarkup:
    """Клавиатура для сохранения программы от AI."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Сохранить программу",
                    callback_data=f"save_ai_program_{program_name[:20]}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data="cancel_ai_program"
                )
            ]
        ]
    )


@router.message(F.text.regexp(r'(?i)(создай|сделай|нужна|хочу).*программ'))
async def detect_program_request(message: Message, state: FSMContext, session: AsyncSession):
    """Обнаружение запроса на создание программы."""
    if not is_ai_enabled():
        return  # AI не настроен, не обрабатываем
    
    # Проверяем, что пользователь не в процессе
    current_state = await state.get_state()
    if current_state is not None:
        return
    
    # Проверяем лимит программ
    user = await crud.get_or_create_user(session, message.from_user.id)
    programs_count = await crud.count_user_sessions(session, user.id)
    if programs_count >= MAX_PROGRAMS_PER_USER:
        await message.answer(
            get_program_limit_message(),
            reply_markup=get_main_keyboard()
        )
        return
    
    # Показываем индикатор печати
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    # Формируем запрос для AI
    ai_request = format_program_for_ai_request(message.text)
    
    # Получаем ответ от AI
    ai_response = await get_ai_response(ai_request)
    
    if not ai_response:
        await message.answer(
            "🤖 Не удалось создать программу через AI.\n\n"
            "Попробуйте создать программу вручную через меню «Добавить программу».",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Парсим программу из ответа AI
    program_data = parse_ai_program_response(ai_response)
    
    if not program_data or not program_data.get("days"):
        # Если не удалось распарсить, показываем ответ AI как есть
        await message.answer(
            f"🤖 AI создал программу, но не удалось её автоматически обработать.\n\n"
            f"{ai_response}\n\n"
            f"Вы можете скопировать программу и добавить её вручную через меню.",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Сохраняем данные программы в состояние
    await state.update_data(program_data=program_data)
    await state.set_state(AIProgramStates.waiting_for_confirmation)
    
    # Формируем предпросмотр программы
    preview = f"🤖 AI создал программу:\n\n"
    preview += f"📋 {program_data['name']}\n\n"
    
    for i, day in enumerate(program_data["days"], 1):
        preview += f"📅 День {i}: {day['name']}\n"
        for exercise in day["exercises"][:3]:  # Показываем первые 3 упражнения
            preview += f"  • {exercise}\n"
        if len(day["exercises"]) > 3:
            preview += f"  ... и ещё {len(day['exercises']) - 3} упражнений\n"
        preview += "\n"
    
    preview += "Сохранить эту программу?"
    
    await message.answer(
        preview,
        reply_markup=get_save_program_keyboard(program_data["name"])
    )


@router.callback_query(F.data.startswith("save_ai_program_"))
async def save_ai_program(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Сохранение программы, созданной AI."""
    await callback.answer()
    
    data = await state.get_data()
    program_data = data.get("program_data")
    
    if not program_data:
        await callback.message.edit_text("❌ Ошибка: данные программы не найдены.")
        return
    
    try:
        # Получаем пользователя
        user = await crud.get_or_create_user(session, callback.from_user.id)
        
        # Создаём программу
        session_obj = await crud.create_session(session, user.id, program_data["name"])
        
        # Создаём дни и упражнения
        for day_index, day_data in enumerate(program_data["days"]):
            workout_day = await crud.create_workout_day(
                session, session_obj.session_id, day_index, day_data["name"]
            )
            
            for exercise_order, exercise_text in enumerate(day_data["exercises"]):
                # Парсим упражнение
                exercise_name, reps_list = parse_exercise_string(exercise_text)
                
                if not exercise_name or not reps_list:
                    continue  # Пропускаем некорректные упражнения
                
                # Сохраняем исходный формат
                exercise_name_to_save = exercise_text
                
                # Создаём упражнение
                exercise = await crud.create_exercise(
                    session, workout_day.id, exercise_name_to_save, exercise_order
                )
                
                # Создаём подходы
                for set_index, reps in enumerate(reps_list, start=1):
                    await crud.create_set(session, exercise.exercise_id, set_index, reps)
        
        await state.clear()
        
        await callback.message.edit_text(
            f"✅ Программа «{program_data['name']}» успешно создана!\n\n"
            f"Добавлено дней: {len(program_data['days'])}\n"
            f"Теперь вы можете начать тренировку."
        )
        
        # Отправляем главное меню
        await callback.message.answer(
            "Выберите действие:",
            reply_markup=get_main_keyboard()
        )
        
    except Exception as e:
        import logging
        logging.error(f"Error saving AI program: {str(e)}", exc_info=True)
        await callback.message.edit_text(
            f"❌ Ошибка при сохранении программы: {str(e)}\n\n"
            f"Попробуйте создать программу вручную."
        )


@router.callback_query(F.data == "cancel_ai_program")
async def cancel_ai_program(callback: CallbackQuery, state: FSMContext):
    """Отмена сохранения программы от AI."""
    await callback.answer()
    await state.clear()
    await callback.message.edit_text("❌ Создание программы отменено.")
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=get_main_keyboard()
    )

