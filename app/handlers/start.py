"""Обработчики команды /start и главного меню."""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import crud
from app.utils.keyboards import get_main_keyboard
from app.utils.messages import get_welcome_message

router = Router()


@router.message(F.text == "Перезапустить Бота")
async def cmd_restart(message: Message, state: FSMContext):
    """Обработчик кнопки перезапуска."""
    await state.clear()
    await message.answer(
        get_welcome_message(),
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "/start")
@router.message(F.text == "/restart")
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession):
    """Обработчик команды /start."""
    await state.clear()
    
    # Создаём или получаем пользователя
    user = await crud.get_or_create_user(session, message.from_user.id)
    
    await message.answer(
        get_welcome_message(),
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "/help")
async def cmd_help(message: Message):
    """Обработчик команды /help."""
    help_text = (
        "📖 Помощь по использованию бота:\n\n"
        "• /start — начать работу с ботом\n"
        "• /restart — перезапустить бота\n"
        "• /myprograms — показать все ваши программы\n\n"
        "Основные функции:\n"
        "• Добавить программу — создать новую программу тренировок\n"
        "• Удалить программу — удалить существующую программу\n"
        "• Начать тренировку — провести тренировку по сохранённой программе\n\n"
        "При добавлении программы вы можете вводить упражнения в разных форматах:\n"
        "• Гакк-присед — 20-16-14-12\n"
        "• Гакк-присед — 4х10\n"
        "• Гакк-присед — 4 подхода по 10 раз"
    )
    await message.answer(help_text, reply_markup=get_main_keyboard())


@router.message(F.text == "/myprograms")
async def cmd_myprograms(message: Message, session: AsyncSession):
    """Обработчик команды /myprograms."""
    user = await crud.get_or_create_user(session, message.from_user.id)
    programs = await crud.get_user_sessions(session, user.id)
    
    if not programs:
        await message.answer(
            "У вас пока нет программ. Добавьте программу через меню.",
            reply_markup=get_main_keyboard()
        )
        return
    
    from app.utils.messages import format_program_list
    text = format_program_list(programs)
    
    await message.answer(text, reply_markup=get_main_keyboard())

