"""Обработчик AI ассистента для свободных сообщений."""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import crud
from app.services.ai_assistant import get_ai_response, is_ai_enabled
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
        "Начать тренировку"
    ]
    if message.text in main_menu_buttons:
        return  # Кнопки обрабатываются другими обработчиками
    
    # Проверяем, что пользователь не в процессе добавления программы или тренировки
    current_state = await state.get_state()
    if current_state is not None:
        return  # Пользователь в процессе, не перехватываем
    
    # Проверяем, включен ли AI
    if not is_ai_enabled():
        # Если AI не настроен, показываем подсказку с диагностикой
        import os
        ai_provider = os.getenv("AI_PROVIDER", "none")
        
        if ai_provider == "none":
            error_msg = (
                "🤖 AI ассистент не настроен.\n\n"
                "Для включения AI установите переменные окружения:\n"
                "• AI_PROVIDER (openai, yandex, anthropic, google, groq, ollama)\n"
                "• Соответствующий API ключ\n\n"
                "Используйте команды бота или меню для работы с программами."
            )
        else:
            error_msg = (
                f"🤖 AI ассистент временно недоступен.\n\n"
                f"Провайдер: {ai_provider}\n"
                f"Проверьте настройку API ключа в переменных окружения.\n\n"
                "Используйте команды бота или меню для работы с программами."
            )
        
        await message.answer(
            error_msg,
            reply_markup=get_main_keyboard()
        )
        return
    
    # Получаем контекст пользователя для AI
    user = await crud.get_or_create_user(session, message.from_user.id)
    programs = await crud.get_user_sessions(session, user.id)
    
    user_context = None
    if programs:
        programs_list = ", ".join([p.name for p in programs])
        user_context = f"У пользователя есть программы: {programs_list}"
    
    # Показываем индикатор печати
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    # Получаем ответ от AI
    try:
        ai_response = await get_ai_response(message.text, user_context)
        
        if ai_response:
            await message.answer(
                ai_response,
                reply_markup=get_main_keyboard()
            )
        else:
            # Если AI не ответил (ошибка API или другие проблемы)
            await message.answer(
                "🤖 Извините, не удалось получить ответ от AI ассистента.\n\n"
                "Возможные причины:\n"
                "• Проблемы с API провайдера\n"
                "• Неверный API ключ\n"
                "• Превышен лимит запросов\n\n"
                "Попробуйте позже или используйте команды бота.",
                reply_markup=get_main_keyboard()
            )
    except Exception as e:
        # Логируем ошибку
        import logging
        logging.error(f"AI handler error: {str(e)}", exc_info=True)
        
        await message.answer(
            "🤖 Произошла ошибка при обращении к AI ассистенту.\n\n"
            "Используйте команды бота или меню для работы с программами тренировок.",
            reply_markup=get_main_keyboard()
        )

