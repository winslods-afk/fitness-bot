"""Обработчик AI ассистента для свободных сообщений."""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import crud
from app.services.ai_assistant import get_ai_response, is_ai_enabled
from app.services.program_generator import is_program_text
from app.utils.keyboards import get_main_keyboard

router = Router()


@router.message(F.text)
async def handle_free_message(message: Message, state: FSMContext, session: AsyncSession):
    """
    Обработчик свободных сообщений пользователя.
    Отвечает через AI, если он настроен.
    """
    # Проверяем, что это не команда и не системное сообщение
    if message.text.startswith("/"):
        return  # Команды обрабатываются другими обработчиками
    
    # Проверяем, что это не кнопка из главного меню
    main_menu_buttons = [
        "Добавить программу",
        "Удалить программу",
        "Перезапустить Бота",
        "Начать тренировку",
        "Посмотреть статистику",
        "Мои Программы тренировок",  # Оставлено для обратной совместимости
        "◀️ Назад"
    ]
    if message.text in main_menu_buttons:
        return  # Кнопки обрабатываются другими обработчиками
    
    # Проверяем, что пользователь не в процессе добавления программы или тренировки
    current_state = await state.get_state()
    if current_state is not None:
        return  # Пользователь в процессе, не перехватываем
    
    # Проверяем, является ли текст программой тренировок
    if is_program_text(message.text):
        # Это программа, пусть обрабатывает ai_program.py
        return
    
    # Если это не программа, показываем сообщение
    await message.answer(
        "Простите, я не умею отвечать на ваши сообщения, пришлите мне программу тренировок.",
        reply_markup=get_main_keyboard()
    )

